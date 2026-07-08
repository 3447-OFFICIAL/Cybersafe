/**
 * CyberSafe Contact Page — Interactive Bindings
 */
(function () {
    'use strict';

    document.addEventListener('DOMContentLoaded', function () {

        // ── Chatbot trigger buttons on contact page ───────────────
        const chatbotTriggers = document.querySelectorAll(
            '#chatbot-trigger-doctor, #chatbot-trigger-assistant'
        );
        chatbotTriggers.forEach(function (el) {
            el.addEventListener('click', function (e) {
                e.preventDefault();
                const widget = document.getElementById('chatbot-widget');
                const toggle = document.getElementById('chatbot-toggle');
                if (widget) {
                    widget.style.display = 'flex';
                    widget.setAttribute('aria-hidden', 'false');
                    document.body.style.overflow = 'hidden';
                }
                if (toggle) {
                    toggle.setAttribute('aria-expanded', 'true');
                }
                // Focus input
                const input = document.getElementById('chatbot-input');
                if (input) {
                    setTimeout(function () { input.focus(); }, 150);
                }
            });
        });

        // ── Animate cards on scroll (IntersectionObserver) ────────
        const cards = document.querySelectorAll(
            '.contact-card, .touch-card, .office-card, .directive-card'
        );
        if ('IntersectionObserver' in window) {
            const observer = new IntersectionObserver(function (entries) {
                entries.forEach(function (entry) {
                    if (entry.isIntersecting) {
                        entry.target.style.opacity = '1';
                        entry.target.style.transform = 'translateY(0)';
                        observer.unobserve(entry.target);
                    }
                });
            }, { threshold: 0.1, rootMargin: '0px 0px -40px 0px' });

            cards.forEach(function (card, i) {
                card.style.opacity = '0';
                card.style.transform = 'translateY(20px)';
                card.style.transition = 'opacity 0.5s ease ' + (i * 0.07) + 's, transform 0.5s ease ' + (i * 0.07) + 's';
                observer.observe(card);
            });
        }
    });
})();
