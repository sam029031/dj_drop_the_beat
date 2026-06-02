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

// ============ 商品 / 訂單 ============

function openAddProductModal() {}
function editProduct(productId) {}
function deleteProduct(productId) {}
function openAddCourseModal() {}
function openAddContestModal() {}

function _escHtml(str) {
    return String(str)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;');
}

function viewOrderDetails(orderId) {
    fetch('/admin/orders/' + orderId)
        .then(r => r.json())
        .then(order => {
            let itemsHtml = '';
            if (order.items && order.items.length) {
                itemsHtml = '<table class="receipt-table"><thead><tr><th>商品</th><th>數量</th><th>單價</th><th>小計</th></tr></thead><tbody>';
                order.items.forEach(item => {
                    itemsHtml += `<tr>
                        <td>${_escHtml(item.set_name)}</td>
                        <td>${_escHtml(item.quantity)}</td>
                        <td>NT$${Number(item.unit_price).toLocaleString()}</td>
                        <td>NT$${Number(item.subtotal).toLocaleString()}</td>
                    </tr>`;
                });
                itemsHtml += '</tbody></table>';
            } else {
                itemsHtml = '<p class="no-data">無商品資料</p>';
            }
            document.getElementById('orderModalContent').innerHTML = `
                <div class="receipt-info">
                    <p><span>訂單編號</span><strong>${_escHtml(order.order_number)}</strong></p>
                    <p><span>訂購人</span><strong>${_escHtml(order.buyer_name)}</strong></p>
                    <p><span>電子郵件</span><strong>${_escHtml(order.buyer_email)}</strong></p>
                    <p><span>電話</span><strong>${_escHtml(order.buyer_phone)}</strong></p>
                </div>
                ${itemsHtml}
                <div class="receipt-total">
                    <span>總金額</span>
                    <strong>NT$${Number(order.final_price).toLocaleString()}</strong>
                </div>
            `;
            document.getElementById('orderModal').style.display = 'flex';
        })
        .catch(() => alert('無法載入訂單資料'));
}

function closeOrderModal(event) {
    if (!event || event.target === document.getElementById('orderModal')) {
        document.getElementById('orderModal').style.display = 'none';
    }
}

function updateOrderStatus(orderId) {
    if (!confirm('確定要將此訂單狀態更新為「已確認」嗎？')) return;
    const form = document.createElement('form');
    form.method = 'POST';
    form.action = '/admin/orders/' + orderId + '/status';
    const input = document.createElement('input');
    input.type = 'hidden';
    input.name = 'status';
    input.value = 'Confirmed';
    form.appendChild(input);
    document.body.appendChild(form);
    form.submit();
}

document.addEventListener('DOMContentLoaded', () => {
    console.log('管理後台已初始化');
});
