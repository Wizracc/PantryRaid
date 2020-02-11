class Pipeline(object):
    """Represents a pipeline to be used by a `pymongo.Collection.aggregate()` call.

    A pipeline is a series of operations to be performed on a collection, typically to perform advanced search functions. The order of steps is important, as aggregration operations are performed only on the document as it exists at that step in the pipeline. If the first operation in a pipeline is a match operation, then subsequent operations are only going to operate against that set of matched documents.

    Attributes
    ----------
    operations : list[dict]
        Ordered list of aggregation operations to be performed on a collection
    """

    def __init__(self):
        self.operations = []

    def add_subset_aggregation(self, field, required_set):
        """Adds pipeline operations to get only documents where `field` is a subset of `required_set`.

        Params
        ------
        field : string
            Field in documents to check

        required_set : list[string] or set[string]
            Set to perform subset operation against
        """
        doc_projection = "doc"
        operator = "setIsSubset"
        self.add_array_projection_doc(operator, field, required_set, doc_projection)
        self.add_boolean_match_projection(f"{operator}_{field}", doc_projection)
        self.replace_root(doc_projection)

    def add_set_intersection_aggregation(self, field, other_set):
        """Adds pipeline operations to get only documents where the result of a set intersection between `field` and `other_set` is a nonzero array.

        Params
        ------
        field : string
            Field in document containing the array

        other_set: list[string] or set[string]
            Set to intersect the contents of `field` with
        """
        doc_projection = "doc"
        operator = "setIntersection"
        self.add_array_projection_doc(operator, field, other_set, doc_projection)
        result_field = "intersection_gtzero"
        self.project_array_size_above_zero_aggregation(f"{operator}_{field}", result_field, doc_projection)
        self.flatten_projected_doc(doc_projection, result_field)
        self.add_boolean_match_projection(result_field, doc_projection)
        self.replace_root(doc_projection)

    def flatten_projected_doc(self, doc_projection, *sibling_fields):
        """Unwinds a nested `$$ROOT` while retaining the contents of `sibling_fields` as part of the flattened document. During pipeline operations, the entire document is typically stored in `doc_projection` to retain its contents, and the results of an aggregation operation is stored in one or more `sibling_fields`. As a result, the `doc_projection` field would contain a `doc_projection` field itself that actually has the document. This function replaces the root with the original document and adds the `sibling_fields` so that pipeline processing may continue.

        Params
        ------
        doc_projection : string
            Field containing the original document

        sibling_fields : string
            One or more fields that exist adjacent to the `doc_projection` field, created through other pipeline operations. Multiple fields would be passed in by calling the function as `flatten_projected_doc("doc", "field1", "field2", ..., "fieldN")`.
        """
        keep_fields = {
            f"{doc_projection}.{sf}": f"${sf}"
            for sf in sibling_fields
        }
        self.add_operation_by_kvp("$addFields", keep_fields)
        self.replace_root(doc_projection)

    def replace_root(self, doc_projection):
        """Replaces the root of the document with the contents of `doc_projection`.

        Params
        ------
        doc_projection : string
            Field to promote as new root
        """
        newRoot = { "newRoot": f"${doc_projection}" }
        self.add_operation_by_kvp("$replaceRoot", newRoot)

    def add_boolean_match_projection(self, agg_field, doc_projection):
        """Collects documents in the pipeline where `agg_field` is `True` and projects (returns in the pipeline) only the value of `doc_projection`.

        Parameters
        ----------
        agg_field : string
            Field in the documents that should be true for the document to continue through the pipeline

        doc_projection : string
            Field in the documents that holds the original document
        """
        aggregateMatch = { agg_field: True }
        self.add_operation_by_kvp("$match", aggregateMatch)

        projectDocument = { doc_projection: True }
        self.add_operation_by_kvp("$project", projectDocument)

    def add_array_projection_doc(self, operator, field, operand_array, doc_projection):
        """Adds pipeline operations to perform an array operation and store the result in a top-level field of the result document, `{operator}_{field}`, with a sibling field, `{doc_projection}`, that contains the actual document matched. The contents of `{operator}_{field}` will be an array.

        Params
        ------
        operator : string
            MongoDB array aggregation operator that returns an array

        field : string
            Field in document database to operate on

        operand_array : list
            Array to operate the field contents against

        doc_projection : string
            Field to store the original document in
        """
        # The field must be prepended by a "$" for MongoDB to substitute the value of the field during the operation
        cash_field = f"${field}" if field[0] != '$' else f"{field}"
        aggregateOperand = {
            doc_projection: "$$ROOT",  # Get the entire document for each match and refer to it as `doc_projection`
            f"{operator}_{field}": {  # Perform the operation
                f"${operator}": [ cash_field, operand_array ]
            }
        }
        # Projection stores the original document as `doc_projection` and the results of the aggregation in another field.
        self.add_operation_by_kvp("$project", aggregateOperand)

    def project_array_size_above_zero_aggregation(self, array_field, result_field, doc_projection):
        """Checks if the size of an array field created through aggregation was larger than zero. For example, if a set intersection result was of size 0, then no elements were in common in the two arrays intersected. The result is stored in the field `{result_field}`.

        Params
        ------
        array_field : string
            Field containing an array

        result_field : string
            Field to store the results of the check in

        doc_projection : string
            Field containing the original document
        """
        arrayProjection = {
            doc_projection: "$$ROOT",
            result_field: {
                "$cond": {
                    "if": { "$gt": [{ "$size": f"${array_field}" }, 0] },
                    "then": True,
                    "else": False
                }
            }
        }
        self.add_operation_by_kvp("$project", arrayProjection)

    def add_operation_by_kvp(self, key, value):
        """Add a generic pipeline operation by a key-value pair.

        Parameters
        ----------
        key : string
            The aggregation operator to use. Must be prefixed with a "$". See https://docs.mongodb.com/v4.0/reference/operator/aggregation/ for valid operators.

        value : dict
            Operands or predicate for this operation
        """
        self.operations.append({
            key: value
        })

    def remove__id(self):
        """Remove the "_id" field from results."""
        self.add_operation_by_kvp("$project", {
            "_id": False
        })

    def add_filter(self, filtr):
        """Adds matching against a Filter to the pipeline.

        Parameters
        ----------
        filtr : pantry_raid.models.filter.Filter
            Filter to match against
        """
        if filtr is not None:
            self.add_operation_by_kvp("$match", filtr.doc)

    def add_sort_options(self, sort_options):
        """Adds sort options to the pipeline

        Parameters
        ----------
        sort_options : pantry_raid.models.sortoptions.SortOptions
            Sort options to sort by
        """
        if sort_options is not None:
            self.add_operation_by_kvp("$sort", sort_options.doc)
