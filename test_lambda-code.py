import json
# import boto3
from string import punctuation
from datetime import datetime
import geojson

import pytest

# s3 = boto3.client('s3')

format = '%Y-%m-%d'

# These are several examples of data with flawed inputs. 
# They fail immediately upon attempting to load, as they don't conform to geojson standard

# First, the purposefully failing tests:

def test_file_typo():
    """This one has a typo in a field name"""
    with pytest.raises(Exception):
            with open('bad_fields_nopoints_footures.geojson', 'r') as bad_name_file:
                bad_data_name = geojson.load(bad_name_file)


def test_file_broken():
    """This one is structurally unsound as a json file"""
    with pytest.raises(Exception):
        with open('bad_fields_nopoints_broken.geojson', 'r') as broken_file:
                broken_data = geojson.load(broken_file)


def test_file_missing_features():
    """This one is missing features"""
    with pytest.raises(Exception):
        with open('bad_fields_nopoints_no_features.geojson', 'r') as no_features_file:
            bad_data_no_features = geojson.load(no_features_file)


def test_nameless_data():
    """This data lacks a name, 
    which is a required field for this API, 
    but not by the .geojson format itself"""
    with open('bad_fields_nopoints_nameless.geojson', 'r') as nameless_file:
            nameless_data = geojson.load(nameless_file)


    with pytest.raises(Exception):
        try:
                file_name = nameless_data['crs']['properties']['name']
        except:
                raise Exception('AttributeError: file name required in crs/properties/')


def test_punctuation_name():
    """This data has a name, 
    but the name is all punctuation, 
    and so it is effectively no name"""     
    
    with open('bad_fields_nopoints_name_all_punct.geojson', 'r') as all_punct_file:
            all_punct_data = geojson.load(all_punct_file)
            all_punct_name = all_punct_data['crs']['properties']['name']
            all_punct_name = all_punct_name.translate(str.maketrans('', '', punctuation)) 

    with pytest.raises(Exception):
        if len(all_punct_name) == 0:
            raise Exception("400: crs/properties/name has an invalid name. Please use alphanumeric characters")




def test_missing_crs_property():
    """This data had a missing property in the crs field."""
    with open('bad_fields_nopoints_null_crs.geojson', 'r') as null_crs_file:
            null_crs_data = geojson.load(null_crs_file)


    with pytest.raises(Exception):        
        for k, v in null_crs_data['crs']['properties'].items():
                    if v is None:
                        raise Exception("ValueError: Nan value in crs")


def test_nan_feature():
    """This data has nulls in a field"""
    with open('bad_fields_nopoints.geojson', 'r') as nan_date_file:
        bad_data = geojson.load(nan_date_file)


    with pytest.raises(Exception):
        for i in bad_data['features']:
                    for k, v in i['properties'].items():
                        if v is None:
                            raise Exception("ValueError: Nan value in features")

def test_missing_field():                
    """This data also has a missing date column"""
    with open('bad_fields_nopoints.geojson', 'r') as nan_date_file:
        bad_data = geojson.load(nan_date_file)

    # tests for necessary fields being present
    with pytest.raises(ValueError):
        for i in bad_data['features']:
                if 'pdate' in i['properties']:
                        date_val = bool(datetime.strptime(i['properties']['pdate'], format))
                        if date_val is False:
                            raise Exception(
                                "ValueError: Date Value not formatted correctly (YYYY-MM-DD)"
                                )        
                else:
                    raise Exception('AttributeError: pdate field is required in feature properties')


                if 'gsstart' in i['properties']:
                        date_val = bool(datetime.strptime(i['properties']['gsstart'], format))
                        if date_val is False:  
                            raise Exception(
                                "ValueError: Date Value not formatted correctly (YYYY-MM-DD)"
                                )            
                else:
                    raise Exception('AttributeError: gsstart field is required in feature properties')


                if 'gsend' in i['properties']:
                        date_val = bool(datetime.strptime(i['properties']['gsend'], format))
                        if date_val is False:
                            raise Exception('gsend in wrong format. Provide YYYY-MM-DD')
                else:
                    raise Exception('AttributeError: gsend is required in field properties')
            

