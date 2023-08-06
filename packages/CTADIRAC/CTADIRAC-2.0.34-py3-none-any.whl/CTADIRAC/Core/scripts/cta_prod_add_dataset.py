#!/usr/bin/env python
"""
Add a dataset from a query specified in a json file, e.g.:

{"MCCampaign": "PROD5b",
"particle": "proton",
"site": "Paranal"}

The created dataset will get the name of the json file (without the extension)

Usage:
   cta-prod-add-dataset <json file with dataset query dict>
Arguments:
   json file with dataset query dict
   The file should have the .json extension, e.g. my_dataset.json
"""

__RCSID__ = "$Id$"

import json
import ast

import DIRAC
from DIRAC.Core.Utilities.DIRACScript import DIRACScript as Script
from DIRAC import gLogger
from DIRAC.Resources.Catalog.FileCatalogClient import FileCatalogClient

@Script()
def main():
  fc = FileCatalogClient()
  Script.parseCommandLine(ignoreErrors=True)
  argss = Script.getPositionalArgs()
  if len(argss) == 1:
    inputJson = argss[0]
    if not inputJson.endswith(".json"):
      Script.showHelp()
  else:
    Script.showHelp()

  # read the meta data query from json file
  content = open(inputJson, 'rt').readlines()
  for line in content:
    json_string = json.dumps(ast.literal_eval(line))

  MDdict = json.loads(json_string)

  # ensure the integer values are written in the right format
  for key, value in MDdict.items():
    if isinstance(value, float):
      MDdict[key] = {'=': value}

  datasetName = inputJson.split('.json')[0]
  datasetPath = '/vo.cta.in2p3.fr/datasets/' + datasetName
  res = (fc.addDataset({datasetPath: MDdict}))

  if not res['OK']:
    gLogger.error("Failed to add dataset %s: %s" % (datasetName, res['Message']))
    DIRAC.exit(-1)

  if datasetName in res['Value']['Failed']:
    gLogger.error("Failed to add dataset %s: %s" % (datasetName, res['Value']['Failed'][datasetName]))
    DIRAC.exit(-1)

  gLogger.notice("Successfully added dataset", datasetName)
  DIRAC.exit()

####################################################
if __name__ == '__main__':
  main()
