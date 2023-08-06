""" 
Launcher script to launch EvnDispProd5SingJob on the WMS or create a Transformation
https://forge.in2p3.fr/issues/441709
https://forge.in2p3.fr/issues/49828

Usage:
python prod5b_sing_evndisp_launcher.py TS <trans_prefix> <dataset name or ascii file with a list of datasets> <group_size>

In testing mode (WMS):
python prod5b_sing_evndisp_launcher.py WMS

Arguments:
mode: WMS for testing, TS for production
Arguments with TS mode:
trans_prefix: prefix to add to the name of the transformation
input_dataset: name of the input dataset
group_size: n files to process

Example:
python prod5b_sing_evndisp_launcher.py TS EvnDispRepro Prod5b_LaPalma_AdvancedBaseline_NSB1x_electron_North_40deg_DL0 5
"""
import os
from copy import copy

from DIRAC.Core.Base import Script
Script.parseCommandLine()

import DIRAC
from CTADIRAC.Core.Utilities.tool_box import read_inputs_from_file
from DIRAC.TransformationSystem.Client.Transformation import Transformation
from CTADIRAC.Interfaces.API.EvnDispProd5SingJob import EvnDispProd5SingJob
from DIRAC.Core.Workflow.Parameter import Parameter
from DIRAC.Interfaces.API.Dirac import Dirac
from CTADIRAC.Core.Utilities.tool_box import get_dataset_MQ

def submit_trans(job, trans_name, input_meta_query, group_size):
  """ Create a transformation executing the job workflow
  """
  DIRAC.gLogger.notice('submit_trans : %s' % trans_name)

  # Initialize JOB_ID
  job.workflow.addParameter(Parameter("JOB_ID", "000000", "string", "", "",
                                      True, False, "Temporary fix"))

  trans = Transformation()
  trans.setTransformationName(trans_name)  # this must be unique
  trans.setType("DataReprocessing")
  trans.setDescription("Prod5 EventDisplay TS")
  trans.setLongDescription("Prod5 EventDisplay processing")  # mandatory
  trans.setBody(job.workflow.toXML())
  trans.setGroupSize(group_size)
  trans.setInputMetaQuery(input_meta_query)
  res = trans.addTransformation()  # transformation is created here
  if not res['OK']:
    return res
  trans.setStatus("Active")
  trans.setAgentType("Automatic")
  trans_id = trans.getTransformationID()
  return trans_id


def submit_wms(job):
  """ Submit the job to the WMS
  @todo launch job locally
  """
  dirac = Dirac()
  input_data = ['/vo.cta.in2p3.fr/MC/PROD5b/Paranal/electron/sim_telarray/2432/Data/000xxx/electron_40deg_0deg_run104___cta-prod5b-paranal_desert-2147m-Paranal-dark.simtel.zst']
  job.setInputData(input_data)
  job.setJobGroup('EvnDispProd5')
  res = dirac.submitJob(job)
  if res['OK']:
    Script.gLogger.notice('Submitted job: ', res['Value'])
  return res


def launch_job(args):
  """ Simple launcher to instanciate a Job and setup parameters
      from positional arguments given on the command line.

      Parameters:
      args -- mode (trans_name dataset_name group_size)
  """
  DIRAC.gLogger.notice('Launching EventDisplay processing')
  # get arguments
  mode = args[0]

  if mode == 'TS':
    name_prefix = args[1]
    group_size = int(args[3])

    dataset_list = []
    if os.path.isfile(args[2]):
      DIRAC.gLogger.notice('Reading datasets from input file:', args[2])
      dataset_list = read_inputs_from_file(args[2])
    else:
      dataset_list.append(args[2])

  # use this mode for testing
  if mode == 'WMS':
    # create a job instance 
    job = EvnDispProd5SingJob(cpuTime=259200.)
    # set the version 
    job.version = 'eventdisplay-cta-dl1-prod5.v06'
    job.setName('Prod5b_EvnDisp')
    # set output SB
    job.setOutputSandbox(['*Log.txt'])
    job.base_path = '/vo.cta.in2p3.fr/user/a/arrabito'
    job.ts_task_id = '62'
    
    # just to test the metadata functionality
    # the following metadata values are arbitrary 
    simtel_meta_data = {'array_layout': 'Advanced-Baseline', 'site': 'LaPalma', 
                        'particle': 'proton', 'phiP': 0.0, 'thetaP': 20.0}
    job.set_meta_data(simtel_meta_data)
    job.set_file_meta_data(nsb=1)
    job.setupWorkflow(debug=True)
    res = submit_wms(job)

  # use this mode for production
  elif mode == 'TS':
    
    for dataset_name in dataset_list:
      job = EvnDispProd5SingJob(cpuTime=259200.)
      # set the version here
      job.version = 'eventdisplay-cta-dl1-prod5.v06'
      job.setName('Prod5b_EvnDisp')
      # set output SB
      job.setOutputSandbox(['*Log.txt'])

      # set the metadata
      input_meta_query = get_dataset_MQ(dataset_name)
      output_meta_data = copy(input_meta_query)
      job.set_meta_data(output_meta_data)
      job.set_file_meta_data(nsb=output_meta_data['nsb']['='])

      # define the job steps
      job.ts_task_id = '@{JOB_ID}'  # dynamic
      job.setupWorkflow(debug=False)
      job.setType('EvnDispProcessing')  # mandatory *here*

      # submit the transformations
      trans_name = name_prefix + '_' + dataset_name      
      res = submit_trans(job, trans_name, input_meta_query, group_size)
  else:
    DIRAC.gLogger.error('1st argument should be the submission mode: WMS or TS,\n\
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
