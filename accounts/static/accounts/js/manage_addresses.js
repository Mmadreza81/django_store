document.addEventListener('DOMContentLoaded', () => {
    const editButtons = document.querySelectorAll('.edit-btn');
    const formTitle = document.getElementById('form-title');
    const submitBtn = document.getElementById('submit-btn');
    const cancelBtn = document.getElementById('cancel-btn');
    const editIdInput = document.getElementById('edit_id');
    const addressInput = document.getElementById('address');
    const postalInput = document.getElementById('postal_code');

    editButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            const id = btn.dataset.id;
            const address = btn.dataset.address;
            const postal = btn.dataset.postal;

            editIdInput.value = id;
            addressInput.value = address;
            postalInput.value = postal;

            formTitle.textContent = "ویرایش آدرس";
            submitBtn.textContent = "به‌روزرسانی";
            cancelBtn.style.display = "inline-block";
        });
    });

    cancelBtn.addEventListener('click', () => {
        editIdInput.value = "";
        addressInput.value = "";
        postalInput.value = "";
        formTitle.textContent = "اضافه کردن آدرس جدید";
        submitBtn.textContent = "ذخیره";
        cancelBtn.style.display = "none";
    });
});