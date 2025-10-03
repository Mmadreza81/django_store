document.addEventListener("DOMContentLoaded", function() {
    const payBtn = document.querySelector("a.btn-success") || document.querySelector("button[disabled]");
    const radios = document.querySelectorAll("input[name='edit_id']");

    radios.forEach(radio => {
        radio.addEventListener("change", () => {
            if (payBtn.tagName === "BUTTON") {
                payBtn.removeAttribute("disabled");
                payBtn.textContent = "Pay";
            }
        });
    });
});