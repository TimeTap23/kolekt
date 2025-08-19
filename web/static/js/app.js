// ThreadStorm Application JavaScript

// Global variables
let currentCharacterCount = 0;
let isSpamDetected = false;
let spamIndicators = [];
let qualityScore = 100;

// Immediately available global functions for HTML onclick handlers
window.openThreadsFormatter = function() {
    console.log('openThreadsFormatter called');
    if (window.kolektApp) {
        console.log('Calling kolektApp.openThreadsFormatter()');
        window.kolektApp.openThreadsFormatter();
    } else {
        console.error('kolektApp not found!');
        // Fallback: try to initialize the app
        if (typeof KolektApp !== 'undefined') {
            window.kolektApp = new KolektApp();
            window.kolektApp.openThreadsFormatter();
        }
    }
};

window.openTemplateLibrary = function() {
    console.log('openTemplateLibrary called');
    if (window.kolektApp) {
        console.log('Calling kolektApp.openTemplateLibrary()');
        window.kolektApp.openTemplateLibrary();
    } else {
        console.error('kolektApp not found!');
        // Fallback: try to initialize the app
        if (typeof KolektApp !== 'undefined') {
            window.kolektApp = new KolektApp();
            window.kolektApp.openTemplateLibrary();
        }
    }
};

window.openAnalytics = function() {
    console.log('openAnalytics called');
    if (window.kolektApp) {
        console.log('Calling kolektApp.openAnalytics()');
        window.kolektApp.openAnalytics();
    } else {
        console.error('kolektApp not found!');
        // Fallback: try to initialize the app
        if (typeof KolektApp !== 'undefined') {
            window.kolektApp = new KolektApp();
            window.kolektApp.openAnalytics();
        }
    }
};

window.openCarouselCreator = function() {
    console.log('openCarouselCreator called');
    if (window.kolektApp) {
        console.log('Calling kolektApp.openCarouselCreator()');
        window.kolektApp.openCarouselCreator();
    } else {
        console.error('kolektApp not found!');
        // Fallback: try to initialize the app
        if (typeof KolektApp !== 'undefined') {
            window.kolektApp = new KolektApp();
            window.kolektApp.openCarouselCreator();
        }
    }
};

console.log('Kolekt functions loaded and available globally');

function showModal(title, content) {
    const modal = document.getElementById('modal');
    const modalBody = document.querySelector('#modal .modal-body');
    
    if (modal && modalBody) {
        modalBody.innerHTML = content;
        modal.classList.add('show');
        
        // Add click outside to close
        modal.onclick = function(event) {
            if (event.target === modal) {
                closeModal();
            }
        };
    }
}

function closeModal() {
    const modal = document.getElementById('modal');
    if (modal) {
        modal.classList.remove('show');
    }
}

class KolektApp {
    constructor() {
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.initializeAnimations();
        this.setupAPIEndpoints();
        this.loadInitialData();
    }

