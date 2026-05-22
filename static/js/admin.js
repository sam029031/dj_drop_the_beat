/*
 * admin.js - 管理後台功能
 */

/**
 * 打開新增商品對話框
 */
function openAddProductModal() {
    alert('打開新增商品表單');
    // 實現模態框或表單
}

/**
 * 編輯商品
 */
function editProduct(productId) {
    alert(`編輯商品 ID: ${productId}`);
    // 實現編輯功能
}

/**
 * 刪除商品
 */
function deleteProduct(productId) {
    if (confirm(`確定要刪除此商品嗎？`)) {
        alert(`刪除商品 ID: ${productId}`);
        // 調用 API 刪除
    }
}

/**
 * 查看訂單詳情
 */
function viewOrderDetails(orderId) {
    alert(`查看訂單 ID: ${orderId}`);
    // 實現詳情頁面或模態框
}

/**
 * 更新訂單狀態
 */
function updateOrderStatus(orderId) {
    const newStatus = prompt('輸入新狀態 (pending_payment/confirmed/shipped/delivered/cancelled):');
    if (newStatus) {
        alert(`更新訂單 ${orderId} 狀態為: ${newStatus}`);
        // 調用 API 更新
    }
}

/**
 * 打開新增課程對話框
 */
function openAddCourseModal() {
    alert('打開新增課程表單');
}

/**
 * 編輯課程
 */
function editCourse(courseId) {
    alert(`編輯課程 ID: ${courseId}`);
}

/**
 * 刪除課程
 */
function deleteCourse(courseId) {
    if (confirm(`確定要刪除此課程嗎？`)) {
        alert(`刪除課程 ID: ${courseId}`);
    }
}

/**
 * 查看課程報名者
 */
function viewRegistrations(courseId) {
    alert(`查看課程 ${courseId} 的報名者列表`);
}

/**
 * 打開新增比賽對話框
 */
function openAddContestModal() {
    alert('打開新增比賽表單');
}

/**
 * 編輯比賽
 */
function editContest(contestId) {
    alert(`編輯比賽 ID: ${contestId}`);
}

/**
 * 刪除比賽
 */
function deleteContest(contestId) {
    if (confirm(`確定要刪除此比賽嗎？`)) {
        alert(`刪除比賽 ID: ${contestId}`);
    }
}

/**
 * 查看比賽報名者
 */
function viewContestRegistrations(contestId) {
    alert(`查看比賽 ${contestId} 的報名者列表`);
}

// 初始化
document.addEventListener('DOMContentLoaded', () => {
    // 可以在這裡添加表格排序、篩選等功能
    console.log('管理後台已初始化');
});
