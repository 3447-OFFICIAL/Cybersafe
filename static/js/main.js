/* ============================================================
   CYBERSAFE — CYBER-TECH UI ENGINE
   IntersectionObserver reveal system, animated counters,
   parallax, cursor glow, navbar scroll effects
   ============================================================ */

// ─── Section Reveal Controller ───────────────────────────────
(function () {
    'use strict';

    const REVEAL_SELECTORS = '.reveal, .reveal-left, .reveal-right, .reveal-scale, .stagger-container';
    const THRESHOLD = 0.12;
    const ROOT_MARGIN = '0px 0px -60px 0px';

    function initRevealObserver() {
        return; // DISABLED: Testing if reveal animations cause scrollbar jumping
        const elements = document.querySelectorAll(REVEAL_SELECTORS);
        if (!elements.length) return;

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('active');
                    // Only unobserve non-repeating reveals
                    if (!entry.target.dataset.repeat) {
                        observer.unobserve(entry.target);
                    }
                }
            });
        }, {
            threshold: THRESHOLD,
            rootMargin: ROOT_MARGIN
        });

        elements.forEach(el => observer.observe(el));
    }

    // ─── Animated Counters ────────────────────────────────────
    function animateCounter(el) {
        const target = parseFloat(el.dataset.target);
        const suffix = el.dataset.suffix || '';
        const prefix = el.dataset.prefix || '';
        const duration = parseInt(el.dataset.duration) || 2000;
        const isDecimal = String(target).includes('.');
        let startTime = null;

        function step(timestamp) {
            if (!startTime) startTime = timestamp;
            const progress = Math.min((timestamp - startTime) / duration, 1);
            // Ease out cubic
            const eased = 1 - Math.pow(1 - progress, 3);
            const current = target * eased;

            if (isDecimal) {
                el.textContent = prefix + current.toFixed(1) + suffix;
            } else {
                el.textContent = prefix + Math.floor(current).toLocaleString() + suffix;
            }

            if (progress < 1) {
                requestAnimationFrame(step);
            } else {
                el.textContent = prefix + (isDecimal ? target.toFixed(1) : target.toLocaleString()) + suffix;
            }
        }

        requestAnimationFrame(step);
    }

    function initCounters() {
        return; // DISABLED: Testing if counter animations cause scrollbar jumping
        const counters = document.querySelectorAll('[data-counter]');
        if (!counters.length) return;

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    animateCounter(entry.target);
                    observer.unobserve(entry.target);
                }
            });
        }, { threshold: 0.3 });

        counters.forEach(el => observer.observe(el));
    }

    // ─── Navbar Scroll Effect (Optimized) ─────────────────────────────────
    function initNavbarScroll() {
        return; // DISABLED: Testing if navbar scroll handler causes scrollbar jumping
        const navbar = document.querySelector('.navbar');
        if (!navbar) return;

        let ticking = false;

        function updateNavbar() {
            if (window.scrollY > 60) {
                navbar.classList.add('scrolled');
            } else {
                navbar.classList.remove('scrolled');
            }
            ticking = false;
        }

        window.addEventListener('scroll', () => {
            if (!ticking) {
                requestAnimationFrame(updateNavbar);
                ticking = true;
            }
        }, { passive: true });
    }

    // ─── Parallax Background Elements (Optimized - Skip in Senior Mode) ─────────────────────────
    function initParallax() {
        return; // DISABLED: Testing if parallax causes scrollbar jumping
        // Disable parallax in senior mode for smoother scrolling
        if (document.body.classList.contains('senior-mode') ||
            document.documentElement.classList.contains('senior-mode')) {
            return;
        }

        const parallaxEls = document.querySelectorAll('[data-parallax]');
        if (!parallaxEls.length) return;

        let ticking = false;
        let lastUpdate = 0;
        const MIN_UPDATE_INTERVAL = 32; // Lower fps to reduce reflows

        function updateParallax() {
            const now = performance.now();
            if (now - lastUpdate < MIN_UPDATE_INTERVAL) {
                ticking = false;
                return;
            }
            lastUpdate = now;

            const scrollY = window.scrollY;
            parallaxEls.forEach(el => {
                const speed = parseFloat(el.dataset.parallax) || 0.3;
                const offset = scrollY * speed;
                // Use GPU acceleration with translate3d for better performance
                el.style.transform = `translate3d(0, ${offset}px, 0)`;
            });
            ticking = false;
        }

        window.addEventListener('scroll', () => {
            if (!ticking) {
                requestAnimationFrame(updateParallax);
                ticking = true;
            }
        }, { passive: true });

        // Disable parallax when senior mode is activated
        const observer = new MutationObserver(() => {
            if (document.body.classList.contains('senior-mode')) {
                parallaxEls.forEach(el => {
                    el.style.transform = 'translate3d(0, 0, 0)';
                });
            }
        });
        observer.observe(document.body, { attributes: true, attributeFilter: ['class'] });
    }

    // ─── Mouse Glow Tracker ───────────────────────────────────
    function initMouseGlow() {
        const glowSections = document.querySelectorAll('.glow-track');
        glowSections.forEach(section => {
            const glowEl = document.createElement('div');
            glowEl.style.cssText = `
                position: absolute;
                width: 300px;
                height: 300px;
                border-radius: 50%;
                background: radial-gradient(circle, rgba(0,212,255,0.06) 0%, transparent 70%);
                pointer-events: none;
                transition: opacity 0.3s ease;
                opacity: 0;
                z-index: 0;
            `;
            section.style.position = section.style.position || 'relative';
            section.style.overflow = 'hidden';
            section.appendChild(glowEl);

            section.addEventListener('mousemove', (e) => {
                const rect = section.getBoundingClientRect();
                const x = e.clientX - rect.left - 150;
                const y = e.clientY - rect.top - 150;
                glowEl.style.left = x + 'px';
                glowEl.style.top = y + 'px';
                glowEl.style.opacity = '1';
            });

            section.addEventListener('mouseleave', () => {
                glowEl.style.opacity = '0';
            });
        });
    }

    // ─── Global Cursor Glow ───────────────────────────────────
    function initGlobalCursorGlow() {
        const glowEl = document.getElementById('cursor-glow');
        if (!glowEl) return;

        window.addEventListener('mousemove', (e) => {
            glowEl.style.transform = `translate(calc(${e.clientX}px - 50%), calc(${e.clientY}px - 50%))`;
            glowEl.style.opacity = '1';
        });

        document.addEventListener('mouseleave', () => {
            glowEl.style.opacity = '0';
        });

        document.addEventListener('mouseenter', () => {
            glowEl.style.opacity = '1';
        });
    }

    // ─── Smooth Scroll for Anchor Links ───────────────────────
    function initSmoothScroll() {
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function (e) {
                const targetId = this.getAttribute('href');
                if (targetId === '#') return;
                const target = document.querySelector(targetId);
                if (target) {
                    e.preventDefault();
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            });
        });
    }

    // ─── Active Nav Link Highlighter ──────────────────────────
    function initActiveNavHighlight() {
        const currentPath = window.location.pathname;
        document.querySelectorAll('.nav-link').forEach(link => {
            const href = link.getAttribute('href');
            if (href && href !== '#') {
                if (currentPath === href || (href !== '/' && currentPath.startsWith(href))) {
                    link.classList.add('active');
                }
            }
        });
    }

    // ─── Cyber Crimes Filter Toggle ──────────────────────────
    function initCrimeFilterToggle() {
        const trigger = document.getElementById('filter-trigger');
        const panel = document.getElementById('filter-panel');
        const mainSection = document.getElementById('registry-main');

        if (!trigger || !panel) return;

        trigger.addEventListener('click', () => {
            trigger.classList.toggle('active');
            panel.classList.toggle('show');
            if (mainSection) {
                mainSection.classList.toggle('filters-active');
            }
        });
    }

    // ─── Cyber Crimes Category Filter ────────────────────────
    function initCrimeCategoryFilter() {
        const buttons = document.querySelectorAll('.category-filter[data-category]');
        const cards = document.querySelectorAll('.crime-card-hp');

        if (!buttons.length || !cards.length) return;

        const allItems = Array.from(cards).map(card => card.closest('.col-md-6, .col-lg-4, .col-md-4, [class*=col]') || card);

        function applyFilter(category) {
            buttons.forEach(button => button.classList.toggle('active', button.dataset.category === category));

            cards.forEach(card => {
                const parent = card.closest('.col-md-6, .col-lg-4, .col-md-4, [class*=col]') || card;
                const matches = category === 'all' || card.dataset.category === category;
                parent.style.display = matches ? '' : 'none';
            });
        }

        buttons.forEach(button => {
            button.addEventListener('click', () => applyFilter(button.dataset.category || 'all'));
        });

        const activeButton = Array.from(buttons).find(button => button.classList.contains('active'));
        applyFilter(activeButton ? activeButton.dataset.category || 'all' : 'all');
    }

    // ─── Boot ─────────────────────────────────────────────────
    function boot() {
        initRevealObserver();
        initCounters();
        initNavbarScroll();
        initParallax();
        initMouseGlow();
        initSmoothScroll();
        initActiveNavHighlight();
        initCrimeFilterToggle();
        initCrimeCategoryFilter();
        initGlobalCursorGlow();
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', boot);
    } else {
        boot();
    }
})();


