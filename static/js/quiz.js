document.addEventListener("DOMContentLoaded", function () {
    const params = new URLSearchParams(window.location.search);
    const subject = params.get("subject");
    const topic = params.get("topic");

    const quizTitle = document.getElementById("quiz-title");
    const questionContainer = document.getElementById("question-container");
    const nextButton = document.getElementById("next-button");
    const prevButton = document.getElementById("prev-button");
    const finishButton = document.getElementById("finish-button");

    let currentQuestionIndex = 0;
    let selectedQuestions = [];
    let selectedAnswers = [];

    const saved = JSON.parse(localStorage.getItem("quizProgress")) || {};
    if (saved.subject === subject && saved.topic === topic) {
        currentQuestionIndex = saved.currentQuestionIndex || 0;
        selectedAnswers = saved.selectedAnswers || [];
    } else {
        localStorage.removeItem("quizProgress");
    }

    fetch(`/get_questions?subject=${subject}&topic=${topic}`)
        .then(res => res.json())
        .then(data => {
            selectedQuestions = data;
            if (!selectedQuestions.length) {
                questionContainer.innerHTML = `<p style="color: black;">No questions available for ${subject} - ${topic}.</p>`;
                nextButton.style.display = "none";
                prevButton.style.display = "none";
                finishButton.style.display = "none";
                return;
            }

            quizTitle.textContent = `${subject} - ${topic} Quiz`;
            displayQuestion();
        });

    nextButton.addEventListener("click", () => {
        if (currentQuestionIndex < selectedQuestions.length - 1) {
            currentQuestionIndex++;
            saveProgress();
            displayQuestion();
        }
    });

    prevButton.addEventListener("click", () => {
        if (currentQuestionIndex > 0) {
            currentQuestionIndex--;
            saveProgress();
            displayQuestion();
        }
    });

    finishButton.addEventListener("click", () => {
        questionContainer.innerHTML = `<p style="color: white;">Quiz Completed! 🎉</p>`;
        nextButton.style.display = "none";
        prevButton.style.display = "none";
        finishButton.style.display = "none";
        localStorage.removeItem("quizProgress");
    });

    function saveProgress() {
        localStorage.setItem("quizProgress", JSON.stringify({
            subject,
            topic,
            currentQuestionIndex,
            selectedAnswers
        }));
    }

    function displayQuestion() {
        const q = selectedQuestions[currentQuestionIndex];
        const savedAnswer = selectedAnswers[currentQuestionIndex];

        questionContainer.innerHTML = `
            <p>${q.question}</p>
            <button class="option" id="option1">${q.option1}</button>
            <button class="option" id="option2">${q.option2}</button>
            <button class="option" id="option3">${q.option3}</button>
            <button class="option" id="option4">${q.option4}</button>
        `;

        const optionButtons = document.querySelectorAll(".option");

        optionButtons.forEach(button => {
            button.addEventListener("click", function () {
                if (selectedAnswers[currentQuestionIndex]) return;

                selectedAnswers[currentQuestionIndex] = this.id;
                saveProgress();

                if (this.id === "option" + q.correct) {
                    this.style.backgroundColor = "green";
                } else {
                    this.style.backgroundColor = "red";
                    document.getElementById("option" + q.correct).style.backgroundColor = "green";
                }

                optionButtons.forEach(btn => btn.disabled = true);
            });
        });

        if (savedAnswer) {
            const selectedBtn = document.getElementById(savedAnswer);
            if (savedAnswer === "option" + q.correct) {
                selectedBtn.style.backgroundColor = "green";
            } else {
                selectedBtn.style.backgroundColor = "red";
                document.getElementById("option" + q.correct).style.backgroundColor = "green";
            }
            optionButtons.forEach(btn => btn.disabled = true);
        }

        prevButton.style.display = currentQuestionIndex > 0 ? "inline-block" : "none";
        nextButton.style.display = currentQuestionIndex < selectedQuestions.length - 1 ? "inline-block" : "none";
        finishButton.style.display = "inline-block";
    }
});
