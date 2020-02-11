// Adds a simple autocompleted field to a form.
// -
// **Parameters**
// ----------
// `ing_list` : Array
//      Array of items used by the autocomplete function.
// `filter_name` : String
//      String used in the `id` and `name` attributes of the resulting input field. Must follow a certain syntax to permit Flask to easily find all values of similar fields. It should also be ID of the parent (container) element for all input fields.
// `counter` : String
//      The ID of a hidden HTML element used to count the number of filters so that IDs are unique.
function addFilter(ing_list, filter_name, counter) {
    // Handle updating the counter element.
    var counter_elem = document.getElementById(counter);
    var total_filters = parseInt(counter_elem.getAttribute('value'));
    total_filters++;
    counter_elem.setAttribute('value', total_filters);

    // Create the new input field and append it to the parent element.
    var parent = document.getElementById(filter_name);
    var new_filter_elem = document.createElement("div");
    new_filter_elem.innerHTML = "<input autocomplete=\"off\" type=\"text\" name=\"" + filter_name + "\" id=\"filter" + total_filters + "\"><br>";
    parent.appendChild(new_filter_elem);

    // Inject the autocompletion functionality.
    autocomplete(document.getElementById("filter" + total_filters), ing_list);
}