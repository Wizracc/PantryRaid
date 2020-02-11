from ingredient_parser import parse
import json
import pymongo


mongourl = 'mongodb://david:davidpass1@ds131747.mlab.com:31747/heroku_nkn2zcvj'
client = pymongo.MongoClient(mongourl)

db = client.heroku_nkn2zcvj

data = {}
updated_data = {'recipes': []}
new_ingredient_set = set({})

with open('scripts/recipes16.json') as json_file:
    data = json.load(json_file)

for recipe in data['recipes']:
    print("Recipe: " + recipe['name'])
    recipe_ings = []
    recipe_dicts = []
    for ingredient_string in recipe['ingredients']:
        ingredient_dict = parse(ingredient_string)
        ingredient_name = ingredient_dict['ingredients']
        if ingredient_name is not None:
            new_ingredient_set.add(ingredient_name)
            recipe_ings.append(ingredient_name)
            recipe_dicts.append(ingredient_dict)

    updated_recipe = recipe
    updated_recipe['ingredient_names'] = recipe_ings
    updated_recipe['ing_dicts'] = recipe_dicts
    updated_data['recipes'].append(updated_recipe)

ingredients_coll = db['ingredients_v2']
ingredient_doc = ingredients_coll.find_one()

old_ingredient_set = set(list(ingredient_doc['ingredients']))

ingredient_array = sorted((new_ingredient_set.union(old_ingredient_set)))

ingredients_coll.update_one({},{"$set":{"ingredients": ingredient_array}})

recipes_coll = db['recipes_v2']
recipes_coll.insert_many(updated_data['recipes'])

print("Success!")
print("New Ingredients: " + str(new_ingredient_set))