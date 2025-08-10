// Function to validate forms
function validateForm(form) {
    let isValid = true;
    const inputs = form.querySelectorAll('input, textarea, select');

    inputs.forEach(input => {
        if (input.hasAttribute('required') && !input.value.trim()) {
            isValid = false;
            input.classList.add('is-invalid');
        } else {
            input.classList.remove('is-invalid');
        }
    });

    if (!isValid) {
        alert('Please fill out all required fields.');
    }

    return isValid;
}

// Add event listeners to forms for validation
document.addEventListener('DOMContentLoaded', function () {
    const forms = document.querySelectorAll('form');

    forms.forEach(form => {
        form.addEventListener('submit', function (event) {
            if (!validateForm(form)) {
                event.preventDefault(); // Prevent form submission if validation fails
            }
        });
    });
});

// Countdown Timer for Quizzes
function startTimer(duration, display) {
    let timer = duration, minutes, seconds;
    const interval = setInterval(function () {
        minutes = parseInt(timer / 60, 10);
        seconds = parseInt(timer % 60, 10);

        minutes = minutes < 10 ? "0" + minutes : minutes;
        seconds = seconds < 10 ? "0" + seconds : seconds;

        display.textContent = minutes + ":" + seconds;

        if (--timer < 0) {
            clearInterval(interval);
            alert('Time is up! Your quiz will be submitted automatically.');
            document.querySelector('form').submit(); // Automatically submit the quiz
        }
    }, 1000);
}

// Initialize the timer if the quiz page has a timer element
document.addEventListener('DOMContentLoaded', function () {
    const timerDisplay = document.getElementById('quiz-timer');

    if (timerDisplay) {
        const timeDuration = timerDisplay.getAttribute('data-duration'); // Get duration in seconds
        const durationInSeconds = parseInt(timeDuration.split(':')[0]) * 60 + parseInt(timeDuration.split(':')[1]);

        startTimer(durationInSeconds, timerDisplay);
    }
});

// Toggle visibility of additional options in quiz questions
document.addEventListener('DOMContentLoaded', function () {
    const toggleButtons = document.querySelectorAll('.toggle-options');

    toggleButtons.forEach(button => {
        button.addEventListener('click', function () {
            const options = this.nextElementSibling;
            options.style.display = options.style.display === 'none' ? 'block' : 'none';
        });
    });
});

// Display a confirmation dialog before deleting items
document.addEventListener('DOMContentLoaded', function () {
    const deleteButtons = document.querySelectorAll('.delete-btn');

    deleteButtons.forEach(button => {
        button.addEventListener('click', function (event) {
            if (!confirm('Are you sure you want to delete this item?')) {
                event.preventDefault(); // Cancel the action if the user clicks "Cancel"
            }
        });
    });
});