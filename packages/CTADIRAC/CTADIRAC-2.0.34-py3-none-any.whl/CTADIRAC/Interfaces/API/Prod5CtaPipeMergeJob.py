"""
  Simple Wrapper on the Job class to run ctapipe merging tool
"""

__RCSID__ = "$Id$"

# generic imports
import json

# DIRAC imports
from CTADIRAC.Interfaces.API.Prod5Stage1Job import Prod5Stage1Job


class Prod5CtaPipeMergeJob(Prod5Stage1Job):
    """Job extension class for ctapipe processing"""

    def __init__(self, cpuTime=432000):
        """Constructor

        Keyword arguments:
        cpuTime -- max cpu time allowed for the job
        """
        Prod5Stage1Job.__init__(self)
        self.setCPUTime(cpuTime)
        # defaults
        self.version = "v0.15.0"
        self.setName("ctapipe_merge")
        self.prog_name = "ctapipe-merge"
        self.configuration_id = 7
        self.output_data_level = 2

    def set_meta_data(self, metadata):
        """Set meta data

        Parameters:
        metadata -- metadata dictionary from the telescope simulation
        """
        # # Set directory meta data
        self.metadata["array_layout"] = metadata["array_layout"]
        self.metadata["site"] = metadata["site"]
        self.metadata["particle"] = metadata["particle"]

        try:
            phiP = metadata["phiP"]["="]
        except BaseException:
            phiP = metadata["phiP"]
        self.metadata["phiP"] = phiP
        try:
            thetaP = metadata["thetaP"]["="]
        except BaseException:
            thetaP = metadata["thetaP"]
        self.metadata["thetaP"] = thetaP
        # metadata values for output data are refined here
        self.metadata[self.program_category + "_prog"] = self.prog_name
        self.metadata[self.program_category + "_prog_version"] = self.version
        self.metadata["data_level"] = self.output_data_level
        self.metadata["configuration_id"] = self.configuration_id
        # There can be multiple stages of merging
        # For each stage of merging we add +1
        try:
            merged = metadata["merged"]["="]
        except BaseException:
            merged = metadata["merged"]
        self.metadata["merged"] = merged + 1

    def setupWorkflow(self, debug=False):
        """Setup job workflow by defining the sequence of all executables
        All parameters shall have been defined before that method is called.
        """
        i_step = 0
        # step 1 -- debug
        if debug:
            ls_step = self.setExecutable("/bin/ls -alhtr", logFile="LS_Init_Log.txt")
            ls_step["Value"]["name"] = "Step%i_LS_Init" % i_step
            ls_step["Value"]["descr_short"] = "list files in working directory"
            i_step += 1

            env_step = self.setExecutable("/bin/env", logFile="Env_Log.txt")
            env_step["Value"]["name"] = "Step%i_Env" % i_step
            env_step["Value"]["descr_short"] = "Dump environment"
            i_step += 1

        # step 2
        sw_step = self.setExecutable(
            "cta-prod-setup-software",
            arguments="-p %s -v %s -a stage1 -g %s"
            % (self.package, self.version, self.compiler),
            logFile="SetupSoftware_Log.txt",
        )
        sw_step["Value"]["name"] = "Step%i_SetupSoftware" % i_step
        sw_step["Value"]["descr_short"] = "Setup software"
        i_step += 1

        # step 3 run merge
        merge_step = self.setExecutable(
            "./dirac_run_stage1_merge",
            logFile="ctapipe_merge_Log.txt",
        )
        merge_step["Value"]["name"] = "Step%i_ctapipe_merge" % i_step
        merge_step["Value"]["descr_short"] = "Run ctapipe merge"
        i_step += 1

        # step 4 set meta data and register Data
        meta_data_json = json.dumps(self.metadata)
        file_meta_data_json = json.dumps(self.file_meta_data)

        meta_data_field = {
            "array_layout": "VARCHAR(128)",
            "site": "VARCHAR(128)",
            "particle": "VARCHAR(128)",
            "phiP": "float",
            "thetaP": "float",
            self.program_category + "_prog": "VARCHAR(128)",
            self.program_category + "_prog_version": "VARCHAR(128)",
            "data_level": "int",
            "configuration_id": "int",
            "merged": "int",
        }
        meta_data_field_json = json.dumps(meta_data_field)

        # register Data
        data_output_pattern = "./Data/*.h5"  # %self.output_data_level
        dm_step = self.setExecutable(
            "cta-prod-managedata",
            arguments="'%s' '%s' '%s' %s '%s' %s %s '%s' Data"
            % (
                meta_data_json,
                meta_data_field_json,
                file_meta_data_json,
                self.base_path,
                data_output_pattern,
                self.package,
                self.program_category,
                self.catalogs,
            ),
            logFile="DataManagement_Log.txt",
        )
        dm_step["Value"]["name"] = "Step%s_DataManagement" % i_step
        dm_step["Value"][
            "descr_short"
        ] = "Save data files to SE and register them in DFC"
        i_step += 1

        # step 6 failover step
        failover_step = self.setExecutable(
            "/bin/ls -l", modulesList=["Script", "FailoverRequest"]
        )
        failover_step["Value"]["name"] = "Step%s_Failover" % i_step
        failover_step["Value"]["descr_short"] = "Tag files as unused if job failed"
        i_step += 1

        # Step 7 - debug only
        if debug:
            ls_step = self.setExecutable("/bin/ls -Ralhtr", logFile="LS_End_Log.txt")
            ls_step["Value"]["name"] = "Step%s_LSHOME_End" % i_step
            ls_step["Value"]["descr_short"] = "list files in Home directory"
            i_step += 1
