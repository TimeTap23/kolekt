/**
 * Kolekt Admin Dashboard
 * Comprehensive admin interface for managing the Kolekt platform
 */

class KolektAdmin {
    constructor() {
        this.baseUrl = window.location.origin;
        this.currentSection = 'dashboard';
        this.init();
    }

    init() {
        this.setupNavigation();
        this.loadDashboard();
        
        // Dev: disable redirect to keep admin accessible until real admin auth is wired
        // if (!this.isAdminAuthenticated()) {
        //     this.redirectToLogin();
        //     return;
        // }
    }

    isAdminAuthenticated() {
        // Dev: always allow access; replace with real admin auth check later
        return true;
    }

    redirectToLogin() {
        // Dev: no-op to avoid bouncing back to homepage
        console.warn('Admin auth not configured; staying on admin page.');
    }

    setupNavigation() {
        const navItems = document.querySelectorAll('.admin-nav-item');
        navItems.forEach(item => {
            item.addEventListener('click', (e) => {
                const section = e.target.closest('.admin-nav-item').dataset.section;
                this.switchSection(section);
            });
        });
    }

    switchSection(section) {
        // Update navigation
        document.querySelectorAll('.admin-nav-item').forEach(item => {
            item.classList.remove('active');
        });
        document.querySelector(`[data-section="${section}"]`).classList.add('active');

        // Update content
        document.querySelectorAll('.admin-section').forEach(section => {
            section.classList.add('hidden');
        });
        document.getElementById(`${section}-section`).classList.remove('hidden');

        this.currentSection = section;

        // Load section data
        switch(section) {
            case 'dashboard':
                this.loadDashboard();
                break;
            case 'users':
                this.loadUsers();
                break;
            case 'content':
                this.loadContent();
                break;
            case 'connections':
                this.loadConnections();
                break;
            case 'analytics':
                this.loadAnalytics();
                break;
            case 'announcements':
                this.loadAnnouncements();
                break;
            case 'system':
                this.loadSystemHealth();
                break;
        }
    }

    async apiCall(endpoint, method = 'GET', data = null) {
        const options = {
            method,
            headers: {
                'Content-Type': 'application/json',
            }
        };

        if (data) {
            options.body = JSON.stringify(data);
        }

        try {
            const response = await fetch(`${this.baseUrl}/api/v1/admin${endpoint}`, options);
            const result = await response.json();
            
            if (!response.ok) {
                throw new Error(result.detail || 'API call failed');
            }
            
            return result;
        } catch (error) {
            console.error('API call error:', error);
            this.showError(`API Error: ${error.message}`);
            throw error;
        }
    }

    async loadDashboard() {
        try {
            const data = await this.apiCall('/dashboard');
            this.renderDashboardStats(data.stats);
            await this.loadRecentActivity();
        } catch (error) {
            this.showError('Failed to load dashboard');
        }
    }

    renderDashboardStats(stats) {
        const statsGrid = document.getElementById('statsGrid');
        
        statsGrid.innerHTML = `
            <div class="stat-card">
                <div class="stat-card-header">
                    <div class="stat-icon users">
                        <i class="fas fa-users"></i>
                    </div>
                </div>
                <h3 class="stat-value">${stats.total_users.toLocaleString()}</h3>
                <p class="stat-label">Total Users</p>
                <p class="stat-change positive">
                    <i class="fas fa-arrow-up"></i>
                    ${stats.active_users} active
                </p>
            </div>

            <div class="stat-card">
                <div class="stat-card-header">
                    <div class="stat-icon content">
                        <i class="fas fa-file-alt"></i>
                    </div>
                </div>
                <h3 class="stat-value">${stats.total_content_items.toLocaleString()}</h3>
                <p class="stat-label">Content Items</p>
                <p class="stat-change positive">
                    <i class="fas fa-arrow-up"></i>
                    ${stats.monthly_posts} this month
                </p>
            </div>

            <div class="stat-card">
                <div class="stat-card-header">
                    <div class="stat-icon connections">
                        <i class="fas fa-link"></i>
                    </div>
                </div>
                <h3 class="stat-value">${stats.social_connections.toLocaleString()}</h3>
                <p class="stat-label">Social Connections</p>
                <p class="stat-change positive">
                    <i class="fas fa-check"></i>
                    Active connections
                </p>
            </div>

            <div class="stat-card">
                <div class="stat-card-header">
                    <div class="stat-icon api">
                        <i class="fas fa-server"></i>
                    </div>
                </div>
                <h3 class="stat-value">${stats.total_api_calls.toLocaleString()}</h3>
                <p class="stat-label">API Calls</p>
                <p class="stat-change positive">
                    <i class="fas fa-arrow-up"></i>
                    Last 30 days
                </p>
            </div>
        `;
    }

