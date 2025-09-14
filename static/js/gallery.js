document.addEventListener("DOMContentLoaded", function () {
    // CAROUSEL AUTO-SLIDE
    const carousel = document.querySelector("#galleryCarousel");
    if (carousel) {
        let currentIndex = 0;
        const slides = carousel.querySelectorAll(".carousel-item");
        const totalSlides = slides.length;

        function showSlide(index) {
            slides.forEach((slide) => slide.classList.remove("active"));
            if (slides[index]) slides[index].classList.add("active");
        }

        setInterval(() => {
            if (totalSlides > 0) {
                currentIndex = (currentIndex + 1) % totalSlides;
                showSlide(currentIndex);
            }
        }, 5000);
    }

    // MODAL IMAGE
    const modal = document.createElement("div");
    modal.id = "imageModal";
    modal.classList.add("modal-overlay");

    const modalImage = document.createElement("img");
    modalImage.id = "modalImage";
    modal.appendChild(modalImage);

    const closeButton = document.createElement("span");
    closeButton.innerHTML = "&times;";
    closeButton.id = "modalClose";
    modal.appendChild(closeButton);

    document.body.appendChild(modal);

    // Ouvrir modal au clic sur image
    document.querySelectorAll(".carousel-item img, .thumbnail img").forEach(img => {
        img.addEventListener("click", () => {
            modalImage.src = img.src;
            modal.style.display = "flex";
        });
    });

    // Fermer modal
    closeButton.addEventListener("click", () => modal.style.display = "none");
    modal.addEventListener("click", e => {
        if (e.target === modal) modal.style.display = "none";
    });
});
