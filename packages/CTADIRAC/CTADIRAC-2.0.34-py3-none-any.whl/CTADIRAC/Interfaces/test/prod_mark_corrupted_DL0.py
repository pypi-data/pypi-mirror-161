'''
Launcher script to mark corrupted DL0 files with nsb=-1 on the WMS or create a Transformation.
https://forge.in2p3.fr/issues/48807

Usage:
python prod_mark_corrupted_DL0.py TS <trans_prefix> <dataset name or ascii file with a list of datasets> <group_size>

In testing mode (WMS):
python prod_mark_corrupted_DL0.py WMS

Arguments:
mode: WMS for testing, TS for production
Arguments with TS mode:
trans_prefix: prefix to add to the name of the transformation
input_dataset: name of the input dataset
group_size: n files to process

Example:
python prod_mark_corrupted_DL0.py TS Mark Prod5b_Paranal_AdvancedBaseline_NSB1x_proton_South_40deg_DL0 10
'''

import os

import DIRAC
from DIRAC import gLogger
from DIRAC.Core.Base import Script
Script.parseCommandLine(ignoreErrors=True)

from CTADIRAC.Core.Utilities.tool_box import read_inputs_from_file
from DIRAC.TransformationSystem.Client.Transformation import Transformation
from DIRAC.Interfaces.API.Job import Job
from DIRAC.Core.Workflow.Parameter import Parameter
from DIRAC.Interfaces.API.Dirac import Dirac
from CTADIRAC.Core.Utilities.tool_box import get_dataset_MQ


def submit_trans(job, trans_name, input_meta_query, group_size):
  """ Create a transformation executing the job workflow
  """
  gLogger.notice('submit_trans : %s' % trans_name)

  # Initialize JOB_ID
  job.workflow.addParameter(Parameter("JOB_ID", "000000", "string", "", "",
                                      True, False, "Temporary fix"))

  trans = Transformation()
  trans.setTransformationName(trans_name)  # this must be unique
  trans.setType("DataReprocessing")
  trans.setDescription("Mark corrupted DL0 files")
  trans.setLongDescription("Mark corrupted DL0 files")  # mandatory
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
  input_data = ['/vo.cta.in2p3.fr/MC/PROD5b/Paranal/proton/sim_telarray/2455/Data/022xxx/proton_40deg_180deg_run22498___cta-prod5b-paranal_desert-2147m-Paranal-dark.simtel.zst',
           '/vo.cta.in2p3.fr/MC/PROD5b/Paranal/proton/sim_telarray/2455/Data/033xxx/proton_40deg_180deg_run33920___cta-prod5b-paranal_desert-2147m-Paranal-dark.simtel.zst',
           '/vo.cta.in2p3.fr/MC/PROD5b/Paranal/proton/sim_telarray/2455/Data/000xxx/proton_40deg_180deg_run100___cta-prod5b-paranal_desert-2147m-Paranal-dark.simtel.zst']
  job.setInputData(input_data)
  job.setJobGroup('Mark corrupted DL0 files')
  result = dirac.submitJob(job)
  if result['OK']:
    gLogger.notice('Submitted job:', result['Value'])
  return result

def launch_job(args):
  """ Simple launcher to instanciate a Job and setup parameters
      from positional arguments given on the command line.

      Parameters:
      args -- mode (trans_name dataset_name group_size)
  """
  # get arguments
  mode = args[0]

  if mode == 'TS':
    name_prefix = args[1]
    group_size = int(args[3])

    dataset_list = []
    if os.path.isfile(args[2]):
      gLogger.notice('Reading datasets from input file:', args[2])
      dataset_list = read_inputs_from_file(args[2])
    else:
      dataset_list.append(args[2])


  job = Job()
  job.setName('Mark corrupted DL0 files')
  # output
  job.setOutputSandbox(['*Log.txt'])
  package = 'corsika_simtelarray'
  version = '2020-06-29b'
  compiler = 'gcc83_matchcpu'
  job.setType('Reprocessing_BySE')

  # Set executables
  job.setExecutable('cta-prod-setup-software',
                                 arguments='-p %s -v %s -a simulations -g %s' %
                                 (package, version, compiler),
                                 logFile='SetupSoftware_Log.txt')
  job.setExecutable('cta-prod-mark-corrupted-DL0',logFile='MarkCorruptedDL0_Log.txt')
  job.setExecutable('/bin/ls -l', modulesList=['Script', 'FailoverRequest'])

  if mode == 'WMS':
    result = submit_wms(job)
  elif mode == 'TS':
    for dataset_name in dataset_list:
      input_meta_query = get_dataset_MQ(dataset_name)
      trans_name = name_prefix + '_' + dataset_name
      result = submit_trans(job, trans_name, input_meta_query, group_size)
  else:
    gLogger.error('1st argument should be the job mode: WMS or TS,\n\
                             not %s' % mode)
    return None

  return result


#########################################################
if __name__ == '__main__':
  arguments = Script.getPositionalArgs()
  if len(arguments) not in [1, 4]:
    Script.showHelp()
  try:
    result = launch_job(arguments)
    if not result['OK']:
      gLogger.error(result['Message'])
      DIRAC.exit(-1)
    else:
      gLogger.notice('Done')
  except Exception:
    gLogger.exception()
    DIRAC.exit(-1)
