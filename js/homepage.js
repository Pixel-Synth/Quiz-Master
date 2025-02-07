document.addEventListener("DOMContentLoaded", function () {
    const categories = document.querySelectorAll(".dropdown div");
    let selectedCategory = "";

    categories.forEach(category => {
        category.addEventListener("click", function () {
            selectedCategory = this.innerText;
            document.getElementById("fill").innerHTML = ("You selected: " + selectedCategory);
        });
    });

    document.getElementById("start-button").addEventListener("click", function (event) {
        if (selectedCategory === "") {
            event.preventDefault();
            document.getElementById("fill").innerHTML = ("Please select a topic before starting the quiz!");
        } else {
            alert("Starting quiz on: " + selectedCategory);
        }
    });
});