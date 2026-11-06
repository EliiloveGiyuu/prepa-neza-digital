
const menuBtn = document.getElementById("menuBtn");
const navLinks = document.getElementById("navLinks");

// MENÚ RESPONSIVE

menuBtn.addEventListener("click", () => {
    navLinks.classList.toggle("active");

    menuBtn.textContent =
        navLinks.classList.contains("active") ? "✕" : "☰";
});

document.querySelectorAll(".nav-links a").forEach(link => {
    link.addEventListener("click", () => {
        navLinks.classList.remove("active");
        menuBtn.textContent = "☰";
    });
});

// ANIMACIONES AL DESPLAZARSE

const elements = document.querySelectorAll(
    ".section-heading, .history-content, .symbol-card, .community-item, .project-card"
);

if ("IntersectionObserver" in window) {
    const observer = new IntersectionObserver(entries => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add("visible");
                observer.unobserve(entry.target);
            }
        });
    }, {
        threshold: 0.12
    });

    elements.forEach(element => {
        element.classList.add("reveal");
        observer.observe(element);
    });
} else {
    elements.forEach(element => {
        element.classList.add("visible");
    });
}
