// ## CHANGESERVINGSIZE
// This function takes a recipe and changes it's values based off of a ratio
// provided by the servings of the recipe divided by the servings the 
// user wants. 
// > Greater than 1: change it to a decimal value
// > Less than 1: change it to a fraction to the 1/16th
function changeservingsize(recipe) {
    // Grab the value from the serving size button
    var newsize = parseFloat(document.getElementById("servingsize").value);
    // Grab the elements of the inlist which are the list of ingredients
    var ul = document.getElementById("inlist");
    // Create the new ratio based on the total number of servings/user selected servings
    var newRatio = newsize / recipe.servings;
    // Grab a reference to the ul which owns the list
    var newUnorderedList = document.createElement("ul");
    newUnorderedList.id = "inlist";

    var ing_dict = recipe.ing_dicts;
    var children = recipe.ingredients
    
    for (let i = 0; i < children.length; ++i) 
    {
        var newVal2 = ing_dict[i].outer_amount;
        var newVal = 0.0;
        // #### String only
        if (newVal2 == null)
        {
            // If the ingredient is just a string, return it
            var newListItem = document.createElement("li");
            newListItem.innerText = children[i];
        }
        // #### Number and a fraction
        else if (newVal2.toString().includes(" "))
        {
            // Grab the fraction and the number and store them
            var fract = newVal2.split(" ");
            var float1 = parseFloat(fract[0]);
            var float2 = parseFloat(fract[1]);
            float2 = eval(fract[1]);
            newVal = float1 + float2;
            var newListItem = document.createElement("li");
            var split = children[i].split(" ");
            // Multiply the new value by the ratio
            // to find the decimal value
            newVal = newVal * newRatio;
            // Round to two decimal places
            newVal = newVal.toFixed(2);
            // Take the new calculated value (decimal) and
            // convert it into a fraction
            var finalVal = toFract(newVal);
            split[0] = finalVal;
            split[1] = "";
            newListItem.innerText = split.join(' ');
        }
        // #### Just a number or a fraction
        else 
        {
            // Convert just a number or a fraction
            // into it's fraction counterpart
            // Or just into a decimal
            newVal = parseFloat(eval(newVal2));
            var newListItem = document.createElement("li");
            var split = children[i].split(" ");
            // Multiply the new value by the ratio
            // to find the decimal value
            newVal = newVal * newRatio;
            // Round to two decimal places
            newVal = newVal.toFixed(2);
            var finalVal = toFract(newVal);
            split[0] = finalVal;
            newListItem.innerText = split.join(' ');
        }
        // Add onto the list replacement
        newUnorderedList.appendChild(newListItem);
    }
    // Replace the old list wtih the new list
    ul.parentNode.replaceChild(newUnorderedList, ul)
}

 // ## TOFRACT
 // This function takes in a decimal and converts it to a fraction
 // to the 1/16th place. This function uses the fraction.min.js
 // library.
 function toFract(decimal) 
 {
    // Round to the nearest 1/16
    var rounded = (Math.round(decimal * 16) / 16);
    var f = new Fraction(rounded);
    var newVal = f.toFraction(true);
    return newVal;
}

// ##  PLUSONE
// This function takes the serving size element and adds one to it
// as to increase the amount of servings the user wants
function plusone()
{
    var nextValue = parseInt(document.getElementById("servingsize").value) + 1;
    document.getElementById("servingsize").value = nextValue;
    document.getElementById("servingsize").innerText = nextValue.toString();
}
// ##  MINUSONE
// This function takes a serving size element and subtracts one from it
// as to decrease the amount of servings the user wants
function minusone()
{
    var nextValue = parseInt(document.getElementById("servingsize").value) - 1;
    document.getElementById("servingsize").value = nextValue;
    document.getElementById("servingsize").innerText = nextValue.toString();
}
