document.addEventListener("DOMContentLoaded", function () {

    const cursor = document.querySelector(".premium-cursor");
    const glow = document.querySelector(".premium-cursor-glow");

    if (!cursor || !glow) {
        return;
    }

    let mouseX = 0;
    let mouseY = 0;

    let glowX = 0;
    let glowY = 0;

    document.addEventListener("mousemove", function (event) {

        mouseX = event.clientX;
        mouseY = event.clientY;

        cursor.style.left = mouseX + "px";
        cursor.style.top = mouseY + "px";

    });


    function animateGlow() {

        glowX += (mouseX - glowX) * 0.12;
        glowY += (mouseY - glowY) * 0.12;

        glow.style.left = glowX + "px";
        glow.style.top = glowY + "px";

        requestAnimationFrame(animateGlow);
    }

    animateGlow();


    const interactiveElements = document.querySelectorAll(
        "a, button, .btn, .zodiac-card, .service-card, .horoscope-card"
    );


    interactiveElements.forEach(function (element) {

        element.addEventListener("mouseenter", function () {
            document.body.classList.add("cursor-hover");
        });

        element.addEventListener("mouseleave", function () {
            document.body.classList.remove("cursor-hover");
        });

    });

});