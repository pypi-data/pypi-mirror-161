import os

from pandas import DataFrame

from ml_sdk.ml.sdk.watchmen.sdk import load_dataset_by_name, push_notebook_to_watchmen, call_indicator_data_api, \
    load_indicator_by_id, load_achievement_by_id
from ml_sdk.ml.unitls import get_notebook, get_environment


class WatchmenClient(object):
    def __init__(self, token):
        if token:
            self.token = token
        else:
            self.token = os.environ.get('TOKEN')

    def load_dataset(self, name,dataframe_type="pandas"):
        return load_dataset_by_name(self.token, name,dataframe_type)


    def load_achievement(self, achievement_id):
        return load_achievement_by_id(self.token,achievement_id)


    def load_indicator_value_by_achievement_id(self,achievement_id,indicator_id,filters):
        pass



    def load_indicator_value(self,indicator_id,aggregate_arithmetic,filters):
        indicator = load_indicator_by_id(self.token, indicator_id)
        payload = {
            "current":{
                "aggregateArithmetic":aggregate_arithmetic,
                "indicatorId":indicator_id,
                "criteria":filters,
                "name":"",
                "variableName":"v2"
            }
        }
        result = call_indicator_data_api(self.token,payload)
        return result

    def load_summary_data(self):

        ## use template report api
        pass


    def register_notebook(self, storage_type="file"):
        notebook = get_notebook(storage_type)
        notebook.environment = get_environment()
        response = push_notebook_to_watchmen(notebook,self.token)
        if response.status_code == 200:
            print("push notebook successfully")
        return notebook

    def save_topic_dataset(self, topic_name: str, dataset:DataFrame):
        pass


    def register_model(self):
        pass

