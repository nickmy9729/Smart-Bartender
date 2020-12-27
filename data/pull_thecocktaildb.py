import pprint
import requests
import re
import string
import json

site = "https://www.thecocktaildb.com"
drink_dir = "./drinks"
ingredients_dir = "./ingredients"
glasses_dir = "./glasses"

def get_drink_list():
    categories = get_category_list()
    pprint.pprint(categories)

    drinks = []
    for c in categories:
        if c['strCategory'] == 'Ordinary Drink' or c['strCategory'] == 'Cocktail' or  c['strCategory'] == 'Shot' or c['strCategory'] == 'Soft Drink / Soda':
            url = site + "/api/json/v1/1/filter.php?c=" + c['strCategory']
            payload = {}
            headers= {}
            response = requests.request("GET", url, headers=headers, data = payload)
            for d in response.json()['drinks']:
                drinks.append(d)
    return drinks

def get_category_list():
    url = site + "/api/json/v1/1/list.php?c=list"
    payload = {}
    headers= {}
    response = requests.request("GET", url, headers=headers, data = payload)
    return response.json()['drinks']

def get_drink_detail():
    drinks = get_drink_list()

    drink_details = []
    for d in drinks:
        url = site + "/api/json/v1/1/lookup.php?i=" + d['idDrink']
        payload = {}
        headers= {}
        response = requests.request("GET", url, headers=headers, data = payload)
        drink_details.append(format_drink_details(response.json()['drinks'][0]))
    return drink_details

def format_drink_details(drink):
    d = {
        'name': drink['strDrink'],
        'id': drink['idDrink'],
        'ingredients': {},
        'glass': drink['strGlass'],
        'image': drink['strImageSource'],
        'category': drink['strCategory'],
        'steps': []
    }

    count = 1
    while count <= 15:
        ind_key = 'strIngredient' + str(count)
        measure_key = 'strMeasure' + str(count)

        if ind_key in drink and measure_key in drink:
            ind = drink[ind_key]
            if ind is None or ind == 'null':
                count += 1
                continue
            measure = drink[measure_key]
            d['ingredients'][ind] = measure
        count += 1
    d['steps'].append(list(d['ingredients'].keys()))
    if 'strInstructions' in drink:
        d['steps'].append(drink['strInstructions'])
    writeToDir(drink_dir, d, d['name'])
    return d

def writeToDir(dir, data, name):
    with open(dir + '/' + slugify(name) + '.json', 'w') as outfile:
        json.dump(data, outfile, sort_keys=True, indent=4)

    
def get_ingrediant_list():
    url = site + "/api/json/v1/1/list.php?i=list"
    payload = {}
    headers= {}
    response = requests.request("GET", url, headers=headers, data = payload)
    return response.json()['drinks']

def get_ingredient_details(ingredient_name):
    url = site + "/api/json/v1/1/search.php?i=" + ingredient_name
    payload = {}
    headers= {}
    response = requests.request("GET", url, headers=headers, data = payload)
    return response.json()


def slugify(text):
    text = text.lower()
    return re.sub(r'[\W_]+', '-', text)

def format_ingredients(i):
    i = i['ingredients'][0]
    abv = 0
    if 'strABV' in i:
        if i['strABV'] is not None:
            abv = int(i['strABV'])
    else:
        abv = 0

    return {slugify(i['strIngredient']): {
        'type': defaultValue(i, 'strType', None),
        'description': defaultValue(i, 'strDescription', ''),
        'abv': abv,
        'brandName': defaultValue(i, 'strIngredient', None),
        'image': '',
        'alternatives': [],
        'quality': { 'high': [], 'medium': [], 'low': [] }
   }}

def defaultValue(i, key, default=None):
    try:
        return i[key]
    except:
        return default

#def get_glasses_list():


#def get_glass_detail(glass_name):

#ingredients = get_ingrediant_list()
#ing = {}
#for i in ingredients:
  #detail = format_ingredients(get_ingredient_details(i['strIngredient1']))
  #for i in detail:
      #ing[i] = detail[i]
#pprint.pprint(ing)

get_drink_detail()

