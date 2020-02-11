from pantry_raid.models.mongocollection import MongoCollection


class Recipes(MongoCollection):
    def __init__(self, collection):
        """Constructor for wrapper class around the pymongo recipes collection.

        Parameters
        ----------
        collection : pymongo.Collection
            MongoDB collection

        collection_key : string
            Key for the main field in the collection
        """
        super().__init__(collection)

    def get_all_using(self, ingredient):
        """Finds all recipes in the database that use this ingredient.

        Parameters
        ----------
        ingredient : string
            Ingredient to find in recipes

        Returns
        -------
        list[dict]
            A list of recipes that use the ingredient
        """
        return [ doc for doc in self.collection.find({ 'ingredient_names': ingredient }, { '_id': False }) ]

    def get_by_id(self, rid):
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
        return self.collection.find_one({ 'id': rid }, { '_id': False })

    def get_from_pantry(self, pantry, data=None):
        """Gets recipes that can be made only using ingredients from the pantry.

        Parameters
        ----------
        pantry : list[string]
            List of ingredients in the pantry

        Returns
        -------
        list[dict]
            List of recipes
        """
        return self.get_subset("ingredient_names", pantry, data)

    def get_by_tag(self, tag):
        """Gets recipes containing `tag` in the `tags` field.

        Parameters
        ----------
        tag : string
        """

        return self.collection.find({ "tags": tag }, { "_id": False })
