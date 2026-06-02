// =========================
// SUBMENUS
// =========================

const submenuToggles = document.querySelectorAll('.submenu-toggle');

submenuToggles.forEach(toggle => {

    toggle.addEventListener('click', function(e){

        e.preventDefault();

        const submenu = this.nextElementSibling;

        submenu.classList.toggle('show');

        const icon = this.querySelector('.submenu-icon');

        icon.classList.toggle('rotate');

    });

});

// =========================
// SIDEBAR COLLAPSE
// =========================

const collapseBtn = document.getElementById('collapse-btn');
const sidebar = document.getElementById('sidebar');

collapseBtn.addEventListener('click', () => {

    sidebar.classList.toggle('sidebar-hidden');

});

// =========================
// MOBILE SIDEBAR
// =========================

const mobileToggle = document.getElementById('mobile-toggle');
const overlay = document.getElementById('sidebar-overlay');

mobileToggle.addEventListener('click', () => {

    sidebar.classList.add('show');
    overlay.classList.add('show');

});

overlay.addEventListener('click', () => {

    sidebar.classList.remove('show');
    overlay.classList.remove('show');

});

// =========================
// USER DROPDOWN
// =========================

const userBtn = document.getElementById('user-dropdown-btn');
const dropdownMenu = document.getElementById('dropdown-menu');

userBtn.addEventListener('click', () => {

    dropdownMenu.classList.toggle('show');

});

window.addEventListener('click', function(e){

    if(!userBtn.contains(e.target)){

        dropdownMenu.classList.remove('show');

    }

});

// =========================
// SEARCH ADMIN
// =========================

const searchAdmin = document.getElementById('searchAdmin');

if(searchAdmin){

    searchAdmin.addEventListener('keyup', function(){

        let value = this.value.toLowerCase();

        let rows = document.querySelectorAll('.search-row');

        rows.forEach(row => {

            row.style.display =
                row.innerText.toLowerCase().includes(value)
                ? ''
                : 'none';

        });

    });

}
