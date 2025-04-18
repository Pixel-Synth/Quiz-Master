document.addEventListener("DOMContentLoaded", function () {
    const params = new URLSearchParams(window.location.search);
    const subject = params.get("subject");
    const topic = params.get("topic");
    const quizTitle = document.getElementById("quiz-title");
    const questionContainer = document.getElementById("question-container");
    const nextButton = document.getElementById("next-button");
    let currentQuestionIndex = 0;
    let selectedQuestions = []; 
    let selectedAnswers = [];
    const savedQuestions = JSON.parse(localStorage.getItem("quizProgress")) || [];
    if (savedQuestions.topic == topic && savedQuestions.subject == subject) {
        currentQuestionIndex = savedQuestions.currentQuestionIndex || 0;
        selectedAnswers = savedQuestions.selectedAnswers || [];
    }
    else{
        localStorage.removeItem("quizProgress");
    }
    console.log(savedQuestions);    
    fetch(`/get_questions?subject=${subject}&topic=${topic}`)
    .then(res => res.json())
    .then(data => {
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
        localStorage.setItem("quizProgress", JSON.stringify({
            subject,
            topic,
            currentQuestionIndex,
            selectedAnswers
        }));    
        if (currentQuestionIndex < selectedQuestions.length) {
            displayQuestion();
        } else {
            questionContainer.innerHTML = `<p style="color: white;">Quiz Completed! 🎉</p>`;
            nextButton.style.display = "none";
            localStorage.removeItem("quizProgress");
        }
    });


    function displayQuestion() {
        const q = selectedQuestions[currentQuestionIndex];
        questionContainer.innerHTML = `
            <p>${q.question}</p>
            <button class="option" id="option1">${q.option1}</button>
            <button class="option" id="option2">${q.option2}</button>
            <button class="option" id="option3">${q.option3}</button>
            <button class="option" id="option4">${q.option4}</button>
        `;
        document.querySelectorAll(".option").forEach(button => {
            button.addEventListener("click", function () {
                const selectedId = selectedAnswers[currentQuestionIndex];
                if (selectedId) {
                    const selectedBtn = document.getElementById(selectedId);
                    if (selectedId === "option" + q.correct) {
                        selectedBtn.style.backgroundColor = "green";
                    } else {
                        selectedBtn.style.backgroundColor = "red";
                        document.getElementById("option" + q.correct).style.backgroundColor = "green";
                    }

                    document.querySelectorAll(".option").forEach(button => {
                        if (button.id !== selectedId) {
                            button.disabled = true;
                        }
                    });
                }
                else{
                    selectedAnswers[currentQuestionIndex] = this.id;
                    localStorage.setItem("quizProgress", JSON.stringify({
                        subject,
                        topic,
                        currentQuestionIndex,
                        selectedAnswers
                    }));
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
                }
            });
        });
    }
});
