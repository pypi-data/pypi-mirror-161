"""
  New job class to run Prod5 Divergent simulations
  Only Paranal in the Alpha layout is supported, using zstd compression
  for simtel output files
          FDP, May 2022

  Adapted from Prod5MCPipeNSBJob.py by JB June 2020 (having a look at what was done for 
  Prod5bMCPipeAlphaSSTsFullMoonNSBJob.py by OG, January 2022)
"""

__RCSID__ = "$Id$"

# generic imports
import json
import collections
# DIRAC imports
from CTADIRAC.Interfaces.API.Prod5MCPipeNSBJob import Prod5MCPipeNSBJob


class Prod5bMCPipeAlphaDivergentJob(Prod5MCPipeNSBJob):
  """ Job extension class for Prod5 MC Divergent simulations,
  takes care of 

  """

  def __init__(self, cpu_time=259200):
    """ Constructor takes almosst everything from base class

    Keyword arguments:
    cpuTime -- max cpu time allowed for the job
    """
    Prod5MCPipeNSBJob.__init__(self, cpu_time)
    self.setCPUTime(cpu_time)
    self.setName('Prod5MC_Generation')
    self.version = '2020-06-29b'
    self.compiler = 'gcc83_matchcpu'
    self.configuration_id = 14
    self.n_shower = 100
    self.output_pattern = './Data/*.simtel.zst'
    self.base_path = '/vo.cta.in2p3.fr/MC/PROD5/'
    self.catalogs = json.dumps(['DIRACFileCatalog', 'TSCatalog'])
    self.metadata = collections.OrderedDict()

  def set_meta_data(self):
    """ define the common meta data of the application
    """
    # The order of the metadata dictionary is important,
    # since it's used to build the directory structure
    self.metadata['array_layout'] = 'Alpha'
    self.metadata['site'] = self.cta_site
    self.metadata['particle'] = self.particle
    # for air shower simulation means North=0 and South=180
    # but here piped into tel_sim so North=180 and South=0
    if self.pointing_dir == 'North':
      self.metadata['phiP'] = 180
    if self.pointing_dir == 'South':
      self.metadata['phiP'] = 0
    self.metadata['thetaP'] = float(self.zenith_angle)
    # back to common write up from class
    self.metadata[self.program_category + '_prog'] = self.prog_name
    self.metadata[self.program_category + '_prog_version'] = self.version
    self.metadata['data_level'] = self.output_data_level
    self.metadata['configuration_id'] = self.configuration_id

  def setupWorkflow(self, debug=False):
    """ Override the base class job workflow to adapt to divergent simulations
        All parameters shall have been defined before that method is called.
    """
    # step 1 - debug only
    i_step = 1
    if debug:
      ls_step = self.setExecutable('/bin/ls -alhtr', logFile='LS_Init_Log.txt')
      ls_step['Value']['name'] = 'Step%i_LS_Init' % i_step
      ls_step['Value']['descr_short'] = 'list files in working directory'

      env_step = self.setExecutable('/bin/env', logFile='Env_Log.txt')
      env_step['Value']['name'] = 'Step%i_Env' % i_step
      env_step['Value']['descr_short'] = 'Dump environment'
      i_step += 1

    # step 2
    sw_step = self.setExecutable('cta-prod-setup-software',
                                 arguments='-p %s -v %s -a simulations -g %s' %
                                 (self.package, self.version, self.compiler),
                                 logFile='SetupSoftware_Log.txt')
    sw_step['Value']['name'] = 'Step%i_SetupSoftware' % i_step
    sw_step['Value']['descr_short'] = 'Setup software'
    i_step += 1

    # step 3 running
    prod_script = './dirac_prod5_alpha_divergent_run'
    if 'gcc10' in self.compiler:
      prod_exe = './dirac_singularity_run'
      prod_args = '%s --start_run %s --run %s %s %s %s %s' % \
                  (prod_script, self.start_run_number, self.run_number,
                   self.cta_site, self.particle, self.pointing_dir,
                   self.zenith_angle)
    else:
      prod_exe = prod_script
      prod_args = '--start_run %s --run %s %s %s %s %s' % \
                  (self.start_run_number, self.run_number,
                   self.cta_site, self.particle, self.pointing_dir,
                   self.zenith_angle)

    cs_step = self.setExecutable(prod_exe, arguments=prod_args,
                                 logFile='CorsikaSimtel_Log.txt')
    cs_step['Value']['name'] = 'Step%i_CorsikaSimtel' % i_step
    cs_step['Value']['descr_short'] = 'Run Corsika piped into simtel'
    i_step += 1

    # step 4 - debug only
    if debug:
      ls_step = self.setExecutable('/bin/ls -Ralhtr', logFile='LS_End_Log.txt')
      ls_step['Value']['name'] = 'Step%i_LS_End' % i_step
      ls_step['Value']['descr_short'] = 'list files in working directory and sub-directory'
      i_step += 1
    
    # step 5  verify the number of events in the simtel file and define meta data, upload file on SE and register in catalogs
    self.set_meta_data()
    md_json = json.dumps(self.metadata)
    meta_data_field = {'array_layout': 'VARCHAR(128)', 'site': 'VARCHAR(128)',
                       'particle': 'VARCHAR(128)',
                       'phiP': 'float', 'thetaP': 'float',
                       self.program_category + '_prog': 'VARCHAR(128)',
                       self.program_category + '_prog_version': 'VARCHAR(128)',
                       'data_level': 'int', 'configuration_id': 'int', 'merged': 'int'}
    md_field_json = json.dumps(meta_data_field)
    
    i_substep = 0
    for div_ang in ['0.0022', '0.0043', '0.008', '0.01135', '0.01453']:
      
      data_output_pattern = 'Data/*-div%s*.simtel.zst'%(div_ang)
     
      #verify the number of events in the simtel file
      mgv_step = self.setExecutable('dirac_simtel_check',
                                  arguments="'%s'" %
                                  (data_output_pattern),
                                  logFile='Verify_n_showers_div%s_Log.txt'%(div_ang))
      mgv_step['Value']['name'] = 'Step%s.%s_VerifyNShowers' % (i_step,i_substep)
      mgv_step['Value']['descr_short'] = 'Verify number of showers'
      
      #define meta data, upload file on SE and register in catalogs

      # Upload and register data 
      file_meta_data = {'runNumber': self.run_number, 'nsb': 1, 'div_ang': div_ang} #adding a new meta data field 
      file_md_json = json.dumps(file_meta_data)

      dm_step = self.setExecutable('cta-prod-managedata',
                                  arguments="'%s' '%s' '%s' %s '%s' %s %s '%s' Data" %
                                 (md_json, md_field_json, file_md_json,
                                  self.base_path, data_output_pattern, self.package,
                                  self.program_category, self.catalogs),
                                 logFile="DataManagement_div%s_Log.txt"%(div_ang))
      dm_step['Value']['name'] = 'Step%s.%s_DataManagement' % (i_step,i_substep)
      dm_step['Value']['descr_short'] = 'Save data files to SE and register them in DFC'
      
      # Upload and register log_and_hist file
      log_file_pattern = 'Data/*-div%s*.log_hist.tar'%(div_ang)
      log_step = self.setExecutable('cta-prod-managedata',
                                  arguments="'%s' '%s' '%s' %s '%s' %s %s '%s' Log" %
                                  (md_json, md_field_json, file_md_json,
                                   self.base_path, log_file_pattern, self.package,
                                   self.program_category, self.catalogs),
                                  logFile="LogManagement_div%s_Log.txt"%(div_ang))
      log_step['Value']['name'] = 'Step%s.%s_LogManagement' % (i_step,i_substep)
      log_step['Value']['descr_short'] = 'Save log to SE and register them in DFC'
      
      i_substep += 1
    i_step += 1

    # Step 6 - debug only
    if debug:
      ls_step = self.setExecutable('/bin/ls -Ralhtr', logFile='LS_End_Log.txt')
      ls_step['Value']['name'] = 'Step%s_LSHOME_End' % i_step
      ls_step['Value']['descr_short'] = 'list files in Home directory'
      #i_step += 1

    # Number of showers is passed via an environment variable
    self.setExecutionEnv({'NSHOW': '%s' % self.n_shower})