/* ============================================================
   CHATBOT — Existing functionality preserved
   ============================================================ */
class Chatbot {
    constructor() {
        this.isOpen = false;
        this.messages = [];
        this.init();
    }

    init() {
        this.createChatbotElements();
        this.bindEvents();
        this.addWelcomeMessage();
    }
    getCSRFToken() {
        return document
            .querySelector('meta[name="csrf-token"]')
            ?.getAttribute('content');
    }

    createChatbotElements() {
        if (document.getElementById('chatbot-widget')) return;

        if (document.getElementById('chatbot-toggle')) return;

        const wrapper = document.createElement('div');
        wrapper.id = 'chatbot-toggle-wrapper';
        wrapper.className = 'chatbot-toggle-wrapper';

        const toggleBtn = document.createElement('button');
        toggleBtn.id = 'chatbot-toggle';
        toggleBtn.className = 'chatbot-toggle';
        toggleBtn.setAttribute('aria-label', 'CyberSafe Chatbot');
        toggleBtn.setAttribute('aria-expanded', 'false');
        toggleBtn.setAttribute('aria-controls', 'chatbot-widget');
        toggleBtn.innerHTML = '<i class="fas fa-comment" aria-hidden="true"></i>';
        toggleBtn.title = 'Chat with CyberSafe AI';
        
        const label = document.createElement('div');
        label.className = 'chatbot-toggle-label';
        label.innerText = 'CyberSafe Chatbot';

        wrapper.appendChild(toggleBtn);
        wrapper.appendChild(label);
        document.body.appendChild(wrapper);

        const widget = document.createElement('div');
        widget.id = 'chatbot-widget';
        widget.className = 'chatbot-widget';
        widget.innerHTML = `
    <div class="chatbot-header d-flex justify-content-between align-items-center">
        <div>
            <strong style="color: var(--cyber-blue);">🛡️ CyberSafe AI</strong>
            <div style="font-size: 0.75rem; color: var(--text-muted);">
                <span class="pulse-dot" style="width:6px;height:6px;margin-right:5px;"></span>
                Online
            </div>
        </div>

        <div style="display:flex; align-items:center; gap:10px;">

            <!-- Reset Button -->
            <button
                id="chatbot-reset"
                style="
                    background:none;
                    border:none;
                    color: var(--text-muted);
                    cursor:pointer;
                    font-size:0.95rem;
                    transition: color 0.2s;
                "
                title="Reset Chat"
                onmouseover="this.style.color='#00d4ff'"
                onmouseout="this.style.color='var(--text-muted)'"
            >
                <i class="fas fa-rotate-right"></i>
            </button>

            <!-- Close Button -->
            <button
                id="chatbot-close"
                style="
                    background:none;
                    border:none;
                    color: var(--text-muted);
                    cursor:pointer;
                    font-size:1.2rem;
                    transition: color 0.2s;
                "
                onmouseover="this.style.color='var(--cyber-blue)'"
                onmouseout="this.style.color='var(--text-muted)'"
            >
                &times;
            </button>

        </div>
    </div>

    <div class="chatbot-messages" id="chatbot-messages"></div>

    <div class="chatbot-input">
        <div class="d-flex gap-2">

            <input
                type="text"
                id="chatbot-input-field"
                class="form-control"
                placeholder="Ask about cyber safety..."
                autocomplete="off"
            >

            <button
                id="chatbot-send"
                class="btn btn-primary"
                style="min-width: 44px;"
            >
                <svg width="18" height="18" fill="none" stroke="currentColor"
                    stroke-width="2" viewBox="0 0 24 24">
                    <path d="M22 2L11 13M22 2l-7 20-4-9-9-4 20-7z"/>
                </svg>
            </button>

        </div>
    </div>
`;
        document.body.appendChild(widget);
    }

