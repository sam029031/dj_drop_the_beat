/*
 * app.js - 全局 JavaScript 初始化和工具函數
 */

// 應用全局狀態
const App = {
    // 工具函數
    utils: {
        /**
         * 格式化貨幣
         */
        formatCurrency: (amount) => {
            return new Intl.NumberFormat('zh-TW', {
                style: 'currency',
                currency: 'TWD',
                minimumFractionDigits: 0
            }).format(amount);
        },

        /**
         * 日期格式化
         */
        formatDate: (dateString) => {
            const date = new Date(dateString);
            return date.toLocaleDateString('zh-TW');
        },

        /**
         * 驗證電子郵件
         */
        validateEmail: (email) => {
            const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            return regex.test(email);
        },

        /**
         * 驗證電話號碼
         */
        validatePhone: (phone) => {
            const regex = /^09\d{8}$/;
            return regex.test(phone);
        },

        /**
         * 複製文字到剪貼簿
         */
        copyToClipboard: (text) => {
            navigator.clipboard.writeText(text).then(() => {
                console.log('已複製到剪貼簿');
            }).catch(err => {
                console.error('複製失敗:', err);
            });
        },

        /**
         * 顯示通知
         */
        showNotification: (message, type = 'info', duration = 3000) => {
            const notification = document.createElement('div');
            notification.className = `notification notification-${type}`;
            notification.textContent = message;
            document.body.appendChild(notification);

            setTimeout(() => {
                notification.classList.add('show');
            }, 10);

            setTimeout(() => {
                notification.classList.remove('show');
                setTimeout(() => {
                    document.body.removeChild(notification);
                }, 300);
            }, duration);
        }
    }
};

// 初始化
document.addEventListener('DOMContentLoaded', () => {
    // 導航欄漢堡菜單
    initNavbarToggle();

    // 初始化表單驗證
    initFormValidation();

    // 初始化工具提示
    initTooltips();
});

/**
 * 初始化導航欄漢堡菜單
 */
function initNavbarToggle() {
    const toggle = document.querySelector('.navbar-toggle');
    const menu = document.querySelector('.navbar-menu');

    if (!toggle || !menu) return;

    const close = () => {
        menu.classList.remove('active');
        toggle.classList.remove('active');
    };

    toggle.addEventListener('click', (e) => {
        e.stopPropagation();
        const opening = menu.classList.toggle('active');
        toggle.classList.toggle('active', opening);
    });

    // 點擊菜單連結後關閉菜單
    menu.querySelectorAll('a').forEach(link => {
        link.addEventListener('click', close);
    });

    // 點擊外部關閉菜單
    document.addEventListener('click', (e) => {
        if (!menu.contains(e.target)) close();
    });
}

/**
 * 初始化表單驗證
 */
function initFormValidation() {
    const forms = document.querySelectorAll('form');

    forms.forEach(form => {
        form.addEventListener('submit', (e) => {
            if (!form.checkValidity()) {
                e.preventDefault();
                e.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });
}

/**
 * 初始化工具提示
 */
function initTooltips() {
    const tooltips = document.querySelectorAll('[data-tooltip]');

    tooltips.forEach(element => {
        const tooltipText = element.getAttribute('data-tooltip');
        const tooltip = document.createElement('div');
        tooltip.className = 'tooltip';
        tooltip.textContent = tooltipText;

        element.addEventListener('mouseenter', () => {
            document.body.appendChild(tooltip);
            const rect = element.getBoundingClientRect();
            tooltip.style.position = 'absolute';
            tooltip.style.top = (rect.top - tooltip.offsetHeight - 10) + 'px';
            tooltip.style.left = rect.left + 'px';
            tooltip.classList.add('show');
        });

        element.addEventListener('mouseleave', () => {
            tooltip.classList.remove('show');
            if (tooltip.parentNode) {
                tooltip.parentNode.removeChild(tooltip);
            }
        });
    });
}

/**
 * 進行 API 請求
 */
async function apiRequest(url, options = {}) {
    const defaultOptions = {
        headers: {
            'Content-Type': 'application/json'
        }
    };

    const finalOptions = { ...defaultOptions, ...options };

    try {
        const response = await fetch(url, finalOptions);

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        return await response.json();
    } catch (error) {
        console.error('API 請求錯誤:', error);
        App.utils.showNotification('發生錯誤，請稍後重試', 'error');
        throw error;
    }
}

// 導出全局函數
window.App = App;
window.apiRequest = apiRequest;
