import json
import boto3
from string import punctuation
from datetime import datetime
import geojson

s3 = boto3.client('s3')

format = '%Y-%m-%d'


def lambda_handler(event, context):

    try:
        data = geojson.loads(event["body"])
    except:
        return {'statusCode': 400, 
        'body': '400: Input is not a valid geojson'}


    try:
        file_name = data['crs']['properties']['name']
    except:
        return {'statusCode': 400, 
        'body': '400: No name found for file. Please add one to crs/properties/name'}
        

    # Stripping punctuation/special characters
    file_name = file_name.translate(str.maketrans('', '', punctuation))

    if len(file_name) == 0:
        return {'statusCode': 400, 
                'body': '400: crs/properties/name has an invalid name. Please use alphanumeric characters'}


    # Validating Geojson (as a redundancy measure)
    validity = data.is_valid
    if validity is False:
        return {'statusCode': 400, 
        'body': '400: Input is not a valid geojson'}


    # Validating no nan values
        # All properties must have non-empty values, but other values could hypothetically be null
    for k, v in data['crs']['properties'].items():
            if v is None:
                return {'statusCode': 400, 
                'body': '400: There are null values in crs/properties'}

        # Checking all properties are not Nan for features, too

    for i in data['features']:
            for k, v in i['properties'].items():
                if v is None:
                    return {'statusCode': 400, 
                    'body': '400: There are null values in features/properties'}


# Checks if each date column is present, fails if they aren't, then enforces YYYY-MM-DD
    for i in data['features']:
        if 'pdate' in i['properties']:
                date_val = bool(datetime.strptime(i['properties']['pdate'], format))
                if date_val is False:
                    return {'statusCode': 400, 
                            'body': '400: pdate in wrong format. Provide YYYY-MM-DD'}

        else:
            return {'statusCode': 400, 
        'body': '400: pdate is required in feature properties'}


        if 'gsstart' in i['properties']:
                date_val = bool(datetime.strptime(i['properties']['gsstart'], format))
                if date_val is False:
                    return {'statusCode': 400, 
                            'body': '400: gsstart in wrong format. Provide YYYY-MM-DD'}  

        else:
            return {'statusCode': 400, 
                'body': '400: gsstart is required in feature properties'}


        if 'gsend' in i['properties']:
                date_val = bool(datetime.strptime(i['properties']['gsend'], format))
                if date_val is False:
                    return {'statusCode': 400, 
                            'body': '400: gsend in wrong format. Provide YYYY-MM-DD'}
        else:
            return {'statusCode': 400, 
                'body': '400: gsend is required in feature properties'}

    try:
        s3.put_object(Body=geojson.dumps(data), Bucket='presia-poc-2024-11-24', Key=f'{file_name}.geojson')
    except:
        return {'statusCode': 500,
        'body': f"Data Failed to send to S3 Bucket. Check API token parameters."
    }    

    return {
        'statusCode': 200,
        'body': f"Submission Accepted as {file_name}.geojson in bucket"
    }