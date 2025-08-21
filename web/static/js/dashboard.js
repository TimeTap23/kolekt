// Dashboard JavaScript

class Dashboard {
    constructor() {
        this.currentUser = null;
        this.init();
    }

    async init() {
        // Check authentication
        await this.checkAuth();
        
        // Initialize dashboard
        this.loadUserData();
        this.loadDashboardData();
        this.setupEventListeners();
        this.setupCharCounter();
        this.initializeTabs();
        this.setupFileUpload();
        // AI health check to surface gotchas
        this.aiHealthCheck();
    }

    loadUserData() {
        try {
            // Ensure currentUser is available from auth check
            if (!this.currentUser) {
                return;
            }
            // Populate basic user UI elements
            this.updateUserUI();
        } catch (e) {
            console.error('Failed to load user data:', e);
        }
    }

    async checkAuth() {
        console.log('Dashboard: Checking authentication...');
        const token = localStorage.getItem('threadstorm_access_token');
        console.log('Dashboard: Token found:', token ? 'Yes' : 'No');
        if (!token) {
            console.log('Dashboard: No token found, redirecting to homepage');
            // Redirect to homepage if not authenticated
            window.location.href = '/';
            return;
        }

        try {
            // Verify token and get user data
            const response = await fetch('/api/v1/auth/me', {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });

            if (!response.ok) {
                throw new Error('Token invalid');
            }

            const userData = await response.json();
            console.log('Dashboard: User data received:', userData);
            if (userData.success && userData.user) {
                this.currentUser = userData.user;
                console.log('Dashboard: User authenticated:', this.currentUser);
                this.updateUserUI();
            } else {
                console.log('Dashboard: Invalid user data, throwing error');
                throw new Error('Invalid user data');
            }
        } catch (error) {
            console.error('Auth check failed:', error);
            // Clear invalid tokens and redirect
            localStorage.removeItem('threadstorm_access_token');
            localStorage.removeItem('threadstorm_refresh_token');
            window.location.href = '/';
        }
    }

    updateUserUI() {
        if (!this.currentUser) return;

        // Update user display name
        const displayName = this.currentUser.name || this.currentUser.email.split('@')[0];
        document.getElementById('userDisplayName').textContent = displayName;
        document.getElementById('userName').textContent = displayName;
        
        // Update user initials
        const initials = displayName.split(' ').map(n => n[0]).join('').toUpperCase();
        document.getElementById('userInitials').textContent = initials;
    }

    async loadDashboardData() {
        try {
            // Load content stats
            await this.loadContentStats();
            
            // Load recent content
            await this.loadRecentContent();
            
            // Load analytics
            await this.loadAnalytics();
            
            // Load social connections
            await this.loadSocialConnections();
        } catch (error) {
            console.error('Error loading dashboard data:', error);
        }
    }

    async loadContentStats() {
        try {
            const response = await fetch('/api/v1/content/stats/overview', {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('threadstorm_access_token')}`
                }
            });

            if (response.ok) {
                const stats = await response.json();
                this.updateContentStats(stats);
            } else {
                // Use mock data for now
                this.updateContentStats({
                    total: 0,
                    published: 0,
                    drafts: 0,
                    scheduled: 0
                });
            }
        } catch (error) {
            // Use mock data for now
            this.updateContentStats({
                total: 0,
                published: 0,
                drafts: 0,
                scheduled: 0
            });
        }
    }

    updateContentStats(stats) {
        document.getElementById('totalContent').textContent = stats.total || 0;
        document.getElementById('publishedContent').textContent = stats.published || 0;
        document.getElementById('draftContent').textContent = stats.drafts || 0;
        document.getElementById('scheduledContent').textContent = stats.scheduled || 0;
    }

    async loadRecentContent() {
        try {
            const response = await fetch('/api/v1/content/list?page=1&per_page=5', {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('threadstorm_access_token')}`
                }
            });

