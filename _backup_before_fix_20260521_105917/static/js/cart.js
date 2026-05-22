/*
 * cart.js - 購物車相關功能
 */

/**
 * 移除購物車項目
 */
function removeItem(cartItemId) {
    if (confirm('確定要移除此項目嗎？')) {
        // 這裡可以調用 API 移除項目
        // 目前使用頁面重載模擬
        alert('項目已移除');
        // location.reload();
    }
}

/**
 * 更新購物車數量
 */
function updateQuantity(cartItemId, newQuantity) {
    if (newQuantity < 1) {
        removeItem(cartItemId);
        return;
    }

    // 可以調用 API 更新數量
    console.log(`更新項目 ${cartItemId} 數量為 ${newQuantity}`);
}

/**
 * 加入購物車
 */
async function addToCart(setId, quantity = 1) {
    try {
        const response = await fetch('/cart/add', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                set_id: setId,
                quantity: quantity
            })
        });

        if (response.ok) {
            const data = await response.json();
            App.utils.showNotification('✅ 已加入購物車', 'success');
            // 更新購物車數量徽章
            updateCartBadge();
        } else {
            const error = await response.json();
            if (response.status === 401) {
                App.utils.showNotification('⚠️ 請先登入', 'warning');
                window.location.href = '/auth/login?next=/cart';
            } else {
                App.utils.showNotification(`❌ ${error.detail || '加入失敗'}`, 'error');
            }
        }
    } catch (error) {
        console.error('加入購物車錯誤:', error);
        App.utils.showNotification('❌ 發生錯誤', 'error');
    }
}

/**
 * 更新購物車數量徽章
 */
function updateCartBadge() {
    // 調用 API 獲取購物車項目數
    fetch('/api/cart/count')
        .then(response => response.json())
        .then(data => {
            const badge = document.querySelector('.cart-badge');
            if (badge) {
                badge.textContent = data.count;
            }
        })
        .catch(error => console.error('更新徽章錯誤:', error));
}

/**
 * 清空購物車
 */
function clearCart() {
    if (confirm('確定要清空購物車嗎？')) {
        // 調用 API 清空購物車
        fetch('/cart/clear', { method: 'POST' })
            .then(response => {
                if (response.ok) {
                    window.location.reload();
                }
            })
            .catch(error => console.error('清空購物車錯誤:', error));
    }
}

// 初始化購物車功能
document.addEventListener('DOMContentLoaded', () => {
    // 為所有"加入購物車"按鈕添加監聽器
    document.querySelectorAll('.add-to-cart-form').forEach(form => {
        form.addEventListener('submit', (e) => {
            e.preventDefault();
            const setId = form.querySelector('input[name="set_id"]').value;
            addToCart(parseInt(setId));
        });
    });

    // 數量輸入框變化監聽
    document.querySelectorAll('.qty-input').forEach(input => {
        input.addEventListener('change', (e) => {
            const newQuantity = parseInt(e.target.value);
            const cartItemId = e.target.dataset.itemId;
            if (cartItemId) {
                updateQuantity(cartItemId, newQuantity);
            }
        });
    });
});
