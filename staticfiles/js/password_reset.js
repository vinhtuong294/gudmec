var slideIndex = 0;
showSlides();

function showSlides() {
    var i;
    var slides = document.getElementsByClassName("slide");
    for (i = 0; i < slides.length; i++) {
        slides[i].style.display = "none";
    }
    slideIndex++;
    if (slideIndex > slides.length) { slideIndex = 1 }
    slides[slideIndex - 1].style.display = "block";
    setTimeout(showSlides, 3000); // Đổi ảnh sau mỗi 2 giây
}
document.getElementById("passwordResetForm").addEventListener("submit", function (event) {
    event.preventDefault(); // Ngăn không cho form submit mặc định

    // Lấy giá trị email từ input
    var email = document.getElementById("email").value;
    console.log("Email:", email);

    // Gửi yêu cầu POST tới endpoint đặt lại mật khẩu
    fetch("http://127.0.0.1:8007/reset-password/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            email: email
        })
    })
        .then(response => {
            if (!response.ok) {
                alert("Email không hợp lệ hoặc không tồn tại trong hệ thống!");
                throw new Error("Failed to send password reset email");
            }
            return response.json();
        })
        .then(data => {
            alert("Yêu cầu đặt lại mật khẩu đã được gửi! Vui lòng kiểm tra email của bạn.");
            console.log("Password reset request successful:", data);
        })
        .catch(error => {
            alert("Đã có lỗi xảy ra, vui lòng thử lại sau!");
            console.error("Password reset error:", error.message);
        });
});