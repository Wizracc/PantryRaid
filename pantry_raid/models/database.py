from flask_login import current_user
from flask import flash
from pymongo import MongoClient
from pantry_raid.models.favorites import Favorites
from pantry_raid.models.ingredients import Ingredients
from pantry_raid.models.pantry import Pantry
from pantry_raid.models.recipes import Recipes
from pantry_raid.models.status import Status
from pantry_raid.models.usercollection import UserCollection


class Database(object):
    """Class for all MongoDB-related operations. This class acts as a public interface to all MongoCollections.

    Attributes
    ----------
    config : pantry_raid.config.Config
        Configuration object used to instantiate the client.

    mongoc : pymongo.MongoClient
        Database client.

    mongodb : pymongo.Database
        Mongo database to interact with.

    pantry : pantry_raid.models.pantry.Pantry
        Deprecated anonymous pantry collection. When the user is logged in, functions instead call functions from UserCollection to act on a specific user's pantry.

    recipes : pantry_raid.models.recipes.Recipes
        Recipe collection.

    ingredients : pantry_raid.models.ingredients.Ingredients
        Ingredients collection.
    """

    def __init__(self, config):
        """Instantiates a database client.

        Parameters
        ----------
        config : config.Config
            Configuration object used to instantiate the client.
        """
        self.config = config
        self.mongoc = self.setup_mongoclient()
        self.mongodb = self.mongoc.get_database()

        self.recipes = Recipes(self.mongodb.recipes_v2)
        self.ingredients = Ingredients(self.mongodb.ingredients_v2)
        self.pantry = Pantry(self.mongodb.pantry)
        self.users = UserCollection(self.mongodb.users)
        self.favorites = Favorites(self.mongodb.favorites)

    def setup_mongoclient(self):
        """Creates a MongoClient with the appropriate connection and authentication string.

        Returns
        -------
        pymongo.MongoClient
            MongoClient for the configured database
        """
        return MongoClient(self.config['CONNECTION_URL'])

    def get_all_ingredients(self):
        """Gets all ingredients from the Ingredients collection.

        Returns
        -------
        list[string]
            List of ingredients
        """
        return self.ingredients.get_as_list()

    def get_all_recipes(self):
        """Gets all recipes from the Recipes collection.

        Returns
        -------
        list[dict]
            List of recipes as dicts
        """
        return self.recipes.get_as_list()

    def get_pantry_contents(self):
        """Gets all inredients from the current Pantry collection.

        Returns
        -------
        list[string]
            List of pantry ingredients
        """
        if current_user.is_active:
            return sorted(self.users.find_by_username(current_user.database["_id"])['pantry'], key=lambda v: v.upper())
        return sorted(self.pantry.get_as_list(), key=lambda v: v.upper())

    def add_ingredient_to_pantry(self, new_ingredient):
        """Attempts to add a new ingredient to the Pantry collection. Ensures that the ingredient requested is both valid (exists in at least one recipe) and isn't already present in the current pantry.

        Parameters
        ----------
        new_ingredient : string
            New ingredient to add

        Returns
        -------
        dict
            Dict containing status text and CSS class to apply to the status text indicating success or failure.
        """
        if new_ingredient not in self.get_all_ingredients():
            return Status("danger", f"Error: '{new_ingredient}' is not a valid ingredient")
        elif new_ingredient in self.get_pantry_contents():
            return Status("danger", f"Error: '{new_ingredient}' is already in your pantry.")

        if current_user.is_active:
            return self.users.pantry_insert_ingredient(new_ingredient, current_user.database["_id"])

        return self.pantry.insert_new_ingredient(new_ingredient)

    def remove_ingredient_from_pantry(self, ingredient_to_remove):
        """Attempts to remove an ingredient from the pantry.

        Parameters
        ----------
        ingredient_to_remove : string
            New ingredient to add

        Returns
        -------
        dict
            Dict containing status text and CSS class to apply to the status text indicating success or failure.
        """
        if ingredient_to_remove not in self.get_pantry_contents():
            return Status("danger", f"Error: '{ingredient_to_remove}' is not in your pantry.")

        if current_user.is_active:
            return self.users.pantry_remove_ingredient(ingredient_to_remove, current_user.database["_id"])

        return self.pantry.remove_ingredient(ingredient_to_remove)

    def find_all_matching_recipes(self, data=None):
        """Finds all recipes that use only ingredients from the current pantry.

        Parameters
        ----------
        filters : list[dict]
            Desired filters

        Returns
        -------
        list[dict]
            List of recipe documents
        """
        if data is not None:
            if data.get('list_filters') is None:
                data['filters'] = data.get('comparator_filters')
            else:
                data['filters'] = data.get('list_filters')
                data['filters'].update(data.get('comparator_filters'))
                data['filters'].update(data.get('macro_value'))
            if data.get('use_subs', 'n') == 'y' and current_user.is_active:
                pantry = self.users.get_pantry_with_substitutions(current_user.get_id())
            else:
                pantry = self.get_pantry_contents()
        else:
            pantry = self.get_pantry_contents()
        return self.recipes.get_from_pantry(pantry, data)

    def get_recipe_by_id(self, rid):
        """Gets a single recipe by the "id" field.

        Parameters
        ----------
        id : string
            Recipe ID

        Returns
        -------
        dict
            Dict representing a single recipe document
        """
        return self.recipes.get_by_id(rid)

    def get_favorites(self):
        """Gets all inredients from the current Favorites collection.

        Returns
        -------
        list[string]
            List of favorite recipes
        """
        if current_user.is_active:
            return sorted(self.users.find_by_username(current_user.database["_id"])['favorites'], key=lambda v: v.upper())
        return []

    def add_recipe_to_favorites(self, recipe):
        """Attempts to add a new ingredient to the Pantry collection. Ensures that the ingredient requested is both valid (exists in at least one recipe) and isn't already present in the current pantry.

        Parameters
        ----------
        recipe : string
            New recipe to add

        Returns
        -------
        dict
            Dict containing status text and CSS class to apply to the status text indicating success or failure.
        """
        if recipe in self.get_favorites():
            flash(f"Error: '{recipe}' is already in your favorites.", "danger")
            return

        if current_user.is_active:
            return self.users.favorites_insert_recipe(recipe, current_user.database["_id"])

        # nothing to return if anonymous
        return

    def remove_recipe_from_favorites(self, recipe):
        """Attempts to remove an ingredient from the pantry.

        Parameters
        ----------
        recipe : string
            recipe to remove

        Returns
        -------
        dict
            Dict containing status text and CSS class to apply to the status text indicating success or failure.
        """
        if recipe not in self.get_favorites():
            flash(f"Error: '{recipe}' is not in your pantry.", "danger")

        if current_user.is_active:
            return self.users.favorites_remove_recipe(recipe, current_user.database["_id"])

        # nothing to remove if anonymous
        return

    def get_substitutions(self):
        """Gets the current user's substitutions.

        Returns
        -------
        list
            Substitutions
        """
        if current_user.is_active:
            return self.users.find_by_username(current_user.get_id()).get('substitutes')
        return []

    def insert_substitution(self, sub):
        """Inserts a new custom substitution.

        Parameters
        ----------
        sub : dict
            Dict containing substitution information to insert

        Returns
        -------
        pantry_raid.models.status.Status
        """
        if current_user.is_active:
            return self.users.substitute_insert(sub, current_user.get_id())
        return Status("danger", "Please log in to create custom ingredient substititions.")

    def remove_substitution(self, sub_index):
        """Removes a custom substitution. Removal is based on index, because the same ingredient and quantity could be substituted in different ways.

        Parameters
        ----------
        sub_index : string or int
            Array index of the substitution to remove

        Returns
        -------
        pantry_raid.models.status.Status
        """
        if current_user.is_active:
            return self.users.substitute_remove(sub_index, current_user.get_id())
        return Status("danger", "Please log in to remove ingredient substititions.")

    def get_recipes_by_tag(self, tag):
        """Gets all recipes of a certain tag.

        Params
        ------
        tag : string

        Returns
        -------
        list
            Matching recipes
        """
        return list(self.recipes.get_by_tag(tag))
