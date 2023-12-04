import os
import json
import re
import functions_framework
import requests
from cloudevents.http.event import CloudEvent
from dapr.clients import DaprClient
import uuid

base_url = os.getenv('DAPR_HTTP_ENDPOINT', 'YOUR_CATALYST_PROJECT_URL')
dapr_api_token = os.getenv('DAPR_API_TOKEN', 'YOUR_APP_ID_API_TOKEN')
kvstore_name = os.getenv('KVSTORE_NAME', 'kvstore')

@functions_framework.cloud_event
def get_recipe_http(cloud_event: CloudEvent):
    """HTTP Cloud Function that fetches a recipe based on the provided criteria.
    Args:
        request (flask.Request): The request object.
    Returns:
        A recipe based on the provided criteria.
    """

    def fetch_recipe(meal_type, food_type, recipe_difficulty, food_restrictions):
        api_key = "YOUR_API_KEY"
        url = "https://api.spoonacular.com/recipes/complexSearch"
        params = {
            "apiKey": api_key,
            "type": meal_type,
            "query": recipe_difficulty,
            "diet": food_type,
            "intolerances": food_restrictions,
            "addRecipeInformation": "true",
            "instructionsRequired": "true",
        }
        response = requests.get(url, params=params)
        if response.status_code == 200:
            recipes = response.json().get('results', [])
            if recipes:
                return recipes[0]
            else:
                return "No recipes found."
        else:
            return "Failed to fetch recipes."

    def persist_recipe_json(recipe_out):
        key = str(uuid.uuid4())
        print("saving state key "+key)
        headers = {'dapr-api-token': dapr_api_token, 'content-type': 'application/json'}
        result = requests.post(
            url='%s//v1.0/state/%s' % (base_url, kvstore_name),
            data=json.dumps([
                {
                    "key": key,
                    "value": recipe_out
                }
            ]),
            headers=headers
        )
        print(result)
        return result.ok

    print(cloud_event)

    if kvstore_name == "" :
        return "KVSTORE_NAME not set"

    if cloud_event.data :
        # outbox does not send the data in properly formatted json because the state is not persisted as a bytearray but as a json
        # food_type = cloud_event.data['foodType']
        # recipe_difficulty = cloud_event.data['recipeDifficulty']
        # food_restrictions = cloud_event.data['foodRestrictions']

        # workaround
        patterns = {
            'createdAt': r'createdAt:([^ ]+)',
            'mealType': r'mealType:([^ ]+)',
            'foodRestrictions': r'foodRestrictions:([^ ]+)',
            'foodType': r'foodType:([^ ]+)',
            'recipeDifficulty': r'recipeDifficulty:([^ ]+)',
            'request': r'request:([^ ]+)'
        }
        variable_values = {}
        for key, pattern in patterns.items():
            match = re.search(pattern, cloud_event.data)
            if match:
                variable_values[key] = match.group(1)
        
        created_at = variable_values['createdAt']

        if "mealType" in variable_values:
            meal_type = variable_values['mealType']
        else:
            meal_type = ""

        if "foodType" in variable_values:
            food_type = variable_values['foodType']
        else:
            food_type = ""

        if "recipeDifficulty" in variable_values:
            recipe_difficulty = variable_values['recipeDifficulty']
        else:
            recipe_difficulty = ""

        if "foodRestrictions" in variable_values:
            food_restrictions = variable_values['foodRestrictions']
        else:
            food_restrictions = ""

    else:
        return 'Invalid or missing payload.'

    recipe = fetch_recipe(meal_type, food_type, recipe_difficulty, food_restrictions)

    recipe_out = {
        "result": "true",
        "createdAt": created_at,
        'mealType': meal_type,
        'foodRestrictions': food_restrictions,
        'foodType': food_type,
        'recipeDifficulty': recipe_difficulty,
        "recipe": recipe,
    }

    # dapr sdk cannot be used to persist data in json format, it forces to persist in bytearray
    # with DaprClient() as d:
    #     d.save_state(kvstore_name, str(uuid.uuid4()), out_json)
    
    if not persist_recipe_json(recipe_out):
        return "error persisting recipe"


    print("successfully processed event")
    return json.dumps(recipe_out)
