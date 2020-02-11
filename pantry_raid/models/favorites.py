from pantry_raid.models.mongocollection import MongoCollection


class Favorites(MongoCollection):
    def __init__(self, collection):
        """Constructor for wrapper class around the pymongo favorites collection.

        Parameters
        ----------
        collection : pymongo.Collection
            MongoDB collection
        """
        super().__init__(collection)
        self.collection_key = 'favorites'
