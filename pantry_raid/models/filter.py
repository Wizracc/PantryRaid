class Filter(object):
    """Represents a filter in the form of a query document.

    This document can be passed as the first argument to the find function of a pymongo Collection.
    """

    def __init__(self, filters=None):
        self.doc = { }

        if filters is None:
            return

        for k, v in filters.items():
            operation = { v['mongo_operator']: v['items'] }
            if v['mongo_field'] in self.doc.keys():  # Don't overwrite the existing query
                self.doc[v['mongo_field']].update(operation)

            else:  # No queries on this field yet, make it
                query = {
                    v['mongo_field']: operation
                }
                self.doc.update(query)
