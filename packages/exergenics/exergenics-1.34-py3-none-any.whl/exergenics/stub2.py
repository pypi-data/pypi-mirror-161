import json
import boto3
import time
from exergenics import ExergenicsApi

API_INSTANCE_IDS = ['i-3']
AWS_REGION = 'ap-southeast-2'

ON_STATES = [
    {"stage": "startapiserver", "status": "running", "checkApi": False},
    {"stage": "data_ready", "status": "completed", "checkApi": True},
    {"stage": "api_ready", "status": "error", "checkApi": True},
    {"stage": "api_ready", "status": "waiting", "checkApi": True},
    {"stage": "api_ready", "status": "running", "checkApi": True},
    {"stage": "merged_ready", "status": "waiting", "checkApi": False},
    {"stage": "merged_ready", "status": "running", "checkApi": False},
    {"stage": "data_selection_ready", "status": "completed", "checkApi": False},
    {"stage": "data_collection_ready", "status": "waiting", "checkApi": False},
    {"stage": "data_collection_ready", "status": "running", "checkApi": False},
    {"stage": "transformed_ready", "status": "waiting", "checkApi": False},
    {"stage": "transformed_ready", "status": "running", "checkApi": False}

]


# target server state is dependant on prod and staging requirements.
targetProductionState = False
targetStagingState = False
targetState = targetProductionState or targetStagingState

# check staging requirements
try:
    api = ExergenicsApi("john.christian@hashtagtechnology.com.au", "M1nd0v3rM4tt3r", False)
except Exception as e:
    print(e)


jobsToReset = []
api.getJobs("api_ready", "error")
if api.numResults() > 0:
    while api.moreResults():
        job = api.nextResult()
        jobsToReset.append(job["jobId"])
for i in range(len(jobsToReset)):
    api.setStage(jobsToReset[i], "data_ready", "completed")

jobsStaging = 0
for onState in ON_STATES:
    api.getJobs(onState["stage"], onState["status"])
    if api.numResults() > 0:
        while api.moreResults():
            job = api.nextResult()
            if onState["checkApi"]:
                if job["usesApi"] == "1":
                    jobsStaging += 1
            else:
                jobsStaging += 1

targetStagingState = jobsStaging > 0

# check production requirements
try:
    api = ExergenicsApi("john.christian@hashtagtechnology.com.au", "M1nd0v3rM4tt3r", True)
except Exception as e:
    print(e)


jobsToReset = [];
api.getJobs("api_ready", "error")
if api.numResults() > 0:
    while api.moreResults():
        job = api.nextResult()
        jobsToReset.append(job["jobId"])
for i in range(len(jobsToReset)):
    api.setStage(jobsToReset[i], "data_ready", "completed")

jobsProduction = 0
for onState in ON_STATES:
    api.getJobs(onState["stage"], onState["status"])
    if api.numResults() > 0:
        while api.moreResults():
            job = api.nextResult()
            if onState["checkApi"]:
                if job["usesApi"] == "1":
                    jobsProduction += 1
            else:
                jobsProduction += 1

targetProductionState = jobsProduction > 0

# target instance state is OR each of the two environments.
targetState = targetProductionState or targetStagingState

targetMessage = ""
if targetProductionState:
    targetMessage += "Target production state: ON\n"
else:
    targetMessage += "Target production state: OFF\n"

if targetStagingState:
    targetMessage += "Target staging state: ON\n"
else:
    targetMessage += "Target staging state: OFF\n"

ec2 = boto3.resource('ec2', region_name=AWS_REGION)

# get the state of the ec2 instances...
instances = ec2.instances.filter(InstanceIds=API_INSTANCE_IDS)
print(instances)

for instance in instances:
    print(instance)

    ec2State = instance.state["Name"]

    if targetState:  # do we want the server on
        if ec2State in ["stopped"]:  # but it is not currently on? (note: not interrupting the 'stopping' status - let next run restart in that case)
            instance.start()
            api.sendSlackMessage("API Server has been restarted.\n{}".format(targetMessage))

    if not targetState:  # do we want the server off?
        if ec2State in ["running"]:  # ignoring "pending" if its booting up we can shut it down next run
            instance.stop()
            api.sendSlackMessage("API Server has been shut down.\n{}".format(targetMessage))




