import food_data_central as fdc

import json
from datetime import datetime, date
import re
import pandas as pd


def get_age(birth_date_str):
    try:
        birth_date = datetime.strptime(birth_date_str, "%d %B %Y").date()
        today = date.today()

        age = today.year - birth_date.year
        # Adjust for the case where the birth date hasn't occurred yet this year
        if (today.month, today.day) < (birth_date.month, birth_date.day):
            age -= 1

        return age
    except:
        return 20

def timestamp_to_int(time_string):
  try:
    time_obj = datetime.strptime(time_string, "%I:%M %p")
    return time_obj.hour * 60 + time_obj.minute
  except:
    return 1380

def get_sleep_duration(sleep_time_string, wake_time_string):
    sleep_time = timestamp_to_int(sleep_time_string)
    wake_time = timestamp_to_int(wake_time_string)

    if(sleep_time > wake_time):
        wake_time += (24*60) # Add 24 hour to wake time to calculate sleep duraton
    
    return wake_time - sleep_time

def get_consumption_detail(consumptions):
    if(not isinstance(consumptions, list)):
        raise ValueError("Need to be list of consumptions")
    
    total_detail = {
        'calorie': 0,
        'protein': 0,
        'carbohydrate': 0,
        'sugars': 0,
        'fiber': 0,
        'fat': 0,
        'saturated_fatty_acid': 0,
        'monounsaturated_fatty_acid': 0,
        'polyunsaturated_fatty_acid': 0,
        'cholesterol': 0,
        'calcium': 0
    }

    for consumption in consumptions:
        detail = fdc.get_food_detail(consumption['name'])
        # Need to update
    
    return total_detail


def preprocess(data_json):
    # Take data in json string then preprocess and output np array
    data_raw = json.loads(data_json)

    age = {
        'Demog1_RIDAGEYR': get_age(data_raw['birth_date'])
    }
    smoking = {
        'Quest22_SMQ890': data_raw['have_smoked'],
        'Quest22_SMQ900': data_raw['have_smoked_ecigarette']
    }
    sleep = {
        'Quest21_SLQ300': timestamp_to_int(data_raw['sleep_time']),
        'Quest21_SLQ330': timestamp_to_int(data_raw['wake_time']),
        'Quest21_SLD012': get_sleep_duration(data_raw['sleep_time'], data_raw['wake_time'])
    }
    pain = {
        'Quest3_CDQ008': 0
    }
    dietary_detail = get_consumption_detail(data_raw['consumptions'])
    dietary = {
        'Dieta1_DR1TKCAL': dietary_detail['calorie'],
        'Dieta1_DR1TPROT': dietary_detail['protein'],
        'Dieta1_DR1TCARB': dietary_detail['carbohydrate'],
        'Dieta1_DR1TSUGR': dietary_detail['sugars'],
        'Dieta1_DR1TFIBE': dietary_detail['fiber'],
        'Dieta1_DR1TTFAT': dietary_detail['fat'],
        'Dieta1_DR1TTFAT': dietary_detail['fat'],
        'Dieta1_DR1TSFAT': dietary_detail['saturated_fatty_acid'],
        'Dieta1_DR1TSFAT': dietary_detail['saturated_fatty_acid'],
        'Dieta1_DR1TMFAT': dietary_detail['monounsaturated_fatty_acid'],
        'Dieta1_DR1TPFAT': dietary_detail['polyunsaturated_fatty_acid'],
        'Dieta1_DR1TCHOL': dietary_detail['cholesterol'],
        'Dieta1_DR1TCALC': dietary_detail['calcium'],
    }
    activity = {

    }