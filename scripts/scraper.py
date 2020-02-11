# This scraper will grab recipies from allrecipes.com,
# from the first page of each of the major categories
# Data is intended to be stored on a mongodb, however
# the database is not currently set up.
# The output will currently be a .json file for development purposes
# We can decide to edit the scraper to place documents in the DB, or
# to write a simple script to put the .json file into the mongodb
from bs4 import BeautifulSoup
import requests
import re
import time
import json
import sys
from selenium import webdriver
from selenium.webdriver.firefox.options import Options

# Initiate debug mode by having literally any additional args
DEBUG = len(sys.argv)-1
SLEEP_TIME = 10

options = Options()
options.headless = True

def main():
  # This is the collection of all the various categories
  # that are to be scraped. It is easier to manually cherry-pick
  # the links than to attempt to make this scraper even more complicated
  # For now, I just chose the "Meal Type" major category while developing
  #category_urls = \
  #  ["https://www.allrecipes.com/recipes/78/breakfast-and-brunch/",
  #  "https://www.allrecipes.com/recipes/79/desserts/",
  #  "https://www.allrecipes.com/recipes/17562/dinner/",
  #  "https://www.allrecipes.com/recipes/17561/lunch/"]

  category_urls = [
    "https://www.allrecipes.com/recipes/200/meat-and-poultry/beef/",
    "https://www.allrecipes.com/recipes/16930/fruits-and-vegetables/beans-and-peas/",
    "https://www.allrecipes.com/recipes/201/meat-and-poultry/chicken/",
    "https://www.allrecipes.com/recipes/17822/ingredients/chocolate/",
    "https://www.allrecipes.com/recipes/1058/fruits-and-vegetables/fruits/",
    "https://www.allrecipes.com/recipes/202/meat-and-poultry/game-meats/",
    "https://www.allrecipes.com/recipes/13329/ingredients/whole-grains/",
    "https://www.allrecipes.com/recipes/15172/fruits-and-vegetables/mushrooms/",
    "https://www.allrecipes.com/recipes/95/pasta-and-noodles/",
    "https://www.allrecipes.com/recipes/205/meat-and-poultry/pork/",
    "https://www.allrecipes.com/recipes/1540/fruits-and-vegetables/vegetables/potatoes/",
    "https://www.allrecipes.com/recipes/224/side-dish/rice/",
    "https://www.allrecipes.com/recipes/416/seafood/fish/salmon/",
    "https://www.allrecipes.com/recipes/430/seafood/shellfish/shrimp/",
    "https://www.allrecipes.com/recipes/16778/everyday-cooking/vegetarian/protein/",
    "https://www.allrecipes.com/recipes/206/meat-and-poultry/turkey/",
    "https://www.allrecipes.com/recipes/225/side-dish/vegetables/"
  ]

  #recipe_data = get_recipe_data_from_urls(category_urls)
  #filename = 'scripts/recipes.json'
  #dump_to_json(recipe_data, filename)
  make_category_json_files(category_urls)

def make_category_json_files(urls):
  for i in range(11, len(urls)):
    recipe_data = get_recipe_data_from_urls([urls[i]])
    filename = 'scripts/recipes' + str(i) + '.json'
    dump_to_json(recipe_data, filename)

#returns a dictionary that contains an array of recipe dictionaries
def get_recipe_data_from_urls(urls):
  # create a dictionary to hold an array of recipes
  recipe_data = {}
  recipe_data['recipes'] = []

  # create a list to hold recipe IDs to prevent duplicates from being added
  recipe_ids = []

  # define range of URLs to go through
  outer_range = []
  if DEBUG:
    outer_range = [0]
  else:
    outer_range = range(len(urls))
  for i in outer_range:
    url = urls[i]

    #extract tags from URL
    tags = url.split("/")[5:-1]
    print(tags)
    if "ingredients" in tags:
      tags.remove("ingredients")

    # get the response of the specific category
    response = requests.get(url)

    # Parse HTML with BeautifulSoup into soup object
    soup = BeautifulSoup(response.content, 'html.parser')

    # Grab the recipe cards and shove them in an array
    recipe_cards = soup.find_all(class_="fixed-recipe-card")

    # From each recipe card, find the link to the recipe
    # Define the range of the inner loop, can set to [0] for testing
    # as opposed to "for card in recipe_cards:"
    inner_range = []
    if DEBUG:
      inner_range = [-1]
    else:
      inner_range = range(len(recipe_cards))
    for i in inner_range:
      # Always make sure to sleep so you don't flood the server
      time.sleep(SLEEP_TIME)

      card = recipe_cards[i]

      # Get the link to the recipe from the card
      card_link_tag = card.find(class_="fixed-recipe-card__title-link")
      card_link = card_link_tag.get("href")

      # Recipe ID
      recipe_id = get_recipe_id(card_link)

      if recipe_id not in recipe_ids:
        recipe_ids.append(recipe_id)
        try:
          recipe_dict = get_recipe_from_card(card_link)
          recipe_dict['tags'] = tags
          recipe_data['recipes'].append(recipe_dict)
        except:
          print("Couldn't get recipe")

  # Always make sure to sleep so you don't flood the server
  time.sleep(SLEEP_TIME)
  # Return the resulting dictionary
  return recipe_data


