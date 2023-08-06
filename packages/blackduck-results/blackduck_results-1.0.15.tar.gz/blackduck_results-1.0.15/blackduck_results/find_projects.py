#!/usr/bin/env python

import argparse
import logging
import sys

from blackduck.HubRestApi import HubInstance, object_id


parser = argparse.ArgumentParser("List matching projects")
parser.add_argument("project_name")
args = parser.parse_args()

logging.basicConfig(format='%(asctime)s:%(levelname)s:%(message)s', stream=sys.stderr, level=logging.DEBUG)
logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)

hub = HubInstance()

projects = hub.get_projects(limit=300, parameters={"q": "name:{}".format(args.project_name)})
for project in projects['items']:
    project_versions = hub.get_project_versions(project)
    for version in project_versions['items']:
        print(f"{project['name']} {version['versionName']}")
