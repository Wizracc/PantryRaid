from flask import flash
from pantry_raid.models.mongocollection import MongoCollection
from pantry_raid.models.status import Status


class UserCollection(MongoCollection):
    """Class to represent the persistent database of users, as opposed to the volatile User class used by Flask-Login."""

    def find_by_username(self, username):
        """Gets the user document from the collection based on the primary key (username).

        Parameters
        ----------
        username : string
            Username to get

        Returns
        -------
        pymongo.Document or None
            Document associated with the user if it exists
        """
        return self.collection.find_one({ "_id": username })

    def username_exists(self, username):
        """Helper function to check if a username is taken.

        Parameters
        ----------
        username : string
            Username to check

        Returns
        -------
        boolean
            Whether the username is taken
        """
        return self.find_by_username(username) is not None

    def add_new_user(self, user):
        """Insert a newly created user into the collection. Before this function is called, `username_exists` was called to verify that the primary key is not already in use.

        Parameters
        ----------
        user : pantry_raid.models.user.User
            Flask-Login user object containing username, hashed password, and e-mail address

        Returns
        -------
        pymongo.results.InsertOneResult
            Result of inserting the document, including the `_id` of the inserted object, which should be the username since it is specified in the document to be inserted.
        """
        user_doc = {
            "_id": user.username,
            "password": user.password,
            "email": user.email,
            "bad_logins": 0,
            "last_bad_login": 0,
            "pantry": [],
            "favorites": [],
            "substitutions": DEFAULT_SUBSTITUTIONS
        }
        return self.collection.insert_one(user_doc)

    def update_user_field(self, uid, operation, field, value):
        """Updates a field inside of a user document.

        Parameters
        ----------
        uid : string
            Username (`_id`, primary key) corresponding to the document to update

        operation : string
            Mongo operation to perform. See https://docs.mongodb.com/manual/reference/operator/update/ for a full list of available operators. **Do not prefix with a `$`**, as that is done by this function.

        field : string
            The field to update

        value : string
            The operand used by the operation


        Returns
        -------
        pymongo.results.UpdateResult
            Results object containing information regarding the result of the operation
        """
        return self.collection.update_one(
            { "_id": uid },
            {
                f"${operation}": {
                    field: value
                }
            }
        )

    def increment_bad_logins(self, user, time):
        """On a failed login, increment the bad login counter and save the time of the last bad login ot prevent bruteforcing of accounts.

        Parameters
        ----------
        user : string
            Username (`_id`) of the account

        time : int
            Unix epoch timestamp of the UTC time of the login attempt
        """
        self.update_user_field(user, "inc", "bad_logins", 1)
        self.update_user_field(user, "set", "last_bad_login", time)

    def reset_bad_logins(self, user):
        """Resets the bad login data. Called after a successful login.

        Parameters
        ----------
        user : string
        """
        self.update_user_field(user, "set", "bad_logins", 0)
        self.update_user_field(user, "set", "last_bad_login", 0)

    def pantry_insert_ingredient(self, new_ingredient, uid):
        """Insert an ingredient into a specific user's pantry.

        Parameters
        ----------
        new_ingredient : string
            Ingredient to add. This has already been verified as a valid ingredient (exists in the ingredient database) that does not already exist in the user's pantry.

        uid : string
            Username whose pantry will be updated


        Returns
        -------
        pantry_raid.models.status.Status
            Status message for the result
        """
        try:
            self.update_user_field(uid, "push", "pantry", new_ingredient)
            return Status("success", f"Added {new_ingredient} to your pantry.")
        except Exception:  # pragma: no cover
            return Status("danger", f"The service encountered a problem when adding {new_ingredient} to your pantry. Please try again later.")

    def pantry_remove_ingredient(self, ingredient_to_remove, uid):
        """Removes an ingredient from a specific user's pantry.

        Parameters
        ----------
        new_ingredient : string
            Ingredient to add. This has already been verified as a valid ingredient (exists in the ingredient database) that does not already exist in the user's pantry.

        uid : string
            Username whose pantry will be updated


        Returns
        -------
        pantry_raid.models.status.Status
            Status message for the result
        """
        try:
            self.update_user_field(uid, "pull", "pantry", ingredient_to_remove)
            return Status("info", f"Removed {ingredient_to_remove} from your pantry.")
        except Exception:  # pragma: no cover
            return Status("danger", f"The service encountered a problem when removing {ingredient_to_remove} from your pantry. Please try again later.")

    def favorites_insert_recipe(self, recipe, uid):
        """Adds a favorite recipe to a specific user's account/

        Parameters
        ----------
        recipe : `fill this in`
            Recipe to add

        uid : string
            User account
        """

        try:
            self.update_user_field(uid, "push", "favorites", recipe)
            return Status("info", f"Added {recipe} to your favorites.")
        except Exception:  # pragma: no cover
            return Status("danger", f"The service encountered a problem when adding {recipe} to your favorites. Please try again later.")

    def favorites_remove_recipe(self, recipe, uid):
        """Adds a favorite recipe to a specific user's account/

        Parameters
        ----------
        recipe : `fill this in`
            Recipe to add

        uid : string
            User account
        """
        try:
            self.update_user_field(uid, "pull", "favorites", recipe)
            return Status("info", f"Removed {recipe} from your favorites.")
        except Exception:  # pragma: no cover
            return Status("danger", f"The service encountered a problem when removing {recipe} from your favorites. Please try again later.")

    def substitute_insert(self, substitution, uid):
        """Inserts a new substitution for the user.

        Parameters
        ----------
        uid : string

        substitution : dict


        Returns
        -------
        pantry_raid.models.status.Status
        """
        try:
            target = f"{substitution.get('quantity')} {substitution.get('name')}"
            self.update_user_field(uid, "push", "substitutes", substitution)
            return Status("success", f"Added substitution for {target} to your account.")
        except Exception:  # pragma: no cover
            return Status("danger", f"The service encountered a problem when adding this substitition to your account. Please try again later.")

    def substitute_remove(self, sub_index, uid):
        """Remove a substitute by array index. Warning: !!fun!! things can happen if the user is trying to do other things with substitutions at the same time, including displaying them.

        Parameters
        ----------
        uid : string

        sub_index : string
            Array index to remove


        Returns
        -------
        pantry_raid.models.status.Status
        """
        try:
            removal_value = { "to_be_removed": { "ingredient": None, "quantity": None } }
            self.update_user_field(uid, "set", f"substitutes.{sub_index}", removal_value)
            self.update_user_field(uid, "pull", "substitutes", removal_value)
            return Status("info", f"Removed substitution from your account.")
        except Exception:  # pragma: no cover
            return Status("danger", f"The service encountered a problem when removing this substitition to your account. Please try again later.")

    def get_pantry_with_substitutions(self, uid):
        """Gets a modified version of the pantry based on presence of substitutions and their ingredients. If all items for a substitution exist in the pantry, then that ingredient is added to the pantry list, so that recipes using it may turn up in results.

        Parameters
        ----------
        uid : string


        Returns
        -------
        list
            Modified pantry
        """
        try:
            user = self.find_by_username(uid)
            subs_dict = user.get('substitutes')
            pantry = user.get('pantry')
            pantry_set = set(pantry)
            for sub in subs_dict:
                sub_ingredients = set([ v
                    for ing in sub.get('items')
                    for k, v in ing.items()
                    if k == 'ingredient'
                ])

                # If all sub ingredients are in the pantry, then "add" the target ingredient to the pantry
                if sub_ingredients.issubset(pantry_set):
                    pantry.append(sub.get('name'))
            return pantry
        except Exception:  # pragma: no cover
            flash("danger", "The service encountered an error when trying to substitute ingredients. No substitutes have been used.")
            return []


