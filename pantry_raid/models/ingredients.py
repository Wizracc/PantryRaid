from pantry_raid.models.mongocollection import MongoCollection


class Ingredients(MongoCollection):
    def __init__(self, collection):
        """Constructor for wrapper class around the pymongo ingredients collection.

        Parameters
        ----------
        collection : pymongo.Collection
            MongoDB collection
        """
        super().__init__(collection)
        self.collection_key = 'ingredients'