    setupEventListeners() {
        // Quick action buttons
        document.querySelectorAll('.bg-white.rounded-xl.shadow-md').forEach(card => {
            card.addEventListener('click', (e) => {
                this.handleQuickAction(e);
            });
        });

        // New Thread button - find by text content
        const buttons = document.querySelectorAll('button');
        buttons.forEach(btn => {
            if (btn.textContent.includes('New Thread')) {
                btn.addEventListener('click', () => {
                    this.openThreadCreator();
                });
            }
        });

        // Thread action buttons
        document.querySelectorAll('.text-blue-600, .text-green-600').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.stopPropagation();
                this.handleThreadAction(e);
            });
        });

        // Search functionality
        this.setupSearch();
    }

    initializeAnimations() {
        // Add animation classes to elements
        const animatedElements = document.querySelectorAll('.bg-white.rounded-xl');
        animatedElements.forEach((el, index) => {
            el.classList.add('animate-fade-in-up');
            el.style.animationDelay = `${index * 0.1}s`;
        });

        // Add hover effects
        document.querySelectorAll('.card').forEach(card => {
            card.classList.add('shadow-hover');
        });
    }

    setupAPIEndpoints() {
        this.api = {
            baseUrl: '/api/v1',
            endpoints: {
                threads: '/threads',
                content: '/content',
                research: '/research',
                users: '/users',
                auth: '/auth'
            }
        };
    }

    async loadInitialData() {
        try {
            // Load recent threads
            await this.loadRecentThreads();
            
            // Load user stats
            await this.loadUserStats();
            
        } catch (error) {
            console.error('Error loading initial data:', error);
            this.showNotification('Error loading data', 'error');
        }
    }

    async loadRecentThreads() {
        // TODO: Implement when threads functionality is added
        console.log('Recent threads loading disabled - endpoint not implemented yet');
    }

    async loadUserStats() {
        // TODO: Implement when user stats functionality is added
        console.log('User stats loading disabled - endpoint not implemented yet');
    }

    updateRecentThreads(threads) {
        const container = document.getElementById('recent-threads');
        if (!container) return;
        
        container.innerHTML = '';
        threads.forEach(thread => {
            const threadElement = document.createElement('div');
            threadElement.className = 'thread-item';
            threadElement.innerHTML = `
                <h4>${thread.title}</h4>
                <p>${thread.excerpt}</p>
                <div class="thread-meta">
                    <span>${thread.created_at}</span>
                    <span>${thread.engagement}% engagement</span>
                </div>
            `;
            container.appendChild(threadElement);
        });
    }

    updateUserStats(stats) {
        const statsContainer = document.getElementById('user-stats');
        if (!statsContainer) return;
        
        statsContainer.innerHTML = `
            <div class="stat-item">
                <span class="stat-number">${stats.total_threads}</span>
                <span class="stat-label">Total Threads</span>
            </div>
            <div class="stat-item">
                <span class="stat-number">${stats.avg_engagement}%</span>
                <span class="stat-label">Avg Engagement</span>
            </div>
            <div class="stat-item">
                <span class="stat-number">${stats.monthly_posts}</span>
                <span class="stat-label">This Month</span>
            </div>
        `;
    }

    setupSearch() {
        const searchInput = document.getElementById('search-input');
        if (searchInput) {
            searchInput.addEventListener('input', (e) => {
                this.performSearch(e.target.value);
            });
        }
    }

    performSearch(query) {
        // Implement search functionality
        console.log('Searching for:', query);
    }

    handleQuickAction(event) {
        const action = event.currentTarget.dataset.action;
        switch (action) {
            case 'formatter':
                this.openThreadsFormatter();
                break;
            case 'templates':
                this.openTemplateLibrary();
                break;
            case 'analytics':
                this.openAnalytics();
                break;
            default:
                console.log('Unknown action:', action);
        }
    }

    handleThreadAction(event) {
        const action = event.currentTarget.dataset.action;
        const threadId = event.currentTarget.dataset.threadId;
        
        switch (action) {
            case 'edit':
                this.editThread(threadId);
                break;
            case 'delete':
                this.deleteThread(threadId);
                break;
            case 'publish':
                this.publishThread(threadId);
                break;
            default:
                console.log('Unknown thread action:', action);
        }
    }

    openThreadCreator() {
        this.showModal('Create New Thread', `
            <div class="thread-creator">
                <h3>Create New Thread</h3>
                <form id="thread-form">
                    <div class="form-group">
                        <label>Title</label>
                        <input type="text" id="thread-title" required>
                    </div>
                    <div class="form-group">
                        <label>Content</label>
                        <textarea id="thread-content" rows="6" required></textarea>
                    </div>
                    <div class="form-actions">
                        <button type="submit" class="btn btn-primary">Create Thread</button>
                        <button type="button" class="btn btn-secondary" onclick="closeModal()">Cancel</button>
                    </div>
                </form>
            </div>
        `);
    }

    editThread(threadId) {
        console.log('Editing thread:', threadId);
        this.showNotification('Edit functionality coming soon!', 'info');
    }

    deleteThread(threadId) {
        if (confirm('Are you sure you want to delete this thread?')) {
            console.log('Deleting thread:', threadId);
            this.showNotification('Thread deleted successfully!', 'success');
        }
    }

    publishThread(threadId) {
        console.log('Publishing thread:', threadId);
        this.showNotification('Thread published successfully!', 'success');
    }

    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.textContent = message;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.remove();
        }, 3000);
    }

    showModal(title, content) {
        const modal = document.getElementById('modal');
        const modalBody = document.querySelector('#modal .modal-body');
        
        if (modal && modalBody) {
            modalBody.innerHTML = content;
            modal.classList.add('show');
            
            // Add click outside to close
            modal.onclick = function(event) {
                if (event.target === modal) {
                    closeModal();
                }
            };
        }
    }

    openThreadsFormatter() {
        console.log('KolektApp.openThreadsFormatter() called');
        this.showModal(`
            <div class="bg-white rounded-lg p-6 max-w-6xl w-full">
                <h3 class="text-xl font-semibold mb-4">Threads App Formatter</h3>
                <p class="text-gray-600 mb-6">Transform your long-form content into engaging Threads posts (500 character limit)</p>
                
                <form id="threadsFormatterForm">
                    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
                        <!-- Input Section -->
                        <div class="lg:col-span-1">
                            <div class="space-y-4">
                                <div>
                                    <label class="block text-sm font-medium text-gray-700 mb-2">Your Content</label>
                                    <div class="relative">
                                        <textarea id="threadsContent" class="textarea-field" rows="12" placeholder="Paste your long-form content here..."></textarea>
                                        <div class="absolute bottom-2 right-2 text-xs text-gray-500">
                                            <span id="contentCharCount">0</span> chars
                                        </div>
                                    </div>
                                    <div class="mt-2">
                                        <div class="w-full bg-gray-200 rounded-full h-2">
                                            <div id="contentProgress" class="bg-blue-600 h-2 rounded-full transition-all duration-300" style="width: 0%"></div>
                                        </div>
                                        <div class="flex justify-between text-xs text-gray-500 mt-1">
                                            <span>0</span>
                                            <span>500</span>
                                            <span>1000</span>
                                        </div>
                                    </div>
                                    <p class="text-xs text-gray-500 mt-1">We'll break this into optimal 200-300 character posts</p>
                                </div>
                                
                                <div>
                                    <label class="block text-sm font-medium text-gray-700 mb-2">Images (Optional)</label>
                                    <textarea id="threadsImages" class="textarea-field" rows="3" placeholder="Describe your images or paste URLs, one per line"></textarea>
                                    <p class="text-xs text-gray-500 mt-1">Leave content empty to produce images-only posts with correctly placed numbering</p>
                                </div>
                                
                                <div>
                                    <label class="block text-sm font-medium text-gray-700 mb-2">Tone</label>
                                    <select id="threadsTone" class="input-field">
                                        <option value="professional">Professional</option>
                                        <option value="casual">Casual</option>
                                        <option value="educational">Educational</option>
                                        <option value="conversational">Conversational</option>
                                    </select>
                                </div>
                                
                                <div class="flex items-center">
                                    <input type="checkbox" id="includeNumbering" class="rounded border-gray-300" checked>
                                    <label for="includeNumbering" class="ml-2 text-sm text-gray-700">Include thread numbering (1/n, 2/n)</label>
                                </div>
                                
                                <div class="bg-blue-50 p-4 rounded-lg">
                                    <h4 class="font-medium text-blue-900 mb-2">Threads App Guidelines</h4>
                                    <ul class="text-sm text-blue-800 space-y-1">
                                        <li>• Maximum 500 characters per post (including numbering)</li>
                                        <li>• Optimal: 200-300 characters for readability</li>
                                        <li>• Each post should be self-contained</li>
                                        <li>• Start with a compelling hook</li>
                                        <li>• End with a strong conclusion</li>
                                    </ul>
                                </div>
                            </div>
                        </div>
                        
                        <!-- Live Preview Section -->
                        <div class="lg:col-span-2">
                            <div class="bg-gray-50 p-4 rounded-lg h-full">
                                <h4 class="font-medium text-gray-900 mb-4">Live Preview</h4>
                                <div id="livePreview" class="space-y-4 max-h-96 overflow-y-auto">
                                    <div class="text-center text-gray-500 py-8">
                                        <i class="fas fa-eye text-2xl mb-2"></i>
                                        <p>Start typing to see live preview</p>
                                    </div>
                                </div>
                                
                                <!-- Preview Stats -->
                                <div class="mt-4 grid grid-cols-3 gap-4 text-center">
                                    <div class="bg-white p-3 rounded-lg">
                                        <div class="text-lg font-semibold text-blue-600" id="previewPostCount">0</div>
                                        <div class="text-xs text-gray-600">Posts</div>
                                    </div>
                                    <div class="bg-white p-3 rounded-lg">
                                        <div class="text-lg font-semibold text-green-600" id="previewAvgLength">0</div>
                                        <div class="text-xs text-gray-600">Avg Length</div>
                                    </div>
                                    <div class="bg-white p-3 rounded-lg">
                                        <div class="text-lg font-semibold text-purple-600" id="previewEngagement">0%</div>
                                        <div class="text-xs text-gray-600">Engagement</div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <div class="flex justify-between items-center mt-6">
                        <div id="threadsFormatterStatus" class="text-sm text-gray-600"></div>
                        <div class="space-x-3">
                            <button type="button" class="btn-secondary" onclick="closeModal()">Cancel</button>
                            <button type="submit" class="btn-primary">
                                <i class="fas fa-magic mr-2"></i>Format for Threads
                            </button>
                        </div>
                    </div>
                </form>

                <div id="threadsFormatterResult" class="mt-8 hidden">
                    <h4 class="text-lg font-semibold mb-3">Formatted Output</h4>
                    <div class="flex justify-between items-center mb-3">
                        <div class="text-sm text-gray-600">Copy-ready output with image placement notes</div>
                        <div class="space-x-2">
                            <button onclick="this.copyToClipboard()" class="btn-secondary text-sm">
                                <i class="fas fa-copy mr-1"></i>Copy All
                            </button>
                            <button onclick="this.openThreadsPublish()" class="btn-success text-sm">
                                <i class="fas fa-paper-plane mr-1"></i>Post to Threads
                            </button>
                        </div>
                    </div>
                    <pre class="bg-gray-50 p-4 rounded-lg overflow-auto text-sm" id="threadsRendered"></pre>

                    <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mt-6">
                        <div class="bg-white border rounded-lg p-4">
                            <h5 class="font-medium mb-2">Posts</h5>
                            <div id="threadsPosts" class="space-y-3"></div>
                        </div>
                        <div class="bg-white border rounded-lg p-4">
                            <h5 class="font-medium mb-2">Suggestions</h5>
                            <ul id="threadsSuggestions" class="list-disc list-inside text-sm text-gray-700 space-y-1"></ul>
                            <div class="mt-3 text-sm text-gray-600">Engagement score: <span id="threadsScore">-</span></div>
                        </div>
                    </div>
                </div>
            </div>
        `);

        // Set up real-time character counter and preview
        this.setupRealTimePreview();
        
        const form = document.getElementById('threadsFormatterForm');
        const statusEl = document.getElementById('threadsFormatterStatus');
        const resultEl = document.getElementById('threadsFormatterResult');
        const renderedEl = document.getElementById('threadsRendered');
        const postsEl = document.getElementById('threadsPosts');
        const suggestionsEl = document.getElementById('threadsSuggestions');
        const scoreEl = document.getElementById('threadsScore');

        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            const content = document.getElementById('threadsContent').value.trim();
            const tone = document.getElementById('threadsTone').value;
            const includeNumbering = document.getElementById('includeNumbering').checked;
            const imagesRaw = document.getElementById('threadsImages').value.trim();
            const images = imagesRaw ? imagesRaw.split('\n').map(s => s.trim()).filter(Boolean) : [];

            statusEl.textContent = 'Formatting...';
            resultEl.classList.add('hidden');

            try {
                const resp = await fetch(`${this.api.baseUrl}/format`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ content: content || null, images, tone, include_numbering: includeNumbering })
                });
                if (!resp.ok) throw new Error('Request failed');
                const data = await resp.json();

                // Rendered block
                renderedEl.textContent = data.rendered_output;

                // Posts list
                postsEl.innerHTML = '';
                data.posts.forEach(p => {
                    const div = document.createElement('div');
                    div.className = 'border rounded p-3';
                    div.innerHTML = `
                        <div class="flex justify-between text-sm text-gray-600 mb-2">
                            <span>Post ${p.post_number}/${p.total_posts}</span>
                            <span>${p.character_count}/500</span>
                        </div>
                        <div class="whitespace-pre-wrap text-gray-900">${this.escapeHtml(p.content)}</div>
                        ${p.image_suggestion ? `<div class="mt-2 text-xs text-indigo-700">[Attach here] ${this.escapeHtml(p.image_suggestion)}</div>` : ''}
                    `;
                    postsEl.appendChild(div);
                });

                // Suggestions
                suggestionsEl.innerHTML = '';
                (data.suggestions || []).forEach(s => {
                    const li = document.createElement('li');
                    li.textContent = s;
                    suggestionsEl.appendChild(li);
                });

                // Score
                scoreEl.textContent = data.engagement_score || 'N/A';

                // Show result
                resultEl.classList.remove('hidden');
                statusEl.textContent = 'Formatting complete!';

            } catch (error) {
                console.error('Formatting error:', error);
                statusEl.textContent = 'Formatting failed. Please try again.';
            }
        });
    }

    setupRealTimePreview() {
        const contentArea = document.getElementById('threadsContent');
        const charCount = document.getElementById('contentCharCount');
        const progress = document.getElementById('contentProgress');
        const preview = document.getElementById('livePreview');
        const postCount = document.getElementById('previewPostCount');
        const avgLength = document.getElementById('previewAvgLength');
        const engagement = document.getElementById('previewEngagement');

        if (contentArea) {
            contentArea.addEventListener('input', () => {
                const content = contentArea.value;
                const charCountValue = content.length;
                
                // Update character count
                if (charCount) charCount.textContent = charCountValue;
                
                // Update progress bar
                if (progress) {
                    const percentage = Math.min((charCountValue / 1000) * 100, 100);
                    progress.style.width = `${percentage}%`;
                }
                
                // Update preview stats
                if (content.length > 0) {
                    const estimatedPosts = Math.ceil(content.length / 250);
                    const avgPostLength = Math.round(content.length / estimatedPosts);
                    const estimatedEngagement = Math.max(85 - (estimatedPosts * 2), 60);
                    
                    if (postCount) postCount.textContent = estimatedPosts;
                    if (avgLength) avgLength.textContent = avgPostLength;
                    if (engagement) engagement.textContent = `${estimatedEngagement}%`;
                    
                    // Update preview content
                    if (preview) {
                        preview.innerHTML = this.generatePreviewContent(content);
                    }
                } else {
                    if (postCount) postCount.textContent = '0';
                    if (avgLength) avgLength.textContent = '0';
                    if (engagement) engagement.textContent = '0%';
                    if (preview) {
                        preview.innerHTML = `
                            <div class="text-center text-gray-500 py-8">
                                <i class="fas fa-eye text-2xl mb-2"></i>
                                <p>Start typing to see live preview</p>
                            </div>
                        `;
                    }
                }
            });
        }
    }

    generatePreviewContent(content) {
        const words = content.split(' ');
        const posts = [];
        let currentPost = '';
        let postNumber = 1;
        
        for (let word of words) {
            if ((currentPost + word).length > 250) {
                posts.push(currentPost.trim());
                currentPost = word + ' ';
                postNumber++;
            } else {
                currentPost += word + ' ';
            }
        }
        
        if (currentPost.trim()) {
            posts.push(currentPost.trim());
        }
        
        return posts.map((post, index) => `
            <div class="bg-white p-4 rounded-lg shadow-sm border">
                <div class="flex items-start space-x-3">
                    <div class="w-10 h-10 bg-gradient-to-r from-purple-400 to-pink-400 rounded-full flex items-center justify-center text-white font-bold">
                        T
                    </div>
                    <div class="flex-1">
                        <div class="flex items-center space-x-2 mb-2">
                            <span class="font-semibold text-gray-900">Your Username</span>
                            <span class="text-gray-500 text-sm">• 2h</span>
                        </div>
                        <p class="text-gray-900 mb-3">${post}</p>
                        <div class="flex items-center justify-between text-gray-500 text-sm">
                            <div class="flex items-center space-x-4">
                                <span>❤️ 24</span>
                                <span>💬 8</span>
                                <span>🔄 3</span>
                            </div>
                            <span>${index + 1}/${posts.length}</span>
                        </div>
                    </div>
                </div>
            </div>
        `).join('');
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    openTemplateLibrary() {
        console.log('KolektApp.openTemplateLibrary() called');
        this.showModal(`
            <div class="bg-white rounded-lg p-6 max-w-6xl w-full">
                <h3 class="text-xl font-semibold mb-4">Template Library</h3>
                <p class="text-gray-600 mb-6">Choose from pre-built templates to jumpstart your Threads content</p>
                
                <!-- Search and Filter -->
                <div class="flex flex-col sm:flex-row gap-4 mb-6">
                    <div class="flex-1">
                        <input type="text" id="templateSearch" class="input-field" placeholder="Search templates...">
                    </div>
                    <select id="templateCategory" class="input-field w-full sm:w-48">
                        <option value="">All Categories</option>
                    </select>
                </div>
                
                <!-- Categories -->
                <div class="mb-6">
                    <h4 class="font-medium text-gray-900 mb-3">Categories</h4>
                    <div id="templateCategories" class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
                        <!-- Categories will be loaded here -->
                    </div>
                </div>
                
                <!-- Featured Templates -->
                <div class="mb-6">
                    <h4 class="font-medium text-gray-900 mb-3">Featured Templates</h4>
                    <div id="featuredTemplates" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                        <!-- Featured templates will be loaded here -->
                    </div>
                </div>
                
                <!-- All Templates -->
                <div>
                    <h4 class="font-medium text-gray-900 mb-3">All Templates</h4>
                    <div id="allTemplates" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                        <!-- All templates will be loaded here -->
                    </div>
                </div>
                
                <div class="flex justify-end mt-6">
                    <button class="btn-secondary" onclick="closeModal()">Close</button>
                </div>
            </div>
        `);

        // Load template data
        this.loadTemplateLibrary();
    }

    loadTemplateLibrary() {
        // Simulate loading templates
        const templates = [
            {
                id: 1,
                title: 'Product Launch',
                category: 'Marketing',
                description: 'Perfect for announcing new products or features',
                content: '🚀 Exciting news! We\'re launching something amazing...'
            },
            {
                id: 2,
                title: 'Educational Thread',
                category: 'Education',
                description: 'Share knowledge and insights with your audience',
                content: '📚 Let\'s dive into this fascinating topic...'
            },
            {
                id: 3,
                title: 'Behind the Scenes',
                category: 'Personal',
                description: 'Show the human side of your brand',
                content: '👥 Ever wondered what goes on behind the scenes...'
            }
        ];

        this.renderTemplates(templates);
    }

    renderTemplates(templates) {
        const container = document.getElementById('featuredTemplates');
        if (!container) return;

        container.innerHTML = templates.map(template => `
            <div class="bg-white border rounded-lg p-4 hover:shadow-md transition-shadow">
                <h5 class="font-medium text-gray-900 mb-2">${template.title}</h5>
                <p class="text-sm text-gray-600 mb-3">${template.description}</p>
                <div class="text-xs text-gray-500 mb-3">${template.content.substring(0, 100)}...</div>
                <button class="btn-primary text-sm" onclick="this.useTemplate(${template.id})">
                    Use Template
                </button>
            </div>
        `).join('');
    }

    useTemplate(templateId) {
        console.log('Using template:', templateId);
        this.showNotification('Template loaded!', 'success');
        closeModal();
    }

    openAnalytics() {
        console.log('KolektApp.openAnalytics() called');
        this.showModal(`
            <div class="bg-white rounded-lg p-6 max-w-6xl w-full">
                <h3 class="text-xl font-semibold mb-4">📊 Analytics Dashboard</h3>
                <p class="text-gray-600 mb-6">Track your content performance and engagement metrics</p>
                
                <!-- Date Range Selector -->
                <div class="mb-6">
                    <label class="block text-sm font-medium text-gray-700 mb-2">Time Period</label>
                    <select id="analyticsDateRange" class="input-field w-48" onchange="this.loadAnalytics()">
                        <option value="7d">Last 7 days</option>
                        <option value="30d" selected>Last 30 days</option>
                        <option value="90d">Last 90 days</option>
                    </select>
                </div>
                
                <!-- Key Metrics -->
                <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
                    <div class="bg-blue-50 p-4 rounded-lg">
                        <div class="text-2xl font-bold text-blue-600" id="totalThreadstorms">-</div>
                        <div class="text-sm text-blue-800">Total Threadstorms</div>
                    </div>
                    <div class="bg-green-50 p-4 rounded-lg">
                        <div class="text-2xl font-bold text-green-600" id="totalCharacters">-</div>
                        <div class="text-sm text-green-800">Characters Written</div>
                    </div>
                    <div class="bg-purple-50 p-4 rounded-lg">
                        <div class="text-2xl font-bold text-purple-600" id="avgEngagement">-</div>
                        <div class="text-sm text-purple-800">Avg Engagement</div>
                    </div>
                    <div class="bg-orange-50 p-4 rounded-lg">
                        <div class="text-2xl font-bold text-orange-600" id="apiCalls">-</div>
                        <div class="text-sm text-orange-800">API Calls</div>
                    </div>
                </div>
                
                <!-- Charts and Graphs -->
                <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
                    <div class="bg-white border rounded-lg p-4">
                        <h4 class="font-medium text-gray-900 mb-4">Engagement Over Time</h4>
                        <div class="h-64 bg-gray-50 rounded flex items-center justify-center">
                            <p class="text-gray-500">Chart placeholder</p>
                        </div>
                    </div>
                    <div class="bg-white border rounded-lg p-4">
                        <h4 class="font-medium text-gray-900 mb-4">Content Performance</h4>
                        <div class="h-64 bg-gray-50 rounded flex items-center justify-center">
                            <p class="text-gray-500">Chart placeholder</p>
                        </div>
                    </div>
                </div>
                
                <!-- Recent Activity -->
                <div class="bg-white border rounded-lg p-4">
                    <h4 class="font-medium text-gray-900 mb-4">Recent Activity</h4>
                    <div class="space-y-3">
                        <div class="flex items-center justify-between">
                            <div>
                                <p class="text-sm font-medium text-gray-900">Threadstorm created</p>
                                <p class="text-xs text-gray-500">2 hours ago</p>
                            </div>
                            <span class="text-sm text-green-600">+15% engagement</span>
                        </div>
                        <div class="flex items-center justify-between">
                            <div>
                                <p class="text-sm font-medium text-gray-900">Template used</p>
                                <p class="text-xs text-gray-500">1 day ago</p>
                            </div>
                            <span class="text-sm text-blue-600">Product Launch</span>
                        </div>
                    </div>
                </div>
                
                <div class="flex justify-end mt-6">
                    <button class="btn-secondary" onclick="closeModal()">Close</button>
                </div>
            </div>
        `);

        // Load analytics data
        this.loadAnalytics();
    }

    loadAnalytics() {
        // Simulate loading analytics data
        const data = {
            totalThreadstorms: 24,
            totalCharacters: 12500,
            avgEngagement: 87,
            apiCalls: 156
        };

        document.getElementById('totalThreadstorms').textContent = data.totalThreadstorms;
        document.getElementById('totalCharacters').textContent = data.totalCharacters.toLocaleString();
        document.getElementById('avgEngagement').textContent = data.avgEngagement + '%';
        document.getElementById('apiCalls').textContent = data.apiCalls;
    }

    openCarouselCreator() {
        console.log('KolektApp.openCarouselCreator() called');
        this.showModal(`
            <div class="bg-white rounded-lg p-6 max-w-6xl w-full">
                <h3 class="text-xl font-semibold mb-4">🎠 Threads Carousel</h3>
                <p class="text-gray-600 mb-6">Create engaging carousels specifically for Threads</p>
                
                <form id="carouselCreatorForm">
                    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
                        <!-- Carousel Settings -->
                        <div class="space-y-4">
                            <div>
                                <label class="block text-sm font-medium text-gray-700 mb-2">Carousel Title</label>
                                <input type="text" id="carouselTitle" class="input-field" placeholder="Enter a compelling title for your carousel">
                            </div>
                            
                            <div>
                                <label class="block text-sm font-medium text-gray-700 mb-2">Platform</label>
                                <select id="carouselPlatform" class="input-field" disabled>
                                    <option value="threads" selected>Threads</option>
                                </select>
                                <p class="text-xs text-gray-500 mt-1">Note: ThreadStorm currently targets Threads only.</p>
                            </div>
                            
                            <div>
                                <label class="block text-sm font-medium text-gray-700 mb-2">Carousel Type</label>
                                <select id="carouselType" class="input-field">
                                    <option value="educational">Educational/How-to</option>
                                    <option value="storytelling">Storytelling</option>
                                    <option value="tips">Tips & Tricks</option>
                                    <option value="comparison">Before/After</option>
                                    <option value="list">List/Numbered</option>
                                    <option value="custom">Custom</option>
                                </select>
                            </div>
                            
                            <div>
                                <label class="block text-sm font-medium text-gray-700 mb-2">Number of Slides</label>
                                <select id="carouselSlides" class="input-field">
                                    <option value="3">3 slides</option>
                                    <option value="5" selected>5 slides</option>
                                    <option value="7">7 slides</option>
                                    <option value="10">10 slides</option>
                                </select>
                                <p class="text-xs text-gray-500 mt-1">Keep each caption under 500 characters (Threads limit).</p>
                            </div>
                            
                            <div>
                                <label class="block text-sm font-medium text-gray-700 mb-2">Content Theme</label>
                                <textarea id="carouselTheme" class="textarea-field" rows="3" placeholder="Describe the main theme or topic for your carousel..."></textarea>
                            </div>
                        </div>
                        
                        <!-- Live Preview -->
                        <div class="bg-gray-50 p-4 rounded-lg">
                            <h4 class="font-medium text-gray-900 mb-4">Carousel Preview</h4>
                            <div id="carouselPreview" class="space-y-3">
                                <div class="text-center text-gray-500 py-8">
                                    <i class="fas fa-images text-2xl mb-2"></i>
                                    <p>Configure your carousel to see preview</p>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Cross-post (scaffold - disabled until configured) -->
                    <div class="mt-6">
                        <h4 class="font-medium text-gray-900 mb-4">Cross-post (Optional)</h4>
                        <div class="bg-gray-50 p-4 rounded-lg flex items-center justify-between">
                            <div>
                                <div class="font-medium text-gray-900">Instagram</div>
                                <div class="text-sm text-gray-600">Enable once connected via Meta</div>
                                <div id="igStatus" class="text-xs text-gray-500 mt-1">Checking status...</div>
                            </div>
                            <div class="flex items-center space-x-3">
                                <label class="inline-flex items-center cursor-not-allowed opacity-60">
                                    <input type="checkbox" id="toggleInstagram" disabled class="rounded border-gray-300">
                                    <span class="ml-2 text-sm">Also publish to Instagram</span>
                                </label>
                                <button type="button" id="connectInstagramBtn" class="btn-secondary text-sm">Connect Instagram</button>
                            </div>
                        </div>
                    </div>

                    <!-- Slide Generator -->
                    <div class="mt-6">
                        <h4 class="font-medium text-gray-900 mb-4">Generate Slides</h4>
                        <div class="bg-blue-50 p-4 rounded-lg">
                            <div class="flex items-center justify-between">
                                <div>
                                    <h5 class="font-medium text-blue-900">AI-Powered Slide Generation</h5>
                                    <p class="text-sm text-blue-800">Let AI create engaging slides based on your theme</p>
                                </div>
                                <button type="button" id="generateSlidesBtn" class="btn-primary">
                                    <i class="fas fa-magic mr-2"></i>Generate Slides
                                </button>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Generated Slides -->
                    <div id="generatedSlides" class="mt-6 hidden">
                        <h4 class="font-medium text-gray-900 mb-4">Generated Slides</h4>
                        <div id="slidesContainer" class="space-y-4">
                            <!-- Slides will be generated here -->
                        </div>
                    </div>
                    
                    <div class="flex justify-between items-center mt-6">
                        <div id="carouselCreatorStatus" class="text-sm text-gray-600"></div>
                        <div class="space-x-3">
                            <button type="button" class="btn-secondary" onclick="closeModal()">Cancel</button>
                            <button type="submit" class="btn-primary">
                                <i class="fas fa-download mr-2"></i>Export Carousel
                            </button>
                        </div>
                    </div>
                </form>

                <!-- Export Options -->
                <div id="carouselExportOptions" class="mt-8 hidden">
                    <h4 class="text-lg font-semibold mb-3">Export Options</h4>
                    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                        <div class="bg-white border rounded-lg p-4">
                            <h5 class="font-medium mb-2">📱 Instagram Format</h5>
                            <p class="text-sm text-gray-600 mb-3">Optimized for Instagram carousel posts</p>
                            <button class="btn-secondary text-sm w-full">Download</button>
                        </div>
                        <div class="bg-white border rounded-lg p-4">
                            <h5 class="font-medium mb-2">💼 LinkedIn Format</h5>
                            <p class="text-sm text-gray-600 mb-3">Professional format for LinkedIn</p>
                            <button class="btn-secondary text-sm w-full">Download</button>
                        </div>
                        <div class="bg-white border rounded-lg p-4">
                            <h5 class="font-medium mb-2">📄 PDF Report</h5>
                            <p class="text-sm text-gray-600 mb-3">Complete carousel with guidelines</p>
                            <button class="btn-secondary text-sm w-full">Download</button>
                        </div>
                    </div>
                </div>
            </div>
        `);

        // Set up carousel creator functionality
        this.setupCarouselCreator();
    }

    setupCarouselCreator() {
        const form = document.getElementById('carouselCreatorForm');
        const generateBtn = document.getElementById('generateSlidesBtn');
        const statusEl = document.getElementById('carouselCreatorStatus');
        const slidesContainer = document.getElementById('slidesContainer');
        const generatedSlides = document.getElementById('generatedSlides');
        const exportOptions = document.getElementById('carouselExportOptions');

        // Update preview when settings change
        const updatePreview = () => {
            const title = document.getElementById('carouselTitle').value;
            const platform = document.getElementById('carouselPlatform').value;
            const type = document.getElementById('carouselType').value;
            const slides = document.getElementById('carouselSlides').value;
            const theme = document.getElementById('carouselTheme').value;

            const preview = document.getElementById('carouselPreview');
            
            if (title || theme) {
                preview.innerHTML = `
                    <div class="bg-white p-4 rounded-lg shadow-sm border">
                        <div class="flex items-center space-x-3 mb-3">
                            <div class="w-10 h-10 bg-gradient-to-r from-purple-400 to-pink-400 rounded-full flex items-center justify-center text-white font-bold">
                                ${platform.charAt(0).toUpperCase()}
                            </div>
                            <div>
                                <div class="font-semibold text-gray-900">${title || 'Your Carousel Title'}</div>
                                <div class="text-sm text-gray-500">${platform} • ${type} • ${slides} slides</div>
                            </div>
                        </div>
                        <div class="flex space-x-2">
                            ${Array.from({length: parseInt(slides)}, (_, i) => `
                                <div class="w-8 h-8 bg-gray-200 rounded flex items-center justify-center text-xs font-medium">
                                    ${i + 1}
                                </div>
                            `).join('')}
                        </div>
                        ${theme ? `<p class="text-sm text-gray-600 mt-2">${theme}</p>` : ''}
                    </div>
                `;
            }
        };

        // Add event listeners for preview updates
        document.getElementById('carouselTitle').addEventListener('input', updatePreview);
        document.getElementById('carouselPlatform').addEventListener('change', updatePreview);
        document.getElementById('carouselType').addEventListener('change', updatePreview);
        document.getElementById('carouselSlides').addEventListener('change', updatePreview);
        document.getElementById('carouselTheme').addEventListener('input', updatePreview);

        // Generate slides button
        generateBtn.addEventListener('click', async () => {
            const title = document.getElementById('carouselTitle').value;
            const theme = document.getElementById('carouselTheme').value;
            const slides = parseInt(document.getElementById('carouselSlides').value);
            const type = document.getElementById('carouselType').value;

            if (!title && !theme) {
                statusEl.textContent = 'Please enter a title or theme to generate slides';
                return;
            }

            statusEl.textContent = 'Generating slides...';
            generateBtn.disabled = true;

            try {
                // Simulate AI generation
                await new Promise(resolve => setTimeout(resolve, 2000));
                
                const generatedSlidesData = this.generateCarouselSlides(title, theme, slides, type);
                
                slidesContainer.innerHTML = generatedSlidesData.map((slide, index) => `
                    <div class="bg-white border rounded-lg p-4">
                        <div class="flex items-center justify-between mb-3">
                            <h5 class="font-medium">Slide ${index + 1}</h5>
                            <div class="flex space-x-2">
                                <button class="text-blue-600 text-sm" onclick="this.editSlide(${index})">Edit</button>
                                <button class="text-red-600 text-sm" onclick="this.deleteSlide(${index})">Delete</button>
                            </div>
                        </div>
                        <div class="space-y-3">
                            <div>
                                <label class="block text-xs font-medium text-gray-700 mb-1">Image Description</label>
                                <input type="text" class="input-field text-sm" value="${slide.image}" placeholder="Describe the image for this slide">
                            </div>
                            <div>
                                <label class="block text-xs font-medium text-gray-700 mb-1">Caption</label>
                                <textarea class="textarea-field text-sm" rows="2" placeholder="Slide caption...">${slide.caption}</textarea>
                            </div>
                            <div>
                                <label class="block text-xs font-medium text-gray-700 mb-1">Call-to-Action</label>
                                <input type="text" class="input-field text-sm" value="${slide.cta}" placeholder="What should viewers do next?">
                            </div>
                        </div>
                    </div>
                `).join('');

                generatedSlides.classList.remove('hidden');
                statusEl.textContent = 'Slides generated successfully!';
                exportOptions.classList.remove('hidden');

            } catch (error) {
                console.error('Error generating slides:', error);
                statusEl.textContent = 'Error generating slides. Please try again.';
            } finally {
                generateBtn.disabled = false;
            }
        });

        // Social status + connect button
        (async () => {
            try {
                const res = await fetch('/api/v1/social/status');
                const data = await res.json();
                const igStatus = document.getElementById('igStatus');
                const toggle = document.getElementById('toggleInstagram');
                const connectBtn = document.getElementById('connectInstagramBtn');
                if (data.success && data.platforms?.instagram?.configured) {
                    igStatus.textContent = 'Instagram: Not connected (app configured)';
                    connectBtn.disabled = false;
                    connectBtn.classList.remove('opacity-60', 'cursor-not-allowed');
                    connectBtn.addEventListener('click', async () => {
                        const r = await fetch('/api/v1/social/instagram/oauth-url');
                        const j = await r.json();
                        if (j.success && j.url) {
                            window.open(j.url, '_blank');
                        } else {
                            this.showNotification('Instagram not configured on server', 'error');
                        }
                    });
                } else {
                    igStatus.textContent = 'Instagram: Not configured';
                    connectBtn.disabled = true;
                    connectBtn.classList.add('opacity-60', 'cursor-not-allowed');
                }
            } catch (e) {
                console.warn('Social status check failed', e);
            }
        })();

        // Form submission
        form.addEventListener('submit', (e) => {
            e.preventDefault();
            statusEl.textContent = 'Exporting carousel...';
            
            // Simulate export
            setTimeout(() => {
                statusEl.textContent = 'Carousel exported successfully!';
                this.showNotification('Carousel created and ready for download!', 'success');
            }, 1000);
        });
    }

    generateCarouselSlides(title, theme, slideCount, type) {
        const slides = [];
        const themes = {
            educational: ['Step 1: Introduction', 'Step 2: Process', 'Step 3: Tips', 'Step 4: Examples', 'Step 5: Conclusion'],
            storytelling: ['The Beginning', 'The Challenge', 'The Journey', 'The Breakthrough', 'The Lesson'],
            tips: ['Tip #1', 'Tip #2', 'Tip #3', 'Tip #4', 'Tip #5'],
            comparison: ['Before', 'During', 'After', 'Results', 'Takeaway'],
            list: ['Point 1', 'Point 2', 'Point 3', 'Point 4', 'Point 5'],
            custom: ['Key Insight 1', 'Key Insight 2', 'Key Insight 3', 'Key Insight 4', 'Key Insight 5']
        };

        const slideTitles = themes[type] || themes.custom;

        for (let i = 0; i < slideCount; i++) {
            slides.push({
                image: `${slideTitles[i] || `Slide ${i + 1}`} - Visual representation with engaging graphics`,
                caption: `${slideTitles[i] || `Key Point ${i + 1}`}: ${theme || 'Your content theme'} - This slide explains the main concept in an engaging way that captures attention and drives engagement.`,
                cta: i === slideCount - 1 ? 'Follow for more tips!' : 'Swipe for more →'
            });
        }

        return slides;
    }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
            console.log('DOM loaded, initializing KolektApp...');
        window.kolektApp = new KolektApp();
        console.log('KolektApp initialized:', window.kolektApp);
});

