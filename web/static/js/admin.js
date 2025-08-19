// ThreadStorm Admin Panel JavaScript
class AdminPanel {
    constructor() {
        this.baseUrl = '/api/v1';
        this.tokenKey = 'threadstorm_access_token';
        this.currentUser = null;
        this.currentPage = 1;
        this.usersPerPage = 50;
        
        this.init();
    }
    
    async init() {
        // Check if user is admin
        await this.checkAdminAccess();
        
        // Load dashboard by default
        this.loadDashboard();
        
        // Setup event listeners
        this.setupEventListeners();
    }
    
    async checkAdminAccess() {
        try {
            // For development, use a simple admin login
            const adminEmail = 'marcus@marteklabs.com';
            const adminPassword = 'Thr34dst0rm2025!';
            
            const response = await fetch(`${this.baseUrl}/admin/login`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    email: adminEmail,
                    password: adminPassword
                })
            });
            
            if (!response.ok) {
                this.redirectToLogin();
                return;
            }
            
            const result = await response.json();
            this.currentUser = result.user;
            
            // Update admin user name
            document.getElementById('admin-user-name').textContent = this.currentUser.name || this.currentUser.email;
            
        } catch (error) {
            console.error('Error checking admin access:', error);
            this.redirectToLogin();
        }
    }
    
    redirectToLogin() {
        window.location.href = '/';
    }
    
    redirectToMain() {
        window.location.href = '/';
    }
    
    setupEventListeners() {
        // Setup search and filter event listeners
        const userSearch = document.getElementById('user-search');
        if (userSearch) {
            userSearch.addEventListener('input', () => this.loadUsers(1));
        }
        
        const userPlanFilter = document.getElementById('user-plan-filter');
        if (userPlanFilter) {
            userPlanFilter.addEventListener('change', () => this.loadUsers(1));
        }
        
        const userStatusFilter = document.getElementById('user-status-filter');
        if (userStatusFilter) {
            userStatusFilter.addEventListener('change', () => this.loadUsers(1));
        }
        
        // Setup modal event listeners
        document.addEventListener('click', (event) => {
            if (event.target.classList.contains('admin-modal')) {
                this.closeModal(event.target.id);
            }
        });
    }
    
    // Navigation
    showSection(sectionName) {
        // Hide all sections
        document.querySelectorAll('.admin-section').forEach(section => {
            section.classList.remove('active');
        });
        
        // Show selected section
        document.getElementById(`${sectionName}-section`).classList.add('active');
        
        // Update navigation buttons
        document.querySelectorAll('.nav-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        document.querySelector(`[data-section="${sectionName}"]`).classList.add('active');
        
        // Load section data
        switch (sectionName) {
            case 'dashboard':
                this.loadDashboard();
                break;
            case 'users':
                this.loadUsers();
                break;
            case 'announcements':
                this.loadAnnouncements();
                break;
            case 'system':
                this.loadSystemHealth();
                break;
        }
    }
    
    // Dashboard
    async loadDashboard() {
        try {
            const response = await this.apiRequest('/admin/dashboard');
            
            if (response.success) {
                const stats = response.stats;
                
                document.getElementById('total-users').textContent = stats.total_users.toLocaleString();
                document.getElementById('active-users').textContent = stats.active_users.toLocaleString();
                document.getElementById('total-threadstorms').textContent = stats.total_threadstorms.toLocaleString();
                document.getElementById('total-api-calls').textContent = stats.total_api_calls.toLocaleString();
                document.getElementById('storage-used').textContent = `${stats.storage_used.toFixed(2)} MB`;
                document.getElementById('revenue-monthly').textContent = `$${stats.revenue_monthly.toFixed(2)}`;
            }
        } catch (error) {
            console.error('Error loading dashboard:', error);
            this.showNotification('Failed to load dashboard data', 'error');
        }
    }
    
    async refreshStats() {
        const spinner = document.getElementById('refresh-spinner');
        if (spinner) spinner.style.display = 'inline-block';
        
        try {
            await this.loadDashboard();
            this.showNotification('Dashboard refreshed', 'success');
        } finally {
            if (spinner) spinner.style.display = 'none';
        }
    }
    
    // User Management
    async loadUsers(page = 1) {
        try {
            const search = document.getElementById('user-search')?.value || '';
            const plan = document.getElementById('user-plan-filter')?.value || '';
            const status = document.getElementById('user-status-filter')?.value || '';
            
            let url = `/admin/users?page=${page}&limit=${this.usersPerPage}`;
            if (search) url += `&search=${encodeURIComponent(search)}`;
            if (plan) url += `&plan=${plan}`;
            if (status !== '') url += `&is_active=${status}`;
            
            const response = await this.apiRequest(url);
            
            if (response.success) {
                this.renderUsersTable(response.users);
                this.renderPagination(response.pagination);
                this.currentPage = page;
            }
        } catch (error) {
            console.error('Error loading users:', error);
            this.showNotification('Failed to load users', 'error');
        }
    }
    
    renderUsersTable(users) {
        const tbody = document.getElementById('users-table-body');
        if (!tbody) return;
        
        tbody.innerHTML = '';
        
        users.forEach(user => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${user.name || 'N/A'}</td>
                <td>${user.email}</td>
                <td><span class="status-badge status-${user.plan || 'free'}">${user.plan || 'free'}</span></td>
                <td><span class="status-badge ${user.is_active ? 'status-active' : 'status-inactive'}">${user.is_active ? 'Active' : 'Inactive'}</span></td>
                <td>${user.last_login ? new Date(user.last_login).toLocaleDateString() : 'Never'}</td>
                <td>
                    <button class="admin-btn admin-btn-secondary" onclick="adminPanel.editUser('${user.id}')">Edit</button>
                    <button class="admin-btn admin-btn-danger" onclick="adminPanel.deleteUser('${user.id}')">Delete</button>
                </td>
            `;
            tbody.appendChild(row);
        });
    }
    
    renderPagination(pagination) {
        const container = document.getElementById('users-pagination');
        if (!container) return;
        
        container.innerHTML = '';
        
        if (pagination.pages <= 1) return;
        
        // Previous button
        if (pagination.page > 1) {
            const prevBtn = document.createElement('button');
            prevBtn.textContent = '← Previous';
            prevBtn.className = 'pagination-btn';
            prevBtn.onclick = () => this.loadUsers(pagination.page - 1);
            container.appendChild(prevBtn);
        }
        
        // Page numbers
        for (let i = 1; i <= pagination.pages; i++) {
            const pageBtn = document.createElement('button');
            pageBtn.textContent = i;
            pageBtn.className = `pagination-btn ${i === pagination.page ? 'active' : ''}`;
            pageBtn.onclick = () => this.loadUsers(i);
            container.appendChild(pageBtn);
        }
        
        // Next button
        if (pagination.page < pagination.pages) {
            const nextBtn = document.createElement('button');
            nextBtn.textContent = 'Next →';
            nextBtn.className = 'pagination-btn';
            nextBtn.onclick = () => this.loadUsers(pagination.page + 1);
            container.appendChild(nextBtn);
        }
    }
    
    // User CRUD Operations
    showCreateUserModal() {
        document.getElementById('create-user-modal').classList.add('show');
    }
    
    async createUser() {
        try {
            const name = document.getElementById('new-user-name').value;
            const email = document.getElementById('new-user-email').value;
            const plan = document.getElementById('new-user-plan').value;
            const role = document.getElementById('new-user-role').value;
            
            if (!name || !email) {
                this.showNotification('Name and email are required', 'error');
                return;
            }
            
            const response = await this.apiRequest('/admin/users', {
                method: 'POST',
                body: JSON.stringify({
                    name,
                    email,
                    plan,
                    role,
                    password: 'tempPassword123!' // Will be changed by user
                })
            });
            
            if (response.success) {
                this.showNotification('User created successfully', 'success');
                this.closeModal('create-user-modal');
                this.loadUsers(this.currentPage);
                
                // Clear form
                document.getElementById('new-user-name').value = '';
                document.getElementById('new-user-email').value = '';
            }
        } catch (error) {
            console.error('Error creating user:', error);
            this.showNotification('Failed to create user', 'error');
        }
    }
    
    async editUser(userId) {
        try {
            const response = await this.apiRequest(`/admin/users/${userId}`);
            
            if (response.success) {
                const user = response.user;
                
                document.getElementById('edit-user-id').value = user.id;
                document.getElementById('edit-user-name').value = user.name || '';
                document.getElementById('edit-user-email').value = user.email;
                document.getElementById('edit-user-plan').value = user.plan || 'free';
                document.getElementById('edit-user-role').value = user.role || 'user';
                document.getElementById('edit-user-status').value = user.is_active ? 'true' : 'false';
                
                document.getElementById('edit-user-modal').classList.add('show');
            }
        } catch (error) {
            console.error('Error loading user:', error);
            this.showNotification('Failed to load user data', 'error');
        }
    }
    
    async updateUser() {
        try {
            const userId = document.getElementById('edit-user-id').value;
            const name = document.getElementById('edit-user-name').value;
            const email = document.getElementById('edit-user-email').value;
            const plan = document.getElementById('edit-user-plan').value;
            const role = document.getElementById('edit-user-role').value;
            const isActive = document.getElementById('edit-user-status').value === 'true';
            
            if (!name || !email) {
                this.showNotification('Name and email are required', 'error');
                return;
            }
            
            const response = await this.apiRequest(`/admin/users/${userId}`, {
                method: 'PUT',
                body: JSON.stringify({
                    name,
                    email,
                    plan,
                    role,
                    is_active: isActive
                })
            });
            
            if (response.success) {
                this.showNotification('User updated successfully', 'success');
                this.closeModal('edit-user-modal');
                this.loadUsers(this.currentPage);
            }
        } catch (error) {
            console.error('Error updating user:', error);
            this.showNotification('Failed to update user', 'error');
        }
    }
    
    async deleteUser(userId) {
        if (!confirm('Are you sure you want to delete this user?')) {
            return;
        }
        
        try {
            const response = await this.apiRequest(`/admin/users/${userId}`, {
                method: 'DELETE'
            });
            
            if (response.success) {
                this.showNotification('User deleted successfully', 'success');
                this.loadUsers(this.currentPage);
            }
        } catch (error) {
            console.error('Error deleting user:', error);
            this.showNotification('Failed to delete user', 'error');
        }
    }
    
    // Announcements
    async loadAnnouncements() {
        try {
            const response = await this.apiRequest('/admin/announcements');
            
            if (response.success) {
                this.renderAnnouncementsTable(response.announcements);
            }
        } catch (error) {
            console.error('Error loading announcements:', error);
            this.showNotification('Failed to load announcements', 'error');
        }
    }
    
    renderAnnouncementsTable(announcements) {
        const tbody = document.getElementById('announcements-table-body');
        if (!tbody) return;
        
        tbody.innerHTML = '';
        
        announcements.forEach(announcement => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${announcement.title}</td>
                <td><span class="status-badge status-${announcement.priority}">${announcement.priority}</span></td>
                <td><span class="status-badge ${announcement.is_active ? 'status-active' : 'status-inactive'}">${announcement.is_active ? 'Active' : 'Inactive'}</span></td>
                <td>${new Date(announcement.created_at).toLocaleDateString()}</td>
                <td>
                    <button class="admin-btn admin-btn-secondary" onclick="adminPanel.editAnnouncement('${announcement.id}')">Edit</button>
                    <button class="admin-btn admin-btn-danger" onclick="adminPanel.deleteAnnouncement('${announcement.id}')">Delete</button>
                </td>
            `;
            tbody.appendChild(row);
        });
    }
    
    showCreateAnnouncementModal() {
        document.getElementById('create-announcement-modal').classList.add('show');
    }
    
    async createAnnouncement() {
        try {
            const title = document.getElementById('new-announcement-title').value;
            const content = document.getElementById('new-announcement-content').value;
            const priority = document.getElementById('new-announcement-priority').value;
            
            if (!title || !content) {
                this.showNotification('Title and content are required', 'error');
                return;
            }
            
            const response = await this.apiRequest('/admin/announcements', {
                method: 'POST',
                body: JSON.stringify({
                    title,
                    content,
                    priority,
                    is_active: true
                })
            });
            
            if (response.success) {
                this.showNotification('Announcement created successfully', 'success');
                this.closeModal('create-announcement-modal');
                this.loadAnnouncements();
                
                // Clear form
                document.getElementById('new-announcement-title').value = '';
                document.getElementById('new-announcement-content').value = '';
            }
        } catch (error) {
            console.error('Error creating announcement:', error);
            this.showNotification('Failed to create announcement', 'error');
        }
    }
    
    // System Health
    async loadSystemHealth() {
        try {
            const response = await this.apiRequest('/admin/system/health');
            
            if (response.success) {
                this.renderSystemHealth(response.health);
            }
        } catch (error) {
            console.error('Error loading system health:', error);
            this.showNotification('Failed to load system health', 'error');
        }
    }
    
    renderSystemHealth(health) {
        const container = document.getElementById('system-health');
        if (!container) return;
        
        container.innerHTML = `
            <div class="health-item">
                <span>Database</span>
                <span class="health-status-text ${health.database === 'healthy' ? 'healthy' : 'unhealthy'}">${health.database}</span>
            </div>
            <div class="health-item">
                <span>API</span>
                <span class="health-status-text ${health.api === 'healthy' ? 'healthy' : 'unhealthy'}">${health.api}</span>
            </div>
            <div class="health-item">
                <span>Storage</span>
                <span class="health-status-text ${health.storage === 'healthy' ? 'healthy' : 'unhealthy'}">${health.storage}</span>
            </div>
        `;
    }
    
    // Modal Management
    closeModal(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.classList.remove('show');
        }
    }
    
    // API Helper
    async apiRequest(endpoint, options = {}) {
        const url = `${this.baseUrl}${endpoint}`;
        const config = {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        };
        
        const response = await fetch(url, config);
        return await response.json();
    }
    
    // Notifications
    showNotification(message, type = 'info') {
        const container = document.getElementById('admin-notification-container');
        if (!container) return;
        
        const notification = document.createElement('div');
        notification.className = `admin-notification admin-notification-${type}`;
        notification.innerHTML = `
            <span>${message}</span>
            <button onclick="this.parentElement.remove()">&times;</button>
        `;
        
        container.appendChild(notification);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (notification.parentElement) {
                notification.remove();
            }
        }, 5000);
    }
    
    // Logout
    logout() {
        localStorage.removeItem(this.tokenKey);
        this.redirectToMain();
    }
}

// Initialize admin panel when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.adminPanel = new AdminPanel();
});
