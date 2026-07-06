/**
 * ══════════════════════════════════════════════════════════
 *   ANTIGRAVITY PREMIUM ADAPTIVE ACCESSIBILITY ENGINE
 *   Comprehensive Accessibility Suite v3.0
 *   Supports: Senior Mode, CVD (Color Blindness)
 * ══════════════════════════════════════════════════════════
 */

(function() {
    'use strict';

    const CONFIG = {
        storage: {
            senior: 'premium_senior_mode',
            cvd: 'premium_cvd_mode',
            textSize: 'premium_text_size'
        },
        classes: {
            senior: 'senior-mode'
        },
        utteranceRate: 0.85,
        utterancePitch: 1.05
    };

    let state = {
        isSeniorMode: localStorage.getItem(CONFIG.storage.senior) === 'true',
        cvdMode: localStorage.getItem(CONFIG.storage.cvd) || 'none',
        textSize: localStorage.getItem(CONFIG.storage.textSize) || 'normal',
        isReading: false,
        isPanelOpen: false
    };

    /**
     * 1. State Management
     */
    function updateState(key, value) {
        state[key] = value;
        
        // Persist
        if (key === 'isSeniorMode') localStorage.setItem(CONFIG.storage.senior, value);
        if (key === 'cvdMode') localStorage.setItem(CONFIG.storage.cvd, value);
        if (key === 'textSize') localStorage.setItem(CONFIG.storage.textSize, value);

        applyAllStates();
        syncUIControls();

        // Announce change to screen readers
        const announcer = document.getElementById('acc-status-announcer');
        if (announcer) {
            let msg = '';
            if (key === 'isSeniorMode') msg = value ? 'Senior friendly mode activated.' : 'Senior friendly mode deactivated.';
            else if (key === 'textSize') msg = 'Text size updated.';
            else if (key === 'cvdMode') msg = 'Color vision settings updated.';
            announcer.textContent = msg;
        }
    }

    function applyAllStates() {
        const root = document.documentElement;
        
        // Senior Mode
        root.classList.toggle(CONFIG.classes.senior, state.isSeniorMode);
        document.body.classList.toggle(CONFIG.classes.senior, state.isSeniorMode); // Keep on body for legacy support
        
        // Force hide map tooltip when entering senior mode
        if (state.isSeniorMode) {
            const tooltip = document.getElementById('tooltip');
            if (tooltip) {
                tooltip.classList.remove('visible');
                tooltip.style.display = 'none';
                tooltip.style.opacity = '0';
                tooltip.style.visibility = 'hidden';
            }
        }
        
        // CVD Modes
        const cvdClasses = ['mode-none', 'mode-protanopia', 'mode-deuteranopia', 'mode-tritanopia'];
        root.classList.remove(...cvdClasses);
        document.body.classList.remove(...cvdClasses);
        
        const targetClass = `mode-${state.cvdMode}`;
        root.classList.add(targetClass);
        document.body.classList.add(targetClass);

        // Text Size
        root.classList.remove('ts-xsmall', 'ts-small', 'ts-normal', 'ts-large', 'ts-xlarge');
        root.classList.add(`ts-${state.textSize}`);

        // Widget Trigger Style
        const trigger = document.getElementById('acc-trigger');
        if (trigger) {
            if (state.isSeniorMode || state.cvdMode !== 'none') {
                trigger.classList.add('active-active');
                trigger.style.background = '#FFC107';
                trigger.style.color = '#000';
            } else {
                trigger.classList.remove('active-active');
                trigger.style.background = '';
                trigger.style.color = '';
            }
        }
    }

    /**
     * 2. UI Construction
     */
    function createWidget() {
        if (document.getElementById('acc-premium-widget')) return;

        const widget = document.createElement('div');
        widget.id = 'acc-premium-widget';
        widget.innerHTML = `
            <div class="acc-panel" id="acc-panel">
                <div class="acc-header">
                    <h4><i class="fas fa-universal-access me-2"></i>Accessibility Center</h4>
                </div>
                
                <div id="acc-status-announcer" aria-live="polite" style="position: absolute; width: 1px; height: 1px; overflow: hidden; clip: rect(0, 0, 0, 0);"></div>

                <div class="acc-onboarding" style="background:#eef2ff; border-left:4px solid #4f46e5; padding:10px; margin-bottom: 0; border-radius:4px; font-size:12px; color:#333;">
                    <strong>Welcome!</strong> Use these tools to make the website easier to read. Turn on "Senior Friendly" for larger text and simplified menus.
                </div>
                
                <!-- Senior Mode -->
                <div class="acc-section">
                    <div class="acc-option">
                        <div class="acc-info">
                            <span class="acc-label">Senior Friendly</span>
                            <small>Larger text, thick scrollbars</small>
                        </div>
                        <label class="acc-switch">
                            <input type="checkbox" id="senior-mode-checkbox" ${state.isSeniorMode ? 'checked' : ''} autocomplete="off">
                            <span class="acc-slider"></span>
                        </label>
                    </div>
                </div>

                <!-- Color Vision Deficiency -->
                <div class="acc-section">
                    <span class="acc-section-title">Color Vision Assistance</span>
                    <select class="acc-select" id="cvd-mode-select" autocomplete="off">
                        <option value="none" ${state.cvdMode === 'none' ? 'selected' : ''}>Standard Vision</option>
                        <option value="protanopia" ${state.cvdMode === 'protanopia' ? 'selected' : ''}>Protanopia (Red-Blind)</option>
                        <option value="deuteranopia" ${state.cvdMode === 'deuteranopia' ? 'selected' : ''}>Deuteranopia (Green-Blind)</option>
                        <option value="tritanopia" ${state.cvdMode === 'tritanopia' ? 'selected' : ''}>Tritanopia (Blue-Blind)</option>
                    </select>
                </div>

                <!-- Text Size -->
                <div class="acc-section">
                    <span class="acc-section-title">Text Size Adjustment</span>
                    <select class="acc-select" id="text-size-select" autocomplete="off">
                        <option value="xsmall" ${state.textSize === 'xsmall' ? 'selected' : ''}>Extra Small (70%)</option>
                        <option value="small" ${state.textSize === 'small' ? 'selected' : ''}>Smaller (85%)</option>
                        <option value="normal" ${state.textSize === 'normal' ? 'selected' : ''}>Default Size</option>
                        <option value="large" ${state.textSize === 'large' ? 'selected' : ''}>Large (120%)</option>
                        <option value="xlarge" ${state.textSize === 'xlarge' ? 'selected' : ''}>Extra Large (150%)</option>
                    </select>
                </div>

                <!-- Voice Reader -->
                <div class="acc-section no-border">
                    <button class="acc-action-btn" id="read-page-btn">
                        <i class="fas fa-volume-up"></i>
                        <span>Read Page Content</span>
                    </button>
                </div>

                <div class="acc-footer">
                    Adaptive Intelligence Enabled
                </div>
            </div>

            <button class="acc-main-trigger" id="acc-trigger" title="Accessibility Options" aria-label="Accessibility Options" aria-expanded="false" aria-controls="acc-panel">
                <i class="fas fa-universal-access" aria-hidden="true"></i>
            </button>
        `;

        document.body.appendChild(widget);
        
        // Add Widget Styles
        injectWidgetStyles();
        attachEventListeners();
    }

    function injectWidgetStyles() {
        if (document.getElementById('acc-widget-extra-styles')) return;
        const style = document.createElement('style');
        style.id = 'acc-widget-extra-styles';
        style.textContent = `
            .acc-section { padding: 8px 0; border-bottom: 1px solid #e2e8f0; }
            .acc-section-title { display: block; font-size: 11px; font-weight: 700; color: #94a3b8; text-transform: uppercase; margin-bottom: 8px; letter-spacing: 0.5px; }
            .acc-info { display: flex; flex-direction: column; }
            .acc-info small { font-size: 10px; color: #64748b; line-height: 1.2; }
            .acc-select { width: 100%; padding: 8px; border-radius: 8px; border: 1px solid #cbd5e1; background: #fff; font-size: 13px; color: #1e293b; cursor: pointer; outline: none; }
            .acc-select:focus { border-color: #3b82f6; box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.1); }
            .acc-footer { font-size: 10px; color: #94a3b8; text-align: center; margin-top: 0; font-style: italic; }
            .acc-action-btn.playing { background: #ef4444 !important; color: white !important; }
            .no-border { border-bottom: none !important; padding-bottom: 0 !important; }
        `;
        document.head.appendChild(style);
    }

    /**
     * 3. Event Handling
     */
    function attachEventListeners() {
        const trigger = document.getElementById('acc-trigger');
        const panel = document.getElementById('acc-panel');
        const seniorCheck = document.getElementById('senior-mode-checkbox');
        const cvdSelect = document.getElementById('cvd-mode-select');
        const textSizeSelect = document.getElementById('text-size-select');
        const readBtn = document.getElementById('read-page-btn');

        // Toggle Panel
        trigger.addEventListener('click', () => {
            state.isPanelOpen = !state.isPanelOpen;
            panel.classList.toggle('show', state.isPanelOpen);
            trigger.classList.toggle('panel-open', state.isPanelOpen);
            trigger.setAttribute('aria-expanded', state.isPanelOpen);
        });

        // Close outside
        document.addEventListener('click', (e) => {
            if (!document.getElementById('acc-premium-widget').contains(e.target) && state.isPanelOpen) {
                state.isPanelOpen = false;
                panel.classList.remove('show');
                trigger.classList.remove('panel-open');
                trigger.setAttribute('aria-expanded', 'false');
            }
        });

        // Mode Listeners
        seniorCheck.addEventListener('change', (e) => updateState('isSeniorMode', e.target.checked));
        cvdSelect.addEventListener('change', (e) => updateState('cvdMode', e.target.value));
        textSizeSelect.addEventListener('change', (e) => updateState('textSize', e.target.value));

        // Reader
        readBtn.addEventListener('click', toggleReading);
    }

    function syncUIControls() {
        const seniorCheck = document.getElementById('senior-mode-checkbox');
        const cvdSelect = document.getElementById('cvd-mode-select');
        const textSizeSelect = document.getElementById('text-size-select');
        
        if (seniorCheck) seniorCheck.checked = state.isSeniorMode;
        if (cvdSelect) cvdSelect.value = state.cvdMode;
        if (textSizeSelect) textSizeSelect.value = state.textSize;

        // External buttons (if any)
        document.querySelectorAll('[data-senior-toggle]').forEach((button) => {
            button.classList.toggle('active', state.isSeniorMode);
            button.innerHTML = state.isSeniorMode
                ? '<i class="fas fa-universal-access me-2"></i>Exit Senior Mode'
                : '<i class="fas fa-universal-access me-2"></i>Senior Mode';
        });
    }

    /**
     * 4. Smart Reader Logic
     */
    function toggleReading() {
        if (window.speechSynthesis.speaking) {
            window.speechSynthesis.cancel();
            updateReadButtonUI(false);
            return;
        }

        const selectors = 'h1, h2, h3, p, .card-title, .nav-link.active, .tile-title, .tile-sub, .alert, .badge, .impact-text, .crime-desc, .module-title';
        const elements = document.querySelectorAll(selectors);
        let textSegments = [];

        elements.forEach(el => {
            if (el.offsetParent !== null && el.innerText.trim().length > 0) {
                if (!el.closest('#acc-premium-widget')) {
                    textSegments.push(el.innerText.trim());
                }
            }
        });

        if (textSegments.length === 0) return;

        const utterance = new SpeechSynthesisUtterance(textSegments.join('. '));
        utterance.rate = CONFIG.utteranceRate;
        utterance.pitch = CONFIG.utterancePitch;
        utterance.lang = document.documentElement.lang || 'en-US';

        utterance.onstart = () => updateReadButtonUI(true);
        utterance.onend = () => updateReadButtonUI(false);
        utterance.onerror = () => updateReadButtonUI(false);

        window.speechSynthesis.speak(utterance);
    }

    function updateReadButtonUI(isPlaying) {
        const btn = document.getElementById('read-page-btn');
        if (!btn) return;
        btn.classList.toggle('playing', isPlaying);
        btn.innerHTML = isPlaying 
            ? '<i class="fas fa-stop"></i> <span>Stop Reading</span>' 
            : '<i class="fas fa-volume-up"></i> <span>Read Page Content</span>';
    }

    /**
     * 5. Initialize
     */
    function init() {
        createWidget();
        applyAllStates();
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

})();