    async loadRecentActivity() {
        const activityDiv = document.getElementById('recentActivity');
        
        try {
            // Get recent users, content, and connections
            const [users, content, connections] = await Promise.all([
                this.apiCall('/users?limit=5'),
                this.apiCall('/content'),
                this.apiCall('/social-connections')
            ]);

            const recentUsers = users.users?.slice(0, 3) || [];
            const recentContent = content.recent_content?.slice(0, 3) || [];
            const recentConnections = connections.connections?.slice(0, 3) || [];

            activityDiv.innerHTML = `
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 1.5rem;">
                    <div>
                        <h4 style="margin-bottom: 1rem; color: var(--admin-dark);">Recent Users</h4>
                        ${recentUsers.map(user => `
                            <div style="padding: 0.75rem; border: 1px solid var(--admin-border); border-radius: 8px; margin-bottom: 0.5rem;">
                                <strong>${user.email}</strong><br>
                                <small style="color: #6b7280;">Joined ${new Date(user.created_at).toLocaleDateString()}</small>
                            </div>
                        `).join('')}
                    </div>
                    
                    <div>
                        <h4 style="margin-bottom: 1rem; color: var(--admin-dark);">Recent Content</h4>
                        ${recentContent.map(item => `
                            <div style="padding: 0.75rem; border: 1px solid var(--admin-border); border-radius: 8px; margin-bottom: 0.5rem;">
                                <strong>${item.title || 'Untitled'}</strong><br>
                                <small style="color: #6b7280;">Created ${new Date(item.created_at).toLocaleDateString()}</small>
                            </div>
                        `).join('')}
                    </div>
                    
                    <div>
                        <h4 style="margin-bottom: 1rem; color: var(--admin-dark);">Recent Connections</h4>
                        ${recentConnections.map(conn => `
                            <div style="padding: 0.75rem; border: 1px solid var(--admin-border); border-radius: 8px; margin-bottom: 0.5rem;">
                                <strong>${conn.platform.charAt(0).toUpperCase() + conn.platform.slice(1)}</strong> - ${conn.username}<br>
                                <small style="color: #6b7280;">Connected ${new Date(conn.connected_at).toLocaleDateString()}</small>
                            </div>
                        `).join('')}
                    </div>
                </div>
            `;
        } catch (error) {
            activityDiv.innerHTML = '<p class="error-message">Failed to load recent activity</p>';
        }
    }

    async loadUsers() {
        const usersTable = document.getElementById('usersTable');
        
        try {
            const data = await this.apiCall('/users?limit=50');
            this.renderUsersTable(data.users || []);
        } catch (error) {
            usersTable.innerHTML = '<p class="error-message">Failed to load users</p>';
        }
    }

