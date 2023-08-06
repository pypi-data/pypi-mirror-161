import requests
import json
import os
import sys
from jsonschema import validate
from jsonschema.exceptions import ValidationError
import pandas as pd
from censius.schemas import register_new_model_version_schema,register_model_schema, revise_model_schema, update_actual_schema, individual_log_schema, batch_log_schema , process_model_schema,register_dataset_schema,register_project_schema,log_explanations_schema
from censius.utils import check_time_format



BASE_URL="http://censius-logs-prod1.us-east-1.elasticbeanstalk.com/v1"
AMS_URL="http://ams-prod.us-east-1.elasticbeanstalk.com"
EXPLAINATION_BASE_URL="http://explainability-prod.us-east-1.elasticbeanstalk.com/explanations"

# Models
REGISTER_MODEL_URL = lambda : f"{AMS_URL}/models/register"
REVISE_MODEL_URL = lambda : f"{AMS_URL}/models/revise"
PROCESS_MODEL_URL = lambda : f"{AMS_URL}/models/schema-updation"
REGISTER_NEW_MODEL_VERSION=lambda : f"{AMS_URL}/models/register_new_version"

# Logs
LOG_URL = lambda : f"{BASE_URL}/logs"
UPDATE_ACTUAL_URL = lambda prediction_id : f"{BASE_URL}/logs/{prediction_id}/updateActual"

# Dataset
REGISTER_DATASET_URL = lambda : f"{AMS_URL}/datasets/register"

# Project
REGISTER_PROJECT_URL = lambda: f"{AMS_URL}/projects/register-project"

#Explainations
EXPLAINATION_URL= lambda: f"{EXPLAINATION_BASE_URL}/insert_local"