    bindEvents() {
        const toggle = document.getElementById('chatbot-toggle');
        const close = document.getElementById('chatbot-close');
        const send = document.getElementById('chatbot-send');
        const input = document.getElementById('chatbot-input-field');
        const reset = document.getElementById('chatbot-reset');

        if (toggle) toggle.addEventListener('click', () => this.toggle());
        if (close) close.addEventListener('click', () => this.close());
        if (send) send.addEventListener('click', () => this.sendMessage());
        if (input) {
            input.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') this.sendMessage();
            });
        }
        if (reset) reset.addEventListener('click', () => this.resetChat());

    }

    toggle() {
        this.isOpen = !this.isOpen;
        const widget = document.getElementById('chatbot-widget');
        const toggleBtn = document.getElementById('chatbot-toggle');
        if (widget) {
            widget.style.display = this.isOpen ? 'flex' : 'none';
            if (toggleBtn) {
                toggleBtn.setAttribute('aria-expanded', this.isOpen);
            }
            if (this.isOpen) {
                const input = document.getElementById('chatbot-input-field');
                if (input) input.focus();
            }
        }
    }

    close() {
        this.isOpen = false;
        const widget = document.getElementById('chatbot-widget');
        const toggleBtn = document.getElementById('chatbot-toggle');
        if (widget) widget.style.display = 'none';
        if (toggleBtn) toggleBtn.setAttribute('aria-expanded', 'false');
    }

    async sendMessage() {
        const input = document.getElementById('chatbot-input-field');
        const message = input.value.trim();
        if (!message) return;

        this.addMessage(message, 'user');
        input.value = '';
        this.showTyping();

        try {
            const response = await fetch('/api/chatbot/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: JSON.stringify({ 
                    message,
                    language: localStorage.getItem('portal_language') || 'en',
                    language_name: localStorage.getItem('portal_language_name') || 'English'
                })
            });

            this.removeTyping();
            
            const data = await response.json();

            if (response.ok) {
                this.addMessage(data.response, 'bot');
            } else {
                // Display the specific error message from the backend if it exists
                const errorMsg = data.response || 'Sorry, I encountered an error. Please try again.';
                this.addMessage(errorMsg, 'bot');
            }
        } catch (error) {
            this.removeTyping();
            this.addMessage('Connection error. Please check your internet and try again.', 'bot');
        }
    }
    async resetChat() {
        try {
            await fetch('/api/chatbot/reset/', {
                method: 'POST',
                headers: {
                    'X-CSRFToken': this.getCSRFToken(),
                    'Content-Type': 'application/json'
                }
            });

            const container = document.getElementById('chatbot-messages');

            if (container) {
                container.innerHTML = '';
            }

            this.messages = [];

            this.addWelcomeMessage();

        } catch (error) {
            console.error('Reset failed:', error);
        }
    }

    addMessage(text, sender) {
        const container = document.getElementById('chatbot-messages');
        if (!container) return;

        const msgDiv = document.createElement('div');
        msgDiv.className = `message ${sender}`;

        const content = document.createElement('div');
        content.className = 'message-content';
        content.innerHTML = formatChatbotMessage(text);

        msgDiv.appendChild(content);
        container.appendChild(msgDiv);
        container.scrollTop = container.scrollHeight;
    }

    addWelcomeMessage() {
        this.addMessage("Welcome to **CyberSafe AI**! 🛡️\nAsk me about cyber crimes, safety tips, or how to report incidents.", 'bot');
    }

    showTyping() {
        const container = document.getElementById('chatbot-messages');
        if (!container) return;

        const typingDiv = document.createElement('div');
        typingDiv.className = 'message bot';
        typingDiv.id = 'typing-indicator';
        typingDiv.innerHTML = `
            <div class="message-content" style="padding: 12px 20px;">
                <div class="d-flex gap-1">
                    <div class="pulse-dot"></div>
                    <div class="pulse-dot" style="animation-delay: 0.2s;"></div>
                    <div class="pulse-dot" style="animation-delay: 0.4s;"></div>
                </div>
            </div>
        `;
        container.appendChild(typingDiv);
        container.scrollTop = container.scrollHeight;
    }

    removeTyping() {
        const el = document.getElementById('typing-indicator');
        if (el) el.remove();
    }

    getCookie(name) {
        const value = `; ${document.cookie}`;
        const parts = value.split(`; ${name}=`);
        if (parts.length === 2) return parts.pop().split(';').shift();
        return null;
    }
}

