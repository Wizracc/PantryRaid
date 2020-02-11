// Adds fields for an additional substitute ingredient to the form.
// -
// **Parameters**
// ----------
// `autocomplete_list` : Array
//      Array of elements used by the autocompletion function.
function addSubstitute(autocomplete_list) {
    // The "target" element contains a custom attribute, `numIngredients`, used to track how many ingredients are in the substitution.
    var target_element = document.getElementById("target");
    var total_ingredients = parseInt(target_element.getAttribute("numIngredients"))
    total_ingredients++;

    // The IDs for the new elements must follow a specific pattern for Flask and WTForms to recognize them as part of a form.
    var new_ing_id = "substitute-" + total_ingredients +"-ingredient";
    var new_qty_id = "substitute-" + total_ingredients +"-quantity";

    // Set up the new elements here.
    var ing_container = document.createElement("div");
    ing_container.class = "search-grid-item";
    ing_container.innerHTML = (total_ingredients + 1).toString() + ". <input type=\"text\" name=\"" + new_qty_id + "\" style=\"width: 100%; max-width: 40%;\" placeholder=\"Quantity\" \> <input type=\"text\" id=\"" + new_ing_id + "\" name=\"" + new_ing_id + "\" style=\"width: 100%; max-width: 40%;\" placeholder=\"Ingredient\" \>";

    // Add the elements to the parent (container).
    var parent = document.getElementById("subs_container")
    parent.appendChild(ing_container);
    target_element.setAttribute("numIngredients", total_ingredients);

    // Enable autocompletion of the ingredient field only.
    autocomplete(document.getElementById(new_ing_id), autocomplete_list);
}