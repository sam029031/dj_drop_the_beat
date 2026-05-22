/*
 * search.js - 搜尋功能
 */

document.addEventListener('DOMContentLoaded', () => {
    // 初始化搜尋表單
    initSearchForm();

    // 初始化搜尋結果分頁
    initSearchPagination();
});

/**
 * 初始化搜尋表單
 */
function initSearchForm() {
    const form = document.querySelector('.search-form');

    if (!form) return;

    const searchInput = form.querySelector('.search-input');

    // 搜尋建議下拉菜單
    searchInput.addEventListener('input', (e) => {
        const query = e.target.value.trim();

        if (query.length > 1) {
            // 可以在這裡實現搜尋建議
            console.log(`搜尋: ${query}`);
        }
    });

    // Enter 鍵提交
    searchInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            form.submit();
        }
    });
}

/**
 * 初始化搜尋結果分頁
 */
function initSearchPagination() {
    const paginationBtns = document.querySelectorAll('.pagination-btn');

    paginationBtns.forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.preventDefault();
            const url = btn.href;
            window.location.href = url;
        });
    });
}

/**
 * 執行搜尋
 */
function performSearch(query) {
    const url = new URL('/search', window.location.origin);
    url.searchParams.set('q', query);
    window.location.href = url.toString();
}
