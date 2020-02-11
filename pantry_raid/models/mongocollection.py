from abc import ABC
from pantry_raid.models.filter import Filter
from pantry_raid.models.pipeline import Pipeline
from pantry_raid.models.sortoptions import SortOptions
"""
The "# noqa" directive tells flake8 to ignore the warning on the below line.
Inheritors of this class do need MongoClient, but those functions aren't implemented in the abstract.
"""
from pymongo import MongoClient  # noqa: F401
from pymongo.collation import Collation
from itertools import chain


class MongoCollection(ABC):
    """Abstract wrapper class around a `pymongo.Collection`.

    Attributes
    ----------
    collection : pymongo.Collection
        MongoDB collection

    collection_key : string
        Key for the main field in the collection, e.g., 'pantry', 'ingredients', etc. This must be set in the inheritor's constructor.
    """

    def __init__(self, collection):
        """Constructor for abstract wrapper class around a `pymongo.Collection`.

        Parameters
        ----------
        collection : pymongo.Collection
            MongoDB collection
        """
        self.collection = collection

    def get_as_list(self):
        """Get the contents of the main field as a list.

        Returns
        -------
        list[dict]
            Deduplicated list of entries in the field 'collection_key' or all entries in the collection.
        """
        try:
            return list(set(self.collection.find_one({}, { '_id': False })[self.collection_key]))
        except AttributeError:
            return list(self.collection.find({}, { '_id': False }))

    def flatten_nested_dict_lists(self, dicts):
        """DEPRECATED. Retained for possible future use.

        Flattens a list of lists of dictionaries.

        Parameters
        ----------
        dicts : list[list[dict]]
            List of lists of dictionaries

        Returns
        -------
        list[dict]
            Flattened version of original list
        """
        if type(dicts[0]) is list:
            dicts = list(chain.from_iterable(dicts))
        return dicts

    def deduplicate_document_list(self, docs):
        """DEPRECATED. Retained for possible future use.

        Removes all duplicates from a list of Documents.
        Two documents are the same if their ID is the same.
        Credit: https://stackoverflow.com/questions/11092511

        Parameters
        ----------
        docs : list[dict]
            List of documents with potentially duplicate entries

        Returns
        -------
        list[dict]
            List of documents without any duplicate entries
        """
        docs = self.flatten_nested_dict_lists(docs)
        return [ i for n, i in enumerate(docs) if i not in docs[n + 1:] ]

    def get_subset(self, field, required_set, data):
        """Gets documents from this collection whose contents of `field` are subsets of `required_set`.

        Optionally, applies a query against the documents that are the subset to further narrow search results.

        Parameters
        ----------
        field : string
            Name of the field in this collection

        required_set : list
            The list of items that the contents of `field` should be a subset of

        filters : pantry_raid.models.filter.Filter
            Filters to apply after getting valid recipes.

        Returns
        -------
        list[dict]
            List of documents satisfying the subset requirement
        """

        pipeline = Pipeline()
        pipeline.add_subset_aggregation(field, required_set)

        if data is not None:
            pipeline.add_filter(Filter(data.get('filters')))
            pipeline.add_sort_options(SortOptions(data.get('sort_options')))

            if data.get('tags') is not None and len(data.get('tags')) > 0:
                pipeline.add_set_intersection_aggregation('tags', data.get('tags'))

        pipeline.remove__id()

        return list(self.collection.aggregate(pipeline.operations, collation=Collation("en", numericOrdering=True)))
