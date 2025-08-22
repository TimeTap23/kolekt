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
        
        // Show welcome message
        this.showSuccess('Welcome to Kolekt Admin Dashboard!');
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
            // If endpoint already includes the full path, use it directly
            const url = endpoint.startsWith('/api/') 
                ? `${this.baseUrl}${endpoint}`
                : `${this.baseUrl}/api/v1/admin${endpoint}`;
            
            const response = await fetch(url, options);
            
            if (!response.ok) {
                if (response.status === 401) {
                    throw new Error('Authentication required. Please log in as admin.');
                } else if (response.status === 403) {
                    throw new Error('Admin access required.');
                } else if (response.status === 404) {
                    throw new Error('API endpoint not found.');
                } else {
                    const errorData = await response.json().catch(() => ({}));
                    throw new Error(errorData.detail || `HTTP ${response.status}: ${response.statusText}`);
                }
            }
            
            const result = await response.json();
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
            this.showError('Failed to load dashboard: ' + error.message);
            this.renderDashboardFallback();
        }
    }

    renderDashboardFallback() {
        const statsGrid = document.getElementById('statsGrid');
        statsGrid.innerHTML = `
            <div class="stat-card">
                <div class="stat-card-header">
                    <div class="stat-icon users">
                        <i class="fas fa-users"></i>
                    </div>
                </div>
                <h3 class="stat-value">--</h3>
                <p class="stat-label">Total Users</p>
                <p class="stat-change">Loading...</p>
            </div>

            <div class="stat-card">
                <div class="stat-card-header">
                    <div class="stat-icon content">
                        <i class="fas fa-file-alt"></i>
                    </div>
                </div>
                <h3 class="stat-value">--</h3>
                <p class="stat-label">Content Items</p>
                <p class="stat-change">Loading...</p>
            </div>

            <div class="stat-card">
                <div class="stat-card-header">
                    <div class="stat-icon connections">
                        <i class="fas fa-link"></i>
                    </div>
                </div>
                <h3 class="stat-value">--</h3>
                <p class="stat-label">Social Connections</p>
                <p class="stat-change">Loading...</p>
            </div>

            <div class="stat-card">
                <div class="stat-card-header">
                    <div class="stat-icon api">
                        <i class="fas fa-server"></i>
                    </div>
                </div>
                <h3 class="stat-value">--</h3>
                <p class="stat-label">API Calls</p>
                <p class="stat-change">Loading...</p>
            </div>
        `;
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
                <h3 class="stat-value">${(stats.total_users || 0).toLocaleString()}</h3>
                <p class="stat-label">Total Users</p>
                <p class="stat-change positive">
                    <i class="fas fa-arrow-up"></i>
                    ${stats.active_users || 0} active
                </p>
            </div>

            <div class="stat-card">
                <div class="stat-card-header">
                    <div class="stat-icon content">
                        <i class="fas fa-file-alt"></i>
                    </div>
                </div>
                <h3 class="stat-value">${(stats.total_content_items || 0).toLocaleString()}</h3>
                <p class="stat-label">Content Items</p>
                <p class="stat-change positive">
                    <i class="fas fa-arrow-up"></i>
                    ${stats.monthly_posts || 0} this month
                </p>
            </div>

            <div class="stat-card">
                <div class="stat-card-header">
                    <div class="stat-icon connections">
                        <i class="fas fa-link"></i>
                    </div>
                </div>
                <h3 class="stat-value">${(stats.social_connections || 0).toLocaleString()}</h3>
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
                <h3 class="stat-value">${(stats.total_api_calls || 0).toLocaleString()}</h3>
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
                    this.apiCall('/users?limit=5').catch(() => ({ users: [] })),
                    this.apiCall('/content').catch(() => ({ recent_content: [] })),
                    this.apiCall('/social-connections').catch(() => ({ connections: [] }))
                ]);

            const recentUsers = users.users?.slice(0, 3) || [];
            const recentContent = content.recent_content?.slice(0, 3) || [];
            const recentConnections = connections.connections?.slice(0, 3) || [];

            activityDiv.innerHTML = `
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 1.5rem;">
                    <div>
                        <h4 style="margin-bottom: 1rem; color: var(--admin-dark);">Recent Users</h4>
                        ${recentUsers.length > 0 ? recentUsers.map(user => `
                            <div style="padding: 0.75rem; border: 1px solid var(--admin-border); border-radius: 8px; margin-bottom: 0.5rem;">
                                <strong>${user.email || 'Unknown'}</strong><br>
                                <small style="color: #6b7280;">Joined ${new Date(user.created_at || Date.now()).toLocaleDateString()}</small>
                            </div>
                        `).join('') : '<p style="color: #6b7280;">No recent users</p>'}
                    </div>
                    
                    <div>
                        <h4 style="margin-bottom: 1rem; color: var(--admin-dark);">Recent Content</h4>
                        ${recentContent.length > 0 ? recentContent.map(item => `
                            <div style="padding: 0.75rem; border: 1px solid var(--admin-border); border-radius: 8px; margin-bottom: 0.5rem;">
                                <strong>${item.title || 'Untitled'}</strong><br>
                                <small style="color: #6b7280;">Created ${new Date(item.created_at || item.added_at || Date.now()).toLocaleDateString()}</small>
                            </div>
                        `).join('') : '<p style="color: #6b7280;">No recent content</p>'}
                    </div>
                    
                    <div>
                        <h4 style="margin-bottom: 1rem; color: var(--admin-dark);">Recent Connections</h4>
                        ${recentConnections.length > 0 ? recentConnections.map(conn => `
                            <div style="padding: 0.75rem; border: 1px solid var(--admin-border); border-radius: 8px; margin-bottom: 0.5rem;">
                                <strong>${conn.platform ? conn.platform.charAt(0).toUpperCase() + conn.platform.slice(1) : 'Unknown'}</strong> - ${conn.username || 'Unknown'}<br>
                                <small style="color: #6b7280;">Connected ${new Date(conn.connected_at || Date.now()).toLocaleDateString()}</small>
                            </div>
                        `).join('') : '<p style="color: #6b7280;">No recent connections</p>'}
                    </div>
                </div>
            `;
        } catch (error) {
            activityDiv.innerHTML = '<p class="error-message">Failed to load recent activity: ' + error.message + '</p>';
        }
    }

    async loadUsers() {
        const usersTable = document.getElementById('usersTable');
        
        try {
                            const data = await this.apiCall('/users?limit=50');
            this.renderUsersTable(data.users || []);
        } catch (error) {
            usersTable.innerHTML = '<p class="error-message">Failed to load users: ' + error.message + '</p>';
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
                        <th>Role</th>
                        <th>Status</th>
                        <th>Last Login</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    ${users.map(user => `
                        <tr>
                            <td>${user.email || 'N/A'}</td>
                            <td>${user.name || 'N/A'}</td>
                            <td>${user.plan || 'free'}</td>
                            <td>${user.role || 'user'}</td>
                            <td>
                                <span class="status-badge ${user.is_active ? 'status-active' : 'status-inactive'}">
                                    ${user.is_active ? 'Active' : 'Inactive'}
                                </span>
                            </td>
                            <td>${user.last_login ? new Date(user.last_login).toLocaleDateString() : 'Never'}</td>
                            <td>
                                <button class="btn btn-secondary" onclick="admin.viewUser('${user.id}')" title="View Details">
                                    <i class="fas fa-eye"></i>
                                </button>
                                <button class="btn btn-primary" onclick="admin.editUser('${user.id}')" title="Edit User">
                                    <i class="fas fa-edit"></i>
                                </button>
                                <button class="btn btn-danger" onclick="admin.deleteUser('${user.id}')" title="Delete User">
                                    <i class="fas fa-trash"></i>
                                </button>
                            </td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        `;
    }

    // User Management Methods
    showCreateUserModal() {
        document.getElementById('createUserModal').classList.remove('hidden');
        document.getElementById('createUserForm').reset();
    }

    closeModal(modalId) {
        document.getElementById(modalId).classList.add('hidden');
    }

    async createUser(event) {
        event.preventDefault();
        const form = event.target;
        const formData = new FormData(form);
        const userData = Object.fromEntries(formData.entries());

        try {
                            const response = await this.apiCall('/users', 'POST', userData);
            this.showSuccess('User created successfully!');
            this.closeModal('createUserModal');
            this.loadUsers(); // Refresh the users table
        } catch (error) {
            this.showError('Failed to create user: ' + error.message);
        }
    }

    async viewUser(userId) {
        try {
            const user = await this.apiCall(`/api/v1/admin/users/${userId}`);
            this.renderUserDetails(user);
            document.getElementById('viewUserModal').classList.remove('hidden');
        } catch (error) {
            this.showError('Failed to load user details: ' + error.message);
        }
    }

    renderUserDetails(user) {
        const userDetails = document.getElementById('userDetails');
        userDetails.innerHTML = `
            <div style="padding: 1.5rem;">
                <div class="form-group">
                    <label>Email</label>
                    <p style="margin: 0; padding: 0.5rem; background: #f9fafb; border-radius: 4px;">${user.email}</p>
                </div>
                <div class="form-group">
                    <label>Name</label>
                    <p style="margin: 0; padding: 0.5rem; background: #f9fafb; border-radius: 4px;">${user.name || 'N/A'}</p>
                </div>
                <div class="form-group">
                    <label>Plan</label>
                    <p style="margin: 0; padding: 0.5rem; background: #f9fafb; border-radius: 4px;">${user.plan || 'free'}</p>
                </div>
                <div class="form-group">
                    <label>Role</label>
                    <p style="margin: 0; padding: 0.5rem; background: #f9fafb; border-radius: 4px;">${user.role || 'user'}</p>
                </div>
                <div class="form-group">
                    <label>Status</label>
                    <p style="margin: 0; padding: 0.5rem; background: #f9fafb; border-radius: 4px;">
                        <span class="status-badge ${user.is_active ? 'status-active' : 'status-inactive'}">
                            ${user.is_active ? 'Active' : 'Inactive'}
                        </span>
                    </p>
                </div>
                <div class="form-group">
                    <label>Created</label>
                    <p style="margin: 0; padding: 0.5rem; background: #f9fafb; border-radius: 4px;">${user.created_at ? new Date(user.created_at).toLocaleString() : 'N/A'}</p>
                </div>
                <div class="form-group">
                    <label>Last Login</label>
                    <p style="margin: 0; padding: 0.5rem; background: #f9fafb; border-radius: 4px;">${user.last_login ? new Date(user.last_login).toLocaleString() : 'Never'}</p>
                </div>
            </div>
        `;
    }

    async editUser(userId) {
        try {
            const user = await this.apiCall(`/api/v1/admin/users/${userId}`);
            this.populateEditForm(user);
            document.getElementById('editUserModal').classList.remove('hidden');
        } catch (error) {
            this.showError('Failed to load user for editing: ' + error.message);
        }
    }

    populateEditForm(user) {
        document.getElementById('editUserId').value = user.id;
        document.getElementById('editUserEmail').value = user.email || '';
        document.getElementById('editUserName').value = user.name || '';
        document.getElementById('editUserPlan').value = user.plan || 'free';
        document.getElementById('editUserRole').value = user.role || 'user';
        document.getElementById('editUserActive').checked = user.is_active !== false;
    }

    async updateUser(event) {
        event.preventDefault();
        const form = event.target;
        const formData = new FormData(form);
        const userData = Object.fromEntries(formData.entries());
        const userId = userData.id;

        // Remove id from userData as it's not needed for the update
        delete userData.id;

        try {
            const response = await this.apiCall(`/api/v1/admin/users/${userId}`, 'PUT', userData);
            this.showSuccess('User updated successfully!');
            this.closeModal('editUserModal');
            this.loadUsers(); // Refresh the users table
        } catch (error) {
            this.showError('Failed to update user: ' + error.message);
        }
    }

    async deleteUser(userId) {
        if (!userId) {
            // Get userId from the edit form if not provided
            userId = document.getElementById('editUserId').value;
        }

        if (!confirm('Are you sure you want to delete this user? This action cannot be undone.')) {
            return;
        }

        try {
            await this.apiCall(`/api/v1/admin/users/${userId}`, 'DELETE');
            this.showSuccess('User deleted successfully!');
            this.closeModal('editUserModal');
            this.loadUsers(); // Refresh the users table
        } catch (error) {
            this.showError('Failed to delete user: ' + error.message);
        }
    }

    editCurrentUser() {
        // Close view modal and open edit modal
        this.closeModal('viewUserModal');
        // The edit form should already be populated from the viewUser call
        document.getElementById('editUserModal').classList.remove('hidden');
    }

    async loadContent() {
        const contentStats = document.getElementById('contentStats');
        
        try {
                            const data = await this.apiCall('/content');
            this.renderContentStats(data.stats, data.recent_content || []);
        } catch (error) {
            contentStats.innerHTML = '<p class="error-message">Failed to load content statistics: ' + error.message + '</p>';
        }
    }

    renderContentStats(stats, recentContent) {
        const contentStats = document.getElementById('contentStats');
        
        contentStats.innerHTML = `
            <div class="stats-grid" style="margin-bottom: 2rem;">
                <div class="stat-card">
                    <h3 class="stat-value">${stats.total_content || 0}</h3>
                    <p class="stat-label">Total Content</p>
                </div>
                <div class="stat-card">
                    <h3 class="stat-value">${stats.published_content || 0}</h3>
                    <p class="stat-label">Published</p>
                </div>
                <div class="stat-card">
                    <h3 class="stat-value">${stats.draft_content || 0}</h3>
                    <p class="stat-label">Drafts</p>
                </div>
                <div class="stat-card">
                    <h3 class="stat-value">${stats.this_month_content || 0}</h3>
                    <p class="stat-label">This Month</p>
                </div>
            </div>
            
            <h3 style="margin-bottom: 1rem;">Recent Content</h3>
            ${recentContent.length > 0 ? `
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
                                <td>${new Date(item.created_at || item.added_at || Date.now()).toLocaleDateString()}</td>
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
            ` : '<p>No recent content found</p>'}
        `;
    }

    async loadConnections() {
        const connectionsStats = document.getElementById('connectionsStats');
        
        try {
                            const data = await this.apiCall('/social-connections');
            this.renderConnectionsStats(data.stats, data.connections || []);
        } catch (error) {
            connectionsStats.innerHTML = '<p class="error-message">Failed to load connection statistics: ' + error.message + '</p>';
        }
    }

    renderConnectionsStats(stats, connections) {
        const connectionsStats = document.getElementById('connectionsStats');
        
        connectionsStats.innerHTML = `
            <div class="stats-grid" style="margin-bottom: 2rem;">
                <div class="stat-card">
                    <h3 class="stat-value">${stats.total_connections || 0}</h3>
                    <p class="stat-label">Total Connections</p>
                </div>
                <div class="stat-card">
                    <h3 class="stat-value">${stats.threads_connections || 0}</h3>
                    <p class="stat-label">Threads</p>
                </div>
                <div class="stat-card">
                    <h3 class="stat-value">${stats.instagram_connections || 0}</h3>
                    <p class="stat-label">Instagram</p>
                </div>
                <div class="stat-card">
                    <h3 class="stat-value">${stats.facebook_connections || 0}</h3>
                    <p class="stat-label">Facebook</p>
                </div>
            </div>
            
            <h3 style="margin-bottom: 1rem;">Recent Connections</h3>
            ${connections.length > 0 ? `
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
                                    <i class="fab fa-${conn.platform || 'link'}"></i>
                                    ${conn.platform ? conn.platform.charAt(0).toUpperCase() + conn.platform.slice(1) : 'Unknown'}
                                </td>
                                <td>${conn.username || 'Unknown'}</td>
                                <td>
                                    <span class="status-badge ${conn.is_active ? 'status-active' : 'status-inactive'}">
                                        ${conn.is_active ? 'Active' : 'Inactive'}
                                    </span>
                                </td>
                                <td>${new Date(conn.connected_at || Date.now()).toLocaleDateString()}</td>
                                <td>
                                    <button class="btn btn-secondary" onclick="admin.removeConnection('${conn.id}')">
                                        <i class="fas fa-unlink"></i>
                                    </button>
                                </td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            ` : '<p>No connections found</p>'}
        `;
    }

    async loadAnalytics() {
        const analyticsOverview = document.getElementById('analyticsOverview');
        
        try {
                            const data = await this.apiCall('/analytics/overview');
            this.renderAnalytics(data.analytics);
        } catch (error) {
            analyticsOverview.innerHTML = '<p class="error-message">Failed to load analytics: ' + error.message + '</p>';
        }
    }

    renderAnalytics(analytics) {
        const analyticsOverview = document.getElementById('analyticsOverview');
        
        analyticsOverview.innerHTML = `
            <div class="stats-grid">
                <div class="stat-card">
                    <h3 class="stat-value">${analytics.user_growth_30d || 0}</h3>
                    <p class="stat-label">New Users (30 days)</p>
                    <p class="stat-change positive">
                        <i class="fas fa-arrow-up"></i>
                        User growth
                    </p>
                </div>
                <div class="stat-card">
                    <h3 class="stat-value">${analytics.content_growth_30d || 0}</h3>
                    <p class="stat-label">New Content (30 days)</p>
                    <p class="stat-change positive">
                        <i class="fas fa-arrow-up"></i>
                        Content growth
                    </p>
                </div>
                <div class="stat-card">
                    <h3 class="stat-value">${analytics.connections_growth_30d || 0}</h3>
                    <p class="stat-label">New Connections (30 days)</p>
                    <p class="stat-change positive">
                        <i class="fas fa-arrow-up"></i>
                        Connection growth
                    </p>
                </div>
                <div class="stat-card">
                    <h3 class="stat-value">${analytics.total_users || 0}</h3>
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
                        <strong>Total Content:</strong> ${analytics.total_content || 0}
                    </div>
                    <div>
                        <strong>Total Connections:</strong> ${analytics.total_connections || 0}
                    </div>
                    <div>
                        <strong>Generated:</strong> ${new Date(analytics.generated_at || Date.now()).toLocaleString()}
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
            announcementsList.innerHTML = '<p class="error-message">Failed to load announcements: ' + error.message + '</p>';
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
                            <td>${announcement.title || 'Untitled'}</td>
                            <td>
                                <span class="status-badge status-${announcement.priority || 'normal'}">
                                    ${announcement.priority || 'normal'}
                                </span>
                            </td>
                            <td>
                                <span class="status-badge ${announcement.is_active ? 'status-active' : 'status-inactive'}">
                                    ${announcement.is_active ? 'Active' : 'Inactive'}
                                </span>
                            </td>
                            <td>${new Date(announcement.created_at || Date.now()).toLocaleDateString()}</td>
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
            systemHealth.innerHTML = '<p class="error-message">Failed to load system health: ' + error.message + '</p>';
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
                    <h3 class="stat-value">${health.database || 'unknown'}</h3>
                    <p class="stat-label">Database</p>
                </div>
                <div class="stat-card">
                    <div class="stat-icon ${health.api === 'healthy' ? 'users' : 'api'}">
                        <i class="fas fa-server"></i>
                    </div>
                    <h3 class="stat-value">${health.api || 'unknown'}</h3>
                    <p class="stat-label">API</p>
                </div>
                <div class="stat-card">
                    <div class="stat-icon connections">
                        <i class="fas fa-memory"></i>
                    </div>
                    <h3 class="stat-value">${health.redis || 'unknown'}</h3>
                    <p class="stat-label">Redis</p>
                </div>
            </div>
            
            <div style="margin-top: 2rem; padding: 1.5rem; background: #f9fafb; border-radius: 12px;">
                <h3 style="margin-bottom: 1rem;">System Information</h3>
                <p><strong>Last Check:</strong> ${new Date(health.timestamp || Date.now()).toLocaleString()}</p>
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
            if (document.body.contains(errorDiv)) {
                document.body.removeChild(errorDiv);
            }
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
            if (document.body.contains(successDiv)) {
                document.body.removeChild(successDiv);
            }
        }, 3000);
    }

    // Action methods
    async viewUser(userId) {
        this.showError('User view feature not implemented yet');
    }

    async editUser(userId) {
        this.showError('User edit feature not implemented yet');
    }

    async viewContent(contentId) {
        this.showError('Content view feature not implemented yet');
    }

    async deleteContent(contentId) {
        if (confirm('Are you sure you want to delete this content?')) {
            try {
                await this.apiCall(`/api/v1/admin/content/${contentId}`, 'DELETE');
                this.showSuccess('Content deleted successfully');
                this.loadContent();
            } catch (error) {
                this.showError('Failed to delete content: ' + error.message);
            }
        }
    }

    async removeConnection(connectionId) {
        if (confirm('Are you sure you want to remove this connection?')) {
            try {
                await this.apiCall(`/api/v1/admin/social-connections/${connectionId}`, 'DELETE');
                this.showSuccess('Connection removed successfully');
                this.loadConnections();
            } catch (error) {
                this.showError('Failed to remove connection: ' + error.message);
            }
        }
    }

    createAnnouncement() {
        this.showError('Announcement creation feature not implemented yet');
    }

    editAnnouncement(announcementId) {
        this.showError('Announcement edit feature not implemented yet');
    }

    async deleteAnnouncement(announcementId) {
        if (confirm('Are you sure you want to delete this announcement?')) {
            try {
                await this.apiCall(`/api/v1/admin/announcements/${announcementId}`, 'DELETE');
                this.showSuccess('Announcement deleted successfully');
                this.loadAnnouncements();
            } catch (error) {
                this.showError('Failed to delete announcement: ' + error.message);
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