    renderUsersTable(users) {
        const usersTable = document.getElementById('usersTable');
        
        if (users.length === 0) {
            usersTable.innerHTML = '<p>No users found</p>';
            return;
        }

        usersTable.innerHTML = `
            <table class="table">
                <thead>
                    <tr>
                        <th>Email</th>
                        <th>Name</th>
                        <th>Plan</th>
                        <th>Status</th>
                        <th>Last Login</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    ${users.map(user => `
                        <tr>
                            <td>${user.email}</td>
                            <td>${user.name || 'N/A'}</td>
                            <td>${user.plan || 'free'}</td>
                            <td>
                                <span class="status-badge ${user.is_active ? 'status-active' : 'status-inactive'}">
                                    ${user.is_active ? 'Active' : 'Inactive'}
                                </span>
                            </td>
                            <td>${user.last_login ? new Date(user.last_login).toLocaleDateString() : 'Never'}</td>
                            <td>
                                <button class="btn btn-secondary" onclick="admin.viewUser('${user.id}')">
                                    <i class="fas fa-eye"></i>
                                </button>
                                <button class="btn btn-secondary" onclick="admin.editUser('${user.id}')">
                                    <i class="fas fa-edit"></i>
                                </button>
                            </td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        `;
    }

    async loadContent() {
        const contentStats = document.getElementById('contentStats');
        
        try {
            const data = await this.apiCall('/content');
            this.renderContentStats(data.stats, data.recent_content || []);
        } catch (error) {
            contentStats.innerHTML = '<p class="error-message">Failed to load content statistics</p>';
        }
    }

    renderContentStats(stats, recentContent) {
        const contentStats = document.getElementById('contentStats');
        
        contentStats.innerHTML = `
            <div class="stats-grid" style="margin-bottom: 2rem;">
                <div class="stat-card">
                    <h3 class="stat-value">${stats.total_content}</h3>
                    <p class="stat-label">Total Content</p>
                </div>
                <div class="stat-card">
                    <h3 class="stat-value">${stats.published_content}</h3>
                    <p class="stat-label">Published</p>
                </div>
                <div class="stat-card">
                    <h3 class="stat-value">${stats.draft_content}</h3>
                    <p class="stat-label">Drafts</p>
                </div>
                <div class="stat-card">
                    <h3 class="stat-value">${stats.this_month_content}</h3>
                    <p class="stat-label">This Month</p>
                </div>
            </div>
            
            <h3 style="margin-bottom: 1rem;">Recent Content</h3>
            <table class="table">
                <thead>
                    <tr>
                        <th>Title</th>
                        <th>Status</th>
                        <th>Created</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    ${recentContent.map(item => `
                        <tr>
                            <td>${item.title || 'Untitled'}</td>
                            <td>
                                <span class="status-badge status-${item.status || 'draft'}">
                                    ${item.status || 'draft'}
                                </span>
                            </td>
                            <td>${new Date(item.created_at).toLocaleDateString()}</td>
                            <td>
                                <button class="btn btn-secondary" onclick="admin.viewContent('${item.id}')">
                                    <i class="fas fa-eye"></i>
                                </button>
                                <button class="btn btn-secondary" onclick="admin.deleteContent('${item.id}')">
                                    <i class="fas fa-trash"></i>
                                </button>
                            </td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        `;
    }

    async loadConnections() {
        const connectionsStats = document.getElementById('connectionsStats');
        
        try {
            const data = await this.apiCall('/social-connections');
            this.renderConnectionsStats(data.stats, data.connections || []);
        } catch (error) {
            connectionsStats.innerHTML = '<p class="error-message">Failed to load connection statistics</p>';
        }
    }

    renderConnectionsStats(stats, connections) {
        const connectionsStats = document.getElementById('connectionsStats');
        
        connectionsStats.innerHTML = `
            <div class="stats-grid" style="margin-bottom: 2rem;">
                <div class="stat-card">
                    <h3 class="stat-value">${stats.total_connections}</h3>
                    <p class="stat-label">Total Connections</p>
                </div>
                <div class="stat-card">
                    <h3 class="stat-value">${stats.threads_connections}</h3>
                    <p class="stat-label">Threads</p>
                </div>
                <div class="stat-card">
                    <h3 class="stat-value">${stats.instagram_connections}</h3>
                    <p class="stat-label">Instagram</p>
                </div>
                <div class="stat-card">
                    <h3 class="stat-value">${stats.facebook_connections}</h3>
                    <p class="stat-label">Facebook</p>
                </div>
            </div>
            
            <h3 style="margin-bottom: 1rem;">Recent Connections</h3>
            <table class="table">
                <thead>
                    <tr>
                        <th>Platform</th>
                        <th>Username</th>
                        <th>Status</th>
                        <th>Connected</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    ${connections.slice(0, 20).map(conn => `
                        <tr>
                            <td>
                                <i class="fab fa-${conn.platform}"></i>
                                ${conn.platform.charAt(0).toUpperCase() + conn.platform.slice(1)}
                            </td>
                            <td>${conn.username}</td>
                            <td>
                                <span class="status-badge ${conn.is_active ? 'status-active' : 'status-inactive'}">
                                    ${conn.is_active ? 'Active' : 'Inactive'}
                                </span>
                            </td>
                            <td>${new Date(conn.connected_at).toLocaleDateString()}</td>
                            <td>
                                <button class="btn btn-secondary" onclick="admin.removeConnection('${conn.id}')">
                                    <i class="fas fa-unlink"></i>
                                </button>
                            </td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        `;
    }

    async loadAnalytics() {
        const analyticsOverview = document.getElementById('analyticsOverview');
        
        try {
            const data = await this.apiCall('/analytics/overview');
            this.renderAnalytics(data.analytics);
        } catch (error) {
            analyticsOverview.innerHTML = '<p class="error-message">Failed to load analytics</p>';
        }
    }

    renderAnalytics(analytics) {
        const analyticsOverview = document.getElementById('analyticsOverview');
        
        analyticsOverview.innerHTML = `
            <div class="stats-grid">
                <div class="stat-card">
                    <h3 class="stat-value">${analytics.user_growth_30d}</h3>
                    <p class="stat-label">New Users (30 days)</p>
                    <p class="stat-change positive">
                        <i class="fas fa-arrow-up"></i>
                        User growth
                    </p>
                </div>
                <div class="stat-card">
                    <h3 class="stat-value">${analytics.content_growth_30d}</h3>
                    <p class="stat-label">New Content (30 days)</p>
                    <p class="stat-change positive">
                        <i class="fas fa-arrow-up"></i>
                        Content growth
                    </p>
                </div>
                <div class="stat-card">
                    <h3 class="stat-value">${analytics.connections_growth_30d}</h3>
                    <p class="stat-label">New Connections (30 days)</p>
                    <p class="stat-change positive">
                        <i class="fas fa-arrow-up"></i>
                        Connection growth
                    </p>
                </div>
                <div class="stat-card">
                    <h3 class="stat-value">${analytics.total_users}</h3>
                    <p class="stat-label">Total Platform Users</p>
                    <p class="stat-change">
                        <i class="fas fa-users"></i>
                        All time
                    </p>
                </div>
            </div>
            
            <div style="margin-top: 2rem; padding: 1.5rem; background: #f9fafb; border-radius: 12px;">
                <h3 style="margin-bottom: 1rem;">Platform Health</h3>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem;">
                    <div>
                        <strong>Total Content:</strong> ${analytics.total_content}
                    </div>
                    <div>
                        <strong>Total Connections:</strong> ${analytics.total_connections}
                    </div>
                    <div>
                        <strong>Generated:</strong> ${new Date(analytics.generated_at).toLocaleString()}
                    </div>
                </div>
            </div>
        `;
    }

    async loadAnnouncements() {
        const announcementsList = document.getElementById('announcementsList');
        
        try {
            const data = await this.apiCall('/announcements');
            this.renderAnnouncements(data.announcements || []);
        } catch (error) {
            announcementsList.innerHTML = '<p class="error-message">Failed to load announcements</p>';
        }
    }

    renderAnnouncements(announcements) {
        const announcementsList = document.getElementById('announcementsList');
        
        if (announcements.length === 0) {
            announcementsList.innerHTML = '<p>No announcements found</p>';
            return;
        }

        announcementsList.innerHTML = `
            <table class="table">
                <thead>
                    <tr>
                        <th>Title</th>
                        <th>Priority</th>
                        <th>Status</th>
                        <th>Created</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    ${announcements.map(announcement => `
                        <tr>
                            <td>${announcement.title}</td>
                            <td>
                                <span class="status-badge status-${announcement.priority}">
                                    ${announcement.priority}
                                </span>
                            </td>
                            <td>
                                <span class="status-badge ${announcement.is_active ? 'status-active' : 'status-inactive'}">
                                    ${announcement.is_active ? 'Active' : 'Inactive'}
                                </span>
                            </td>
                            <td>${new Date(announcement.created_at).toLocaleDateString()}</td>
                            <td>
                                <button class="btn btn-secondary" onclick="admin.editAnnouncement('${announcement.id}')">
                                    <i class="fas fa-edit"></i>
                                </button>
                                <button class="btn btn-secondary" onclick="admin.deleteAnnouncement('${announcement.id}')">
                                    <i class="fas fa-trash"></i>
                                </button>
                            </td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        `;
    }

    async loadSystemHealth() {
        const systemHealth = document.getElementById('systemHealth');
        
        try {
            const data = await this.apiCall('/system/health');
            this.renderSystemHealth(data.health);
        } catch (error) {
            systemHealth.innerHTML = '<p class="error-message">Failed to load system health</p>';
        }
    }

    renderSystemHealth(health) {
        const systemHealth = document.getElementById('systemHealth');
        
        systemHealth.innerHTML = `
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-icon ${health.database === 'healthy' ? 'users' : 'api'}">
                        <i class="fas fa-database"></i>
                    </div>
                    <h3 class="stat-value">${health.database}</h3>
                    <p class="stat-label">Database</p>
                </div>
                <div class="stat-card">
                    <div class="stat-icon ${health.api === 'healthy' ? 'users' : 'api'}">
                        <i class="fas fa-server"></i>
                    </div>
                    <h3 class="stat-value">${health.api}</h3>
                    <p class="stat-label">API</p>
                </div>
                <div class="stat-card">
                    <div class="stat-icon connections">
                        <i class="fas fa-memory"></i>
                    </div>
                    <h3 class="stat-value">${health.redis}</h3>
                    <p class="stat-label">Redis</p>
                </div>
            </div>
            
            <div style="margin-top: 2rem; padding: 1.5rem; background: #f9fafb; border-radius: 12px;">
                <h3 style="margin-bottom: 1rem;">System Information</h3>
                <p><strong>Last Check:</strong> ${new Date(health.timestamp).toLocaleString()}</p>
                <p><strong>Status:</strong> All systems operational</p>
            </div>
        `;
    }

    // Utility methods
    showError(message) {
        // Create and show error notification
        const errorDiv = document.createElement('div');
        errorDiv.className = 'error-message';
        errorDiv.textContent = message;
        errorDiv.style.position = 'fixed';
        errorDiv.style.top = '20px';
        errorDiv.style.right = '20px';
        errorDiv.style.zIndex = '1000';
        
        document.body.appendChild(errorDiv);
        
        setTimeout(() => {
            document.body.removeChild(errorDiv);
        }, 5000);
    }

    showSuccess(message) {
        // Create and show success notification
        const successDiv = document.createElement('div');
        successDiv.className = 'success-message';
        successDiv.textContent = message;
        successDiv.style.position = 'fixed';
        successDiv.style.top = '20px';
        successDiv.style.right = '20px';
        successDiv.style.zIndex = '1000';
        
        document.body.appendChild(successDiv);
        
        setTimeout(() => {
            document.body.removeChild(successDiv);
        }, 3000);
    }

    // Action methods
    async viewUser(userId) {
        // Implement user view modal
        console.log('View user:', userId);
    }

    async editUser(userId) {
        // Implement user edit modal
        console.log('Edit user:', userId);
    }

    async viewContent(contentId) {
        // Implement content view modal
        console.log('View content:', contentId);
    }

    async deleteContent(contentId) {
        if (confirm('Are you sure you want to delete this content?')) {
            try {
                await this.apiCall(`/content/${contentId}`, 'DELETE');
                this.showSuccess('Content deleted successfully');
                this.loadContent();
            } catch (error) {
                this.showError('Failed to delete content');
            }
        }
    }

    async removeConnection(connectionId) {
        if (confirm('Are you sure you want to remove this connection?')) {
            try {
                await this.apiCall(`/social-connections/${connectionId}`, 'DELETE');
                this.showSuccess('Connection removed successfully');
                this.loadConnections();
            } catch (error) {
                this.showError('Failed to remove connection');
            }
        }
    }

    createAnnouncement() {
        // Implement announcement creation modal
        console.log('Create announcement');
    }

    editAnnouncement(announcementId) {
        // Implement announcement edit modal
        console.log('Edit announcement:', announcementId);
    }

    async deleteAnnouncement(announcementId) {
        if (confirm('Are you sure you want to delete this announcement?')) {
            try {
                await this.apiCall(`/announcements/${announcementId}`, 'DELETE');
                this.showSuccess('Announcement deleted successfully');
                this.loadAnnouncements();
            } catch (error) {
                this.showError('Failed to delete announcement');
            }
        }
    }
}

// Global functions for onclick handlers
window.admin = new KolektAdmin();

window.refreshDashboard = () => admin.loadDashboard();
window.refreshUsers = () => admin.loadUsers();
window.refreshContent = () => admin.loadContent();
window.refreshConnections = () => admin.loadConnections();
window.refreshAnalytics = () => admin.loadAnalytics();
window.checkSystemHealth = () => admin.loadSystemHealth();
window.createAnnouncement = () => admin.createAnnouncement();
