// ===== CUANDO CARGA LA PÁGINA =====
document.addEventListener("DOMContentLoaded", function () {

    const elements = document.querySelectorAll('.fade-in');

    function showOnScroll() {
        elements.forEach(el => {
            const position = el.getBoundingClientRect().top;
            const screen = window.innerHeight;

            if (position < screen - 100) {
                el.classList.add('visible');
            }
        });
    }

    window.addEventListener('scroll', showOnScroll);
    showOnScroll();


    // ===== CONTADOR =====
    const counters = document.querySelectorAll('.counter');

    counters.forEach(counter => {
        counter.innerText = '0';

        const updateCounter = () => {
            const target = +counter.getAttribute('data-target');
            const current = +counter.innerText;

            const increment = target / 80;

            if (current < target) {
                counter.innerText = Math.ceil(current + increment);
                setTimeout(updateCounter, 20);
            } else {
                counter.innerText = target;
            }
        };

        updateCounter();
    });

});

// NAVBAR CAMBIO AL HACER SCROLL
window.addEventListener("scroll", function () {
    const navbar = document.querySelector(".custom-navbar");

    if (navbar) {
        if (window.scrollY > 50) {
            navbar.classList.add("scrolled");
        } else {
            navbar.classList.remove("scrolled");
        }
    }
});