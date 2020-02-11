from flask import abort, Blueprint, render_template, request
from flask import current_app as app
from flask_login import current_user, login_required
from pantry_raid.models.forms import PantryForm, SearchForm, SubstitutionForm
import pantry_raid.routes.api as api


router = Blueprint('routes', __name__, template_folder='templates')


@router.route('/')
def index():
    """Route to index page."""
    return render_template('index.html',
                           user=current_user)


@router.app_errorhandler(404)
def page_not_found(err):
    """Handles HTTP 404 (resource not found) errors."""
    return render_template('404.html', user=current_user, path=request.path), 404


@router.app_errorhandler(500)
def internal_server_error(err):  # pragma: no cover
    """Handles HTTP 500 (internal server error) errors."""
    return render_template('500.html', user=current_user, path=request.path, error=err), 500


@router.route('/recipe')
def all_recipes():
    """Route to recipe page."""
    return render_template('all_recipes.html',
                            user=current_user,
                            recipes=api.get(api.all_recipes))


@router.route('/favorites')
@login_required
def favorite_recipes():
    """Route to favorite recipes page."""
    return render_template('favorites.html',
                            user=current_user,
                            favorites=api.get(api.favorites).get('favorites'),
                            app=app)


@router.route('/recipe/<rid>')
def recipe(rid=None):
    """Route to individual recipe pages based on the "id" field of the document (recipe)."""
    recipe = api.get_arg(api.recipe, arg=rid)
    if recipe is None:
        abort(404)
    favorites = api.get(api.favorites).get('favorites')
    return render_template('recipe.html',
                            user=current_user,
                            recipe=recipe,
                            favorites=favorites)


@router.route('/recipe/<rid>', methods=["POST"])
@login_required
def recipe_post(rid=None):
    """Route to individual recipe pages based on the "id" field of the document (recipe)."""
    recipe = api.get_arg(api.recipe, arg=rid)
    favorites = api.get(api.favorites).get('favorites')
    if rid in favorites:
        app.db.remove_recipe_from_favorites(rid)
        favorites = api.get(api.favorites).get('favorites')
        return render_template('recipe.html', user=current_user, recipe=recipe, favorites=favorites)
    else:
        app.db.add_recipe_to_favorites(rid)
        favorites = api.get(api.favorites).get('favorites')
        return render_template('recipe.html', user=current_user, recipe=recipe, favorites=favorites)


def setup_searchform():
    form = SearchForm()
    all_tags = sorted(app.db.recipes.collection.distinct('tags'))
    form.tags.choices = [ (tag, tag) for tag in all_tags ]
    return form


@router.route('/search', methods=["GET"])
def search():
    """Route to initial search page."""
    form = setup_searchform()
    return render_template('search.html',
                            user=current_user,
                            form=form,
                            pantry=api.get(api.pantry))


@router.route('/search', methods=["POST"])
def search_results():
    """Route to search results page after a POST request."""
    form = setup_searchform()
    data = {
        "list_filters": {
            k: {
                "items": list(filter(None, request.form.getlist(k))),
                "mongo_operator": form[k].render_kw.get('mongo_operator'),
                "mongo_field": form[k].render_kw.get('mongo_field')
            }
            for k in request.form if k in ('pinned_ingredients', 'excluded_ingredients')
        },
        "comparator_filters": {
            k: {
                "items": form[k].data,
                "mongo_operator": form[k].render_kw.get('mongo_operator'),
                "mongo_field": form[k].render_kw.get('mongo_field')
            }
            for k in request.form if k in ('prep_time') and form[k].data is not None
        },
        "macro_value": {
            k: {
                "items": form[k].data,
                "mongo_operator": form['compare_options'].data,
                "mongo_field": "nutritional info." + form['macronutrients'].data
            }
            for k in request.form if k in ('macronutrient_value') and form[k].data is not None
        },
        "use_subs": request.form.get('use_subs'),
        "sort_options": request.form.get('sort_options'),
        "tags": request.form.getlist('tags')
    }
    return render_template('search.html',
                            user=current_user,
                            matches=api.post(api.search_post, data),
                            form=form,
                            pantry=api.get(api.pantry))


@router.route('/pantry')
def pantry():
    """Route to pantry page."""
    return render_template('pantry.html',
                            user=current_user,
                            data=api.get(api.pantry),
                            form=PantryForm())


@router.route('/pantry', methods=["POST"])
def pantry_post():
    """Route to pantry page on form submission."""
    return render_template('pantry.html',
                            user=current_user,
                            data=api.post(api.pantry_post, request.form),
                            form=PantryForm())


@router.route('/help')
def help():
    """Route to help page."""
    return render_template('help.html', user=current_user)


@router.route('/about')
def about():
    """Route to about page."""
    return render_template('about.html', user=current_user)


@router.route('/substitute')
@login_required
def substitute():
    """Route to the substitutes page."""
    return render_template('substitution.html',
                            user=current_user,
                            data=api.get(api.substitute),
                            form=SubstitutionForm())


@router.route('/substitute', methods=["POST"])
@login_required
def substitute_post():
    """Route to submit changes to the substitute page."""
    form = SubstitutionForm()
    to_remove = request.form.get('remove', None)
    if to_remove:
        data = { "remove_ingredient_index": to_remove }
    else:
        subs = form.data['substitute']  # Originally immutable
        # Strip csrf tokens from the data
        for item in subs:
            item.pop('csrf_token', None)
        data = {
            "name": form.add_target.data,
            "quantity": form.target_qty.data,
            "items": subs
        }
    return render_template('substitution.html',
                            user=current_user,
                            data=api.post(api.substitute_post, data),
                            form=form)


@router.route('/tags/<tag>')
def tags(tag):
    """Route to get recipes by tag."""
    return render_template('tags.html',
                            user=current_user,
                            recipes=api.get_arg(api.tags, tag).get('recipes'),
                            tag=tag)


@router.route('/tags')
def all_tags():
    """Route to show list of all tags."""
    return render_template('all_tags.html',
                            user=current_user,
                            tags=api.get(api.all_tags).get('tags'))
