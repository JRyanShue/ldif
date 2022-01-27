# Copyright 2020 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# Lint as: python3
"""Trains a ldif network locally."""

# Commands required in-between imports to silence tensorflow
# pylint: disable=g-import-not-at-top
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

import sys
import time

from absl import app
from absl import flags

import numpy as np

import tensorflow as tf
tf.compat.v1.logging.set_verbosity(tf.compat.v1.logging.ERROR)

# LDIF is an internal package, should be imported last.
# pylint: disable=g-bad-import-order
from ldif.datasets import local_inputs
from ldif.util import gaps_util
from ldif.inference import example
from ldif.model import hparams
from ldif.inference import experiment as experiments
from ldif.training import shared_launcher
from ldif.util import file_util
from ldif.util import gpu_util
from ldif.util import path_util
from ldif.util.file_util import log
# pylint: enable=g-bad-import-order
# pylint: enable=g-import-not-at-top

FLAGS = flags.FLAGS

flags.DEFINE_integer('batch_size', 1, 'The batch size to use when training.')

flags.DEFINE_integer(
    'summary_step_interval', 10,
    'Summaries are written on step indices divisible by this number.')

flags.DEFINE_integer(
    'checkpoint_interval', 250,
    'Model checkpoints are written at the end of training, and at step'
    ' indices divisible by this number. Here written does not mean permanently'
    ' saved, due to how tf.train.Saver works. There is a maximum number of'
    ' checkpoints written before old checkpoints are erased, and a permanent'
    ' save frequency.')


flags.DEFINE_string(
    'experiment_name', 'reproduce-ldif',
    'The name of the experiment. It will be saved to disk under this name,'
    ' and can be reloaded for inference, eval, interactive notebooks, or'
    ' further training by providing this experiment_name. To resume training'
    ' from an already partially trained model, simply provide an experiment'
    ' name that is already written. Note that global step will be reloaded.')

flags.DEFINE_integer(
    'train_step_count', 1000000,
    'The number of training steps to take before training is complete.')

flags.DEFINE_string(
    'model_directory', 'trained_models/',
    'The path to the trained model root directory. Can be'
    ' absolute or relative to the LDIF repository root.')

flags.DEFINE_string(
    'dataset_directory', '',
    'The path to the dataset generated by meshes2dataset.py'
    ' Must be provided. The train split will be used.')

flags.DEFINE_string('split', 'train', 'The split to train on.')

flags.DEFINE_boolean(
    'visualize', False, 'If true, visualizes the training'
    ' data before training. Useful for debugging data errors.')

flags.DEFINE_string('model_type', 'ldif', 'The type of model to train. Can be'
                    'ldif (the LDIF paper model), sif (the SIF paper)'
                    ', or sif++ (an improved version of SIF using the LDIF'
                    ' architecture changes)')

flags.DEFINE_string('log_level', 'INFO',
                    'One of VERBOSE, INFO, WARNING, ERROR. Sets logs to print '
                    'only at or above the specified level.')

flags.DEFINE_boolean('reserve_memory_for_inference_kernel', True,
                     'Normally TensorFlow preallocates the entire GPU\'s memory'
                     ' when the session is created. The inference CUDA'
                     ' executable requires some memory to run. This flag stops'
                     ' TensorFlow from allocating everything, leaving ~1GB'
                     ' for the kernel (enough for 512^3 reconstruction).'
                     ' Automatically disabled on MacOS.')


def build_model_config(dataset):
  """Creates the ModelConfig object, which contains model hyperparameters."""
  # TODO(kgenova) This needs to somehow at least support LDIF/SIF/SingleView.
  # TODO(kgenova) Add support for eval/inference.
  builder_fun_dict = {
      'ldif': hparams.build_ldif_hparams,
      'sif': hparams.build_sif_hparams,
      'sif++': hparams.build_improved_sif_hparams
  }
  model_config = experiments.ModelConfig(builder_fun_dict[FLAGS.model_type]())
  model_config.hparams.bs = FLAGS.batch_size
  model_config.train = True
  model_config.eval = False
  model_config.inference = False
  model_config.inputs['dataset'] = dataset
  model_config.inputs['split'] = FLAGS.split
  model_config.inputs['proto'] = 'ShapeNetNSSDodecaSparseLRGMediumSlimPC'
  # This function is defined by the library; we don't need it, but
  # the launcher may call it.
  model_config.wrap_optimizer = lambda x: x
  return model_config


def visualize_data(session, dataset):
  """Visualizes the dataset with two interactive visualizer windows."""
  (bounding_box_samples, depth_renders, mesh_name, near_surface_samples, grid,
   world2grid, surface_point_samples) = session.run([
       dataset.bounding_box_samples, dataset.depth_renders, dataset.mesh_name,
       dataset.near_surface_samples, dataset.grid, dataset.world2grid,
       dataset.surface_point_samples
   ])
  gaps_util.ptsview(
      [bounding_box_samples, near_surface_samples, surface_point_samples])
  mesh_name = mesh_name.decode(sys.getdefaultencoding())
  log.info(f'depth max: {np.max(depth_renders)}')
  log.info(f'Mesh name: {mesh_name}')
  assert '|' in mesh_name
  mesh_hash = mesh_name[mesh_name.find('|') + 1:]
  log.info(f'Mesh hash: {mesh_hash}')
  dyn_obj = example.InferenceExample(FLAGS.split, 'airplane', mesh_hash)

  gaps_util.gapsview(
      msh=dyn_obj.normalized_gt_mesh,
      pts=near_surface_samples[:, :3],
      grd=grid,
      world2grid=world2grid,
      grid_threshold=-0.07)


