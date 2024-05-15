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

def get_portion(portion_string):
    portion = re.search(r'\b\d+\b', portion_string)
    if portion:
        return portion.group()
    else:
        return 0

def get_nutrient_value(nutrients, nutrient_name, nutrient_name_simple):
    try:
        nutrient = nutrients[nutrient_name]

        # Standardize Metrics of Measurement for each nutrients
        if nutrient_name_simple in ['energy']:
            if(nutrient['unitName'] == "KCAL"):
                multiplier = 1
            else:
                multiplier = 0
        if nutrient_name_simple in ['protein', 'carbohydrate', 'sugars', 'fiber', 'fat', 'saturated_fatty_acid', 'monounsaturated_fatty_acid', 'polyunsaturated_fatty_acid']:
            if(nutrient['unitName'] == "G"):
                multiplier = 1
            elif(nutrient['unitName'] == "MG"):
                multiplier = 1000
            elif(nutrient['unitName'] == "KG"):
                multiplier = 0.001
            else:
                multiplier = 0
        if nutrient_name_simple in ['cholesterol', 'calcium']:
            if(nutrient['unitName'] == "G"):
                multiplier = 0.001
            elif(nutrient['unitName'] == "MG"):
                multiplier = 1
            elif(nutrient['unitName'] == "KG"):
                multiplier = 0.000001
            else:
                multiplier = 0
        
        return nutrient['value'] * multiplier

    except:
        return 0



def get_consumption_detail(consumptions):
    if(not isinstance(consumptions, list)):
        raise ValueError("Need to be list of consumptions")
    
    total_detail = {
        'energy': 0,
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

    food_central = fdc.FoodCentral()

    for consumption in consumptions:
        if(consumption['type'] == 'Minuman'):
            continue
        
        # Might Need to Translate the consumption name first
        food_name = consumption['name']

        # Get Nutrient Detail From USDA Food Data Central
        nutrient = food_central.get_nutrients(food_name)
        try:
            portion_multiplier = 100/get_portion(consumption['portion'])
        except:
            portion_multiplier = 1

        detail = {}
        if(nutrient['status'] == 200):
            detail['energy'] = get_nutrient_value(nutrient['foodNutrients'], 'Energy', 'energy') * portion_multiplier
            detail['protein'] = get_nutrient_value(nutrient['foodNutrients'], 'Protein', 'protein') * portion_multiplier
            detail['carbohydrate'] = get_nutrient_value(nutrient['foodNutrients'], 'Carbohydrate, by difference', 'carbohydrate') * portion_multiplier
            detail['sugars'] = get_nutrient_value(nutrient['foodNutrients'], 'Sugars, Total', 'sugars') * portion_multiplier
            detail['fiber'] = get_nutrient_value(nutrient['foodNutrients'], 'Fiber, total dietary', 'fiber') * portion_multiplier
            detail['fat'] = get_nutrient_value(nutrient['foodNutrients'], 'Total lipid (fat)', 'fat') * portion_multiplier
            detail['saturated_fatty_acid'] = get_nutrient_value(nutrient['foodNutrients'], 'Fatty acids, total saturated', 'saturated_fatty_acid') * portion_multiplier
            detail['monounsaturated_fatty_acid'] = get_nutrient_value(nutrient['foodNutrients'], 'Fatty acids, total monounsaturated', 'monounsaturated_fatty_acid') * portion_multiplier
            detail['polyunsaturated_fatty_acid'] = get_nutrient_value(nutrient['foodNutrients'], 'Fatty acids, total polyunsaturated', 'polyunsaturated_fatty_acid') * portion_multiplier
            detail['cholesterol'] = get_nutrient_value(nutrient['foodNutrients'], 'Cholesterol', 'cholesterol') * portion_multiplier
            detail['calcium'] = get_nutrient_value(nutrient['foodNutrients'], 'Calcium, Ca', 'calcium') * portion_multiplier
        
        # Update total nutrients
        for key in total_detail:
            if key in detail:
                total_detail[key] += detail[key]
    
    return total_detail

def get_vigorous_activity_minute(activities):
    if(not isinstance(activities, list)):
        raise ValueError("Need to be list of activities")
    
    total_minutes = 0

    for activity in activities:
        if(activity['heartRate'] > 142):
            total_minutes += activity['duration']
    
    return total_minutes

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

    # ! Need to Update !
    pain = {
        'Quest3_CDQ008': 0
    }

    consumption = data_raw['consumptions']
    if(consumption == None):
        consumption = []

    dietary_detail = get_consumption_detail(consumption)
    dietary = {
        'Dieta1_DR1TKCAL': dietary_detail['energy'],
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

    activities = dietary_detail['activities']
    if(activities == None):
        activities = []
    activity = {
        'Quest19_PAD615': get_vigorous_activity_minute(activities)
    }
    
    body_metrics = data_raw['bodyMetrics']
    if(body_metrics == None):
        body_metrics = {}
    height_weight = {
        'Exami2_BMXWT': body_metrics.get('bodyWeight'),
        'Exami2_BMXHT': body_metrics.get('bodyHeight'),
        'Exami2_BMXBMI': body_metrics.get(
            'bmi',
            body_metrics.get('bodyWeight')/(body_metrics.get('bodyHeight')**2)
        ),
    }

    pressure = {
        'Exami1_SysPulse': body_metrics.get('systolicPressure'),
        'Exami1_DiaPulse': body_metrics.get('diastolicPressure')
    }

    # Rearrage Data for Model Consumption
    data = {}

    # Lifestyle
    data.update(smoking)
    data.update(sleep)
    data.update(dietary)
    data.update(activity)

    # Characteristics
    data.update(age)
    data.update(height_weight)
    data.update(pain)
    data.update(pressure)
