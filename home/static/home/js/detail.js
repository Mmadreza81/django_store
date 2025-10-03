function toggleReplyForm(commentOrReplyid) {
        const form = document.getElementById('reply-form-' + commentOrReplyid);
        if (form.style.display === 'none' || form.style.display === ''){
            form.style.display = 'block';
        } else {
            form.style.display = 'none';
        }
    }

function toggleCommentForm() {
    const form = document.getElementById('comment-form');
    if (form.style.display === 'none' || form.style.display === ''){
            form.style.display = 'block';
    } else {
            form.style.display = 'none';
    }
}

document.addEventListener("DOMContentLoaded", function () {
    const stars = document.querySelectorAll("#rating-stars .star");
    const scoreInput = document.getElementById("rating-value"); // تغییر داده شد
    let currentRating = 0;

    // مقدار ذخیره‌شده قبلی (اگر وجود داشت)
    const userRating = parseInt(document.getElementById("rating-stars").dataset.userRating, 10) || 0;
    if (userRating > 0) {
        highlightStars(userRating);
        currentRating = userRating;
        scoreInput.value = userRating;
    }

    stars.forEach(star => {
        star.addEventListener("click", function () {
            currentRating = parseInt(this.dataset.value, 10);
            scoreInput.value = currentRating;
            highlightStars(currentRating);
        });
    });

    function highlightStars(rating) {
        stars.forEach((s, i) => {
            if (i < rating) {
                s.classList.remove("bi-star");
                s.classList.add("bi-star-fill", "selected");
            } else {
                s.classList.remove("bi-star-fill", "selected");
                s.classList.add("bi-star");
            }
        });
    }
});