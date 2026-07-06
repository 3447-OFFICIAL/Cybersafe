document.addEventListener('DOMContentLoaded', () => {
    // Advanced statistics counter animation
    const counters = document.querySelectorAll('.counter');
    counters.forEach(counter => {
        const target = +counter.innerText.replace(/,/g, '');
        const duration = 1800; // 1.8 seconds duration
        const step = target / (duration / 16); // ~60 FPS steps
        
        let current = 0;
        const updateCounter = () => {
            current += step;
            if (current < target) {
                counter.innerText = Math.floor(current).toLocaleString();
                requestAnimationFrame(updateCounter);
            } else {
                counter.innerText = target.toLocaleString();
            }
        };
        
        if (target > 0) {
            updateCounter();
        } else {
            counter.innerText = '0';
        }
    });
});

// Integrated Intelligent Client-Side Search
const searchInput = document.getElementById('intelligent-search');
const searchDropdown = document.getElementById('search-dropdown');
const dynamicGrid = document.getElementById('dynamic-grid');
const emptyState = document.getElementById('empty-state');
const filterBtns = document.querySelectorAll('.btn-filter-neon[data-filter]');
const relatedDomainsPanel = document.getElementById('related-domains-panel');
const relatedDomainsList = document.getElementById('related-domains-list');

let searchTimeout;
let currentFocus = -1;

// Highlight search match
function highlightMatch(text, query) {
    if (!query) return text;
    const escapeRegExp = (string) => string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    const regex = new RegExp(`(${escapeRegExp(query)})`, "gi");
    return text.replace(regex, "<span class='highlight-match'>$1</span>");
}

// Fetch threats from the intelligent TF-IDF API
async function fetchThreats(query = '') {
    try {
        const res = await fetch(`/api/threat-intelligence/search/?q=${encodeURIComponent(query)}`);
        const data = await res.json();
        renderGrid(data.results);
        renderRelatedDomains(data.related_domains);
        
        // Render Dropdown if searching by typing
        if (query && document.activeElement === searchInput) {
            renderDropdown(data.results, query);
        }
    } catch (err) {
        console.error("Error fetching intelligent search results:", err);
    }
}

// Check if we have an active search from Django Request
const urlParams = new URLSearchParams(window.location.search);
const initialQuery = urlParams.get('search') || '';

// Initial load: only fetch if there is a search query in the URL, otherwise we rely on Django's server-side render
if (initialQuery) {
    searchInput.value = initialQuery;
    fetchThreats(initialQuery);
}

// Search Input Event (Debounced)
searchInput.addEventListener('input', (e) => {
    clearTimeout(searchTimeout);
    const query = e.target.value.trim();
    
    // Remove active class from buttons
    filterBtns.forEach(b => b.classList.remove('active'));
    
    if (query.length > 0) {
        searchTimeout = setTimeout(() => fetchThreats(query), 250); // 250ms debounce
    } else {
        searchDropdown.classList.remove('active');
        filterBtns[0].classList.add('active'); // 'All Vectors'
        fetchThreats();
    }
});

// Keyboard Navigation
searchInput.addEventListener('keydown', (e) => {
    let items = searchDropdown.getElementsByClassName('dropdown-item-cyber');
    if (!searchDropdown.classList.contains('active') || items.length === 0) return;
    
    if (e.key === "ArrowDown") {
        currentFocus++;
        addActive(items);
    } else if (e.key === "ArrowUp") {
        currentFocus--;
        addActive(items);
    } else if (e.key === "Enter") {
        e.preventDefault();
        if (currentFocus > -1) {
            items[currentFocus].click();
        } else {
            fetchThreats(searchInput.value);
            searchDropdown.classList.remove('active');
        }
    } else if (e.key === "Tab") {
        if (currentFocus > -1) {
            e.preventDefault();
            items[currentFocus].click();
        } else if (items.length > 0) {
            e.preventDefault();
            items[0].click();
        }
    }
});

function addActive(x) {
    if (!x) return false;
    removeActive(x);
    if (currentFocus >= x.length) currentFocus = 0;
    if (currentFocus < 0) currentFocus = (x.length - 1);
    x[currentFocus].classList.add("selected");
    x[currentFocus].scrollIntoView({ block: 'nearest' });
}

function removeActive(x) {
    for (let i = 0; i < x.length; i++) {
        x[i].classList.remove("selected");
    }
}

// Handle clicks outside dropdown to close it
document.addEventListener('click', (e) => {
    if (!searchInput.contains(e.target) && !searchDropdown.contains(e.target)) {
        searchDropdown.classList.remove('active');
    }
});

searchInput.addEventListener('focus', () => {
    if (searchInput.value.trim().length > 0 && searchDropdown.innerHTML.trim() !== '') {
        searchDropdown.classList.add('active');
    }
});

// Filter Buttons logic
filterBtns.forEach(btn => {
    btn.addEventListener('click', () => {
        filterBtns.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        
        const filterValue = btn.getAttribute('data-filter');
        if (filterValue === 'all') {
            searchInput.value = '';
            fetchThreats();
        } else {
            searchInput.value = filterValue;
            fetchThreats(filterValue);
            searchDropdown.classList.remove('active');
        }
    });
});

