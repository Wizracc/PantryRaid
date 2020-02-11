// Toggles visibility of an element by its ID attribute.
// -
function toggleHide(element_id) {
  var x = document.getElementById(element_id);
  if (x.style.display === "block") {
    x.style.display = "none";
  } else {
    x.style.display = "block";
  }
}
