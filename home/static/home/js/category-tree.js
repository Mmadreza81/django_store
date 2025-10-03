document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll(".category-header").forEach(function (header) {
        header.addEventListener("click", function () {
            let parent = header.parentElement;
            let children = parent.querySelector(".category-children");

            if (children) {
                parent.classList.toggle("open");
                children.style.display = parent.classList.contains("open") ? "block" : "none";
            }
        });
    });
});