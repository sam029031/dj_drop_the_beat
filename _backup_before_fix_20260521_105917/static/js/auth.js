/*
 * auth.js - 登入/註冊頁面功能
 */

document.addEventListener('DOMContentLoaded', () => {
    // 初始化密碼強度檢查
    initPasswordStrength();

    // 初始化表單驗證
    initAuthForm();
});

/**
 * 初始化密碼強度檢查
 */
function initPasswordStrength() {
    const passwordInputs = document.querySelectorAll('input[type="password"]');

    passwordInputs.forEach(input => {
        if (input.name === 'password') {
            input.addEventListener('input', () => {
                checkPasswordStrength(input);
            });
        }
    });
}

/**
 * 檢查密碼強度
 */
function checkPasswordStrength(input) {
    const password = input.value;
    let strength = 0;
    let feedback = [];

    // 長度檢查
    if (password.length >= 8) strength += 1;
    else feedback.push('至少 8 個字符');

    // 大寫字母檢查
    if (/[A-Z]/.test(password)) strength += 1;
    else feedback.push('包含大寫字母');

    // 小寫字母檢查
    if (/[a-z]/.test(password)) strength += 1;
    else feedback.push('包含小寫字母');

    // 數字檢查
    if (/\d/.test(password)) strength += 1;
    else feedback.push('包含數字');

    // 特殊字符檢查
    if (/[!@#$%^&*]/.test(password)) strength += 1;
    else feedback.push('包含特殊字符');

    // 顯示強度指示器
    let strengthLabel = '';
    let strengthClass = '';

    if (strength <= 1) {
        strengthLabel = '弱';
        strengthClass = 'weak';
    } else if (strength <= 2) {
        strengthLabel = '中';
        strengthClass = 'medium';
    } else if (strength <= 3) {
        strengthLabel = '良好';
        strengthClass = 'good';
    } else {
        strengthLabel = '強';
        strengthClass = 'strong';
    }

    // 更新或創建強度指示器
    let indicator = input.nextElementSibling;
    if (!indicator || !indicator.classList.contains('password-strength')) {
        indicator = document.createElement('div');
        indicator.className = 'password-strength';
        input.parentNode.insertBefore(indicator, input.nextElementSibling);
    }

    indicator.className = `password-strength strength-${strengthClass}`;
    indicator.innerHTML = `
        <div class="strength-label">密碼強度: ${strengthLabel}</div>
        <div class="strength-bar"><div class="strength-fill" style="width: ${(strength / 5) * 100}%"></div></div>
    `;

    if (feedback.length > 0) {
        const feedback_elem = indicator.nextElementSibling;
        if (!feedback_elem || !feedback_elem.classList.contains('password-feedback')) {
            const feedbackDiv = document.createElement('div');
            feedbackDiv.className = 'password-feedback';
            indicator.parentNode.insertBefore(feedbackDiv, indicator.nextElementSibling);
        }
    }
}

/**
 * 初始化表單驗證
 */
function initAuthForm() {
    const forms = document.querySelectorAll('.auth-form');

    forms.forEach(form => {
        form.addEventListener('submit', (e) => {
            e.preventDefault();

            // 基本驗證
            const inputs = form.querySelectorAll('input');
            let isValid = true;

            inputs.forEach(input => {
                if (input.type === 'email') {
                    if (!App.utils.validateEmail(input.value)) {
                        isValid = false;
                        highlightError(input);
                    }
                } else if (input.required && !input.value.trim()) {
                    isValid = false;
                    highlightError(input);
                }

                // 密碼確認檢查
                if (input.name === 'password_confirm') {
                    const passwordInput = form.querySelector('input[name="password"]');
                    if (passwordInput && passwordInput.value !== input.value) {
                        isValid = false;
                        highlightError(input, '密碼不相符');
                    }
                }
            });

            if (isValid) {
                form.submit();
            } else {
                App.utils.showNotification('⚠️ 請檢查表單資訊', 'warning');
            }
        });
    });
}

/**
 * 突出顯示錯誤欄位
 */
function highlightError(input, message = null) {
    input.classList.add('is-invalid');

    input.addEventListener('focus', () => {
        input.classList.remove('is-invalid');
    });

    if (message) {
        const error = document.createElement('div');
        error.className = 'form-error';
        error.textContent = message;
        input.parentNode.insertBefore(error, input.nextElementSibling);
    }
}

/**
 * 切換密碼顯示/隱藏
 */
function togglePasswordVisibility(inputId) {
    const input = document.getElementById(inputId);
    if (input) {
        input.type = input.type === 'password' ? 'text' : 'password';
    }
}
