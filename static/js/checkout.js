/*
 * checkout.js - 結帳頁面功能
 */

document.addEventListener('DOMContentLoaded', () => {
    // 初始化表單驗證
    initCheckoutForm();

    // 自動填充已登入用戶資訊
    autoFillUserInfo();
});

/**
 * 初始化結帳表單驗證
 */
function initCheckoutForm() {
    const form = document.querySelector('.form-large');

    if (!form) return;

    // 實時驗證
    const inputs = form.querySelectorAll('input, textarea');

    inputs.forEach(input => {
        input.addEventListener('blur', () => {
            validateField(input);
        });

        input.addEventListener('input', () => {
            if (input.classList.contains('is-invalid')) {
                validateField(input);
            }
        });
    });

    // 表單提交
    form.addEventListener('submit', (e) => {
        e.preventDefault();

        // 驗證所有欄位
        let isValid = true;
        inputs.forEach(input => {
            if (!validateField(input)) {
                isValid = false;
            }
        });

        if (isValid) {
            submitCheckoutForm(form);
        } else {
            App.utils.showNotification('⚠️ 請填寫所有必填欄位', 'warning');
        }
    });
}

/**
 * 驗證表單欄位
 */
function validateField(field) {
    const formGroup = field.closest('.form-group');
    let isValid = true;

    if (field.type === 'email') {
        isValid = App.utils.validateEmail(field.value);
    } else if (field.name === 'buyer_phone') {
        isValid = App.utils.validatePhone(field.value);
    } else if (field.required && !field.value.trim()) {
        isValid = false;
    }

    if (isValid) {
        formGroup.classList.remove('is-invalid');
        formGroup.classList.add('is-valid');
    } else {
        formGroup.classList.add('is-invalid');
        formGroup.classList.remove('is-valid');
    }

    return isValid;
}

/**
 * 自動填充已登入用戶資訊
 */
function autoFillUserInfo() {
    const userData = document.querySelector('script[type="application/json"][data-user]');

    if (userData) {
        try {
            const user = JSON.parse(userData.textContent);
            document.querySelector('#buyer_name').value = user.full_name || '';
            document.querySelector('#buyer_email').value = user.email || '';
            document.querySelector('#buyer_phone').value = user.phone || '';
            document.querySelector('#buyer_address').value = user.address || '';
        } catch (error) {
            console.error('解析用戶數據錯誤:', error);
        }
    }
}

/**
 * 提交結帳表單
 */
async function submitCheckoutForm(form) {
    try {
        const formData = new FormData(form);
        const data = Object.fromEntries(formData);

        const response = await fetch('/checkout', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });

        if (response.ok) {
            const result = await response.json();
            App.utils.showNotification('✅ 訂單已成功提交', 'success');
            window.location.href = `/order-success?order_id=${result.order_id}`;
        } else {
            const error = await response.json();
            App.utils.showNotification(`❌ ${error.detail || '提交失敗'}`, 'error');
        }
    } catch (error) {
        console.error('結帳錯誤:', error);
        App.utils.showNotification('❌ 發生錯誤，請稍後重試', 'error');
    }
}
