// Auto-scrolling slider functionality
document.addEventListener('DOMContentLoaded', function() {
    const slider = document.querySelector('.slider');
    
    // Clone slides for infinite scroll effect
    const slides = document.querySelectorAll('.slide');
    slides.forEach(slide => {
        const clone = slide.cloneNode(true);
        slider.appendChild(clone);
    });

    // Pause animation on hover
    slider.addEventListener('mouseenter', function() {
        this.style.animationPlayState = 'paused';
    });

    slider.addEventListener('mouseleave', function() {
        this.style.animationPlayState = 'running';
    });
});
