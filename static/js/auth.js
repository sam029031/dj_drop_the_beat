document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('input[type="password"]').forEach(input => {
        input.addEventListener('input', () => {
            if (input.value.length > 0 && input.value.length < 8) {
                input.setCustomValidity('密碼至少需要 8 個字元');
            } else {
                input.setCustomValidity('');
            }
        });
    });
});