function resetSearch() {
    searchInput.value = '';
    filterBtns.forEach(b => b.classList.remove('active'));
    filterBtns[0].classList.add('active');
    searchDropdown.classList.remove('active');
    fetchThreats();
}

function renderDropdown(results, query) {
    searchDropdown.innerHTML = '';
    currentFocus = -1; // Reset focus when dropdown renders
    
    if (results.length === 0) {
        searchDropdown.classList.remove('active');
        return;
    }
    
    // Show up to 7 in dropdown for predictive autocomplete
    const topResults = results.slice(0, 7);
    
    topResults.forEach((crime, index) => {
        const div = document.createElement('div');
        div.className = 'dropdown-item-cyber';
        
        // Remove the score entirely and use highlightMatch
        const highlightedTitle = highlightMatch(crime.type, query);
        
        div.innerHTML = `
            <div>
                <div class="title">${highlightedTitle}</div>
                <div class="threat-tag-mini mt-1">${crime.category}</div>
            </div>
        `;
        
        // Hover updates currentFocus
        div.addEventListener('mouseenter', () => {
            removeActive(searchDropdown.getElementsByClassName('dropdown-item-cyber'));
            currentFocus = index;
            div.classList.add('selected');
        });

        div.onclick = () => {
            searchInput.value = crime.type;
            searchDropdown.classList.remove('active');
            fetchThreats(crime.type); // Execute search
        };
        searchDropdown.appendChild(div);
    });
    
    searchDropdown.classList.add('active');
}

function renderRelatedDomains(domains) {
    relatedDomainsList.innerHTML = '';
    if (!domains || domains.length === 0) {
        relatedDomainsPanel.classList.remove('active');
        return;
    }
    
    domains.forEach(domain => {
        const span = document.createElement('span');
        span.className = 'related-domain-tag';
        span.innerText = domain;
        span.onclick = () => {
            searchInput.value = domain;
            filterBtns.forEach(b => {
                b.classList.remove('active');
                if(b.getAttribute('data-filter') === domain) {
                    b.classList.add('active');
                }
            });
            fetchThreats(domain);
            // Scroll up slightly
            document.querySelector('.search-container-cyber').scrollIntoView({ behavior: 'smooth' });
        };
        relatedDomainsList.appendChild(span);
    });
    
    relatedDomainsPanel.classList.add('active');
}

function renderGrid(results) {
    dynamicGrid.innerHTML = '';
    
    if (results.length === 0) {
        dynamicGrid.style.display = 'none';
        emptyState.style.display = 'block';
        return;
    }
    
    dynamicGrid.style.display = 'grid';
    emptyState.style.display = 'none';
    
    results.forEach(crime => {
        // Process tags and related domains for the "People Also Search" feature
        let tagsHtml = '';
        if (crime.tags && crime.tags.length > 0) {
            tagsHtml = `<div class="mb-3">
                ${crime.tags.slice(0, 3).map(tag => `<span class="threat-tag-mini">${tag}</span>`).join('')}
            </div>`;
        } else if (crime.related_domains && crime.related_domains.length > 0) {
             tagsHtml = `<div class="mb-3">
                ${crime.related_domains.slice(0, 3).map(domain => `<span class="threat-tag-mini">${domain}</span>`).join('')}
            </div>`;
        }
        
        // Prevention tips fallback
        let tipsList = '';
        try {
            // If it's a string from JSON stringify, we need to parse it (sometimes happens with serializers)
            let tips = typeof crime.prevention_tips === 'string' ? JSON.parse(crime.prevention_tips) : crime.prevention_tips;
            
            if (Array.isArray(tips) && tips.length > 0) {
                tips.slice(0,3).forEach(tip => {
                    tipsList += `<li>${tip}</li>`;
                });
            } else {
                tipsList = `<li>Stay alert and protect your personal credentials.</li>`;
            }
        } catch(e) {
            tipsList = `<li>Stay alert and protect your personal credentials.</li>`;
        }
        
        const cardHtml = `
            <div class="crime-card" style="animation: slideDown 0.4s ease forwards;">
                <div class="crime-top">
                    <span class="crime-category">${crime.category || 'Threat'}</span>
                    <span class="level ${crime.severity ? crime.severity.toLowerCase() : 'low'}">${crime.severity ? crime.severity.toUpperCase() : 'UNKNOWN'}</span>
                </div>

                <h3>${crime.type}</h3>
                
                <div class="card-scroll-area">
                    ${tagsHtml}

                    <p class="crime-desc">
                        ${crime.description ? crime.description : ''}
                    </p>

                    <div class="info-box">
                        <h4>COMMON INDICATORS</h4>
                        <ul>
                            ${tipsList}
                        </ul>
                    </div>
                </div>

                <div class="d-flex justify-content-between align-items-center mt-auto pt-3" style="border-top: 1px solid rgba(255, 255, 255, 0.05);">
                    <span class="small text-secondary" style="font-size: 0.85rem;">
                        <i class="fas fa-eye me-1"></i> ${crime.learn_more_clicks || '0'} views
                    </span>
                    <a href="/crime/${crime.id}/" class="details-btn" style="font-size: 0.9rem;">
                        Details →
                    </a>
                </div>
            </div>
        `;
        dynamicGrid.insertAdjacentHTML('beforeend', cardHtml);
    });
}