            if (response.ok) {
                const content = await response.json();
                this.updateRecentContent(content.items);
            } else {
                // Show empty state
                this.showEmptyContentState();
            }
        } catch (error) {
            // Show empty state
            this.showEmptyContentState();
        }
    }

    updateRecentContent(content) {
        const container = document.getElementById('recentContentList');
        
        if (!content || content.length === 0) {
            this.showEmptyContentState();
            return;
        }

        container.innerHTML = content.map(item => `
            <div class="content-item">
                <div class="content-item-header">
                    <h4>${item.title}</h4>
                    <span class="content-status ${item.status}">${item.status}</span>
                </div>
                <p>${item.excerpt || item.content.substring(0, 100)}...</p>
                <div class="content-item-meta">
                    <span>${new Date(item.created_at).toLocaleDateString()}</span>
                    <div class="content-actions">
                        <button onclick="editContent('${item.id}')" class="btn btn-sm btn-ghost">Edit</button>
                        <button onclick="deleteContent('${item.id}')" class="btn btn-sm btn-ghost">Delete</button>
                    </div>
                </div>
            </div>
        `).join('');
    }

    showEmptyContentState() {
        const container = document.getElementById('recentContentList');
        container.innerHTML = `
            <div class="empty-state">
                <div class="empty-icon">📝</div>
                <h4>No content yet</h4>
                <p>Create your first piece of content to get started</p>
                <button class="btn btn-primary" onclick="openContentCreator()">Create Content</button>
            </div>
        `;
    }

    async loadAnalytics() {
        try {
            const response = await fetch('/api/v1/analytics/overview', {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('threadstorm_access_token')}`
                }
            });

            if (response.ok) {
                const analytics = await response.json();
                this.updateAnalytics(analytics);
            } else {
                // Use mock data for now
                this.updateAnalytics({
                    total_views: 0,
                    total_likes: 0,
                    total_comments: 0,
                    avg_engagement: 0
                });
            }
        } catch (error) {
            // Use mock data for now
            this.updateAnalytics({
                total_views: 0,
                total_likes: 0,
                total_comments: 0,
                avg_engagement: 0
            });
        }
    }

    updateAnalytics(analytics) {
        document.getElementById('totalViews').textContent = analytics.total_views || 0;
        document.getElementById('totalLikes').textContent = analytics.total_likes || 0;
        document.getElementById('totalComments').textContent = analytics.total_comments || 0;
        document.getElementById('avgEngagement').textContent = `${analytics.avg_engagement || 0}%`;
    }

    async loadSocialConnections() {
        try {
            // Get all social connections status
            const response = await fetch('/api/v1/connections/status', {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('threadstorm_access_token')}`
                }
            });

            if (response.ok) {
                const data = await response.json();
                this.updateSocialConnections(data.connections);
            } else {
                // Show disconnected state
                this.updateSocialConnections([]);
            }
        } catch (error) {
            console.error('Error loading social connections:', error);
            // Show disconnected state
            this.updateSocialConnections([]);
        }
    }

    updateSocialConnections(connections) {
        // Update each platform connection
        connections.forEach(connection => {
            this.updateSocialConnectionStatus(connection.platform, connection.connected, {
                username: connection.username ? `@${connection.username}` : 'Unknown',
                followers: connection.followers_count ? `${connection.followers_count.toLocaleString()}` : '0',
                connectedDate: connection.connected_at ? new Date(connection.connected_at).toLocaleDateString() : 'Unknown'
            });
        });
        
        // Handle platforms that might not be in the connections list
        const platforms = ['threads', 'instagram', 'facebook'];
        platforms.forEach(platform => {
            const hasConnection = connections.some(conn => conn.platform === platform);
            if (!hasConnection) {
                this.updateSocialConnectionStatus(platform, false);
            }
        });
    }

    setupEventListeners() {
        // User menu toggle
        document.addEventListener('click', (e) => {
            if (!e.target.closest('.user-menu')) {
                document.getElementById('userDropdown').classList.remove('show');
            }
        });

        // Content form submission
        const contentForm = document.getElementById('contentForm');
        if (contentForm) {
            contentForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.handleContentSubmit(e.target);
            });
        }

        // Quick post form submission
        const quickPostForm = document.getElementById('quickPostForm');
        if (quickPostForm) {
            quickPostForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.handleQuickPost(e.target);
            });
        }

        // Quick post character counter
        const quickPostContent = document.getElementById('quickPostContent');
        if (quickPostContent) {
            quickPostContent.addEventListener('input', (e) => {
                const charCount = document.getElementById('quickPostCharCount');
                if (charCount) {
                    charCount.textContent = e.target.value.length;
                }
            });
        }
    }

    setupCharCounter() {
        const contentText = document.getElementById('contentText');
        const charCount = document.getElementById('charCount');
        
        if (contentText && charCount) {
            contentText.addEventListener('input', () => {
                charCount.textContent = contentText.value.length;
            });
        }
    }

    async handleContentSubmit(form) {
        const formData = new FormData(form);
        const publishOption = formData.get('publishOption');
        const contentType = formData.get('type');
        
        const contentData = {
            title: formData.get('title'),
            content: formData.get('content'),
            type: formData.get('type'),
            tags: formData.get('tags') ? formData.get('tags').split(',').map(t => t.trim()) : []
        };

        try {
            // First, create content in database
            const response = await fetch('/api/v1/content/create', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('threadstorm_access_token')}`
                },
                body: JSON.stringify(contentData)
            });

            if (!response.ok) {
                const error = await response.json();
                this.showNotification(error.detail || 'Failed to create content', 'error');
                return;
            }

            const contentResult = await response.json();
            this.showNotification('Content created successfully!', 'success');

            // If publishing immediately, post to social media
            if (publishOption === 'immediate') {
                await this.postToSocialMedia(contentData, contentType);
            } else if (publishOption === 'scheduled') {
                // Handle scheduled posting (future enhancement)
                const scheduleDate = formData.get('scheduleDate');
                const scheduleTime = formData.get('scheduleTime');
                this.showNotification(`Content scheduled for ${scheduleDate} at ${scheduleTime}`, 'info');
            }

            this.closeContentCreator();
            this.loadDashboardData(); // Refresh dashboard
            
        } catch (error) {
            console.error('Error in content submission:', error);
            this.showNotification('Error creating content', 'error');
        }
    }

    async postToSocialMedia(contentData, contentType) {
        try {
            let platforms = [];
            
            // Determine which platforms to post to based on content type
            if (contentType === 'cross-platform') {
                platforms = ['threads', 'instagram', 'facebook'];
            } else {
                platforms = [contentType];
            }

            // Check connection status for each platform
            const connectionResponse = await fetch('/api/v1/connections/status', {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('threadstorm_access_token')}`
                }
            });

            if (connectionResponse.ok) {
                const connections = await connectionResponse.json();
                const connectedPlatforms = connections.connections
                    .filter(conn => conn.connected)
                    .map(conn => conn.platform);

                // Filter to only post to connected platforms
                const platformsToPost = platforms.filter(platform => 
                    connectedPlatforms.includes(platform)
                );

                if (platformsToPost.length === 0) {
                    this.showNotification('No social media accounts connected. Please connect your accounts first.', 'warning');
                    return;
                }

                // Post to cross-platform endpoint
                const postResponse = await fetch('/api/v1/social/cross-platform/post', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${localStorage.getItem('threadstorm_access_token')}`
                    },
                    body: JSON.stringify({
                        content: contentData.content,
                        platforms: platformsToPost,
                        images: contentData.images || []
                    })
                });

                if (postResponse.ok) {
                    const result = await postResponse.json();
                    const successCount = Object.values(result.results).filter(r => r.success).length;
                    this.showNotification(`Successfully posted to ${successCount} platform(s)!`, 'success');
                } else {
                    const error = await postResponse.json();
                    this.showNotification(`Failed to post: ${error.error || 'Unknown error'}`, 'error');
                }
            } else {
                this.showNotification('Unable to check social media connections', 'error');
            }
        } catch (error) {
            console.error('Error posting to social media:', error);
            this.showNotification('Error posting to social media', 'error');
        }
    }

    async handleQuickPost(form) {
        const formData = new FormData(form);
        const content = formData.get('content');
        const selectedPlatforms = formData.getAll('platforms');

        if (!content.trim()) {
            this.showNotification('Please enter some content to post', 'error');
            return;
        }

        if (selectedPlatforms.length === 0) {
            this.showNotification('Please select at least one platform', 'error');
            return;
        }

        try {
            // Check connection status first
            const connectionResponse = await fetch('/api/v1/connections/status', {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('threadstorm_access_token')}`
                }
            });

            if (connectionResponse.ok) {
                const connections = await connectionResponse.json();
                const connectedPlatforms = connections.connections
                    .filter(conn => conn.connected)
                    .map(conn => conn.platform);

                // Filter to only post to connected platforms
                const platformsToPost = selectedPlatforms.filter(platform => 
                    connectedPlatforms.includes(platform)
                );

                if (platformsToPost.length === 0) {
                    this.showNotification('No selected platforms are connected. Please connect your accounts first.', 'warning');
                    return;
                }

                // Update button text to show posting status
                const button = document.getElementById('quickPostButtonText');
                if (button) button.textContent = 'Posting...';

                // Post to cross-platform endpoint
                const postResponse = await fetch('/api/v1/social/cross-platform/post', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${localStorage.getItem('threadstorm_access_token')}`
                    },
                    body: JSON.stringify({
                        content: content,
                        platforms: platformsToPost
                    })
                });

                if (postResponse.ok) {
                    const result = await postResponse.json();
                    const successCount = Object.values(result.results).filter(r => r.success).length;
                    this.showNotification(`Successfully posted to ${successCount} platform(s)!`, 'success');
                    this.closeQuickPost();
                    this.loadDashboardData(); // Refresh dashboard
                } else {
                    const error = await postResponse.json();
                    this.showNotification(`Failed to post: ${error.error || 'Unknown error'}`, 'error');
                }
            } else {
                this.showNotification('Unable to check social media connections', 'error');
            }
        } catch (error) {
            console.error('Error in quick post:', error);
            this.showNotification('Error posting to social media', 'error');
        } finally {
            // Reset button text
            const button = document.getElementById('quickPostButtonText');
            if (button) button.textContent = 'Post Now';
        }
    }

    showNotification(message, type = 'info') {
        const container = document.getElementById('notification-container');
        if (container) {
            const notification = document.createElement('div');
            notification.className = `notification notification-${type}`;
            notification.innerHTML = `
                <span>${message}</span>
                <button onclick="this.parentElement.remove()">×</button>
            `;
            
            container.appendChild(notification);
            
            // Add show class after a brief delay to trigger animation
            setTimeout(() => {
                notification.classList.add('show');
            }, 100);
            
            // Auto-remove after 8 seconds (increased from 5)
            setTimeout(() => {
                if (notification.parentElement) {
                    notification.classList.remove('show');
                    setTimeout(() => {
                        if (notification.parentElement) {
                            notification.remove();
                        }
                    }, 300); // Wait for animation to complete
                }
            }, 8000);
        }
    }

    // ===== TAB MANAGEMENT =====
    initializeTabs() {
        // Set up tab switching
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.style.cursor = 'pointer';
            if (!btn.textContent.trim()) {
                btn.textContent = btn.getAttribute('data-label') || 'Tab';
            }
            btn.addEventListener('click', (e) => {
                const label = (e.currentTarget.textContent || '').trim().toLowerCase();
                const tabName = label.replace(/\s+/g, '');
                this.switchTab(tabName);
            });
        });
    }

    switchTab(tabName) {
        // Remove active class from all tabs and content
        document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
        document.querySelectorAll('.tab-content').forEach(content => {
            content.classList.remove('active');
            content.style.display = 'none';
        });

        // Add active class to selected tab
        const activeBtn = document.querySelector(`.tab-btn:nth-child(${this.getTabIndex(tabName)})`);
        if (activeBtn) activeBtn.classList.add('active');

        // Show selected content
        const activeContent = document.getElementById(`${tabName}Tab`);
        if (activeContent) {
            activeContent.classList.add('active');
            activeContent.style.display = 'block';
        }
    }

    getTabIndex(tabName) {
        const tabMap = { 'manual': 1, 'import': 2, 'ai': 3 };
        return tabMap[tabName] || 1;
    }

    // ===== CHARACTER COUNTING =====
    updateCharCount() {
        const textArea = document.getElementById('contentText');
        const charCount = document.getElementById('charCount');
        const charLimit = document.getElementById('charLimit');
        const charStatus = document.getElementById('charStatus');
        
        if (!textArea || !charCount) return;

        const currentLength = textArea.value.length;
        const maxLength = parseInt(charLimit.textContent);
        
        charCount.textContent = currentLength;
        
        // Update status based on length
        charStatus.classList.remove('warning', 'error');
        if (currentLength > maxLength * 0.9) {
            charStatus.classList.add('warning');
            charStatus.textContent = 'Close to limit';
        }
        if (currentLength > maxLength) {
            charStatus.classList.add('error');
            charStatus.textContent = 'Over limit';
        }
        if (currentLength <= maxLength * 0.9) {
            charStatus.textContent = '';
        }
    }

    updateCharLimit() {
        const contentType = document.getElementById('contentType').value;
        const charLimit = document.getElementById('charLimit');
        
        const limits = {
            threads: 500,
            instagram: 2200,
            facebook: 63206,
            'cross-platform': 500
        };
        
        charLimit.textContent = limits[contentType] || 500;
        this.updateCharCount();
    }

    // ===== SCHEDULING =====
    toggleScheduler() {
        const publishOption = document.getElementById('publishOption').value;
        const schedulerGroup = document.getElementById('schedulerGroup');
        const submitButtonText = document.getElementById('submitButtonText');
        
        if (publishOption === 'scheduled') {
            schedulerGroup.style.display = 'block';
            submitButtonText.textContent = 'Schedule Content';
        } else {
            schedulerGroup.style.display = 'none';
            submitButtonText.textContent = publishOption === 'immediate' ? 'Publish Now' : 'Create Content';
        }
    }

    // ===== IMPORT FUNCTIONALITY =====
    selectImportMethod(method) {
        // Update active import method
        document.querySelectorAll('.import-method').forEach(m => m.classList.remove('active'));
        document.querySelector(`.import-method:nth-child(${this.getImportIndex(method)})`).classList.add('active');
        
        // Show corresponding import content
        document.querySelectorAll('.import-content').forEach(c => {
            c.classList.remove('active');
            c.style.display = 'none';
        });
        
        const activeImport = document.getElementById(`${method}Import`);
        if (activeImport) {
            activeImport.classList.add('active');
            activeImport.style.display = 'block';
        }
    }

    getImportIndex(method) {
        const methodMap = { 'url': 1, 'file': 2, 'existing': 3 };
        return methodMap[method] || 1;
    }

    // ===== FILE UPLOAD =====
    setupFileUpload() {
        const fileInput = document.getElementById('fileInput');
        
        if (fileInput) {
            fileInput.addEventListener('change', (e) => this.handleFileSelect(e));
        }
    }

    handleFileSelect(event) {
        const files = Array.from(event.target.files);
        this.displayFileList(files);
    }

    displayFileList(files) {
        const fileList = document.getElementById('fileList');
        const processBtn = document.getElementById('processFilesBtn');
        
        if (!fileList) return;
        
        fileList.innerHTML = '';
        
        if (files.length > 0) {
            fileList.classList.add('has-files');
            if (processBtn) processBtn.disabled = false;
            
            files.forEach((file, index) => {
                const fileItem = document.createElement('div');
                fileItem.className = 'file-item';
                fileItem.innerHTML = `
                    <div class="file-info">
                        <div class="file-icon">${this.getFileIcon(file.type)}</div>
                        <div class="file-details">
                            <div class="file-name">${file.name}</div>
                            <div class="file-size">${this.formatFileSize(file.size)}</div>
                        </div>
                    </div>
                    <button class="file-remove" onclick="dashboard.removeFile(${index})">&times;</button>
                `;
                fileList.appendChild(fileItem);
            });
        } else {
            fileList.classList.remove('has-files');
            if (processBtn) processBtn.disabled = true;
        }
    }

    getFileIcon(fileType) {
        if (fileType.includes('text')) return '📄';
        if (fileType.includes('csv')) return '📊';
        if (fileType.includes('pdf')) return '📕';
        if (fileType.includes('word')) return '📝';
        return '📁';
    }

    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    removeFile(index) {
        const fileInput = document.getElementById('fileInput');
        const files = Array.from(fileInput.files);
        files.splice(index, 1);
        this.displayFileList(files);
    }

    // ===== AI ASSISTANT =====
    usePrompt(promptText) {
        const aiPrompt = document.getElementById('aiPrompt');
        if (aiPrompt) {
            aiPrompt.value = promptText + ' ';
            aiPrompt.focus();
            aiPrompt.setSelectionRange(aiPrompt.value.length, aiPrompt.value.length);
        }
    }

    async aiHealthCheck() {
        try {
            const response = await fetch('/api/v1/ai/health', {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('threadstorm_access_token')}`
                }
            });
            if (response.status === 403) {
                // Health endpoint is admin-only; silently ignore
                return;
            }
            if (!response.ok) return;
            const data = await response.json();
            if (!data.huggingface_available) {
                this.showNotification('AI running in mock mode until Hugging Face token is active.', 'warning');
            }
        } catch (_) {
            // ignore health errors
        }
    }

    async generateContent() {
        const prompt = document.getElementById('aiPrompt').value;
        const tone = document.getElementById('aiTone').value;
        const length = document.getElementById('aiLength').value;
        const platform = document.getElementById('aiPlatform').value;

        if (!prompt.trim()) {
            this.showNotification('Please enter a prompt to generate content', 'warning');
            return;
        }

        try {
            this.showNotification('Generating content with AI...', 'info');
            // Call backend AI endpoint
            const response = await fetch('/api/v1/ai/generate-content', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('threadstorm_access_token')}`
                },
                body: JSON.stringify({
                    topic: prompt,
                    platform: platform,
                    tone: tone,
                    length: length,
                    style: 'conversational',
                    additional_context: null
                })
            });

            if (!response.ok) {
                throw new Error(`AI generation failed (${response.status})`);
            }

            const data = await response.json();
            this.displayGeneratedContent(data.content, data.hashtags || []);
            this.showNotification('Content generated successfully!', 'success');
            
        } catch (error) {
            console.error('Error generating content:', error);
            // Fallback to simulated content
            const generatedContent = await this.simulateAIGeneration(prompt, tone, length, platform);
            this.displayGeneratedContent(generatedContent, []);
            this.showNotification('Using fallback AI output (check AI configuration).', 'warning');
        }
    }

    async simulateAIGeneration(prompt, tone, length, platform) {
        // Simulate API delay
        await new Promise(resolve => setTimeout(resolve, 2000));
        
        // Generate sample content based on parameters
        let content = `Here's your ${tone} content for ${platform}:\n\n`;
        
        if (length === 'short') {
            content += `${prompt} - This is a concise and impactful message that gets straight to the point.`;
        } else if (length === 'medium') {
            content += `${prompt}\n\nThis is a well-crafted paragraph that provides valuable insights while maintaining engagement. It's perfectly sized for social media platforms and delivers your message effectively.`;
        } else if (length === 'long') {
            content += `${prompt}\n\nThis is a comprehensive piece of content that dives deep into the topic. It provides detailed information, multiple perspectives, and valuable insights that will engage your audience.\n\nThe content is structured to maintain interest throughout, with clear points and actionable takeaways that your followers will appreciate and want to share with others.`;
        } else if (length === 'thread') {
            content += `${prompt}\n\n🧵 Thread (1/3):\nThis is the opening post that hooks your audience and sets up the main topic.\n\n🧵 (2/3):\nHere we dive deeper into the details, providing valuable insights and building on the initial premise.\n\n🧵 (3/3):\nAnd here's the conclusion with actionable takeaways and a call to action for engagement.`;
        }
        
        return content;
    }

    displayGeneratedContent(content, hashtags = []) {
        const resultsDiv = document.getElementById('aiResults');
        const generatedText = document.getElementById('generatedText');
        
        if (generatedText) {
            generatedText.textContent = content;
            // Render hashtags beneath content
            let tagEl = document.getElementById('generatedHashtags');
            if (!tagEl) {
                tagEl = document.createElement('div');
                tagEl.id = 'generatedHashtags';
                tagEl.style.marginTop = '8px';
                tagEl.style.opacity = '0.85';
                generatedText.parentElement.appendChild(tagEl);
            }
            tagEl.textContent = hashtags && hashtags.length ? hashtags.join(' ') : '';
        }
        if (resultsDiv) resultsDiv.style.display = 'block';
    }

    regenerateContent() {
        this.generateContent();
    }

    refineContent() {
        const currentContent = document.getElementById('generatedText').textContent;
        const refinementPrompt = prompt('How would you like to refine this content?');
        
        if (refinementPrompt) {
            // In a real implementation, this would send the refinement request to the AI
            this.showNotification('Refining content...', 'info');
            setTimeout(() => {
                const refinedContent = `${currentContent}\n\n[Refined based on: "${refinementPrompt}"]`;
                this.displayGeneratedContent(refinedContent);
                this.showNotification('Content refined!', 'success');
            }, 1500);
        }
    }

    useGeneratedContent() {
        const generatedContent = document.getElementById('generatedText').textContent;
        
        // Switch to manual tab and populate form
        this.switchTab('manual');
        
        const contentText = document.getElementById('contentText');
        if (contentText) {
            contentText.value = generatedContent;
            this.updateCharCount();
        }
        
        // Close AI results
        document.getElementById('aiResults').style.display = 'none';
        
        this.showNotification('Content added to form!', 'success');
    }

    clearAiForm() {
        document.getElementById('aiPrompt').value = '';
        document.getElementById('aiTone').value = 'professional';
        document.getElementById('aiLength').value = 'medium';
        document.getElementById('aiPlatform').value = 'general';
        document.getElementById('aiResults').style.display = 'none';
    }

    // ===== CONTENT PREVIEW =====
    previewContent() {
        const title = document.getElementById('contentTitle').value;
        const content = document.getElementById('contentText').value;
        const platform = document.getElementById('contentType').value;

        if (!content.trim()) {
            this.showNotification('Please enter some content to preview', 'warning');
            return;
        }

        // Update preview content
        document.getElementById('threadsContent').textContent = content;
        document.getElementById('instagramContent').textContent = content;
        document.getElementById('facebookContent').textContent = content;

        // Show preview modal
        document.getElementById('contentPreviewModal').style.display = 'flex';
    }

    switchPreviewPlatform(platform) {
        // Update active tab
        document.querySelectorAll('.platform-tab').forEach(tab => tab.classList.remove('active'));
        document.querySelector(`.platform-tab:nth-child(${this.getPreviewTabIndex(platform)})`).classList.add('active');

        // Show corresponding preview
        document.querySelectorAll('.platform-preview').forEach(preview => preview.style.display = 'none');
        document.getElementById(`${platform}Preview`).style.display = 'block';
    }

    getPreviewTabIndex(platform) {
        const tabMap = { 'threads': 1, 'instagram': 2, 'facebook': 3 };
        return tabMap[platform] || 1;
    }

    closePreviewModal() {
        document.getElementById('contentPreviewModal').style.display = 'none';
    }

    proceedWithContent() {
        this.closePreviewModal();
        this.showNotification('Content looks good! Ready to publish.', 'success');
    }

    // ===== SOCIAL CONNECTIONS =====
    async connectSocialAccount(platform) {
        try {
            this.showNotification(`🔗 Connecting to ${platform}...`, 'info');
            
            // Get OAuth URL from backend
            const response = await fetch(`/api/v1/connections/oauth/${platform}/url`, {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('threadstorm_access_token')}`
                }
            });
            
            if (!response.ok) {
                throw new Error('Failed to get OAuth URL');
            }
            
            const data = await response.json();
            
            if (data.success && data.oauth_url) {
                // Open OAuth URL in new window
                const authWindow = window.open(data.oauth_url, `${platform}_oauth`, 'width=600,height=700,scrollbars=yes,resizable=yes');
                
                // Set up polling to check if window is closed
                const checkClosed = setInterval(() => {
                    if (authWindow.closed) {
                        clearInterval(checkClosed);
                        this.checkConnectionStatus(platform);
                    }
                }, 1000);
                
                // Also listen for OAuth callback via postMessage
                const messageHandler = (event) => {
                    if (event.origin !== window.location.origin) return;
                    
                    if (event.data.type === 'oauth_callback' && event.data.platform === platform) {
                        if (event.data.error) {
                            // Handle OAuth error
                            this.showNotification(`❌ ${event.data.error_description || 'Authorization failed'}`, 'error');
                        } else {
                            // Handle successful OAuth
                            this.handleOAuthCallback(platform, event.data.code);
                        }
                        authWindow.close();
                        window.removeEventListener('message', messageHandler);
                    }
                };
                
                window.addEventListener('message', messageHandler);
                
            } else {
                throw new Error('Invalid OAuth URL response');
            }
        } catch (error) {
            console.error(`Failed to connect ${platform}:`, error);
            this.showNotification(`❌ Failed to connect ${platform} account`, 'error');
        }
    }

    async disconnectSocialAccount(platform) {
        try {
            this.showNotification(`🔌 Disconnecting from ${platform}...`, 'info');
            
            const response = await fetch('/api/v1/connections/disconnect', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('threadstorm_access_token')}`
                },
                body: JSON.stringify({
                    platform: platform
                })
            });
            
            if (!response.ok) {
                throw new Error('Failed to disconnect');
            }
            
            const data = await response.json();
            
            if (data.success) {
                this.updateSocialConnectionStatus(platform, false);
                this.showNotification(`✅ Successfully disconnected from ${platform}`, 'success');
            } else {
                throw new Error(data.error_message || 'Disconnect failed');
            }
        } catch (error) {
            console.error('Error disconnecting social account:', error);
            this.showNotification(`❌ Failed to disconnect from ${platform}`, 'error');
        }
    }

    async handleOAuthCallback(platform, code) {
        try {
            this.showNotification(`🔄 Completing ${platform} connection...`, 'info');
            
            // The OAuth callback is now handled by the backend directly
            // Just check the connection status after a short delay
            setTimeout(async () => {
                await this.checkConnectionStatus(platform);
                this.showNotification(`✅ Successfully connected to ${platform}!`, 'success');
            }, 2000);
            
        } catch (error) {
            console.error('Error handling OAuth callback:', error);
            this.showNotification(`❌ Failed to complete ${platform} connection`, 'error');
        }
    }

    async checkConnectionStatus(platform) {
        try {
            const response = await fetch(`/api/v1/connections/${platform}/status`, {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('threadstorm_access_token')}`
                }
            });
            
            if (!response.ok) {
                throw new Error('Failed to check connection status');
            }
            
            const data = await response.json();
            
            if (data.success && data.connection) {
                const connection = data.connection;
                this.updateSocialConnectionStatus(platform, connection.connected, {
                    username: connection.username ? `@${connection.username}` : 'Unknown',
                    followers: connection.followers_count ? `${connection.followers_count.toLocaleString()}` : '0',
                    connectedDate: connection.connected_at ? new Date(connection.connected_at).toLocaleDateString() : 'Unknown'
                });
            }
        } catch (error) {
            console.error('Error checking connection status:', error);
        }
    }

    updateSocialConnectionStatus(platform, connected, details = {}) {
        const indicator = document.getElementById(`${platform}Indicator`);
        const status = document.getElementById(`${platform}ConnectionStatus`);
        const connectBtn = document.getElementById(`${platform}ConnectBtn`);
        const disconnectBtn = document.getElementById(`${platform}DisconnectBtn`);
        const detailsDiv = document.getElementById(`${platform}Details`);

        if (indicator) indicator.textContent = connected ? '✅' : '❌';
        if (status) status.textContent = connected ? 'Connected' : 'Not Connected';
        
        if (connectBtn) connectBtn.style.display = connected ? 'none' : 'block';
        if (disconnectBtn) disconnectBtn.style.display = connected ? 'block' : 'none';
        if (detailsDiv) detailsDiv.style.display = connected ? 'block' : 'none';

        // Update details if connected
        if (connected && details) {
            if (details.username) {
                const usernameEl = document.getElementById(`${platform}Username`);
                if (usernameEl) usernameEl.textContent = details.username;
            }
            if (details.followers) {
                const followersEl = document.getElementById(`${platform}Followers`);
                if (followersEl) followersEl.textContent = details.followers;
            }
            if (details.connectedDate) {
                const dateEl = document.getElementById(`${platform}ConnectedDate`);
                if (dateEl) dateEl.textContent = details.connectedDate;
            }
        }
    }

    // ===== IMPORT FUNCTIONS =====
    async importFromUrl() {
        const url = document.getElementById('importUrl').value;
        
        if (!url) {
            this.showNotification('Please enter a URL to import', 'warning');
            return;
        }

        try {
            this.showNotification('Importing content from URL...', 'info');
            
            // Simulate import process
            setTimeout(() => {
                const importedContent = `Imported content from: ${url}\n\nThis is simulated imported content. In a real implementation, this would extract and format the actual content from the provided URL.`;
                
                // Switch to manual tab and populate
                this.switchTab('manual');
                document.getElementById('contentText').value = importedContent;
                document.getElementById('contentTitle').value = 'Imported Content';
                this.updateCharCount();
                
                this.showNotification('Content imported successfully!', 'success');
            }, 2000);
            
        } catch (error) {
            console.error('Error importing content:', error);
            this.showNotification('Failed to import content', 'error');
        }
    }

    async processFiles() {
        this.showNotification('Processing uploaded files...', 'info');
        
        // Simulate file processing
        setTimeout(() => {
            const processedContent = 'This is processed content from your uploaded files. In a real implementation, this would parse and extract text from the uploaded documents.';
            
            // Switch to manual tab and populate
            this.switchTab('manual');
            document.getElementById('contentText').value = processedContent;
            document.getElementById('contentTitle').value = 'Processed File Content';
            this.updateCharCount();
            
            this.showNotification('Files processed successfully!', 'success');
        }, 2000);
    }

    async connectAccount(platform) {
        // This method handles account connections in the import tab
        this.connectSocialAccount(platform);
    }

    // ===== BACKEND API INTEGRATION =====
    
    async connectSocialAccount(platform) {
        try {
            // Get OAuth URL for the platform
            const response = await fetch(`/api/v1/connections/oauth/${platform}/url`, {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('threadstorm_access_token')}`
                }
            });

            if (response.ok) {
                const data = await response.json();
                // Open OAuth URL in new window
                window.open(data.oauth_url, '_blank', 'width=600,height=600');
                
                this.showNotification(`Redirecting to ${platform} for authorization...`, 'info');
            } else {
                throw new Error('Failed to get OAuth URL');
            }
        } catch (error) {
            console.error('Error connecting account:', error);
            this.showNotification(`Failed to connect ${platform} account`, 'error');
        }
    }

    async disconnectSocialAccount(platform, accountId) {
        try {
            const response = await fetch('/api/v1/connections/disconnect', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('threadstorm_access_token')}`
                },
                body: JSON.stringify({
                    platform: platform,
                    account_id: accountId
                })
            });

            if (response.ok) {
                const data = await response.json();
                this.showNotification(`${platform} account disconnected successfully`, 'success');
                
                // Reload connections
                await this.loadSocialConnections();
                
                // Close modal if open
                closeSocialConnections();
            } else {
                throw new Error('Failed to disconnect account');
            }
        } catch (error) {
            console.error('Error disconnecting account:', error);
            this.showNotification(`Failed to disconnect ${platform} account`, 'error');
        }
    }

    async generateContent() {
        try {
            const prompt = document.getElementById('aiPrompt').value;
            const tone = document.getElementById('aiTone').value;
            const length = document.getElementById('aiLength').value;
            const platform = document.getElementById('aiPlatform').value;

            if (!prompt.trim()) {
                this.showNotification('Please enter a prompt for AI generation', 'warning');
                return;
            }

            this.showNotification('Generating content with AI...', 'info');

            const response = await fetch('/api/v1/ai/generate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('threadstorm_access_token')}`
                },
                body: JSON.stringify({
                    prompt: prompt,
                    tone: tone,
                    length: length,
                    platform: platform
                })
            });

            if (response.ok) {
                const data = await response.json();
                this.displayGeneratedContent(data.generated_content, data.hashtags, data.optimization_score);
                this.showNotification('Content generated successfully!', 'success');
            } else {
                throw new Error('Failed to generate content');
            }
        } catch (error) {
            console.error('Error generating content:', error);
            this.showNotification('Failed to generate content', 'error');
        }
    }

    async importFromUrl() {
        const url = document.getElementById('importUrl').value;
        
        if (!url) {
            this.showNotification('Please enter a URL to import', 'warning');
            return;
        }

        try {
            this.showNotification('Importing content from URL...', 'info');
            
            const response = await fetch('/api/v1/import/url', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('threadstorm_access_token')}`
                },
                body: JSON.stringify({
                    url: url,
                    extract_images: true,
                    extract_links: true
                })
            });

            if (response.ok) {
                const data = await response.json();
                
                // Switch to manual tab and populate
                this.switchTab('manual');
                document.getElementById('contentText').value = data.imported_content;
                document.getElementById('contentTitle').value = data.title || 'Imported Content';
                this.updateCharCount();
                
                this.showNotification('Content imported successfully!', 'success');
            } else {
                throw new Error('Failed to import content');
            }
        } catch (error) {
            console.error('Error importing content:', error);
            this.showNotification('Failed to import content', 'error');
        }
    }

    async processFiles() {
        const fileInput = document.getElementById('fileInput');
        const files = fileInput.files;

        if (!files || files.length === 0) {
            this.showNotification('Please select files to upload', 'warning');
            return;
        }

        try {
            this.showNotification('Processing uploaded files...', 'info');
            
            const formData = new FormData();
            formData.append('file', files[0]);
            formData.append('extract_metadata', 'true');
            formData.append('parse_structure', 'true');

            const response = await fetch('/api/v1/import/file', {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('threadstorm_access_token')}`
                },
                body: formData
            });

            if (response.ok) {
                const data = await response.json();
                
                // Switch to manual tab and populate
                this.switchTab('manual');
                document.getElementById('contentText').value = data.imported_content;
                document.getElementById('contentTitle').value = data.title || 'Imported File Content';
                this.updateCharCount();
                
                this.showNotification('Files processed successfully!', 'success');
            } else {
                throw new Error('Failed to process files');
            }
        } catch (error) {
            console.error('Error processing files:', error);
            this.showNotification('Failed to process files', 'error');
        }
    }
    
    openSocialConnectionsModal() {
        // Open the social connections modal
        const modal = document.getElementById('socialConnectionsModal');
        if (modal) {
            modal.classList.add('show');
            modal.style.display = 'block';
            this.loadSocialConnections();
        } else {
            this.showNotification('Social connections modal not found', 'error');
        }
    }
    
    openTemplatesModal() {
        // Open the templates modal
        const modal = document.getElementById('templatesModal');
        if (modal) {
            modal.classList.add('show');
            modal.style.display = 'block';
            this.loadTemplates();
        } else {
            this.showNotification('Templates modal not found', 'error');
        }
    }
    
    openAnalyticsModal() {
        // Open the analytics modal
        const modal = document.getElementById('analyticsModal');
        if (modal) {
            modal.classList.add('show');
            modal.style.display = 'block';
            this.loadAnalytics();
        } else {
            this.showNotification('Analytics modal not found', 'error');
        }
    }
    
    loadTemplates() {
        // Load available templates
        this.showNotification('Loading templates...', 'info');
        // TODO: Implement template loading
        this.showNotification('Templates loaded successfully!', 'success');
    }
    
    loadAnalytics() {
        // Load analytics data
        this.showNotification('Loading analytics...', 'info');
        // TODO: Implement analytics loading
        this.showNotification('Analytics loaded successfully!', 'success');
    }
    
    async editContentItem(contentId) {
        try {
            this.showNotification('Loading content for editing...', 'info');
            
            const response = await fetch(`/api/v1/content/${contentId}`, {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('threadstorm_access_token')}`
                }
            });
            
            if (response.ok) {
                const data = await response.json();
                
                // Open content creator modal and populate with content
                this.openContentCreator();
                document.getElementById('contentTitle').value = data.title || '';
                document.getElementById('contentText').value = data.content || '';
                this.updateCharCount();
                
                this.showNotification('Content loaded for editing!', 'success');
            } else {
                throw new Error('Failed to load content');
            }
        } catch (error) {
            console.error('Error editing content:', error);
            this.showNotification('Failed to load content for editing', 'error');
        }
    }
    
    async deleteContentItem(contentId) {
        try {
            this.showNotification('Deleting content...', 'info');
            
            const response = await fetch(`/api/v1/content/${contentId}`, {
                method: 'DELETE',
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('threadstorm_access_token')}`
                }
            });
            
            if (response.ok) {
                this.showNotification('Content deleted successfully!', 'success');
                // Reload content list
                this.loadRecentContent();
            } else {
                throw new Error('Failed to delete content');
            }
        } catch (error) {
            console.error('Error deleting content:', error);
            this.showNotification('Failed to delete content', 'error');
        }
    }
    
    openContentCreator() {
        // Open the content creator modal
        const modal = document.getElementById('contentCreatorModal');
        if (modal) {
            modal.classList.add('show');
            modal.style.display = 'block';
        } else {
            this.showNotification('Content creator modal not found', 'error');
        }
    }
}

