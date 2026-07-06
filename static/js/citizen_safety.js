document.addEventListener('DOMContentLoaded', () => {
    setTimeout(() => {
        document.querySelectorAll('.reveal:not(.active), .reveal-left:not(.active), .reveal-right:not(.active), .reveal-scale:not(.active), .stagger-container:not(.active)').forEach(el => {
            el.classList.add('active');
        });
    }, 3000);
});
