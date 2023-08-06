"""
  Simple Wrapper on the Job class to run a ctapipe modeling job
"""

__RCSID__ = "$Id$"

# generic imports
import json

# DIRAC imports
from CTADIRAC.Interfaces.API.Prod5Stage1Job import Prod5Stage1Job


class Prod5CtaPipeModelingJob(Prod5Stage1Job):
    """ Job extension class for ctapipe stage1 modeling processing,
    """

    def __init__(self, cpuTime=432000):
        """ Constructor

    Keyword arguments:
    cpuTime -- max cpu time allowed for the job
    """
        Prod5Stage1Job.__init__(self)
        self.setCPUTime(cpuTime)
        # defaults
        self.version = 'v0.15.0'
        self.setName('ctapipe_modeling')
        self.program_category = 'stage1'
        self.prog_name = 'ctapipe-modeling'
        self.ctapipe_base_dl2_config = 'base_dl2_config.yml'
        self.ctapipe_site_config = 'prod5b_paranal_alpha_nectarcam.yml'
        self.configuration_id = 7
        self.output_data_level = 2

    def setupWorkflow(self, debug=False):
        """ Setup job workflow by defining the sequence of all executables
        All parameters shall have been defined before that method is called.
    """
        i_step = 0
        # step 1 -- debug
        if debug:
            ls_step = self.setExecutable('/bin/ls -alhtr', logFile='LS_Init_Log.txt')
            ls_step['Value']['name'] = 'Step%i_LS_Init' % i_step
            ls_step['Value']['descr_short'] = 'list files in working directory'
            i_step += 1

        # step 2
        sw_step = self.setExecutable('cta-prod-setup-software',
                                     arguments='-p %s -v %s -a stage1 -g %s' %
                                               (self.package, self.version, self.compiler),
                                     logFile='SetupSoftware_Log.txt')
        sw_step['Value']['name'] = 'Step%i_SetupSoftware' % i_step
        sw_step['Value']['descr_short'] = 'Setup software'
        i_step += 1

        # step 3 run stage1
        ev_step = self.setExecutable('./dirac_run_ctapipe_modeling',
                                     arguments=f"--base_config {self.ctapipe_base_dl2_config} \
                                             --site_config {self.ctapipe_site_config} \
                                             --input_ext {self.simtel_ext}",
                                     logFile='ctapipe_stage1_Log.txt')
        ev_step['Value']['name'] = 'Step%i_ctapipe_stage1' % i_step
        ev_step['Value']['descr_short'] = 'Run ctapipe stage 1'
        i_step += 1

        # step 4 set meta data and register Data
        meta_data_json = json.dumps(self.metadata)
        file_meta_data_json = json.dumps(self.file_meta_data)

        meta_data_field = {'array_layout': 'VARCHAR(128)', 'site': 'VARCHAR(128)',
                           'particle': 'VARCHAR(128)',
                           'phiP': 'float', 'thetaP': 'float',
                           self.program_category + '_prog': 'VARCHAR(128)',
                           self.program_category + '_prog_version': 'VARCHAR(128)',
                           'data_level': 'int', 'configuration_id': 'int', 'merged': 'int'}
        meta_data_field_json = json.dumps(meta_data_field)

        # register Data
        data_output_pattern = './Data/*.h5'  # %self.output_data_level
        dm_step = self.setExecutable('cta-prod-managedata',
                                     arguments="'%s' '%s' '%s' %s '%s' %s %s '%s' Data" %
                                               (meta_data_json, meta_data_field_json,
                                                file_meta_data_json,
                                                self.base_path, data_output_pattern, self.package,
                                                self.program_category, self.catalogs),
                                     logFile='DataManagement_Log.txt')
        dm_step['Value']['name'] = 'Step%s_DataManagement' % i_step
        dm_step['Value']['descr_short'] = 'Save data files to SE and register them in DFC'
        i_step += 1

        # step 5 register Log
        log_file_pattern = './Data/*.log_and_prov.tgz'
        file_meta_data = {}
        file_meta_data_json = json.dumps(file_meta_data)
        log_step = self.setExecutable('cta-prod-managedata',
                                      arguments="'%s' '%s' '%s' %s '%s' %s %s '%s' Log" %
                                                (meta_data_json, meta_data_field_json,
                                                 file_meta_data_json,
                                                 self.base_path, log_file_pattern, self.package,
                                                 self.program_category, self.catalogs),
                                      logFile='LogManagement_Log.txt')
        log_step['Value']['name'] = 'Step%s_LogManagement' % i_step
        log_step['Value']['descr_short'] = 'Save log to SE and register them in DFC'
        i_step += 1

        # step 6 failover step
        failover_step = self.setExecutable('/bin/ls -l',
                                           modulesList=['Script', 'FailoverRequest'])
        failover_step['Value']['name'] = 'Step%s_Failover' % i_step
        failover_step['Value']['descr_short'] = 'Tag files as unused if job failed'
        i_step += 1

        # Step 7 - debug only
        if debug:
            ls_step = self.setExecutable('/bin/ls -Ralhtr', logFile='LS_End_Log.txt')
            ls_step['Value']['name'] = 'Step%s_LSHOME_End' % i_step
            ls_step['Value']['descr_short'] = 'list files in Home directory'
            i_step += 1
