from exergenics import ExergenicsApi
from datetime import date

api = ExergenicsApi("john.christian@hashtagtechnology.com.au", "M1nd0v3rM4tt3r", False)

if not api.authenticate():
    exit("couldnt authenticate")

api.getAutoDataRefreshJobs(date.today().strftime("%Y-%m-%d"))

while api.moreResults():
    nextResult = api.nextResult()
    print(nextResult)
