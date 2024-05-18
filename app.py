from firebase_connect import FireBase
from food_data_central import FoodCentral as fdc
from preprocess import PreProcess
from pprint import pprint

def temp_get_raw_data(user_id):
    firebase = FireBase('PulseWise Firebase Admin.json')
    raw_data = firebase.get_data(user_id)
    pprint(raw_data)

    preprocess = PreProcess()
    data = preprocess.preprocess(raw_data)
    pprint(data)

    return data

temp_get_raw_data('6VJsITsuYzTQYqU7HaPZIfaYpCH3')

