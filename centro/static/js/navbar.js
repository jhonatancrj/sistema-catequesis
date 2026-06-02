// ===== SCROLL EFFECT =====
window.addEventListener("scroll", function () {
    const header = document.getElementById("header");
    header.classList.toggle("scrolled", window.scrollY > 50);
});

// ===== SIDEBAR MENU =====
const menuToggle = document.getElementById("menu-toggle");
const sidebar = document.getElementById("sidebar");
const sidebarClose = document.getElementById("sidebar-close");
const sidebarOverlay = document.getElementById("sidebar-overlay");

// ABRIR SIDEBAR
menuToggle.addEventListener("click", () => {
    sidebar.classList.add("active");
    menuToggle.classList.add("active");
});

// CERRAR SIDEBAR CON BOTÓN X
sidebarClose.addEventListener("click", () => {
    sidebar.classList.remove("active");
    menuToggle.classList.remove("active");
});

// CERRAR SIDEBAR AL HACER CLICK EN OVERLAY
sidebarOverlay.addEventListener("click", () => {
    sidebar.classList.remove("active");
    menuToggle.classList.remove("active");
});

// CERRAR SIDEBAR AL HACER CLICK EN UN ENLACE
const sidebarLinks = sidebar.querySelectorAll("a");
sidebarLinks.forEach(link => {
    link.addEventListener("click", () => {
        sidebar.classList.remove("active");
        menuToggle.classList.remove("active");
    });
});

// CERRAR SIDEBAR AL PRESIONAR ESC
document.addEventListener("DOMContentLoaded", () => {

    // ===== SCROLL EFFECT =====
    window.addEventListener("scroll", function () {
        const header = document.getElementById("header");

        if (header) {
            header.classList.toggle("scrolled", window.scrollY > 50);
        }
    });

    // ===== SIDEBAR MENU =====
    const menuToggle = document.getElementById("menu-toggle");
    const sidebar = document.getElementById("sidebar");
    const sidebarClose = document.getElementById("sidebar-close");
    const sidebarOverlay = document.getElementById("sidebar-overlay");

    // Verificar que existan los elementos
    if (menuToggle && sidebar) {

        // ABRIR SIDEBAR
        menuToggle.addEventListener("click", () => {
            sidebar.classList.add("active");
            menuToggle.classList.add("active");
        });

        // CERRAR SIDEBAR CON BOTÓN X
        if (sidebarClose) {
            sidebarClose.addEventListener("click", () => {
                sidebar.classList.remove("active");
                menuToggle.classList.remove("active");
            });
        }

        // CERRAR SIDEBAR AL HACER CLICK EN OVERLAY
        if (sidebarOverlay) {
            sidebarOverlay.addEventListener("click", () => {
                sidebar.classList.remove("active");
                menuToggle.classList.remove("active");
            });
        }

        // CERRAR SIDEBAR AL HACER CLICK EN UN ENLACE
        const sidebarLinks = sidebar.querySelectorAll("a");

        sidebarLinks.forEach(link => {
            link.addEventListener("click", () => {
                sidebar.classList.remove("active");
                menuToggle.classList.remove("active");
            });
        });

        // CERRAR SIDEBAR AL PRESIONAR ESC
        document.addEventListener("keydown", (e) => {
            if (e.key === "Escape" && sidebar.classList.contains("active")) {
                sidebar.classList.remove("active");
                menuToggle.classList.remove("active");
            }
        });
    }

});


// ===== PROFILE DROPDOWN =====

const profileBtn = document.getElementById("profile-btn");
const profileMenu = document.getElementById("profile-menu");

if (profileBtn && profileMenu) {

    profileBtn.addEventListener("click", (e) => {

        e.stopPropagation();

        profileMenu.classList.toggle("active");

    });

    document.addEventListener("click", () => {

        profileMenu.classList.remove("active");

    });

}