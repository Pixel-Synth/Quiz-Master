document.addEventListener("DOMContentLoaded", function () {
    const params = new URLSearchParams(window.location.search);
    const subject = params.get("subject");
    const topic = params.get("topic");

    const quizTitle = document.getElementById("quiz-title");
    const questionContainer = document.getElementById("question-container");
    const nextButton = document.getElementById("next-button");
    const prevButton = document.getElementById("prev-button");
    const finishButton = document.getElementById("finish-button");
    const timer = document.getElementById("timer");
    let marks = 0;
    let currentQuestionIndex = 0;
    let selectedQuestions = [];
    let selectedAnswers = [];
    let time = 0; 
    let timerInterval = null;
    const saved = JSON.parse(localStorage.getItem("quizProgress")) || {};
    if (saved.subject === subject && saved.topic === topic) {
        currentQuestionIndex = saved.currentQuestionIndex || 0;
        selectedAnswers = saved.selectedAnswers || [];
        time = saved.time || 0;
    } else {
        localStorage.removeItem("quizProgress");
    }
    startTimer();

    function startTimer() {
        timerInterval = setInterval(() => {
            time++;
            const minutes = Math.floor(time / 60);
            const seconds = time % 60;
            timer.innerText = `Time: ${minutes}:${seconds < 10 ? "0" : ""}${seconds}`;
        }, 1000);
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
                timer.innerHTML = "";
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
        questionContainer.innerHTML = `<p style="color: white;">Quiz Completed! 🎉</p><p>Your score: ${marks}/${selectedQuestions.length}</p>`;
        nextButton.style.display = "none";
        prevButton.style.display = "none";
        finishButton.style.display = "none";
        timer.innerHTML = "";
        clearInterval(timerInterval);
        
        percentage = (marks / selectedQuestions.length) * 100;
        const url = `/update_score?subject=${subject}&topic=${topic}&score=${percentage}&time=${time}`;
        fetch(url, { method: "POST" });
        localStorage.removeItem("quizProgress");

        const homeUrl = document.querySelector(".container").dataset.homeUrl;
        const exitButton = document.createElement("button");
        exitButton.textContent = "Exit to Homepage";
        exitButton.className = "exit-button"; 
        exitButton.style.marginTop = "20px";
        exitButton.onclick = function () {
            window.location.href = homeUrl;
        };
        document.querySelector(".container").appendChild(exitButton);
    });
    
    function saveProgress() {
        localStorage.setItem("quizProgress", JSON.stringify({
            subject,
            topic,
            currentQuestionIndex,
            selectedAnswers,
            time
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
                    marks++;
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
