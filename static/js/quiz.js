document.addEventListener("DOMContentLoaded", function () {
    const params = new URLSearchParams(window.location.search);
    const subject = params.get("subject");
    const topic = params.get("topic");
    const quizTitle = document.getElementById("quiz-title");
    const questionContainer = document.getElementById("question-container");
    const nextButton = document.getElementById("next-button");
    let currentQuestionIndex = 0;
    let selectedQuestions = []; 

    fetch(`/get_questions?subject=${subject}&topic=${topic}`)
    .then(res => res.json())
    .then(data => {
        console.log(data);
        selectedQuestions = data;
        if (!selectedQuestions.length) {
            questionContainer.innerHTML = `<p style="color: black;">No questions available for ${subject} - ${topic}.</p>`;
            nextButton.style.display = "none";
            return;
        }
        quizTitle.textContent = `${subject} - ${topic} Quiz`;
        displayQuestion();
    });

    nextButton.addEventListener("click", () => {
        currentQuestionIndex++;
        if (currentQuestionIndex < selectedQuestions.length) {
            displayQuestion();
        } else {
            questionContainer.innerHTML = `<p style="color: white;">Quiz Completed! 🎉</p>`;
            nextButton.style.display = "none";
        }
    });

    function displayQuestion() {
        const q = selectedQuestions[currentQuestionIndex];
        console.log(q);
        questionContainer.innerHTML = `
            <p>${q.question}</p>
            <button class="option" id="option1">${q.option1}</button>
            <button class="option" id="option2">${q.option2}</button>
            <button class="option" id="option3">${q.option3}</button>
            <button class="option" id="option4">${q.option4}</button>
        `;

        document.querySelectorAll(".option").forEach(button => {
            button.addEventListener("click", function () {
                if (this.id == ("option"+q.correct)) {
                    this.style.backgroundColor = "green";
                    buttons = document.querySelectorAll(".option");
                    buttons.forEach(button => {
                        if (button.id !== "option"+q.correct) {
                            button.disabled = true;
                        }
                    });
                } else {
                    this.style.backgroundColor = "red";
                    buttons = document.querySelectorAll(".option");
                    buttons.forEach(button => {
                        if (button != this) {
                            button.disabled = true;
                        }
                        if (button.id === "option"+q.correct) {
                            button.style.backgroundColor = "green";
                        }
                    });
                }
            });
        });
    }
});
