"""
    Launcher script to launch a production with 2 steps on a split dataset test/train
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
            "python %s.py <name> <dataset>" % Script.scriptName,
            "Arguments:",
            "  name: name of the production",
            "  input_dataset: name of the input dataset",
            "\ne.g: python %s.py Split_Merge ProdTestAF_LaPalma_AdvancedBaseline_gamma"
            % Script.scriptName,
        ]
    )
)
Script.parseCommandLine()
import DIRAC

from DIRAC.ProductionSystem.Client.ProductionClient import ProductionClient
from DIRAC.ProductionSystem.Client.ProductionStep import ProductionStep
from CTADIRAC.Interfaces.API.Prod5CtaPipeModelingJob import Prod5CtaPipeModelingJob
from CTADIRAC.Core.Utilities.tool_box import get_dataset_MQ
from CTADIRAC.Interfaces.API.Prod5CtaPipeMergeJob import Prod5CtaPipeMergeJob


def define_meta_query(dl0_data_set, split="train", merged=0):
    """Return meta query"""

    meta_query = get_dataset_MQ(dl0_data_set)

    meta_data = {
        "array_layout": meta_query["array_layout"],
        "site": meta_query["site"],
        "particle": meta_query["particle"],
        "phiP": meta_query["phiP"],
        "thetaP": meta_query["thetaP"],
        "configuration_id": {"=": 7},
        "outputType": "Data",
        "MCCampaign": "ProdTestAF",
        "stage1_prog_version": "v0.15.0",
        "merged": {"=": merged},
        "split": split
    }
    return meta_data


def build_processing_step(dl0_data_set, split="train"):
    """Setup ctapipe step

    @return ProductionStep object
    """

    if split == "train":
        DIRAC.gLogger.notice("Train Analysis")
        dl0_data_set_split = dl0_data_set + "_train"
    elif split == "test":
        DIRAC.gLogger.notice("Test Analysis")
        dl0_data_set_split = dl0_data_set + "_test"

    prod_step_1 = ProductionStep()
    prod_step_1.Name = "Processing_ctapipe"
    DIRAC.gLogger.notice("\tBuilding Processing Production step: %s" % prod_step_1.Name)
    prod_step_1.Type = "DataReprocessing"
    prod_step_1.Inputquery = get_dataset_MQ(dl0_data_set_split)
    # Here define the job description (i.e. Name, Executable, etc.)
    # to be associated to the first ProductionStep, as done when using the TS
    job1 = Prod5CtaPipeModelingJob(cpuTime=259200.0)
    job1.setName("Prod5_ctapipe_modeling")
    job1.setOutputSandbox(["*Log.txt"])
    job1.base_path = "/vo.cta.in2p3.fr/user/a/afaure/prod5b"

    output_meta_data = deepcopy(prod_step_1.Inputquery)
    job1.set_meta_data(output_meta_data)
    job1.set_file_meta_data(split=output_meta_data["split"])
    output_query = define_meta_query(dl0_data_set_split, split, merged=0)
    prod_step_1.Outputquery = output_query

    # configuration
    # set site dependent config
    cta_site = prod_step_1.Inputquery["site"].lower()
    if cta_site == "paranal":
        job1.ctapipe_site_config = "prod5b_paranal_alpha_nectarcam.yml"
    elif cta_site == "lapalma":
        job1.ctapipe_site_config = "prod5b_lapalma_alpha.yml"

    job1.setupWorkflow(debug=False)
    job1.setType("Stage1Processing")  # mandatory *here*

    # Add the job description to the first ProductionStep
    prod_step_1.Body = job1.workflow.toXML()
    prod_step_1.GroupSize = 5  # have to match the above group size?

    # return ProductionStep object
    return prod_step_1


def build_merging_step(dl0_data_set, group_size, split="train", merged=0):
    """Merge files from different runs from a split dataset

    @return ProductionStep object
    """

    prod_step_2 = ProductionStep()
    prod_step_2.Name = "Merge"
    DIRAC.gLogger.notice("\tBuilding Merging Production step: %s" % prod_step_2.Name)
    prod_step_2.Type = "Merging"  # This corresponds to the Transformation Type
    prod_step_2.Inputquery = define_meta_query(dl0_data_set, split, merged)

    # Here define the job description to be associated to the second ProductionStep
    job2 = Prod5CtaPipeMergeJob(cpuTime=259200.0)
    job2.setName("Prod5_ctapipe_merging")
    job2.base_path = "/vo.cta.in2p3.fr/user/a/afaure/prod5b"

    # output
    job2.setOutputSandbox(["*Log.txt"])
    # refine output meta data if needed
    output_meta_data = deepcopy(prod_step_2.Inputquery)
    job2.set_meta_data(output_meta_data)
    job2.set_file_meta_data(split=output_meta_data["split"])

    prod_step_2.Outputquery = define_meta_query(dl0_data_set, split, merged + 1)

    job2.setupWorkflow(debug=False)
    job2.setType("Merging")  # mandatory *here*
    prod_step_2.Body = job2.workflow.toXML()
    prod_step_2.GroupSize = group_size  # number of files to merge
    # return ProductionStep object
    return prod_step_2


########################################################
if __name__ == "__main__":
    args = Script.getPositionalArgs()
    if len(args) != 2:
        Script.showHelp()
    dl0_data_set = args[1]

    ##################################
    # Create the production
    prod_name = "ProdTestAF_split_%s" % args[0]
    DIRAC.gLogger.notice("Building new production: %s" % prod_name)
    prod_sys_client = ProductionClient()

    ##################################
    # Define the first ProductionStep (ctapipe with train data)
    prod_step_1 = build_processing_step(dl0_data_set, split="train")
    # Add the step to the production
    prod_sys_client.addProductionStep(prod_step_1)

    ##################################
    # Define the second ProductionStep (ctapipe with test data)
    prod_step_2 = build_processing_step(dl0_data_set, split="test")
    # Add the step to the production
    prod_sys_client.addProductionStep(prod_step_2)

    ###################################
    # Merging steps : 5 train files (group_size = 5) / 10 test files (group_size = 5 then 2)
    # Define merging step for train data and add it to the production
    prod_step_3 = build_merging_step(dl0_data_set, 5, split="train", merged=0)
    prod_step_3.ParentStep = prod_step_1
    prod_sys_client.addProductionStep(prod_step_3)
    ###################################
    # Define first merging step for test data and add it to the production
    prod_step_4 = build_merging_step(dl0_data_set, 5, split="test", merged=0)
    prod_step_4.ParentStep = prod_step_2
    prod_sys_client.addProductionStep(prod_step_4)
    # # Define second merging step for merged test data and add it to the production
    prod_step_5 = build_merging_step(dl0_data_set, 2, split="test", merged=1)
    prod_step_5.ParentStep = prod_step_4
    prod_sys_client.addProductionStep(prod_step_5)

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
