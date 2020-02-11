from pantry_raid.models.mongocollection import MongoCollection
from pantry_raid.models.status import Status


class Pantry(MongoCollection):
    def __init__(self, collection):
        """Constructor for wrapper class around the pymongo pantry collection.
        Represents the old global pantry. Soon to be deprecated or left as the anonymous user.

        Parameters
        ----------
        collection : pymongo.Collection
            MongoDB collection
        """
        super().__init__(collection)
        self.collection_key = 'pantry'

    def get_partial_match_recipes(self, recipes):
        """DEPRECATED. Retained for possible future use.

        Finds all recipes that use any ingredient from the pantry.

        Parameters
        ----------
        recipes : pantry_raid.models.recipes.Recipes
            Recipes collection from the database to search

        Returns
        -------
        list[dict]
            List of recipes that use at least one ingredient present in the pantry with no duplicate recipes
        """
        partial_matches = [ recipes.get_all_using(ing) for ing in self.get_as_list() ]
        return self.deduplicate_document_list(partial_matches)

    def get_complete_match_recipes(self, recipes):
        """DEPRECATED. Retained for possible future use.

        Get only recipes that contain ingredients in the pantry.

        Parameters
        ----------
        recipes : pantry_raid.models.recipes.Recipes
            Recipes collection to search

        Returns
        -------
        list[dict]
            List of recipes that can be made using only ingredients in this pantry
        """
        partial_matches = self.get_partial_match_recipes(recipes)
        return [
                recipe for recipe in partial_matches
                if set(recipe['ingredient_names']).issubset(self.get_as_list())
        ]

    def insert_new_ingredient(self, new_ingredient):
        """Adds a new ingredient to his pantry.

        Parameters
        ----------
        new_ingredient : string
            New ingredient to insert

        Returns
        -------
        pantry_raid.models.status.Status
        """
        try:
            self.collection.update_one(
                {},
                {
                    "$push": {
                        "pantry": new_ingredient
                    }
                }
            )
            return Status("success", f"Added {new_ingredient} to your pantry.")
        except Exception:  # pragma: no cover
            return Status("danger", f"The service encountered a problem when adding {new_ingredient} to your pantry. Please try again later.")

    def remove_ingredient(self, ingredient):
        """
        Returns
        -------
        pantry_raid.models.status.Status
        """
        try:
            self.collection.update_one(
                {},
                {
                    "$pull": {
                        "pantry": ingredient
                    }
                }
            )
            return Status("info", f"Removed {ingredient} from your pantry.")
        except Exception:  # pragma: no cover
            return Status("danger", f"The service encountered a problem when removing {ingredient} from your pantry. Please try again later.")