# Some basic substitution to add to all users on account creation
DEFAULT_SUBSTITUTIONS = [
    {
        "name": "allspice",
        "quantity": "1 teaspoon",
        "items": [
            {
                "quantity": "1/2 teaspoon",
                "ingredient": "cinnamon"
            },
            {
                "quantity": "1/4 teaspoon",
                "ingredient": "ginger"
            },
            {
                "quantity": "1/4 teaspoon",
                "ingredient": "cloves"
            }
        ]
    },
    {
        "name": "baking powder",
        "quantity": "1 teaspoon",
        "items": [
            {
                "quantity": "1/4 teaspoon",
                "ingredient": "baking soda"
            },
            {
                "quantity": "1/2 teaspoon",
                "ingredient": "cream of tartar"
            }
        ]
    },
    {
        "name": "baking powder",
        "quantity": "1 teaspoon",
        "items": [
            {
                "quantity": "1/4 teaspoon",
                "ingredient": "baking soda"
            },
            {
                "quantity": "1/2 cup",
                "ingredient": "buttermilk"
            }
        ]
    },
    {
        "name": "beer",
        "quantity": "1 cup",
        "items": [
            {
                "quantity": "1 cup",
                "ingredient": "chicken broth"
            }
        ]
    },
    {
        "name": "butter",
        "quantity": "1 cup",
        "items": [
            {
                "quantity": "1 cup",
                "ingredient": "margarine"
            }
        ]
    },
    {
        "name": "butter",
        "quantity": "1 cup",
        "items": [
            {
                "quantity": "1 cup",
                "ingredient": "shortening"
            }
        ]
    },
    {
        "name": "butter",
        "quantity": "1 cup",
        "items": [
            {
                "quantity": "7/8 cup",
                "ingredient": "vegetable oil"
            }
        ]
    },
    {
        "name": "buttermilk",
        "quantity": "1 cup",
        "items": [
            {
                "quantity": "1 tablespoon",
                "ingredient": "lemon juice"
            },
            {
                "quantity": "15 tablespoon",
                "ingredient": "milk"
            }
        ]
    },
    {
        "name": "bittersweet chocolate",
        "quantity": "1 ounce",
        "items": [
            {
                "quantity": "3 tablespoons",
                "ingredient": "unsweetened cocoa powder"
            },
            {
                "quantity": "1 tablespoon",
                "ingredient": "shortening"
            }
        ]
    },
    {
        "name": "bittersweet chocolate",
        "quantity": "1 ounce",
        "items": [
            {
                "quantity": "3 tablespoons",
                "ingredient": "unsweetened cocoa powder"
            },
            {
                "quantity": "1 tablespoon",
                "ingredient": "vegetable oil"
            }
        ]
    },
    {
        "name": "light corn syrup",
        "quantity": "1 cup",
        "items": [
            {
                "quantity": "1 1/4 cup",
                "ingredient": "white sugar"
            },
            {
                "quantity": "1/3 cup",
                "ingredient": "water"
            }
        ]
    },
    {
        "name": "light corn syrup",
        "quantity": "1 cup",
        "items": [
            {
                "quantity": "1 cup",
                "ingredient": "honey"
            }
        ]
    },
    {
        "name": "heavy cream",
        "quantity": "1 cup",
        "items": [
            {
                "quantity": "1 cup",
                "ingredient": "evaporated milk"
            }
        ]
    },
    {
        "name": "heavy cream",
        "quantity": "1 cup",
        "items": [
            {
                "quantity": "3/4 cup",
                "ingredient": "milk"
            },
            {
                "quantity": "1/3 cup",
                "ingredient": "butter"
            }
        ]
    },
    {
        "name": "egg",
        "quantity": "1",
        "items": [
            {
                "quantity": "1/2 mashed",
                "ingredient": "banana"
            },
            {
                "quantity": "1/2 teaspoon",
                "ingredient": "baking powder"
            }
        ]
    },
    {
        "name": "ketchup",
        "quantity": "1 cup",
        "items": [
            {
                "quantity": "1 cup",
                "ingredient": "tomato sauce"
            },
            {
                "quantity": "1 teaspoon",
                "ingredient": "white vinegar"
                },
            {
                "quantity": "1 tablespoon",
                "ingredient": "white sugar"
            }
        ]
    },
    {
        "name": "saffron",
        "quantity": "1/4 teaspoon",
        "items": [
            {
                "quantity": "1/4 teaspoon",
                "ingredient": "turmeric"
            }
        ]
    },
    {
        "name": "soy sauce",
        "quantity": "1/2 cup",
        "items": [
            {
                "quantity": "1/4 cup",
                "ingredient": "Worcestershire sauce"
            },
            {
                "quantity": "1 tablespoon",
                "ingredient": "water"
            }
        ]
    }
]
