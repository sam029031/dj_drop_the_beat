function updateCartBadge() {
    fetch('/cart/count')
        .then(response => response.json())
        .then(data => {
            const badge = document.querySelector('.cart-badge');
            if (badge) badge.textContent = data.count;
        })
        .catch(() => {});
}

async function addToCart(setId, quantity = 1) {
    const response = await fetch('/cart/add', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({preorder_set_id: setId, quantity: quantity})
    });

    if (response.ok) {
        if (window.App && App.utils) App.utils.showNotification('✅ 已加入購物車', 'success');
        updateCartBadge();
    } else if (response.status === 401) {
        window.location.href = '/login?next=/cart';
    } else {
        const error = await response.json().catch(() => ({}));
        alert(error.detail || '加入購物車失敗');
    }
}

document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.add-to-cart-form').forEach(form => {
        form.addEventListener('submit', (e) => {
            e.preventDefault();
            const setId = form.querySelector('input[name="set_id"], input[name="preorder_set_id"]').value;
            const qtyInput = form.querySelector('input[name="quantity"]');
            addToCart(parseInt(setId), qtyInput ? parseInt(qtyInput.value || '1') : 1);
        });
    });
});
