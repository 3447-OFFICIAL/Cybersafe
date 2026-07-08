/**
 * CyberSafe Report Crime Page — Interactive Bindings
 */
(function () {
    'use strict';

    document.addEventListener('DOMContentLoaded', function () {

        // ── Chatbot trigger on "Cyber Doctor AI" emergency card ───
        const chatbotTrigger = document.getElementById('chatbot-trigger-doctor');
        if (chatbotTrigger) {
            chatbotTrigger.addEventListener('click', function (e) {
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
                const input = document.getElementById('chatbot-input');
                if (input) {
                    setTimeout(function () { input.focus(); }, 150);
                }
            });
        }

        // ── Wizard step hover highlight ──────────────────────────
        const wizardSteps = document.querySelectorAll('.wizard-step');
        wizardSteps.forEach(function (step) {
            step.addEventListener('mouseenter', function () {
                step.style.opacity = '1';
            });
            step.addEventListener('mouseleave', function () {
                step.style.opacity = '0.7';
            });
        });

        // ── Emergency card entrance animation ─────────────────────
        const cards = document.querySelectorAll('.emergency-card');
        if ('IntersectionObserver' in window) {
            const observer = new IntersectionObserver(function (entries) {
                entries.forEach(function (entry) {
                    if (entry.isIntersecting) {
                        entry.target.style.opacity = '1';
                        entry.target.style.transform = 'translateY(0)';
                        observer.unobserve(entry.target);
                    }
                });
            }, { threshold: 0.1 });

            cards.forEach(function (card, i) {
                card.style.opacity = '0';
                card.style.transform = 'translateY(20px)';
                card.style.transition = 'opacity 0.5s ease ' + (i * 0.1) + 's, transform 0.5s ease ' + (i * 0.1) + 's';
                observer.observe(card);
            });
        }
    });
})();
