/*
 * detail.js - 商品詳情頁面功能
 */

document.addEventListener('DOMContentLoaded', () => {
    // 初始化商品詳情頁面
    initProductDetail();

    // 初始化"加入購物車"按鈕
    initAddToCartButtons();

    // 初始化圖片相冊
    initImageGallery();
});

/**
 * 初始化商品詳情頁面
 */
function initProductDetail() {
    // 可以在這裡添加詳情頁面的初始化邏輯
    console.log('商品詳情頁面已初始化');

    // 高亮顯示規格
    const specs = document.querySelectorAll('.detail-specs li');
    specs.forEach(spec => {
        spec.addEventListener('mouseenter', () => {
            spec.style.backgroundColor = 'rgba(255, 0, 110, 0.1)';
        });

        spec.addEventListener('mouseleave', () => {
            spec.style.backgroundColor = 'transparent';
        });
    });
}

/**
 * 初始化"加入購物車"按鈕
 */
function initAddToCartButtons() {
    const forms = document.querySelectorAll('.add-to-cart-form');

    forms.forEach(form => {
        form.addEventListener('submit', (e) => {
            e.preventDefault();

            const setId = form.querySelector('input[name="set_id"]').value;
            const setName = form.querySelector('h3').textContent;

            // 調用購物車函數
            addToCart(parseInt(setId), 1);
        });
    });
}

/**
 * 初始化圖片相冊
 */
function initImageGallery() {
    const mainImage = document.querySelector('.detail-image img');

    if (!mainImage) return;

    // 可以添加縮圖功能
    mainImage.addEventListener('click', () => {
        // 全屏顯示圖片
        console.log('打開圖片全屏');
    });

    // 滑鼠移動改變圖片位置 (放大效果)
    const imageContainer = document.querySelector('.detail-image');

    if (imageContainer) {
        imageContainer.addEventListener('mousemove', (e) => {
            const rect = imageContainer.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;

            // 可以在這裡實現放大效果
        });
    }
}

/**
 * 複製商品連結
 */
function copyProductLink() {
    const url = window.location.href;
    App.utils.copyToClipboard(url);
    App.utils.showNotification('✅ 商品連結已複製', 'success');
}

/**
 * 分享到社群媒體
 */
function shareToSocial(platform) {
    const url = window.location.href;
    const title = document.querySelector('.detail-info h1').textContent;

    let shareUrl = '';

    switch (platform) {
        case 'facebook':
            shareUrl = `https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(url)}`;
            break;
        case 'twitter':
            shareUrl = `https://twitter.com/intent/tweet?text=${encodeURIComponent(title)}&url=${encodeURIComponent(url)}`;
            break;
        case 'line':
            shareUrl = `https://line.me/R/msg/text/${encodeURIComponent(title + ' ' + url)}`;
            break;
        default:
            return;
    }

    window.open(shareUrl, '_blank');
}
