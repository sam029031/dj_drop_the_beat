/*
 * course.js - 課程相關功能
 */

document.addEventListener('DOMContentLoaded', () => {
    // 初始化課程報名表單
    initCourseRegistration();

    // 平滑滾動到報名表單
    initSmoothScroll();
});

/**
 * 初始化課程報名表單
 */
function initCourseRegistration() {
    const form = document.querySelector('.registration-form');

    if (!form) return;

    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        // 驗證必填欄位
        const requiredFields = form.querySelectorAll('input[required]');
        let isValid = true;

        requiredFields.forEach(field => {
            if (!field.value.trim()) {
                isValid = false;
                field.classList.add('is-invalid');
            } else {
                field.classList.remove('is-invalid');
            }
        });

        if (!isValid) {
            App.utils.showNotification('⚠️ 請填寫所有必填欄位', 'warning');
            return;
        }

        // 提交報名表單
        await submitCourseRegistration(form);
    });
}

/**
 * 提交課程報名
 */
async function submitCourseRegistration(form) {
    try {
        const formData = new FormData(form);
        const data = Object.fromEntries(formData);

        const response = await fetch('/course/register', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });

        if (response.ok) {
            const result = await response.json();
            App.utils.showNotification('✅ 報名成功！', 'success');

            // 顯示報名編號
            if (result.registration_number) {
                setTimeout(() => {
                    alert(`報名編號: ${result.registration_number}\n\n請妥善保管此編號以便後續查詢`);
                }, 500);
            }

            // 重置表單
            form.reset();

            // 重定向或刷新
            setTimeout(() => {
                window.location.reload();
            }, 2000);
        } else {
            const error = await response.json();
            if (response.status === 401) {
                App.utils.showNotification('⚠️ 請先登入', 'warning');
                window.location.href = '/auth/login?next=' + window.location.pathname;
            } else {
                App.utils.showNotification(`❌ ${error.detail || '報名失敗'}`, 'error');
            }
        }
    } catch (error) {
        console.error('報名錯誤:', error);
        App.utils.showNotification('❌ 發生錯誤，請稍後重試', 'error');
    }
}

/**
 * 初始化平滑滾動到表單
 */
function initSmoothScroll() {
    document.querySelectorAll('a[href*="#form"]').forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const formElement = document.querySelector('#form');
            if (formElement) {
                formElement.scrollIntoView({ behavior: 'smooth' });
                setTimeout(() => {
                    const firstInput = formElement.querySelector('input');
                    if (firstInput) firstInput.focus();
                }, 500);
            }
        });
    });
}
