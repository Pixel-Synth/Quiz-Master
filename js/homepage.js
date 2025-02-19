let selectedCategory = "";
let subject = "";

document.addEventListener("DOMContentLoaded", function () {
    const header = document.querySelector("header");
    const title = document.querySelector("h1");
    const description = document.querySelector("p");
    const categoriesforcss = document.querySelectorAll(".category");
    const categories = document.querySelectorAll(".dropdown div");
    const startButton = document.getElementById("start-button");

    header.classList.add("hidden");
    title.classList.add("hidden");
    description.classList.add("hidden");
    categoriesforcss.forEach(category => category.classList.add("hidden"));
    startButton.classList.add("hidden");

    setTimeout(() => {
        header.classList.remove("hidden");
        header.classList.add("fade-drop-in");
        title.classList.remove("hidden");
        title.classList.add("fade-in");
    }, 500); 

    setTimeout(() => {
        description.classList.remove("hidden");
        description.classList.add("fade-in");
    }, 2000); 

    setTimeout(() => {
        categoriesforcss.forEach((category, index) => {
            setTimeout(() => {
                category.classList.remove("hidden");
                category.classList.add("drop-in"); 
            }, index * 300); 
        });

        setTimeout(() => {
            startButton.classList.remove("hidden");
            startButton.classList.add("drop-in");
        }, categoriesforcss.length * 300 + 500); 
    }, 3500); 

    categories.forEach(category => {
        category.addEventListener("click", function () {
            selectedCategory = this.innerText;
            //subject = this.parentElement.parentElement.innerHTML;
            subject = this.closest('.category').innerText.split('\n')[0];
            document.getElementById("fill").innerHTML = ("You selected: " + subject + " - " + selectedCategory);
        });
    });

    document.getElementById("start-button").addEventListener("click", function (event) {
        if (!selectedCategory) {
            event.preventDefault();
            document.getElementById("fill").innerHTML = ("Please select a topic before starting the quiz!");
        } /*else {
            alert("Starting quiz on: " + selectedCategory);
        }*/
        else {
            const url = `quiz.html?subject=${encodeURIComponent(subject)}&topic=${encodeURIComponent(selectedCategory)}`;
            window.location.href = url;
        }
    });
});


