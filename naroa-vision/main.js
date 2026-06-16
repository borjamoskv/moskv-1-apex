document.addEventListener('DOMContentLoaded', () => {
    const container = document.querySelector('.gallery-container');
    const indicator = document.querySelector('.scroll-indicator');

    container.addEventListener('scroll', () => {
        // Hide scroll indicator if user scrolls past the first slide
        if (container.scrollTop > 50) {
            indicator.style.opacity = '0';
            indicator.style.transition = 'opacity 0.5s ease';
        } else {
            indicator.style.opacity = '1';
        }
    });
});
