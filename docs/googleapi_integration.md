# Academic Advising Setup and Configuration Documentation

> Written by [Hope Fauble](https://github.com/hopefauble/) and [Emmalyn Foster](https://github.com/emmalynfoster/) for the CSXL Web Application <br> _Last Updated: 12/08/2024_

This document is for CSXL developers who need the Google API integration in their feature work.

## Table of Contents

- [Google API Integration](#google-api-integration)
  - [Deployment](#deployment)
    - [Secrets](#secrets)
    - [CronJobs](#setting-up-cronjobs-for-recurring-scripts-in-cloudapps)
  - [Local Devlopment](#local-development)
    - [Establishing Credentials](#establishing-the-service-account-credentials)
    - [Environment Variables](#environment-variables)
    - [Necessary Dependencies](#requirementstxt-dependencies)

This feature serves as a ‘hub’ for students to access information from advising documents and upcoming drop-in sessions CS advisors are holding. One of the other important goals of this feature is to consolidate advising information to one source, providing a knowledge-base for staff to easily edit. For this knowledge-base, we chose Google Drive and Google Calendar, storing advising documents and drop-in sessions, respectively.

This required integrating third-party APIs into the CSXL application using Google Cloud to easily grab information and insert into the CSXL database. Following will be descriptions of requirements and configuration necessary for this integration.

## Google API Integration<a name='GoogleAPIIntegration'></a>

To access Google APIs, a service account is required to receive an API key and make calls to those API. For our purposes, we recommend a CSXL specific account or account of the product owner/manager. It is important to keep in mind that using Google APIs may eventually require payment for this project.

If you do not have a service account credentials file associated with a Google Cloud Console project:

1. Go to Google Cloud Console
2. Create a new project, then navigate inside the project if you are not automatically from the project selection.
3. From the sidebar, navigate to APIs and Services
4. Enable the API for Google Drive, Google Docs, and Google Calendar.
5. In the APIs and Services menu, navigate to credentials.
6. Create credentials, select a new Service Account, all default configurations are fine.
7. Click on your established Service Account, then to Keys → Add Key → create → JSON
8. Download this JSON, then continue to the next set of steps for either use of the credentials in local development branches, or in OpenShift deployment.

The next step on how to use the credentials depends on if this branch will be used for deployment (stage branch) or development branches. Within the codebase, this distinction must be made manually in `backend/services/establish_credentials.py`.

---

### Deployment<a name='Deployment'></a>

#### Secrets<a name='Secrets'></a>

To establish the credentials file in CloudApps Deployment, we will add it as a secret in the environment.

Once your development build is up and the pods are running, navigate to the pod details. The environment tab is where all the secrets can be loaded from the pod environment. Add three secrets to the environment by navigating to the parent resource within the pod (the pod environment will not allow you to edit these values directly as they are inherited from the resource):

`GOOGLE_CALENDAR_ID`, `GOOGLE_FOLDER_ID`, and `GOOGLE_CREDS`.

The calendar ID and the folder ID can be pasted directly into the values, and the `GOOGLE_CREDS` must be grabbed from the workspace secrets.

1. In developer mode, navigate to secrets, then create a key-value secret. Name this something identifiable, then paste your API service account credentials as the value.
2. Once created, in the pod environment add the google credentials from secret.

In your staging branch, the deployment mode must be distinguished in the establish_credentials.py file. Make sure that the code that retrieves the credentials from the environment is being used, and comment out the code that retrieves it from filepath.

Due to the feature’s functionality being dependent on the existence of the service account credentials, the initial population of the drop-in calendar and registration guide is not included in the CSXL’s existing database population scripts. Instead, on initial deployment run these three API calls from the `/docs`:

1. api/documents (refresh documents)
2. api/drop-ins (reset drop-ins)
3. api/webhook/resubscribe

#### Setting up CronJobs for Recurring Scripts in CloudApps<a name='CronJobs'></a>

Documentation on CronJobs can be found [here](https://docs.openshift.com/container-platform/3.11/dev_guide/cron_jobs.html).

This .yaml file uses our FastAPI route hosted by CloudApps in deployment, which resubscribes to our webhooks to ensure we will get notified of changes to resources and repopulates our data daily.

_URLs:_  
Resetting drop-ins daily 11:50 pm: `https://csxl-advising.apps.cloudapps.unc.edu/api/drop-ins`  
Resubscribing to the webhook watching our resources every 28 days: `https://csxl-advising.apps.cloudapps.unc.edu/api/webhook/resubscribe`

```
apiVersion: batch/v1
kind: CronJob
metadata:
    name: resubscribe-webhook
spec:
    # Runs at 12:00 AM on the 28th day of every month
    schedule: "0 0 28 \* \*"
    # Ensures only one job runs at a time; new job replaces the old one if it's still running
    concurrencyPolicy: "Replace"
    # Defines a time window for job execution if missed
    startingDeadlineSeconds: 200
    # Keeps the history of the last 3 successful jobs
    successfulJobsHistoryLimit: 3
    # Keeps the history of the last failed job
    failedJobsHistoryLimit: 1
    jobTemplate:
        spec:
            template:
                metadata:
                    labels:
                        parent: "cronjob-subscribe-webhook"
                spec:
                    containers:
                    - name: resubscribe-webhook
                    # Lightweight image for making HTTP requests
                      image: curlimages/curl:latest
                      command:
                        - "curl"
                        - "-X"
                        - "GET"
-"[https://csxl-advising.apps.cloudapps.unc.edu/api/webhook/resubscribe](https://csxl-advising.apps.cloudapps.unc.edu/api/webhook/resubscribe)"
                    # Restarts the container if it fails
                    restartPolicy: OnFailure
```

---

### Local Development<a name='LocalDevelopment'></a>

#### Establishing the Service Account Credentials<a name='EstablishCredentials'></a>

After retrieving the JSON service account credentials file:

1. Ensure your branch is caught up to date, and includes the credentials file in the .gitignore
2. Download the credentials .json file.
3. Move the credentials file to this folder in your local repository in the root directory.
4. After checking that the `establish_credentials.py` file is retrieving the .json from the local repository (not from environmental variables), the feature should now be able to retrieve documents and calendar information from the specified google IDs.

**Necessary imports:**  
from googleapiclient.discovery import build  
from google.oauth2.service_account import Credentials

**Usage of Service Account Credentials:**

These credentials are used to build the API service.

```
# A path to your account credentials:
SERVICE_ACCOUNT_FILE = "csxl-academic-advising-feature.json"

# The scope of usage that your service should be allowed, depending on the service will need more or different scopes:
SCOPES = "https://www.googleapis.com/auth/calendar.readonly"

# Retrieving the credentials:
creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
```

#### Environment Variables<a name='EnvironmentVariables'></a>

Two environmental variables must be added to the .env: GOOGLE_CALENDAR_ID, GOOGLE_FOLDER_ID  
The calendar ID and google folder ID are obtained from the public sharing information of the desired calendar and folder.

1. The calendar ID will have the form of `123456789@group.calendar.google.com` and be located under calendar settings → integrate calendar
2. The folder ID can be found in the route and sharing links in Google drive.

```
MODE\=development
POSTGRES_USER\=postgres
POSTGRES_PASSWORD\=postgres
POSTGRES_HOST\=db
POSTGRES_PORT\=5432
POSTGRES_DATABASE\=csxl
HOST\=localhost
JWT_SECRET\=1fa8e1d0-acb1-41f3-b300-a110c09e8a39
GOOGLE_CALENDAR_ID\=cs.unc.edu\_340oonr4ec26n1fo9l854r3ip8@group.calendar.google.com
GOOGLE_FOLDER_ID\=1fAwD7P4MVDDza_7qKL5fTuXi0pJgOGZ4
```

#### Requirements.txt Dependencies<a name='Dependencies'></a>

```
fastapi\[all\] \>=0.111.0, \<0.112.0
honcho \>=1.1.0, \<1.2.0
psycopg2 \>=2.9.9, \<2.10.0
pyjwt \>=2.8.0, \<2.9.0
pytest \>=8.2.2, \<8.3.0
pytest-cov \>=5.0.0, \<5.1.0
python-dotenv \>=1.0.1, \<1.1.0
requests \>=2.32.0, \<2.33.0
sqlalchemy \>=2.0.30, \<2.1.0
alembic \>=1.13.1, \<1.14.0
pygithub \>=2.3.0, \<2.4.0
black \>=24.4.2, \<24.5.0
setuptools \>=70.0.0, \<70.1.0
bs4 \>=0.0.2
python-dateutil \>=2.8.2, \<2.9.0
google-auth
google-auth-oauthlib
google-auth-httplib2
google-api-python-client
```
