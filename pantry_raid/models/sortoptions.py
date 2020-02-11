class SortOptions(object):
    """Represents a sort option in the form of a query document.
    """

    def __init__(self, sort_options):
        self.doc = { }

        if sort_options == "cal+":
            self.doc = {"nutritional info.calories": 1}
        elif sort_options == "cal-":
            self.doc = {"nutritional info.calories": -1}
        elif sort_options == "fat+":
            self.doc = {"nutritional info.grams fat": 1}
        elif sort_options == "fat-":
            self.doc = {"nutritional info.grams fat": -1}
        elif sort_options == "carb+":
            self.doc = {"nutritional info.grams carbohydrates": 1}
        elif sort_options == "carb-":
            self.doc = {"nutritional info.grams carbohydrates": -1}
        elif sort_options == "prot+":
            self.doc = {"nutritional info.grams protein": 1}
        elif sort_options == "prot-":
            self.doc = {"nutritional info.grams protein": -1}
        elif sort_options == "chol+":
            self.doc = {"nutritional info.milligrams cholesterol": 1}
        elif sort_options == "chol-":
            self.doc = {"nutritional info.milligrams cholesterol": -1}
        elif sort_options == "na+":
            self.doc = {"nutritional info.milligrams sodium": 1}
        elif sort_options == "na-":
            self.doc = {"nutritional info.milligrams sodium": -1}
        elif sort_options == "abc+":
            self.doc = {"name": 1}
        elif sort_options == "abc-":
            self.doc = {"name": -1}
        else:
            self.doc = {"name": 1}
