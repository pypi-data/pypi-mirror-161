"""
    Launcher script to launch a production with 3 steps
    simulation Step: Prod5bMCPipeNSBJob
    processing Step: Prod5CtaPipeModelingJob
    merging step : Prod5CtaPipeMergeJob
"""

__RCSID__ = "$Id$"

import json
from copy import deepcopy

from DIRAC.Core.Base import Script

Script.setUsageMessage(
    "\n".join(
        [
            __doc__.split("\n")[1],
            "Usage:",
            "python %s.py <mode> <site> <particle> <pointing> <zenith> <n showers>"
            % Script.scriptName,
            "Arguments:",
            "  name: name of the production",
            "  site: either Paranal or LaPalma",
            "  particle: in gamma, gamma-diffuse, electron, proton",
            "  pointing: North or South",
            "  zenith: 20, 40 or 60",
            "  n shower: 100 for testing",
            "\ne.g: python %s.py Merge1 Paranal gamma North 20 100" % Script.scriptName,
        ]
    )
)
Script.parseCommandLine()
import DIRAC

from DIRAC.ProductionSystem.Client.ProductionClient import ProductionClient
from DIRAC.ProductionSystem.Client.ProductionStep import ProductionStep
from CTADIRAC.Interfaces.API.Prod5bMCPipeNSBJob import Prod5bMCPipeNSBJob
from CTADIRAC.Interfaces.API.Prod5CtaPipeModelingJob import Prod5CtaPipeModelingJob
from CTADIRAC.Interfaces.API.Prod5CtaPipeMergeJob import Prod5CtaPipeMergeJob


def define_meta_data_DL0(args):
    """Return meta query"""
    if args[3] == "North":
        phiP = 180.0
    elif args[3] == "South":
        phiP = 0

    dl0_meta_data = {
        "array_layout": "Advanced-Baseline",
        "site": args[1],
        "particle": args[2],
        "phiP": phiP,
        "thetaP": args[4],
        "data_level": 0,
        "nsb": 1,
        "outputType": "Data",
        "MCCampaign": "ProdTestAF"
    }
    return dl0_meta_data


def build_simulation_step(dl0_meta_data, args):
    """Setup MC simulation step

    @return ProductionStep object
    """
    prod_step_1 = ProductionStep()
    prod_step_1.Name = "MC_Simulation"
    DIRAC.gLogger.notice("\tBuilding Processing Production step: %s" % prod_step_1.Name)
    prod_step_1.Type = "MCSimulation"
    prod_step_1.Outputquery = dl0_meta_data

    # job setup
    job1 = Prod5bMCPipeNSBJob()  # to be adjusted!!
    job1.version = "2020-06-29b"
    job1.compiler = "gcc83_matchcpu"
    # override for testing
    job1.setName("Prod5b_MC_Pipeline_NSB")
    # parameters from command line
    job1.set_site(args[1])
    job1.set_particle(args[2])
    job1.set_pointing_dir(args[3])
    job1.zenith_angle = args[4]
    job1.n_shower = args[5]

    # output
    job1.base_path = "/vo.cta.in2p3.fr/user/a/afaure/prod5b/"
    job1.setOutputSandbox(["*Log.txt"])
    job1.start_run_number = "0"
    job1.run_number = "@{JOB_ID}"  # dynamic
    job1.output_file_size = 10000  # 200 MB
    job1.setupWorkflow(debug=False)
    # Add the job description to the first ProductionStep
    prod_step_1.Body = job1.workflow.toXML()
    # return ProductionStep object
    return prod_step_1


