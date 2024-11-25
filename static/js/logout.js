function logout() {
    fetch("/api/logout/", {
        method: "POST",
        credentials: "include"  // Đảm bảo cookie được gửi kèm theo yêu cầu
    })
    .then(response => {
        if (response.ok) {
            console.log("Đăng xuất thành công.");
            // Chuyển hướng người dùng đến trang đăng nhập hoặc trang khác
            window.location.href = "/login";
        } else {
            console.error("Đăng xuất không thành công.");
        }
    })
    .catch(error => {
        console.error("Có lỗi xảy ra khi đăng xuất:", error);
    });
}

// Gọi hàm logout khi người dùng nhấn nút đăng xuất
document.querySelector('.btn-logout').addEventListener("click", logout);