function escapeHtml(text) {
    return String(text)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/\"/g, '&quot;')
        .replace(/'/g, '&#39;');
}

function formatChatbotMessage(text) {
    let formatted = escapeHtml(text);

    formatted = formatted.replace(/(https?:\/\/[^\s<]+)/g, function (match) {
        return '<a href="' + match + '" target="_blank" rel="noopener noreferrer" style="color: #2563eb; text-decoration: underline;">' + match + '</a>';
    });

    formatted = formatted.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    formatted = formatted.replace(/\n/g, '<br>');

    return formatted;
}

// Initialize chatbot
document.addEventListener('DOMContentLoaded', function () {
    if (!document.querySelector('.admin-panel')) {
        window.chatbotInstance = new Chatbot();
    }

    const doctorTrigger = document.getElementById("chatbot-trigger-doctor");
    if (doctorTrigger) {
        doctorTrigger.addEventListener("click", function(e) {
            e.preventDefault();
            if (typeof window.openCyberSafeChatbot === 'function') {
                window.openCyberSafeChatbot();
            }
        });
    }
});

// Global access function for templates
window.openCyberSafeChatbot = function () {
    if (window.chatbotInstance) {
        if (!window.chatbotInstance.isOpen) {
            window.chatbotInstance.toggle();
        }
    }
};


/* ============================================================
   CRIME FILTER (existing functionality)
   ============================================================ */
function filterCrimes(category, btn) {
    const cards = document.querySelectorAll('.cyber-card, .crime-card-enhanced, .crime-card, .crime-card-hp');
    const buttons = document.querySelectorAll('.category-filter');

    buttons.forEach(b => b.classList.remove('active'));
    if (btn) btn.classList.add('active');

    cards.forEach(card => {
        const cardCat = card.dataset.category;
        const parent = card.closest('.col-md-6, .col-lg-4, .col-md-4, [class*=col]');
        if (category === 'all' || cardCat === category) {
            if (parent) parent.style.display = '';
            card.style.animation = 'fadeInUp 0.5s ease-out both';
        } else {
            if (parent) parent.style.display = 'none';
        }
    });
}

function incrementClicks(crimeId) {
    if (!crimeId) return;
    fetch('/api/increment-clicks/', {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ crime_id: crimeId }),
        keepalive: true
    }).catch(() => { });
}

function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
    return null;
}
