"""
Launcher script to launch Prod5Stage1MergeJob on the WMS or create a Transformation

Usage:
python prod5_stage1_merge_launcher.py TS <trans_prefix> <dataset name or ascii file with a list of datasets> <group_size>

In testing mode (WMS):
python prod5_stage1_merge_launcher.py WMS

Arguments:
mode: WMS for testing, TS for production
Arguments with TS mode:
trans_prefix: prefix to add to the name of the transformation
input_dataset: name of the input dataset
group_size: n files to process

Example:
python prod5_ctapipe_merge_launcher.py TS ctapipe_merge Prod5_Paranal_AdvancedBaseline_NSB1x_gamma-diffuse_North_20deg_DL2_train_en 25
"""
import os
from copy import copy

from DIRAC.Core.Base import Script
Script.parseCommandLine()

import DIRAC
from CTADIRAC.Core.Utilities.tool_box import read_inputs_from_file
from DIRAC.TransformationSystem.Client.Transformation import Transformation
from CTADIRAC.Interfaces.API.Prod5CtaPipeMergeJob import Prod5CtaPipeMergeJob
from DIRAC.Interfaces.API.Dirac import Dirac
from CTADIRAC.Core.Utilities.tool_box import get_dataset_MQ


def submit_trans(job, trans_name, input_meta_query, group_size):
  """ Create a transformation executing the job workflow
  """
  DIRAC.gLogger.notice('submit_trans : %s' % trans_name)

  trans = Transformation()
  trans.setTransformationName(trans_name)  # this must be unique
  trans.setType("Merging")
  trans.setDescription("ctapipe merge")
  trans.setLongDescription("ctapipe merge trans")  # mandatory
  trans.setBody(job.workflow.toXML())
  trans.setGroupSize(group_size)
  trans.setInputMetaQuery(input_meta_query)
  result = trans.addTransformation()  # transformation is created here
  if not result['OK']:
    return result
  trans.setStatus("Active")
  trans.setAgentType("Automatic")
  trans_id = trans.getTransformationID()
  return trans_id


def submit_wms(job):
  """ Submit the job to the WMS
  @todo launch job locally
  """
  dirac = Dirac()
  base_path = '/vo.cta.in2p3.fr/MC/PROD5/Paranal/gamma-diffuse/ctapipe-modeling/3008/Data/000xxx/'
  input_data = ['%s/gamma_20deg_0deg_run100___cta-prod5-paranal_desert-2147m-Paranal-dark_cone10.modeling.DL2.h5' % base_path,
                '%s/gamma_20deg_0deg_run101___cta-prod5-paranal_desert-2147m-Paranal-dark_cone10.modeling.DL2.h5' % base_path]

  job.setInputData(input_data)
  job.setJobGroup('prod5_ctapipe_merge')
  result = dirac.submitJob(job)
  if result['OK']:
    Script.gLogger.notice('Submitted job: ', result['Value'])
  return result

def launch_job(args):
  """ Simple launcher to instanciate a Job and setup parameters
      from positional arguments given on the command line.

      Parameters:
      args -- mode (trans_name dataset_name group_size)
  """
  DIRAC.gLogger.notice('Launching ctapipe merging')
  # get arguments
  mode = args[0]

  # use this mode for testing
  if mode == 'WMS':
    # job setup
    job = Prod5CtaPipeMergeJob(cpuTime=259200.)
    job.version = 'v0.15.0'
    # job.stage1_config = 'stage1_config_Prod3_LaPalma_Baseline_NSB1x.json'
    job.setName('Prod5_ctapipe_merge')
    job.setOutputSandbox(['*Log.txt'])

    job.base_path = '/vo.cta.in2p3.fr/user/a/arrabito'
    output_meta_data = {'array_layout': 'Advanced-Baseline', 'site': 'Paranal',
                     'particle': 'gamma-diffuse', 'phiP': 180.0, 'thetaP': 20.0,
                     'data_level': 2, 'outputType': 'Data',
                     'MCCampaign': 'PROD5', 'stage1_prog': 'ctapipe-merge',
                     'stage1_prog_version': 'v0.15.0'}

    job.set_meta_data(output_meta_data)
    job.set_file_meta_data(nsb=1, split='train_en')
    job.setupWorkflow(debug=True)
    res = submit_wms(job)

  # use this mode for production
  if mode == 'TS':
    # get arguments
    name_prefix = args[1]
    group_size = int(args[3])

    dataset_list = []
    if os.path.isfile(args[2]):
      DIRAC.gLogger.notice('Reading datasets from input file:', args[2])
      dataset_list = read_inputs_from_file(args[2])
    else:
      dataset_list.append(args[2])

    for dataset_name in dataset_list:
      # job setup
      job = Prod5CtaPipeMergeJob(cpuTime=259200.)
      job.version = 'v0.15.0'
      job.setName('Prod5_ctapipe_merge')
      job.setOutputSandbox(['*Log.txt'])
      job.base_path = '/vo.cta.in2p3.fr/MC/PROD5'

      # set meta data for output data

      # start with input metadata
      input_meta_query = get_dataset_MQ(dataset_name)
      output_meta_data = copy(input_meta_query)
      # then refine some metadata in the Job module
      job.set_meta_data(output_meta_data)
      job.set_file_meta_data(nsb=output_meta_data['nsb']['='],split=output_meta_data['split'])

      # define the job steps
      job.setupWorkflow(debug=False)
      job.setType('Merging')  # mandatory *here*

    # submit the transformations
      trans_name = name_prefix + '_' + dataset_name
      res = submit_trans(job, trans_name, input_meta_query, group_size)
  else:
    DIRAC.gLogger.error('1st argument should be the job mode: WMS or TS,\n\
                             not %s' % mode)
    return None

  return res


#########################################################
if __name__ == '__main__':

  arguments = Script.getPositionalArgs()
  if len(arguments) not in [1, 4]:
    Script.showHelp()
  try:
    res = launch_job(arguments)
    if not res['OK']:
      DIRAC.gLogger.error(res['Message'])
      DIRAC.exit(-1)
    else:
      DIRAC.gLogger.notice('Done')
  except Exception:
    DIRAC.gLogger.exception()
    DIRAC.exit(-1)
