var slideIndex = 0;
showSlides();

function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
}

function handleLoginSuccess(token) {
    // Lưu token vào localStorage
    document.cookie = `authToken=${token}; path=/; secure; SameSite=Strict`
}

// Kiểm tra và chuyển hướng đến trang home
function redirectToHome() {
    const token = getCookie("authToken");

    if (!token) {
        // Nếu không có token, chuyển hướng người dùng đến trang đăng nhập
        window.location.href = "/login";
        return;
    }

    // Gửi yêu cầu đến server với token trong header
    fetch("/homepage/", {
        method: "GET",
        headers: {
            "Authorization": `Bearer ${token}`
        }
    })
        .then(response => {
            if (response.ok) {
                // Nếu xác thực thành công, chuyển hướng đến trang `home`
                window.location.href = "/homepage/";
            } else {
                // Nếu xác thực thất bại, chuyển hướng đến trang đăng nhập
                //window.location.href = "/login";
            }
        })
        .catch(error => {
            console.error("Có lỗi xảy ra:", error);
            // window.location.href = "/login";
        });
}


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

document.getElementById("loginForm").addEventListener("submit", function (event) {
    event.preventDefault(); // Prevent default form submission

    // Fetch the input values
    var u = document.getElementById("username").value;
    var p = document.getElementById("password").value;
    console.log("username: ", u);
    console.log("password: ", p);

    // Make a POST request to the authentication API endpoint
    fetch("http://localhost:8007/login/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            username: u,
            password: p
        })
    })
        .then(response => {
            if (!response.ok) {
                console.log("Tên tài khoản hoặc mật khẩu không chính xác!");
                alert("Tên tài khoản hoặc mật khẩu không chính xác!");
                throw new Error("Failed to authenticate");
            }
            return response.json();


        })
        .then(data => {
            const decodedToken = jwt_decode(data.access);
            handleLoginSuccess(data.access);
            console.log("Decoded token payload:", decodedToken);
            console.log("Authentication successful:", data);
            redirectToHome()

        })
        .catch(error => {
            // show diaglog error
            console.log("Đã có lỗi xảy ra, vui lòng thử lại sau!");
            console.error("Authentication error:", error.message);
        });
});
