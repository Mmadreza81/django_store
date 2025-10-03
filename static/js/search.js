document.addEventListener("DOMContentLoaded", function (){
    const searchForm = document.getElementById('search-form');
    if (!searchForm) return;

    const input = searchForm.querySelector('input[name="search"]');
    if (!input) return;

    // وقتی صفحه رفرش میشه و search توی URL هست → مقدار رو نمایش بده
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.has('search')) {
        input.value = urlParams.get('search');

        // بعد نیم ثانیه آدرس رو بدون search جایگزین کن
        setTimeout(() => {
            const cleanUrl = window.location.origin + window.location.pathname;
            window.history.replaceState({}, '', cleanUrl);
        }, 500);
    }

    // اگر سرچ خالی باشه → جلوگیری از ارسال فرم
    searchForm.addEventListener('submit', function (e){
        if (input.value.trim() === ''){
            e.preventDefault();
            window.location.href = searchForm.getAttribute('action') || window.location.pathname;
        }
    });
});