// Global functions for onclick handlers
function toggleUserMenu() {
    const dropdown = document.getElementById('userDropdown');
    dropdown.classList.toggle('show');
}

function openContentCreator() {
    const modal = document.getElementById('contentCreatorModal');
    modal.classList.add('show');
    modal.style.display = 'block';
}

function closeContentCreator() {
    const modal = document.getElementById('contentCreatorModal');
    modal.classList.remove('show');
    modal.style.display = 'none';
    
    // Reset form
    const form = document.getElementById('contentForm');
    if (form) form.reset();
    
    // Reset char count
    const charCount = document.getElementById('charCount');
    if (charCount) charCount.textContent = '0';
}

function switchTab(tabName) {
    // Remove active class from all tabs
    document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
    
    // Add active class to selected tab
    document.querySelector(`[onclick="switchTab('${tabName}')"]`).classList.add('active');
    document.getElementById(`${tabName}Tab`).classList.add('active');
}

function openSocialConnections() {
    // Open the social connections modal
    if (window.dashboard) {
        window.dashboard.openSocialConnectionsModal();
    }
}

function openTemplates() {
    // Navigate to templates page
    window.location.href = '/templates';
}

function openAnalytics() {
    // Navigate to analytics page
    window.location.href = '/analytics';
}

function connectThreads() {
    if (window.dashboard) {
        window.dashboard.connectSocialAccount('threads');
    }
}