def get_model_root():
  """Finds the path to the trained model's root directory based on flags."""
  ldif_abspath = path_util.get_path_to_ldif_root()
  model_dir_is_relative = FLAGS.model_directory[0] != '/'
  if model_dir_is_relative:
    model_dir_path = os.path.join(ldif_abspath, FLAGS.model_directory)
  else:
    model_dir_path = FLAGS.model_directory
  if not os.path.isdir(model_dir_path):
    os.makedirs(model_dir_path)
  return model_dir_path


def main(argv):
  if len(argv) > 1:
    raise app.UsageError('Too many command-line arguments.')
  tf.disable_v2_behavior()
  log.set_level(FLAGS.log_level)

  log.info('Making dataset...')
  if not FLAGS.dataset_directory:
    raise ValueError('A dataset directory must be provided.')
  if not os.path.isdir(FLAGS.dataset_directory):
    raise ValueError(f'No dataset directory found at {FLAGS.dataset_directory}')
  # TODO(kgenova) This batch size should match.
  dataset = local_inputs.make_dataset(
      FLAGS.dataset_directory,
      mode='train',
      batch_size=FLAGS.batch_size,
      split=FLAGS.split)

  # Sets up the hyperparameters and tf.Dataset
  model_config = build_model_config(dataset)

  # Generates the graph for a single train step, including summaries
  shared_launcher.sif_transcoder(model_config)
  summary_op = tf.summary.merge_all()
  global_step_op = tf.compat.v1.train.get_global_step()

  saver = tf.train.Saver(
      max_to_keep=5, pad_step_number=False, save_relative_paths=True)

  init_op = tf.initialize_all_variables()

  model_root = get_model_root()

  experiment_dir = f'{model_root}/sif-transcoder-{FLAGS.experiment_name}'
  checkpoint_dir = f'{experiment_dir}/1-hparams/train/'

  if FLAGS.reserve_memory_for_inference_kernel and sys.platform != "darwin" and False: # Disabled this block with 'and False'
    current_free = gpu_util.get_free_gpu_memory(0)
    allowable = current_free - (1024 + 512)  # ~1GB
    allowable_fraction = allowable / current_free
    if allowable_fraction <= 0.0:
      raise ValueError(f"Can't leave 1GB over for the inference kernel, because"
                       f" there is only {allowable} total free GPU memory.")
    log.info(f'TensorFlow can use up to {allowable_fraction*100}% of the total'
             ' GPU memory.')
  else:
    allowable_fraction = 1.0
  gpu_options = tf.GPUOptions(
      per_process_gpu_memory_fraction=allowable_fraction)

  with tf.Session(config=tf.ConfigProto(gpu_options=gpu_options)) as session:
    writer = tf.summary.FileWriter(f'{experiment_dir}/log', session.graph)
    log.info('Initializing variables...')
    session.run([init_op])

    if FLAGS.visualize:
      visualize_data(session, model_config.inputs['dataset'])

    # Check whether the checkpoint directory already exists (resuming) or
    # needs to be created (new model).
    if not os.path.isdir(checkpoint_dir):
      log.info('No previous checkpoint detected, training from scratch.')
      os.makedirs(checkpoint_dir)
      # Serialize hparams so eval can load them:
      hparam_path = f'{checkpoint_dir}/hparam_pickle.txt'
      if not file_util.exists(hparam_path):
        hparams.write_hparams(model_config.hparams, hparam_path)
      initial_index = 0
    else:
      log.info(
          f'Checkpoint root {checkpoint_dir} exists, attempting to resume.')
      latest_checkpoint = tf.train.latest_checkpoint(checkpoint_dir)
      log.info(f'Latest checkpoint: {latest_checkpoint}')
      saver.restore(session, latest_checkpoint)
      initial_index = session.run(global_step_op)
      log.info(f'The global step is {initial_index}')
      initial_index = int(initial_index)
      log.info(f'Parsed to {initial_index}')
    start_time = time.time()
    log_every = 10
    for i in range(initial_index, FLAGS.train_step_count):
      log.verbose(f'Starting step {i}...')
      is_summary_step = i % FLAGS.summary_step_interval == 0
      if is_summary_step:
        _, summaries, loss = session.run(
            [model_config.train_op, summary_op, model_config.loss])
        writer.add_summary(summaries, i)
      else:
        _, loss = session.run([model_config.train_op, model_config.loss])
      if not (i % log_every):
        end_time = time.time()
        steps_per_second = float(log_every) / (end_time - start_time)
        start_time = end_time
        log.info(f'Step: {i}\tLoss: {loss}\tSteps/second: {steps_per_second}')

      is_checkpoint_step = i % FLAGS.checkpoint_interval == 0
      if is_checkpoint_step or i == FLAGS.train_step_count - 1:
        ckpt_path = os.path.join(checkpoint_dir, 'model.ckpt')
        log.info(f'Writing checkpoint to {ckpt_path}...')
        saver.save(session, ckpt_path, global_step=i)
    log.info('Done training!')


if __name__ == '__main__':
  app.run(main)
