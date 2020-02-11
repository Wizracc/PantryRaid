// ## STRIKE
// This function is used to strike through text
// by changing the id to strike or no strike 
// depending on its current state.
function strike(ele)
{
    if (ele.id == "strike")
    {
        ele.id = "nostrike"
    }
    else
    {
        ele.id = "strike";
    }
}