// Additional global functions
window.openThreadsAPI = function() {
            if (window.kolektApp) {
            window.kolektApp.openThreadsAPI();
        }
};

window.testThreadsAPI = function() {
            if (window.kolektApp) {
            window.kolektApp.testThreadsAPI();
        }
};

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = KolektApp;
}

// Review Queue Functions
function openReviewQueue() {
    document.getElementById('reviewQueueModal').style.display = 'block';
    loadReviewItems();
}

function closeReviewQueue() {
    document.getElementById('reviewQueueModal').style.display = 'none';
}

async function loadReviewItems() {
    try {
        const response = await fetch('/api/v1/curation/review-queue?user_id=550e8400-e29b-41d4-a716-446655440000');
        const data = await response.json();
        
        const container = document.getElementById('reviewItems');
        container.innerHTML = '';
        
        if (data.items && data.items.length > 0) {
            data.items.forEach(item => {
                const itemDiv = document.createElement('div');
                itemDiv.className = 'review-item';
                itemDiv.innerHTML = `
                    <div class="review-item-header">
                        <h3>${item.title || 'Untitled'}</h3>
                        <span class="score">Score: ${item.score}</span>
                    </div>
                    <p>${item.normalized?.substring(0, 200)}...</p>
                    <div class="review-actions">
                        <button onclick="approveItem('${item.id}')" class="btn btn-success">✅ Approve</button>
                        <button onclick="rejectItem('${item.id}')" class="btn btn-danger">❌ Reject</button>
                        <button onclick="createDraft('${item.id}')" class="btn btn-primary">📝 Create Draft</button>
                    </div>
                `;
                container.appendChild(itemDiv);
            });
        } else {
            container.innerHTML = '<p>No items in review queue</p>';
        }
    } catch (error) {
        console.error('Error loading review items:', error);
    }
}

        async function approveItem(itemId) {
    try {
        const response = await fetch(`/api/v1/curation/review-queue/${itemId}/approve`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({user_id: '550e8400-e29b-41d4-a716-446655440000'})
        });
        
        if (response.ok) {
            loadReviewItems();
        }
    } catch (error) {
        console.error('Error approving item:', error);
    }
}

async function rejectItem(itemId) {
    try {
        const response = await fetch(`/api/v1/curation/review-queue/${itemId}/reject`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({user_id: '550e8400-e29b-41d4-a716-446655440000'})
        });
        
        if (response.ok) {
            loadReviewItems();
        }
    } catch (error) {
        console.error('Error rejecting item:', error);
    }
}

async function createDraft(itemId) {
    try {
        const response = await fetch(`/api/v1/curation/drafts/threads?user_id=550e8400-e29b-41d4-a716-446655440000&item_id=${itemId}&variants=1`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'}
        });
        
        if (response.ok) {
            alert('Draft created successfully!');
        }
    } catch (error) {
        console.error('Error creating draft:', error);
    }
}
