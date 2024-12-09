var radioButton = document.getElementsByClassName('btn-radio')
var checkbox = document.querySelector('.checkbox')
var Imgs = document.querySelectorAll('.first-img')


checkbox.onclick = () => {
    Array.from(radioButton).forEach((e) => {
        if (e.checked) {
            e.nextElementSibling.classList.add('active')
        }
        if (!e.checked) {
            e.nextElementSibling.classList.remove('active')
        }
    })
}

var img1 = Imgs[0]
var img2 = Imgs[1]
var img3 = Imgs[2]
var img4 = Imgs[3]

var left = -100
setInterval(() => {
    left -= 1225
    if (left === -5000) {
        left = -100
    }
    img1.style.left = left + 'px'
    img2.style.left = left + 'px'
    img3.style.left = left + 'px'
    img4.style.left = left + 'px'
}, 4000)

document.getElementById("form-1").addEventListener("submit", function (event) {
    event.preventDefault();

    var u = document.getElementById("username").value;
    var m = document.getElementById("fullname").value;
    var e = document.getElementById("email").value;
    var p = document.getElementById("password").value;
    var c = document.getElementById("birth").value;
    var g = document.querySelector('input[name="gender"]:checked');
    var sdt = document.getElementById("sdt").value;
    var pa = document.getElementById("password_confirmation").value;

    if (!g) {
        alert("Please select a gender.");
        return;
    }

    const genderValue = g.value === "1";
    if (p == pa) {
        const userData = {
            "username": u,
            "email": e,
            "telephone": sdt,
            "fullname": m,
            "gender": genderValue,
            "birthday": c,
            "role": "PATIENT",
            "password": p
        };

        console.log("Sending user data:", JSON.stringify(userData));

        fetch("http://localhost:8007/register/", {
            method: 'POST',
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(userData)
        })
            .then(response => {
                if (!response.ok) {
                    return response.json().then(errorData => {
                        console.error("Error response from server:", errorData);
                    });
                }
                return response.json();
            })
            .then(data => {
                alert("Register successful!");
                console.log("Authentication successful:", data);
            })
            .catch(error => {
                alert("Error with registration! Please try again later.");
                console.error("Authentication error:", error.message);
            });


    }
    else {
        alert("Mật khẩu nhập lại không đúng");
    }
});