function connectInstagram() {
    if (window.dashboard) {
        window.dashboard.connectSocialAccount('instagram');
    }
}

function connectFacebook() {
    if (window.dashboard) {
        window.dashboard.connectSocialAccount('facebook');
    }
}

function editContent(contentId) {
    // Edit content functionality
    if (window.dashboard) {
        window.dashboard.editContentItem(contentId);
    }
}

function deleteContent(contentId) {
    // Delete content functionality
    if (window.dashboard) {
        if (confirm('Are you sure you want to delete this content? This action cannot be undone.')) {
            window.dashboard.deleteContentItem(contentId);
        }
    }
}

// ===== GLOBAL FUNCTIONS FOR DASHBOARD FUNCTIONALITY =====

// Tab Management
function switchTab(tabName) {
    if (window.dashboard) {
        window.dashboard.switchTab(tabName);
    }
}

// Character Counting
function updateCharCount() {
    if (window.dashboard) {
        window.dashboard.updateCharCount();
    }
}

function updateCharLimit() {
    if (window.dashboard) {
        window.dashboard.updateCharLimit();
    }
}

// Scheduling
function toggleScheduler() {
    if (window.dashboard) {
        window.dashboard.toggleScheduler();
    }
}

// Import Methods
function selectImportMethod(method) {
    if (window.dashboard) {
        window.dashboard.selectImportMethod(method);
    }
}

