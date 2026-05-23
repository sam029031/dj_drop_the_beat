/*
 * admin.js - 管理後台功能
 */

// ============ 比賽 ============

function editContest(contestId) {
    document.querySelectorAll('.contest-edit-row').forEach(row => {
        if (row.id !== 'edit-contest-' + contestId) row.classList.remove('open');
    });
    const row = document.getElementById('edit-contest-' + contestId);
    if (row) row.classList.toggle('open');
}

function cancelEditContest(contestId) {
    const row = document.getElementById('edit-contest-' + contestId);
    if (row) row.classList.remove('open');
}

function deleteContest(contestId) {
    if (!confirm('確定要刪除此比賽嗎？')) return;
    const form = document.createElement('form');
    form.method = 'POST';
    form.action = '/admin/contests/' + contestId + '/delete';
    document.body.appendChild(form);
    form.submit();
}

function viewContestRegistrations(contestId) {
    window.location.href = '/admin/contests/' + contestId + '/registrations';
}

// ============ 課程 ============

function editCourse(courseId) {
    document.querySelectorAll('.course-edit-row').forEach(row => {
        if (row.id !== 'edit-course-' + courseId) row.classList.remove('open');
    });
    const row = document.getElementById('edit-course-' + courseId);
    if (row) row.classList.toggle('open');
}

function cancelEditCourse(courseId) {
    const row = document.getElementById('edit-course-' + courseId);
    if (row) row.classList.remove('open');
}

function deleteCourse(courseId) {
    if (!confirm('確定要刪除此課程嗎？')) return;
    const form = document.createElement('form');
    form.method = 'POST';
    form.action = '/admin/courses/' + courseId + '/delete';
    document.body.appendChild(form);
    form.submit();
}

function viewRegistrations(courseId) {
    window.location.href = '/admin/courses/' + courseId + '/registrations';
}

// ============ 商品 / 訂單 (stubs kept for compatibility) ============

function openAddProductModal() {}
function editProduct(productId) {}
function deleteProduct(productId) {}
function viewOrderDetails(orderId) {}
function updateOrderStatus(orderId) {}
function openAddCourseModal() {}
function openAddContestModal() {}

document.addEventListener('DOMContentLoaded', () => {
    console.log('管理後台已初始化');
});
