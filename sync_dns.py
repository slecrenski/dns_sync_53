#!/bin/python

import route53
from requests import get
import yaml
import argparse
import os.path
from argparse import RawTextHelpFormatter

class Settings:
    def __init__(self):
        self.DNS_STATUS_FILE = ''
        self.DNS_CONFIG_FILE = ''
        self.CREDENTIALS_FILE = ''
        self.AWS_ACCESS_KEY = ''
        self.AWS_SECRET_ACCESS_KEY = ''
        self.AWS_SECRET_ACCESS_KEY = ''
        self.IP = ''
        self.IPV4URL = 'https://api.ipify.org'

def init():
   settings = Settings()
   settings.DNS_STATUS_FILE = ''
   settings.DNS_CONFIG_FILE = ''
   settings.CREDENTIALS_FILE = ''
   settings.AWS_ACCESS_KEY = ''
   settings.AWS_SECRET_ACCESS_KEY = ''
   settings.AWS_SECRET_ACCESS_KEY = ''
   settings.IP = get(settings.IPV4URL).text

   settings.DNS_STATUS_FILE = 'dns.status.yaml'
   parser = argparse.ArgumentParser(description='Amazon Route 53 DNS Sync',
   formatter_class=RawTextHelpFormatter)

   parser.add_argument('--credentials', required=True,
    help="""credentials.yaml format:\n
    ###\ncredentials:\n   AWS_ACCESS_KEY:\n   AWS_SECRET_ACCESS_KEY:\n""")

   parser.add_argument('--config', required=True,
     help="DNS Configuration File Path")

   args = parser.parse_args()

   settings.CREDENTIALS_FILE = args.credentials
   settings.DNS_CONFIG_FILE = args.config

   if os.path.isfile(settings.CREDENTIALS_FILE):
      with open(settings.CREDENTIALS_FILE, 'r') as stream:
         yml = yaml.load(stream)
         settings.AWS_ACCESS_KEY = yml["credentials"]["AWS_ACCESS_KEY"]
         settings.AWS_SECRET_ACCESS_KEY = yml["credentials"]["AWS_SECRET_ACCESS_KEY"]
   else:
      print("Credentials File: " + settings.CREDENTIALS_FILE + " Not Found.")
      print("Credentials Format:\n###\ncredentials:\n   AWS_ACCESS_KEY:\n   AWS_SECRET_ACCESS_KEY:\n")
      exit(1)

   if os.path.isfile(settings.DNS_CONFIG_FILE):
      """"""
   else:
      print("DNS Configuration File Not Found")
      exit(1)

   return settings

def main():
   settings = init()
   print("Starting Syncronize - " + "IPV4: " + settings.IP)
   config = getConfiguration(settings)
   syncronizeWithRoute53(config, settings)
   saveStatus(config, settings)

def syncronizeWithRoute53(config, settings):
   conn = route53.connect(
          aws_access_key_id=settings.AWS_ACCESS_KEY,
          aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
   )
   for zone in conn.list_hosted_zones():
      if zone.name[:-1] in config["zones"]:
         zoneConfig = config["zones"][zone.name[:-1]]
         aRecordExists = False
         for record_set in zone.record_sets:
            if isinstance(record_set, route53.resource_record_set.AResourceRecordSet):
               for record in zoneConfig["records"]:
                  if record["name"] + "." == record_set.name:
                      record["exists"] = True
                      if record_set.records[0] == record["value"]:
                         record["synced"] = True
                      else:
                         print("Updating: ", record["name"])
                         auditChange("Updated: " + record["name"] + ":" + record_set.records[0] + ":" + record["value"])
                         record_set.records = [record["value"]]
                         record_set.values = [record["value"]]
                         record_set.ttl = record["ttl"]
                         try:
                            out = record_set.save()
                         except route53.exceptions.Route53Error as err:
                            print(err)
                         record["synced"] = True
         for record in zoneConfig["records"]:
             if not "exists" in record:
                 record["exists"] = False
             if not "synced" in record:
                 record["synced"] = False

         for record in zoneConfig["records"]:
             if record["synced"] == False:
                 if record["type"] == "A":
                     print("Creating: " + record["name"])
                     new_record, change_info = zone.create_a_record(
                        name=record["name"] + ".",
                        values=[record["value"]],
                        ttl=record["ttl"],
                     )
                     record["synced"] = True
                     record["exists"] = True
                     auditChange("Created: " + record["name"] + ":" + record["value"])


def auditChange(message):
    with open("audit.log", "a+") as f:
        f.write(message + "\n")

def getConfiguration(settings):
   modifiedConfig = ""
   readConfig = ""
   with open(settings.DNS_CONFIG_FILE, 'r') as f:
       readConfig=f.read()
   modifiedConfig = readConfig.replace("{{IPV4}}", settings.IP)
   config = yaml.load(modifiedConfig)
   return config

def saveStatus(config, settings):
    with open(settings.DNS_STATUS_FILE, 'w') as outfile:
       yaml.dump(config, outfile, default_flow_style=False)

if __name__ == "__main__":
    main()
