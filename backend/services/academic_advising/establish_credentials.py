"""Establishes the source for the google api service account credentials. This will need to be edited manually depending on if the branch is in development or deployment."""

import json
from backend.env import getenv

__authors__ = ["Hope Fauble"]

# If this is a developing branch off stage, this is true. If this is a deployment branch (stage) for CloudApps, this is false.
DEVELOPMENT = False

def getcredentials():

    ## During testing (outside of stage branch) bring the credentials .json to the root directory, and make sure it is included in the .gitignore
    if DEVELOPMENT:
        with open("csxl-academic-advising-feature.json") as file:
            creds = json.load(file)
    ## For deployment (on stage branch) establish the .json as an environmental variable in the cloudapps deployment and retrieve the credentials from the environement.
    else:
        creds = json.loads(getenv("GOOGLE_CREDS"))

    return creds