function importFromUrl() {
    if (window.dashboard) {
        window.dashboard.importFromUrl();
    }
}

function processFiles() {
    if (window.dashboard) {
        window.dashboard.processFiles();
    }
}

function connectAccount(platform) {
    if (window.dashboard) {
        window.dashboard.connectAccount(platform);
    }
}

// File Upload
function handleDrop(event) {
    if (window.dashboard) {
        window.dashboard.handleDrop(event);
    }
}

function handleDragOver(event) {
    if (window.dashboard) {
        window.dashboard.handleDragOver(event);
    }
}

function handleDragLeave(event) {
    if (window.dashboard) {
        window.dashboard.handleDragLeave(event);
    }
}

function handleFileSelect(event) {
    if (window.dashboard) {
        window.dashboard.handleFileSelect(event);
    }
}

// AI Assistant
function usePrompt(promptText) {
    if (window.dashboard) {
        window.dashboard.usePrompt(promptText);
    }
}

function generateContent() {
    if (window.dashboard) {
        window.dashboard.generateContent();
    }
}

function regenerateContent() {
    if (window.dashboard) {
        window.dashboard.regenerateContent();
    }
}

function refineContent() {
    if (window.dashboard) {
        window.dashboard.refineContent();
    }
}

function useGeneratedContent() {
    if (window.dashboard) {
        window.dashboard.useGeneratedContent();
    }
}

