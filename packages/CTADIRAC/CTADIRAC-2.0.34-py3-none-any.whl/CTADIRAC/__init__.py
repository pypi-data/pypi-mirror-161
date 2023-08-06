""""

"""

def extension_metadata():
  return {
      "primary_extension": True,
      "priority": 100,
      "setups": {
          "CTA": "dips://dcta-servers03.pic.es:9135/Configuration/Server,"
                  "dips://dcta-agents03.pic.es:9135/Configuration/Server,"
                  "dips://ccdcta-server04.in2p3.fr:9135/Configuration/Server,"
                  "dips://ccdcta-server05.in2p3.fr:9135/Configuration/Server,"
                  "dips://ccdcta-web01.in2p3.fr:9135/Configuration/Server,"
                  "dips://cta-dirac.zeuthen.desy.de:9135/Configuration/Server",
          "CTA-cert": "dips://ccdcta-cert.in2p3.fr:9135/Configuration/Server",
      },
      "default_setup": "CTA",
  }

