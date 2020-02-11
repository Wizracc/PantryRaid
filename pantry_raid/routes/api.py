from flask import Blueprint, abort, jsonify
from flask import current_app as app
from bson import json_util as bson
import json


api = Blueprint('api', __name__, template_folder='templates')


def _get(func):
    """Calls the JSON API using a HTTP GET request.

    Parameters
    ----------
    func : function
        API function name

    Returns
    -------
    requests.Response object
        full response of HTTP GET request
    """
    return func()


def get(func):
    """Wrapper for HTTP GET API call for only the content, instead of extra information like headers and status code.
    The JSON data of the response is automatically converted into a Python object. Since responses are typically going to be pymongo Documents or lists of them, the result will be a list of dicts.

    Parameters
    ----------
    func : function
        API function name corresponding the path. For example, the API function
    ```
    @api.route('/api/foo')
    def sample_function():
        pass
    ```
    requires "sample_function" -- without parentheses -- to be passed as the 'func' parameter for this function.

    Returns
    -------
    list[dict]
        JSON content of response object as a Python list
    """
    return _get(func).json


def _get_arg(func, arg):
    """Calls the JSON API using a HTTP GET request that takes one argument.

    Parameters
    ----------
    func : function
        API function name

    arg
        Function argument

    Returns
    -------
    requests.Response object
        full response of HTTP GET request
    """
    return func(arg)


def get_arg(func, arg):
    """Wrapper for HTTP GET API call with one argument for only the content, instead of extra information like headers and status code.
    The JSON data of the response is automatically converted into a Python object. Since responses are typically going to be pymongo Documents or lists of them, the result will be a list of dicts.

    Parameters
    ----------
    func : function
        API function name corresponding the path. For example, the API function
    ```
    @api.route('/api/foo')
    def sample_function():
        pass
    ```
    requires "sample_function" -- without parentheses -- to be passed as the 'func' parameter for this function.

    arg
        Function argument

    Returns
    -------
    list[dict]
        JSON content of response object as a Python list
    """
    return _get_arg(func, arg).json


def _post(func, data):
    """Calls the JSON API using a HTTP POST request.

    Parameters
    ----------
    func : function
        API function name

    data : ImmutableMultiDict
        Data to be passed into the POST request. Usually 'request.form' from the caller.

    Returns
    -------
    requests.Response object
        full response of HTTP POST request
    """
    return func(data)


def post(func, data=None):
    """Wrapper for HTTP POST API call for only the content, instead of extra information like headers and status code.

    The JSON data of the response is automatically converted into a Python object. Since responses are typically going to be pymongo Documents or lists of them, the result will be a list of dicts.


    Parameters
    ----------
    func : function
        API function name corresponding the path. For example, the API function
    ```
    @api.route('/api/foo')
    def sample_function():
        pass
    ```
    requires "sample_function" -- without parentheses -- to be passed as the 'func' parameter for this function.

    data : ImmutableMultiDict
        POST data. Typically supplied as 'request.form' by the caller to transfer form data from the frontend web API to the backend JSON API.


    Returns
    -------
    list[dict]
        JSON content of response object as a Python list
    """
    return _post(func, data).json


def from_bson(bs):
    """Helper function to convert BSON to JSON.

    Pymongo returns data in BSON, which is not immediately usable as a Python object. First, bson.dumps is needed to serialize the BSON into a Python string. Then, json.loads can be called on the resulting string to deserialize it into a Python object. This is necessary for the API to function as a JSON API.

    Parameters
    ----------
    bs : BSON (Binary JSON)
        BSON object to convert

    Returns
    -------
    list[dict] or any Python object representing the BSON
        serialized JSON representation of original BSON
    """
    return json.loads(bson.dumps(bs))


@api.route('/api/recipe')
def all_recipes():
    """Handles GET requests to the /api/recipe page.

    Returns
    -------
    flask.Response JSON object
        JSON response containing all recipes in the database
    """
    return jsonify(from_bson(app.db.get_all_recipes()))


@api.route('/api/recipe/<arg>')
def recipe(arg=None):
    """Handles GET requests to a specific /api/recipe/<> page.

    Parameters
    ----------
    arg : string
        Recipe ID

    Returns
    -------
    flask.Response JSON object
        JSON response containing a single recipe
    """
    if arg is None:
        abort(404)  # pragma: no cover
    return jsonify(from_bson(app.db.get_recipe_by_id(arg)))


@api.route('/api/search', methods=["POST"])
def search_post(data=None):
    """Handles POST requests to the /api/search page.

    Filters will need to be applied to the initial `results` object if filtering is done by postprocessing rather than narrowing the Mongo search.

    Returns
    -------
    flask.Response JSON object
        JSON response containing search results
    """
    return jsonify(from_bson(app.db.find_all_matching_recipes(data)))


@api.route('/api/pantry')
def pantry():
    """Handles GET requests to the /api/pantry page.

    Returns
    -------
    flask.Response JSON object
        JSON response containing current pantry and valid ingredients
    """
    return jsonify({
                "pantry": list(app.db.get_pantry_contents()),
                "ingredients": list(app.db.get_all_ingredients())
    })


@api.route('/api/pantry', methods=["POST"])
def pantry_post(data=None):
    """Handles POST requests to the /api/pantry page. Occurs when the user submits the form on the pantry page to add a new ingredient.

    Parameters
    ----------
    data : dict
        POST data

    Returns
    -------
    flask.Response JSON object
        JSON response containing updated pantry, valid ingredients, and a status message for the requested action
    """
    k = list(data.keys())
    if "add_food" in k:
        new_ingredient = data['add_food']
        status = app.db.add_ingredient_to_pantry(new_ingredient)
    else:
        status = app.db.remove_ingredient_from_pantry(k[0])
    return jsonify({
        "pantry": app.db.get_pantry_contents(),
        "ingredients": app.db.get_all_ingredients(),
        "status": { "css": status.css, "text": status.text }
    })


@api.route('/api/substitute')
def substitute(data=None):
    """Handles GET requests to the /api/substitute page.

    Returns
    -------
    flask.Response JSON object
        JSON response containing current pantry and valid ingredients
    """
    return jsonify({
        "substitutions": app.db.get_substitutions(),
        "pantry": app.db.get_pantry_contents(),
        "ingredients": app.db.get_all_ingredients()
    })


@api.route('/api/substitute', methods=["POST"])
def substitute_post(data=None):
    """Handles POST requests to the /api/substitute page.

    Returns
    -------
    flask.Response JSON object
        JSON response containing current pantry and valid ingredients
    """
    remove_index = data.get("remove_ingredient_index", None)
    if remove_index is not None:
        status = app.db.remove_substitution(remove_index)
    else:
        status = app.db.insert_substitution(data)
    return jsonify({
        "substitutions": app.db.get_substitutions(),
        "pantry": app.db.get_pantry_contents(),
        "ingredients": app.db.get_all_ingredients(),
        "status": { "css": status.css, "text": status.text }
    })


@api.route('/api/favorites')
def favorites():
    """Handles GET requests to the /api/favorites page.

    Returns
    -------
    flask.Response JSON object
        JSON response containing favorites
    """
    return jsonify({
        "favorites": list(app.db.get_favorites())
    })


@api.route('/api/tags/<tag>')
def tags(tag=None):
    return jsonify({
        "recipes": app.db.get_recipes_by_tag(tag)
    })


@api.route('/api/tags')
def all_tags():
    return jsonify({
        "tags": sorted(app.db.recipes.collection.distinct('tags'))
    })