def test_lambda_handler():
    """
    This is a full run with the good data. 
    I am testing equivalency before/after processing to show no data mutation prior to sendoff.
    """
    with open('good_fields_nopoints.geojson', 'r') as control_file:
            control_data = geojson.load(control_file)

    with open('good_fields_nopoints.geojson', 'r') as good_file:
            data = geojson.load(good_file)

    try:
        file_name = data['crs']['properties']['name']
    except:
        # return {'statusCode': 400, 
        # 'body': '400: No name found for file. Please add one to crs/properties/name'}
        raise Exception('AttributeError: file name required in crs/properties/')    


    # Stripping punctuation/special characters
    file_name = file_name.translate(str.maketrans('', '', punctuation))


    # Validating Geojson (as a redundancy measure)
    validity = data.is_valid
    if validity is False:
        # return {'statusCode': 400, 
        # 'body': '400: Input is not a valid geojson'}
        raise ValueError('Input is not a valid geojson')

    # Validating no nan values
        # All properties must have non-empty values, but other values could hypothetically be null
    for k, v in data['crs']['properties'].items():
            if v is None:
                # return {'statusCode': 400, 
                # 'body': '400: There are null values in crs/properties'}
                raise Exception("ValueError: Nan value in crs")

        # Checking all properties are not Nan for features, too

    for i in data['features']:
            for k, v in i['properties'].items():
                if v is None:
                    # return {'statusCode': 400, 
                    # 'body': '400: There are null values in features/properties'}
                    raise Exception("ValueError: Nan value in features")


# Checks if each date column is present, fails if they aren't, then enforces YYYY-MM-DD
    for i in data['features']:
        if 'pdate' in i['properties']:
                date_val = bool(datetime.strptime(i['properties']['pdate'], format))
                if date_val is False:
                    # return {'statusCode': 400, 
                    #         'body': '400: pdate in wrong format. Provide YYYY-MM-DD'}
                    raise Exception(
                        "ValueError: Date Value not formatted correctly (YYYY-MM-DD)"
                        )        
        else:
        #     return {'statusCode': 400, 
        # 'body': '400: pdate is required in feature properties'}
            raise Exception('AttributeError: gsstart field is required in feature properties')

        if 'gsstart' in i['properties']:
                date_val = bool(datetime.strptime(i['properties']['gsstart'], format))
                if date_val is False:
                    # return {'statusCode': 400, 
                    #         'body': '400: gsstart in wrong format. Provide YYYY-MM-DD'} 
                    raise Exception(
                        "ValueError: Date Value not formatted correctly (YYYY-MM-DD)"
                        )             
        else:
            # return {'statusCode': 400, 
            #     'body': '400: gsstart is required in feature properties'}
            raise Exception('AttributeError: gsstart field is required in feature properties')
    

        if 'gsend' in i['properties']:
                date_val = bool(datetime.strptime(i['properties']['gsend'], format))
                if date_val is False:
                    # return {'statusCode': 400, 
                    #         'body': '400: gsend in wrong format. Provide YYYY-MM-DD'}
                    raise Exception('AttributeError: gsstart field is required in feature properties')
        else:
            # return {'statusCode': 400, 
            #     'body': '400: gsend is required in feature properties'}
            raise Exception('AttributeError: gsend is required in field properties')

    # The runtime for this command is presently out of scope to implement in local code,
    # on account of IAM permission structures for this project in AWS
    # s3.put_object(Body=geojson.dumps(data), Bucket='presia-poc-2024-11-24', Key=f'{file_name}.geojson')

    # return {
    #     'statusCode': 200,
    #     'body': f"Submission Accepted as {file_name}.geojson in bucket"
    # }

    assert data == control_data