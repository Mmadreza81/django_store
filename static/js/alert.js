document.addEventListener("DOMContentLoaded", function () {
    const alerts = document.querySelectorAll("#django-messages .alert");

    alerts.forEach((alert) => {
        // انتخاب آیکون مناسب بر اساس کلاس alert-*
        const icon = alert.querySelector(".bi");
        if (icon) {
            if (alert.classList.contains("alert-success")) {
                icon.className = "bi bi-check-circle-fill me-2 text-success";
            } else if (alert.classList.contains("alert-danger")) {
                icon.className = "bi bi-x-circle-fill me-2 text-danger";
            } else if (alert.classList.contains("alert-warning")) {
                icon.className = "bi bi-exclamation-triangle-fill me-2 text-warning";
            } else if (alert.classList.contains("alert-info")) {
                icon.className = "bi bi-info-circle-fill me-2 text-info";
            } else {
                icon.className = "bi bi-bell-fill me-2";
            }
        }

        // زمان محو شدن (میلی‌ثانیه)
        const delay = parseInt(alert.dataset.dismissDelay || "4000", 10);

        // شروع تایمر حذف
        setTimeout(() => {
            alert.classList.add("alert--fadeout");

            // وقتی انیمیشن تمام شد، عنصر رو حذف کن
            alert.addEventListener("animationend", () => {
                if (alert && alert.parentNode) {
                    alert.parentNode.removeChild(alert);
                }
            }, { once: true });
        }, delay);

        // اگر کاربر دکمه بستن رو بزنه → انیمیشن اجرا بشه
        const closeBtn = alert.querySelector(".btn-close");
        if (closeBtn) {
            closeBtn.addEventListener("click", (e) => {
                e.preventDefault();
                alert.classList.add("alert--fadeout");
                alert.addEventListener("animationend", () => {
                    if (alert && alert.parentNode) {
                        alert.parentNode.removeChild(alert);
                    }
                }, { once: true });
            });
        }
    });
});