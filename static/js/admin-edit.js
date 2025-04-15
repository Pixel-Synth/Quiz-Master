function modifyQuestion(id, index) {
    const data = {
        id: id,
        option_a: document.getElementById(`opt-a-${index}`).value,
        option_b: document.getElementById(`opt-b-${index}`).value,
        option_c: document.getElementById(`opt-c-${index}`).value,
        option_d: document.getElementById(`opt-d-${index}`).value,
        correct: document.getElementById(`correct-${index}`).value
    };

    fetch('/update_question', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    }).then(res => {
        if (res.ok) alert("Updated!");
        else alert("Update failed.");
    });
}

function deleteQuestion(id) {
    if (!confirm("Are you sure you want to delete this question?")) return;

    fetch('/delete_question', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ id })
    }).then(res => {
        if (res.ok) {
            alert("Deleted!");
            location.reload();
        } else {
            alert("Deletion failed.");
        }
    });
}