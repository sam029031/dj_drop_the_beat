/*
 * contact.js - 聯絡頁面功能
 */

document.addEventListener('DOMContentLoaded', () => {
    // 初始化聯絡表單
    initContactForm();

    // 初始化聯絡類型變化
    initMessageTypeChange();
});

/**
 * 初始化聯絡表單
 */
function initContactForm() {
    const form = document.querySelector('.contact-form');

    if (!form) return;

    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        // 驗證必填欄位
        const requiredFields = form.querySelectorAll('[required]');
        let isValid = true;

        requiredFields.forEach(field => {
            if (field.type === 'email') {
                if (!App.utils.validateEmail(field.value)) {
                    isValid = false;
                    field.classList.add('is-invalid');
                } else {
                    field.classList.remove('is-invalid');
                }
            } else if (field.name === 'phone') {
                if (!App.utils.validatePhone(field.value) && field.value.trim()) {
                    isValid = false;
                    field.classList.add('is-invalid');
                } else {
                    field.classList.remove('is-invalid');
                }
            } else if (!field.value.trim()) {
                isValid = false;
                field.classList.add('is-invalid');
            } else {
                field.classList.remove('is-invalid');
            }
        });

        if (!isValid) {
            App.utils.showNotification('⚠️ 請填寫有效的資訊', 'warning');
            return;
        }

        // 提交聯絡表單
        await submitContactForm(form);
    });
}

/**
 * 提交聯絡表單
 */
async function submitContactForm(form) {
    try {
        const formData = new FormData(form);
        const data = Object.fromEntries(formData);

        const response = await fetch('/contact/submit', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });

        if (response.ok) {
            App.utils.showNotification('✅ 訊息已成功送出！我們將盡快回覆', 'success');

            // 重置表單
            form.reset();

            // 清除驗證狀態
            form.querySelectorAll('.form-group').forEach(group => {
                group.classList.remove('is-valid', 'is-invalid');
            });
        } else {
            const error = await response.json();
            App.utils.showNotification(`❌ ${error.detail || '送出失敗'}`, 'error');
        }
    } catch (error) {
        console.error('送出聯絡表單錯誤:', error);
        App.utils.showNotification('❌ 發生錯誤，請稍後重試', 'error');
    }
}

/**
 * 初始化聯絡類型變化
 */
function initMessageTypeChange() {
    const typeRadios = document.querySelectorAll('input[name="message_type"]');

    typeRadios.forEach(radio => {
        radio.addEventListener('change', (e) => {
            const type = e.target.value;

            // 可以根據類型隱藏/顯示某些欄位
            console.log(`聯絡類型已變更為: ${type}`);

            if (type === 'sponsor_inquiry') {
                // 贊助查詢
                console.log('顯示贊助相關資訊');
            } else {
                // 個人意見回饋
                console.log('顯示一般意見回饋');
            }
        });
    });
}
