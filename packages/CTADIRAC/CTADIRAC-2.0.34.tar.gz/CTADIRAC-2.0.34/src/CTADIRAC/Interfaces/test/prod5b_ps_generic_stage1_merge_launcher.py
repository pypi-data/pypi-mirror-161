"""
    Launcher script to launch a production with 3 steps on a train or test dataset
    processing step: Prod5CtaPipeModelingJob
    2 successive merging steps : Prod5CtaPipeMergeJob
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
            "  input_dataset: name of the input dataset (already split)",
            "\ne.g: python %s.py Train_Merge ProdTestAF_LaPalma_AdvancedBaseline_gamma_train"
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


def define_meta_query(dl0_data_set, merged=0):
    """Return meta query"""

    meta_query = get_dataset_MQ(dl0_data_set)

    meta_data = {
        "MCCampaign": meta_query["MCCampaign"],
        "array_layout": meta_query["array_layout"],
        "site": meta_query["site"],
        "particle": meta_query["particle"],
        "phiP": meta_query["phiP"],
        "thetaP": meta_query["thetaP"],
        "configuration_id": meta_query["configuration_id"],
        "outputType": meta_query["outputType"],
        "stage1_prog_version": "v0.15.0",
        "merged": {"=": merged},
        "split": meta_query["split"]
    }
    return meta_data


def build_processing_step(dl0_data_set):
    """Setup ctapipe step

    @return ProductionStep object
    """

    prod_step_1 = ProductionStep()
    prod_step_1.Name = "Processing_ctapipe"
    DIRAC.gLogger.notice("\tBuilding Processing Production step: %s" % prod_step_1.Name)
    prod_step_1.Type = "DataReprocessing"
    prod_step_1.Inputquery = get_dataset_MQ(dl0_data_set)

    # Here define the job description (i.e. Name, Executable, etc.)
    # to be associated to the first ProductionStep, as done when using the TS
    job1 = Prod5CtaPipeModelingJob(cpuTime=259200.0)
    job1.setName("Prod5_ctapipe_modeling")
    job1.setOutputSandbox(["*Log.txt"])
    job1.base_path = "/vo.cta.in2p3.fr/user/a/afaure/prod5b"

    output_meta_data = deepcopy(prod_step_1.Inputquery)
    job1.set_meta_data(output_meta_data)
    job1.set_file_meta_data(split=output_meta_data["split"])
    output_query = define_meta_query(dl0_data_set, merged=0)

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
    prod_step_1.GroupSize = 5
    # return ProductionStep object
    return prod_step_1


def build_merging_step(parent_prod_step, group_size, merged=0):
    """Merge files from different runs from a split dataset

    @return ProductionStep object
    """

    prod_step_2 = ProductionStep()
    prod_step_2.Name = "Merge"
    DIRAC.gLogger.notice("\tBuilding Merging Production step: %s" % prod_step_2.Name)
    prod_step_2.Type = "Merging"  # This corresponds to the Transformation Type
    prod_step_2.Inputquery = parent_prod_step.Outputquery
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

    output_meta_data['merged']['='] = merged + 1
    prod_step_2.Outputquery = output_meta_data
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
    prod_name = "ProdTestAF_generic_%s" % args[0]
    DIRAC.gLogger.notice("Building new production: %s" % prod_name)
    prod_sys_client = ProductionClient()

    ##################################
    # Define the first ProductionStep (ctapipe with train or test data)
    prod_step_1 = build_processing_step(dl0_data_set)
    # Add the step to the production
    prod_sys_client.addProductionStep(prod_step_1)

    ###################################
    # Define first merging step and add it to the production
    prod_step_2 = build_merging_step(prod_step_1, 5, merged=0)
    prod_step_2.ParentStep = prod_step_1
    prod_sys_client.addProductionStep(prod_step_2)
    # # Define second merging step and add it to the production
    prod_step_3 = build_merging_step(prod_step_2, 2, merged=1)
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
