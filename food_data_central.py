import requests

class FoodCentral:
    __base_endpoint = 'https://api.nal.usda.gov/fdc/v1/'
    __search_endpoint = __base_endpoint + 'foods/search'
    __list_endpoint = __base_endpoint + 'foods/list'

    def _init_(self, food_combination:list=[], api_key:str=''):
        self.__api_key = api_key
        self.__food_combination = food_combination
        return

    def deconstruct_food(self, food_combination):
        return

    def get_nutrients(self, keyword):
        params = {
            'api_key': self.__api_key,
            'query': keyword,
            'dataType': ['Foundation'],
            'sortBy': 'publishedDate',
            'sortOrder': 'desc'
        }

        response = requests.get(self.__search_endpoint, params=params)
        try:
            if response.json()['totalHits'] > 0:
                food = response.json()['foods'][0]
                obj_data = {
                    'query': response.json()['foodSearchCriteria']['query'],
                    'description': food['description'],
                    'publishedDate': food['publishedDate'],
                    'foodNutrients': {},
                    'portion': {
                        'size': 100,
                        'unit': 'g'
                    },
                    'status': response.status_code
                }
                obj_data['foodNutrients'] = {}
                for nutrient in food['foodNutrients']:
                    obj_data['foodNutrients'][nutrient['nutrientName']] = {
                        'value': nutrient['value'],
                        'unitName': nutrient['unitName'],
                    }
            else:
                raise Exception
        except:
            obj_data = {
                'query': response.json()['foodSearchCriteria']['query'],
                'status': response.status_code
            }

        return obj_data