import json
import os

from dotenv import load_dotenv

from lib import HOME
from utils import read_json

# Load .env from the given path
load_dotenv(os.path.join(f"{HOME}/.eBlocBroker/", ".env"))


def addElement(data, key, elementToAdd):
    data[key] = elementToAdd


def removeElement(data, elementToRemove):
    for element in list(data):
        if elementToRemove in element:
            del data[elementToRemove]


f = os.getenv("LOG_PATH") + "/" + "cachingRecord.json"
print(f)

if not os.path.isfile(f):
    data = {}
else:
    success, data = read_json(f)

addElement(data, "jobKey", ["local", "userName", "timestamp", "keepTime"])
addElement(data, "ipfsHash", "timestamp")

with open("data.json", "w") as outfile:
    json.dump(data, outfile)

if "jobKey" in data:
    print(data["jobKey"][0])
    print(data["jobKey"])

removeElement(data, "ipfsHash")
with open(f, "w") as data_file:
    data = json.dump(data, data_file)