def build_processing_step(dl0_meta_data):
    """Setup ctapipe step

    @return ProductionStep object
    """
    prod_step_2 = ProductionStep()
    prod_step_2.Name = "Processing_ctapipe"
    DIRAC.gLogger.notice("\tBuilding Processing Production step: %s" % prod_step_2.Name)
    prod_step_2.Type = "DataReprocessing"
    prod_step_2.Inputquery = dl0_meta_data

    # Here define the job description (i.e. Name, Executable, etc.)
    # to be associated to the first ProductionStep, as done when using the TS
    job2 = Prod5CtaPipeModelingJob(cpuTime=259200.0)
    job2.setName("Prod5_ctapipe_modeling")
    job2.setOutputSandbox(["*Log.txt"])
    job2.base_path = "/vo.cta.in2p3.fr/user/a/afaure/prod5b"

    output_meta_data = deepcopy(prod_step_2.Inputquery)
    job2.set_meta_data(output_meta_data)
    job2.set_file_meta_data(nsb=output_meta_data["nsb"])
    prod_step_2.Outputquery = job2.metadata

    # configuration
    # set site dependent config
    cta_site = prod_step_2.Inputquery["site"].lower()
    if cta_site == "paranal":
        job2.ctapipe_site_config = "prod5b_paranal_alpha_nectarcam.yml"
    elif cta_site == "lapalma":
        job2.ctapipe_site_config = "prod5b_lapalma_alpha.yml"

    job2.setupWorkflow(debug=False)
    job2.setType("Stage1Processing")  # mandatory *here*

    # Add the job description to the first ProductionStep
    prod_step_2.Body = job2.workflow.toXML()
    prod_step_2.GroupSize = 5  # have to match the above group size?

    # return ProductionStep object
    return prod_step_2


def build_merging_step(prod_step_2):
    """Merge files from different runs

    @return ProductionStep object
    """

    prod_step_3 = ProductionStep()
    prod_step_3.Name = "Merge"
    DIRAC.gLogger.notice("\tBuilding Merging Production step: %s" % prod_step_3.Name)
    prod_step_3.Type = "Merging"  # This corresponds to the Transformation Type
    prod_step_3.Inputquery = prod_step_2.Outputquery
    prod_step_3.Outputquery = deepcopy(prod_step_3.Inputquery)

    # Here define the job description to be associated to the second ProductionStep
    job3 = Prod5CtaPipeMergeJob(cpuTime=259200.0)
    job3.setName("Prod5_ctapipe_merging")
    job3.base_path = "/vo.cta.in2p3.fr/user/a/afaure/prod5b"

    # output
    job3.setOutputSandbox(["*Log.txt"])
    # refine output meta data if needed
    output_meta_data = deepcopy(prod_step_3.Inputquery)
    job3.set_meta_data(output_meta_data)
    job3.set_file_meta_data(nsb=1)

    job3.ts_task_id = "@{JOB_ID}"  # dynamic
    job3.setupWorkflow(debug=False)
    job3.setType("Merging")  # mandatory *here*
    prod_step_3.Body = job3.workflow.toXML()
    prod_step_3.GroupSize = 5  # number of files to merge
    # return ProductionStep object
    return prod_step_3


########################################################
if __name__ == "__main__":

    arguments = Script.getPositionalArgs()
    if len(arguments) != 6:
        Script.showHelp()
    ##################################
    # Create the production
    prod_name = "ProdTestAF%s" % arguments[0]
    DIRAC.gLogger.notice("Building new production: %s" % prod_name)
    prod_sys_client = ProductionClient()

    dl0_meta_data = define_meta_data_DL0(arguments)
    dl1_meta_data = deepcopy(dl0_meta_data)
    dl1_meta_data["data_level"] = 1
    # Define the first ProductionStep (MC simulation)
    prod_step_1 = build_simulation_step(dl0_meta_data, arguments)
    # Add the step to the production
    prod_sys_client.addProductionStep(prod_step_1)
    ##################################
    # Define the second ProductionStep (ctapipe)
    prod_step_2 = build_processing_step(dl0_meta_data)
    prod_step_2.ParentStep = prod_step_1
    # Add the step to the production
    prod_sys_client.addProductionStep(prod_step_2)

    # ##################################
    # # Define merging step and add them to the production
    prod_step_3 = build_merging_step(prod_step_2)
    prod_step_3.ParentStep = prod_step_2
    prod_sys_client.addProductionStep(prod_step_3)

    ##################################
    # Get the production description
    prod_description = prod_sys_client.prodDescription
    # Create the production
    DIRAC.gLogger.notice("Creating production.")
    res = prod_sys_client.addProduction(prod_name, json.dumps(prod_description))
    if not res["OK"]:
        DIRAC.gLogger.error(res["Message"])
        DIRAC.exit(-1)

    # Start the production, i.e. instantiate the transformation steps
    res = prod_sys_client.startProduction(prod_name)

    if not res["OK"]:
        DIRAC.gLogger.error(res["Message"])
        DIRAC.exit(-1)

    DIRAC.gLogger.notice("Production %s successfully created" % prod_name)