class CensiusClient(object):
    def __init__(self, api_key, tenant_id):
        if api_key == None or len(api_key) == 0:
            raise ValueError("You need to pass an API key")
        if tenant_id == None or len(tenant_id) == 0:
            raise ValueError("You need to pass a tenant ID")
        self.api_key = api_key
        self.tenantKey=tenant_id       

    
    def register_project(self, *args,**kwargs):
        try:
            validate(instance=kwargs, schema=register_project_schema)
        except ValidationError as e:
            return e.message

        Icon=None
        if 'icon' in kwargs:
            Icon=str(kwargs["icon"])

        Type=None
        if 'type' in kwargs:
            Type=kwargs["type"]
        
        Key=None
        if 'key' in kwargs:
            Key=kwargs["key"]

        payload = json.dumps({k: v for k, v in {
            "icon": Icon,
            "name": kwargs['name'],
            "key": Key,
            "type":Type,
            "apiKey":self.api_key,
        }.items() if v})
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }

        response = requests.request("POST", REGISTER_PROJECT_URL(), headers=headers, data=payload)
        return self.__return_message(response)


    def register_new_model_version(self, *args, **kwargs):
        try:
            validate(instance=kwargs, schema=register_new_model_version_schema)
        except ValidationError as e:
            return e.message



        WindowSize=None
        if "window_size" in kwargs:
            WindowSize=kwargs["window_size"]

        WindowStartTime=None
        if "start_time" in kwargs:
            WindowStartTime=kwargs["start_time"]

        payload = json.dumps({k: v for k, v in {
            "userDefinedModelID": kwargs['model_id'],
            "version": kwargs['model_version'],
            "datasetId": kwargs['training_info']['id'],
            "targets": kwargs["targets"],
            "features": kwargs["features"],
            "apiKey":self.api_key,
            "windowSize":WindowSize,
            "window_start_time":WindowStartTime,
            "tenantKey":self.tenantKey
        }.items() if v})
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }

        response = requests.request("POST", REGISTER_NEW_MODEL_VERSION(), headers=headers, data=payload)
        if 'error' in response.json().keys():
            return self.__return_message(response)
        else:
            values=[]
            for i in kwargs["targets"]:
                temp={}
                temp["target"] = i
                values.append(temp)
            primary_response = response
            self.process_model(
                dataset_id=kwargs['training_info']['id'],
                model_id=response.json()["message"]["ID"],
                values=values
            )
            return self.__return_message(primary_response)


    def register_dataset(self, *args, **kwargs):
        try:
            validate(instance=kwargs, schema=register_dataset_schema)
        except ValidationError as e:
            return e.message
    
        rawValues=None
        if 'raw_values' in kwargs:
            rawValues=str(kwargs["raw_values"])

        timestampBase=None
        timestampCol=None
        unixInterval=None
        timestampType=None
        if 'timestamp' in kwargs:
            timestampBase=kwargs["timestamp"]
            timestampCol=timestampBase["name"]
            if "iso" not in timestampBase["type"]:
                timestampType="unix"
                unixInterval=timestampBase["type"]
            else:
                timestampType=timestampBase["type"]

        Version=None
        if 'version' in kwargs:
            Version=kwargs["version"]

        file=None
        if 'file' in kwargs:
            file=kwargs["file"]
        file_path=None
        if 'file_path' in kwargs:
            file_path=kwargs["file_path"]
        
        file_name=kwargs["name"]+".csv"
        if file_path:
            if '.csv' not in file_path:
                return {"error":"Please provide a valid path for the csv file"}
            try:
                file=pd.read_csv(file_path)
                if (file.memory_usage().sum())//1000000 > 500:
                    return {"error":"Max allowed file size is 500 MB"}
                file.to_csv(file_name)
                
            except Exception as e:
                return {"error":"unable to read the csv file"}
        elif file is not None:
            if (file.memory_usage().sum())//1000000 > 500:
                    return {"error":"Max allowed file size is 500 MB"}
            file.to_csv(file_name)  
        else:
            return {"error":"Please provide a df object or a file path"}

        headers = {
            'Authorization': f'Bearer {self.api_key}'
        }

        payload={'name': kwargs["name"],
                'projectId': kwargs['project_id'],
                'version': Version,
                'features': json.dumps(kwargs["features"]),
                'apiKey':self.api_key,
                'timestampCol':timestampCol,
                'unixInterval':unixInterval,
                'timestampType':timestampType,
                'rawValues':json.dumps(rawValues)


        }
        files=[
                ('File',(file_name,open(os.getcwd()+"/"+file_name,'rb'),'text/csv'))
            ]



        response = requests.request("POST", REGISTER_DATASET_URL(), headers=headers, data=payload, files=files)
        os.remove(os.getcwd()+"/"+file_name)
        return self.__return_message(response)


    def process_model(self,*args,**kwargs):
        try:
            validate(instance=kwargs, schema=process_model_schema)
        except ValidationError as e:
            return e.message
            
        WindowSize=None
        if "window_size" in kwargs:
            WindowSize=kwargs["window_size"]

        WindowStartTime=None
        if "window_start_time" in kwargs:
            WindowStartTime=kwargs["window_start_time"]

        payload = json.dumps({k: v for k, v in {
            "windowSize":WindowSize,
            "window_start_time": WindowStartTime,
            "dataset_id": kwargs['dataset_id'],
            "model_id": kwargs['model_id'],
            "values": kwargs['values'],
            "apiKey":self.api_key,
        }.items() if v})
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }

        response = requests.request("POST", PROCESS_MODEL_URL(), headers=headers, data=payload)
        return self.__return_message(response)




    def register_model(self, *args, **kwargs):
        try:
            validate(instance=kwargs, schema=register_model_schema)
        except ValidationError as e:
            return e.message

        targets = kwargs['targets']

        features = kwargs['features']

        WindowSize=None
        if "window_size" in kwargs:
            WindowSize=kwargs["window_size"]

        WindowStartTime=None
        if "start_time" in kwargs:
            WindowStartTime=kwargs["start_time"]

        ModelName=None
        if "model_name" in kwargs:
            ModelName=kwargs["model_name"]

        payload = json.dumps({k: v for k, v in {
            "userDefinedModelID": kwargs['model_id'],
            "version": kwargs['model_version'],
            "datasetId": kwargs['training_info']['id'],
            "name": ModelName,
            "projectId": kwargs['project_id'],
            "type": kwargs['model_type'],
            "target": targets,
            "features": features,
            "apiKey":self.api_key,
            "windowSize":WindowSize,
            "window_start_time":WindowStartTime,
            "tenantKey":self.tenantKey
        }.items() if v})
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }

        response = requests.request("POST", REGISTER_MODEL_URL(), headers=headers, data=payload)
        if 'error' in response.json().keys():
            return self.__return_message(response)
        else:
            values=[]
            for i in targets:
                temp={}
                temp["target"] = i
                values.append(temp)
            primary_response = response
            self.process_model(
                dataset_id=kwargs['training_info']['id'],
                model_id=response.json()["message"]["ID"],
                values=values
            )
            return self.__return_message(primary_response)
        

    def update_model(self, *args, **kwargs):
        try:
            validate(instance=kwargs, schema=revise_model_schema)
        except ValidationError as e:
            return e.message
        
        TrainingData=kwargs["training_info"]
        IsRollingWindow=False
        reMapped=False
        MappedTo=None
        WindowSize=None
        WindowEndTime=None
        WindowStartTime=None
        
        if "fixed" in TrainingData['method']:
            IsRollingWindow=False
            reMapped=False
            if "start_time" in TrainingData.keys():
                    WindowStartTime=TrainingData["start_time"]
            if "end_time" in TrainingData.keys():
                    WindowEndTime=TrainingData["end_time"]
            

        elif "id" in TrainingData["method"]:
            IsRollingWindow=False
            reMapped=True
            MappedTo=TrainingData["id"]   
        else:
            IsRollingWindow=True
            if "start_time" in TrainingData.keys():
                    WindowStartTime=TrainingData["start_time"]
            if "window_size" in TrainingData.keys():
                WindowSize=TrainingData["window_size"]

        
        payload = json.dumps({k: v for k, v in {
            "userDefinedModelID": kwargs['model_id'],
            "version": kwargs['model_version'],
            "isRollingWindow": IsRollingWindow,
            "apiKey":self.api_key,
            "windowSize":WindowSize,
            "window_start_time":WindowStartTime,
            "window_end_time":WindowEndTime,
            "isRemapped":reMapped,
            "remap_to":MappedTo
        }.items() if v})
        headers = {
            'Authorization': "Bearer "+self.api_key,
            'Content-Type': 'application/json'
        }
        
        response = requests.request("POST", REVISE_MODEL_URL(), headers=headers, data=payload)
        return self.__return_message(response)


    def log(self, *args, **kwargs):
        if len(args) > 0 and str(type(args[0])) == "<class 'list'>":
            return self.__batch_log(args[0])
        else:
            return self.__individual_log(**kwargs)
        
    def __individual_log(self, *args, **kwargs):
        try:
            validate(instance=kwargs, schema=individual_log_schema)
        except ValidationError as e:
            return e.message

        raw_values = None
        if 'raw_values' in kwargs:
            raw_values = kwargs['raw_values']

        actual = None
        if 'actual' in kwargs:
            actual = kwargs['actual']

        rightFormat=check_time_format(kwargs['timestamp'])
        if not rightFormat:
            return "Timestamp is not of the Unix MS format"
            

        payload = json.dumps({k: v for k, v in {
            "predictionID": kwargs['prediction_id'],
            "modelVersion": kwargs['model_version'],
            "modelID": kwargs['model_id'],
            "features": kwargs['features'],
            "prediction": kwargs['prediction'],
            "timestamp": kwargs['timestamp'],
            "rawValues": raw_values,
            "actual": actual,
        }.items() if v})
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }

        response = requests.request("POST", LOG_URL(), headers=headers, data=payload)
        
        return self.__return_message(response)

    def __batch_log(self, *args, **kwargs):
        try:
            validate(instance=args[0], schema=batch_log_schema)
        except ValidationError as e:
            return e.message

        payload = []
        for log_data in args[0]:
            raw_values = None
            if 'raw_values' in log_data:
                raw_values = log_data['raw_values']

            actual = None
            if 'actual' in log_data:
                actual = log_data['actual']

            payload.append({k: v for k, v in {
                "predictionID": log_data['prediction_id'],
                "modelVersion": log_data['model_version'],
                "modelID": log_data['model_id'],
                "features": log_data['features'],
                "prediction": log_data['prediction'],
                "timestamp": log_data['timestamp'],
                "rawValues": raw_values,
                "actual": actual,
            }.items() if v})

        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }

        response = requests.request("POST", LOG_URL(), headers=headers, data=json.dumps(payload))
        return self.__return_message(response)

    def update_actual(self, *args, **kwargs):
        try:
            validate(instance=kwargs, schema=update_actual_schema)
        except ValidationError as e:
            return e.message
        
        payload = json.dumps({
            "modelID": kwargs['model_id'],
            "modelVersion": kwargs['model_version'],
            "actual": kwargs['actual'],
        })
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }

        response = requests.request("POST", UPDATE_ACTUAL_URL(kwargs['prediction_id']), headers=headers, data=payload)
        return self.__return_message(response)


    def log_explanation(self, *args, **kwargs):
        try:
            validate(instance=kwargs, schema=log_explanations_schema)
        except ValidationError as e:
            return e.message

        payload = json.dumps({k: v for k, v in {
            "custom_model_id": kwargs['model_id'],
            "model_version": kwargs['model_version'],
            "log_id": kwargs["prediction_id"],
            "apiKey":self.api_key,
            "explanation_type":kwargs["explanation_type"],
            "explanation_values":kwargs["explanation_values"]
        }.items() if v})
        headers = {
            'Authorization': "Bearer "+self.api_key,
            'Content-Type': 'application/json'
        }
        
        response = requests.request("POST", EXPLAINATION_URL(), headers=headers, data=payload)
        return self.__return_message(response)

    def __return_message(self, response):
        try:
            return response.json()['message']
        except:
            if 'error' in response.json().keys():
                return response.json()['error']
            else:
                return "Something went wrong. Request failed with status code"+" "+str(response.status_code)

