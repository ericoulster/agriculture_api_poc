import requests
import json

# Ensure the API key you were provided is in a json file in the local directory, with the structure {"key": "keyname"}

with open('aws-key.json', 'r') as file:
        data = json.load(file)

headers = {"Content-Type": "application/json", "x-api-key": data["key"]}

with open('good_fields_nopoints.geojson', 'r') as file: # replace the geojson file name with the file you wish to upload.
        data = json.load(file)

r = requests.post('https://vw4mpw6lx8.execute-api.us-east-2.amazonaws.com/develop', headers=headers, json=data)

print(r)
print(r)