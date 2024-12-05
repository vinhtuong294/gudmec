const NAV_INDEX_STORAGE_KEY = 'INDEX'

var navLink = document.querySelectorAll('.link')
var popUp = document.querySelector('.pop-up');
var divStickynav = document.querySelector('.sticky-nav');
var btnClose = document.querySelector('.btn-close');
var btnDK = document.querySelector('#link-popup');
var formCheckToday = document.querySelector('#form-check-today');
var inputCheckToday = document.querySelector('#check-today');
var departmentItems = document.querySelectorAll('.item-department');

function scrollToElement(elementId) {
    var element = document.getElementById(elementId);
    console.log(elementId)
    if (element) {
        element.scrollIntoView({
            behavior: 'smooth',
            block: 'start'
        });
    }
}

function toast({
    title = '',
    msg = '',
    type = 'info',
    duration = 3000
}) {
    const main = document.getElementById('toasts_show');
    if (main) {
        const icons = {
            succeces: 'fa-circle-check',
            warnming: 'fa-triangle-exclamation'
        }
        const icon = icons[type];
        const toast = document.createElement('div');
        const delay = (duration / 1000).toFixed(2);

        const myTimeOut = setTimeout(function () {
            main.removeChild(toast);
        }, duration + 1000);

        toast.onclick = function (e) {
            if (e.target.classList[0] === 'fa-regular') {
                main.removeChild(toast);
                clearTimeout(myTimeOut);
            }
        }

        toast.classList.add('toast_show', `toast--${type}`);

        toast.innerHTML = ` 
        <div class="toast__icon">
            <i class="fa-solid ${icon}"></i>
        </div>
        <div class="toast__body">
            <h3 class="toast__title">${title}</h3> 
            <p class="toast__msg">${msg}</p>
        </div>
        <div class="toast__close">
            <i class="fa-regular fa-circle-xmark"></i>
        </div>
        `
        main.appendChild(toast);
        toast.style.animation = `slideInleft ease .3s, fadeOut ease 1s ${delay}s forwards`;
    }
}

const storage = {
    get() {
        return JSON.parse(localStorage.getItem(NAV_INDEX_STORAGE_KEY));
    },
    set(index) {
        localStorage.setItem(NAV_INDEX_STORAGE_KEY, JSON.stringify(index));
    },
    delete() {
        localStorage.clear();
    }
}
navLink[0].classList.add('active');

for (let i = 0; i < navLink.length; i++) {
    if (navLink[i].classList.contains('active') && storage.get()) {
        navLink[i].classList.remove('active');
        navLink[storage.get()]?.classList.add('active')
        break;
    }
}

const _$ = document.querySelector('.link.active');
const lines = document.querySelector('.nav-link .line');

lines.style.left = _$?.offsetLeft + 'px';
lines.style.width = _$?.offsetWidth + 'px';
lines.style.top = _$?.offsetTop + 42 + 'px';
lines.style.display = 'block';

window.addEventListener('resize', function (event) {
    const $$ = document.querySelector('.link.active');
    lines.style.left = $$.offsetLeft + 'px';
    lines.style.width = $$.offsetWidth + 'px';
});

navLink.forEach((link, index) => {

    link.onclick = () => {
        console.log(link);

        if (index == 0) {
            lines.style.display = 'none';
        }
        if (link.classList.contains('team-of-doctors')) {
            scrollToElement('list-bs')
        }
        for (var i = 0; i < navLink.length; i++) {
            if (navLink[i].classList.value.includes('active')) {
                navLink[i].classList.remove('active');
            }
        }
        lines.style.left = navLink[index].offsetLeft + 'px';
        lines.style.width = navLink[index].offsetWidth + 'px';


        if (link.id === "link-popup") {
            popUp.style.display = 'block';
        }
        link.classList.add('active');
        storage.set(index)
    }
})

document.onclick = function (e) {
    if (e.target !== btnDK && !popUp.contains(e.target) && popUp.style.display === 'block') {

        console.log(e.target)
        popUp.style.display = 'none';
    }
}

btnClose.onclick = function (e) {
    console.log(e.target)
    popUp.style.display = 'none';
}
//const getDoctorInDepartment = (index) => {
//    fetch("http://localhost:8007/api/doctors-in-department/", {
//        method: "POST",
//        headers: {
//            "Content-Type": "application/json"
//        },
//        body: JSON.stringify({
//            department_id: index,
//        })
//    })
//    .then(response => response.json())
//    .then(data => {
//        console.log("data payload:", data);
//    })
//    .catch(error => {
//        console.log("Đã có lỗi xảy ra, vui lòng thử lại sau!", error);
//    });
//};
//
//for(let i=0; i<departmentItems.length; i++){
//     departmentItems[i].addEventListener('click', () => getDoctorInDepartment(i+1) )
//}