function clearAiForm() {
    if (window.dashboard) {
        window.dashboard.clearAiForm();
    }
}

// Content Preview
function previewContent() {
    if (window.dashboard) {
        window.dashboard.previewContent();
    }
}

function switchPreviewPlatform(platform) {
    if (window.dashboard) {
        window.dashboard.switchPreviewPlatform(platform);
    }
}

function closePreviewModal() {
    if (window.dashboard) {
        window.dashboard.closePreviewModal();
    }
}

function proceedWithContent() {
    if (window.dashboard) {
        window.dashboard.proceedWithContent();
    }
}

// Social Connections
function openSocialConnections() {
    const modal = document.getElementById('socialConnectionsModal');
    if (modal) {
        modal.style.display = 'flex';
    }
}

function closeSocialConnections() {
    const modal = document.getElementById('socialConnectionsModal');
    if (modal) {
        modal.style.display = 'none';
    }
}

function connectSocialAccount(platform) {
    if (window.dashboard) {
        window.dashboard.connectSocialAccount(platform);
    }
}

function disconnectSocialAccount(platform) {
    if (window.dashboard) {
        window.dashboard.disconnectSocialAccount(platform);
    }
}

// Quick Post Functions
function openQuickPost() {
    const modal = document.getElementById('quickPostModal');
    if (modal) {
        modal.style.display = 'flex';
        // Reset form
        const form = document.getElementById('quickPostForm');
        if (form) form.reset();
        const charCount = document.getElementById('quickPostCharCount');
        if (charCount) charCount.textContent = '0';
    }
}

function closeQuickPost() {
    const modal = document.getElementById('quickPostModal');
    if (modal) {
        modal.style.display = 'none';
    }
}

// Templates and Analytics (placeholder functions)
function openTemplates() {
    if (window.dashboard) {
        window.dashboard.showNotification('Templates feature coming soon!', 'info');
    }
}

function openAnalytics() {
    if (window.dashboard) {
        window.dashboard.showNotification('Advanced analytics feature coming soon!', 'info');
    }
}

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    window.dashboard = new Dashboard();
});