# Returns a dictionary of a recipe's information
def get_recipe_from_card(card_link):
  # Recipe id
  recipe_id = get_recipe_id(card_link)

  # prepare the dictionary for the recipe data
  recipe_dict = {}
  # Get the HTML for the recipe using selenium
  # recipe_response = requests.get(card_link)

  driver = webdriver.Firefox(options=options, executable_path='scripts/geckodriver.exe')
  driver.get(card_link)
  # Click button for nutrition info
  recipe_response = driver.page_source
  driver.quit()

  # Parse HTML for the recipe
  recipe_soup = BeautifulSoup(recipe_response, 'html.parser')

  # Get the various components:
  # Recipe Name
  recipe_name_tag = recipe_soup.find(class_="recipe-summary__h1")
  # Sometimes titles don't exist... This indicates further errors.
  # Ignore these recipes
  if recipe_name_tag is not None:
    recipe_name = recipe_name_tag.string

    # Ingredients
    ingredients = []
    ingredient_items = recipe_soup.find_all(attrs={"itemprop":"recipeIngredient"})

    for item in ingredient_items:
      ingredients.append(item.string)

    # Instructions
    instructions = []
    instructions_items = recipe_soup.find_all(class_="recipe-directions__list--item")
    # For some reason there are sometimes "blank" instructions. We don't want these
    for item in instructions_items:
      if item.string is not None:
        instructions.append(item.string.strip())
    # Image
    image_item = recipe_soup.find(class_="rec-photo")
    recipe_image = image_item["src"]
    # Link to Recipe
    recipe_link = card_link
    # Serving Size
    serving_size = recipe_soup.find(attrs={"ng-bind":"adjustedServings"}).string
    # Prep time
    prep_time = recipe_soup.find(class_="ready-in-time").string

    # Nutrition information
    nut_dict = {}

    calories_text = recipe_soup.find(attrs={"itemprop":"calories"}).string
    calories = calories_text.split()[0]
    nut_dict['calories'] = calories

    fat_text = recipe_soup.find(attrs={"itemprop":"fatContent"})
    fat_content = str(fat_text).split(">")[1].split()[0]
    nut_dict['grams fat'] = fat_content

    carb_text = recipe_soup.find(attrs={"itemprop":"carbohydrateContent"})
    carb_content = str(carb_text).split(">")[1].split("<")[0]
    nut_dict['grams carbohydrates'] = carb_content

    protein_text = recipe_soup.find(attrs={"itemprop":"proteinContent"})
    protein_content = str(protein_text).split(">")[1].split()[0]
    nut_dict['grams protein'] = protein_content

    chol_text = recipe_soup.find(attrs={"itemprop":"cholesterolContent"})
    chol_content = str(chol_text).split(">")[1].split()[0]
    nut_dict['milligrams cholesterol'] = chol_content

    na_text = recipe_soup.find(attrs={"itemprop":"sodiumContent"})
    na_content = str(na_text).split(">")[1].split()[0]
    nut_dict['milligrams sodium'] = na_content

    #add items to dictionary
    recipe_dict['name'] = recipe_name
    recipe_dict['id'] = recipe_id
    recipe_dict['servings'] = serving_size
    recipe_dict['ingredients'] = ingredients
    recipe_dict['instructions'] = instructions
    recipe_dict['image'] = recipe_image
    recipe_dict['link'] = recipe_link
    recipe_dict['prep-time'] = prep_time
    recipe_dict['nutritional info'] = nut_dict

    print(recipe_dict['name'])
    return recipe_dict


# returns the id of a given recipe from its link
def get_recipe_id(card_link):
  # Recipe ID
  id_re = re.compile(r".+/(\d+)/.+")
  recipe_id = id_re.match(card_link).group(1)
  return recipe_id


# dump the contents of a given data dictionary to the provided file
def dump_to_json(data, filename):
  with open(filename, 'w') as outfile:
    json.dump(data, outfile, indent=2)

main()