#!/usr/bin/env python

__RCSID__ = "$Id$"

# generic imports
from multiprocessing import Pool

# DIRAC imports
from DIRAC import gLogger
from CTADIRAC.Core.Utilities.tool_box import read_inputs_from_file
from DIRAC.Resources.Catalog.TSCatalogClient import TSCatalogClient
from DIRAC.Core.Utilities.DIRACScript import DIRACScript as Script


Script.parseCommandLine(ignoreErrors=True)

args = Script.getPositionalArgs()
if len(args) == 1:
  infile = args[0]
else:
  Script.showHelp()

@Script()
def main():
  infileList = read_inputs_from_file(infile)
  p = Pool(10)
  p.map(addfile, infileList)

def addfile(lfn):
  tsCatalogClient = TSCatalogClient()
  res = tsCatalogClient.addFile(lfn)
  if not res['OK']:
    gLogger.error('Error uploading file', lfn)
    return res['Message']

if __name__ == '__main__':
  main()