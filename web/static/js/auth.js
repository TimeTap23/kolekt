// ThreadStorm Authentication JavaScript
// Handles user authentication, token management, and session persistence

class ThreadStormAuth {
    constructor() {
        this.baseUrl = '/api/v1';
        this.tokenKey = 'threadstorm_access_token';
        this.refreshTokenKey = 'threadstorm_refresh_token';
        this.userKey = 'threadstorm_user';
        this.isAuthenticated = false;
        this.currentUser = null;
        this.tokenRefreshTimer = null;
        
        // Initialize authentication
        this.init();
    }
    
    async init() {
        // Check for existing tokens
        const token = this.getAccessToken();
        if (token) {
            try {
                // Verify token is still valid
                await this.verifyToken();
                this.isAuthenticated = true;
                this.setupTokenRefresh();
                this.updateUI();
            } catch (error) {
                console.log('Token invalid, clearing auth state');
                this.logout();
            }
        } else {
            this.showLoginForm();
        }
    }
    
    // Token Management
    getAccessToken() {
        return localStorage.getItem(this.tokenKey);
    }
    
    getRefreshToken() {
        return localStorage.getItem(this.refreshTokenKey);
    }
    
    setTokens(accessToken, refreshToken) {
        localStorage.setItem(this.tokenKey, accessToken);
        localStorage.setItem(this.refreshTokenKey, refreshToken);
    }
    
    clearTokens() {
        localStorage.removeItem(this.tokenKey);
        localStorage.removeItem(this.refreshTokenKey);
        localStorage.removeItem(this.userKey);
    }
    
    // User Management
    getCurrentUser() {
        const userStr = localStorage.getItem(this.userKey);
        return userStr ? JSON.parse(userStr) : null;
    }
    
    setCurrentUser(user) {
        localStorage.setItem(this.userKey, JSON.stringify(user));
        this.currentUser = user;
    }
    
    // Authentication Methods
    async register(email, password, name = null) {
        try {
            const response = await fetch(`${this.baseUrl}/auth/register`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    email,
                    password,
                    name
                })
            });
            
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.detail || 'Registration failed');
            }
            
            this.showNotification('Registration successful! Please check your email to verify your account.', 'success');
            return data;
            
        } catch (error) {
            console.error('Registration error:', error);
            this.showNotification(error.message, 'error');
            throw error;
        }
    }
    
    async login(email, password) {
        try {
            const response = await fetch(`${this.baseUrl}/auth/login`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    email,
                    password
                })
            });
            
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.detail || 'Login failed');
            }
            
            // Store tokens and user data
            this.setTokens(data.access_token, data.refresh_token);
            this.setCurrentUser(data.user);
            this.isAuthenticated = true;
            
            // Setup token refresh
            this.setupTokenRefresh();
            
            // Update UI
            this.updateUI();
            this.hideAuthForms();
            
            this.showNotification('Login successful!', 'success');
            return data;
            
        } catch (error) {
            console.error('Login error:', error);
            this.showNotification(error.message, 'error');
            throw error;
        }
    }
    
    async logout() {
        try {
            const refreshToken = this.getRefreshToken();
            if (refreshToken) {
                await fetch(`${this.baseUrl}/auth/logout`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${this.getAccessToken()}`
                    },
                    body: JSON.stringify({
                        refresh_token: refreshToken
                    })
                });
            }
        } catch (error) {
            console.error('Logout error:', error);
        } finally {
            // Clear local state
            this.clearTokens();
            this.isAuthenticated = false;
            this.currentUser = null;
            
            // Clear refresh timer
            if (this.tokenRefreshTimer) {
                clearTimeout(this.tokenRefreshTimer);
                this.tokenRefreshTimer = null;
            }
            
            // Update UI
            this.updateUI();
            this.showLoginForm();
            
            this.showNotification('Logged out successfully', 'info');
        }
    }
    
    async refreshToken() {
        try {
            const refreshToken = this.getRefreshToken();
            if (!refreshToken) {
                throw new Error('No refresh token available');
            }
            
            const response = await fetch(`${this.baseUrl}/auth/refresh`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    refresh_token: refreshToken
                })
            });
            
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.detail || 'Token refresh failed');
            }
            
            // Update access token
            localStorage.setItem(this.tokenKey, data.access_token);
            
            // Setup next refresh
            this.setupTokenRefresh();
            
            return data.access_token;
            
        } catch (error) {
            console.error('Token refresh error:', error);
            // If refresh fails, logout user
            this.logout();
            throw error;
        }
    }
    
    async verifyToken() {
        try {
            const response = await fetch(`${this.baseUrl}/auth/me`, {
                headers: {
                    'Authorization': `Bearer ${this.getAccessToken()}`
                }
            });
            
            if (!response.ok) {
                throw new Error('Token verification failed');
            }
            
            const user = await response.json();
            this.setCurrentUser(user);
            return user;
            
        } catch (error) {
            console.error('Token verification error:', error);
            throw error;
        }
    }
    
    // Token Refresh Setup
    setupTokenRefresh() {
        // Clear existing timer
        if (this.tokenRefreshTimer) {
            clearTimeout(this.tokenRefreshTimer);
        }
        
        // Set up refresh 5 minutes before token expires (25 minutes from now)
        const refreshTime = 25 * 60 * 1000; // 25 minutes
        this.tokenRefreshTimer = setTimeout(() => {
            this.refreshToken().catch(error => {
                console.error('Auto token refresh failed:', error);
            });
        }, refreshTime);
    }
    
    // API Request Helper
    async apiRequest(endpoint, options = {}) {
        const token = this.getAccessToken();
        
        const defaultHeaders = {
            'Content-Type': 'application/json',
        };
        
        if (token) {
            defaultHeaders['Authorization'] = `Bearer ${token}`;
        }
        
        const config = {
            ...options,
            headers: {
                ...defaultHeaders,
                ...options.headers
            }
        };
        
        try {
            const response = await fetch(`${this.baseUrl}${endpoint}`, config);
            
            // If token expired, try to refresh
            if (response.status === 401) {
                try {
                    await this.refreshToken();
                    // Retry request with new token
                    config.headers['Authorization'] = `Bearer ${this.getAccessToken()}`;
                    return await fetch(`${this.baseUrl}${endpoint}`, config);
                } catch (refreshError) {
                    // If refresh fails, logout
                    this.logout();
                    throw new Error('Authentication required');
                }
            }
            
            return response;
            
        } catch (error) {
            console.error('API request error:', error);
            throw error;
        }
    }
    
    // UI Methods
    showLoginForm() {
        const authContainer = document.getElementById('auth-container');
        if (authContainer) {
            authContainer.innerHTML = `
                <div class="auth-form">
                    <h2>Welcome to ThreadStorm</h2>
                    <div class="auth-tabs">
                        <button class="auth-tab active" onclick="threadStormAuth.showTab('login')">Login</button>
                        <button class="auth-tab" onclick="threadStormAuth.showTab('register')">Register</button>
                    </div>
                    
                    <div id="login-tab" class="auth-tab-content active">
                        <form id="login-form" onsubmit="threadStormAuth.handleLogin(event)">
                            <div class="form-group">
                                <label for="login-email">Email</label>
                                <input type="email" id="login-email" required>
                            </div>
                            <div class="form-group">
                                <label for="login-password">Password</label>
                                <input type="password" id="login-password" required>
                            </div>
                            <button type="submit" class="btn btn-primary">Login</button>
                        </form>
                        <div class="auth-links">
                            <a href="#" onclick="threadStormAuth.showForgotPassword()">Forgot Password?</a>
                        </div>
                    </div>
                    
                    <div id="register-tab" class="auth-tab-content">
                        <form id="register-form" onsubmit="threadStormAuth.handleRegister(event)">
                            <div class="form-group">
                                <label for="register-name">Name</label>
                                <input type="text" id="register-name" required>
                            </div>
                            <div class="form-group">
                                <label for="register-email">Email</label>
                                <input type="email" id="register-email" required>
                            </div>
                            <div class="form-group">
                                <label for="register-password">Password</label>
                                <input type="password" id="register-password" required minlength="8">
                            </div>
                            <div class="form-group">
                                <label for="register-confirm-password">Confirm Password</label>
                                <input type="password" id="register-confirm-password" required minlength="8">
                            </div>
                            <button type="submit" class="btn btn-primary">Register</button>
                        </form>
                    </div>
                </div>
            `;
        }
    }
    
    showTab(tabName) {
        // Update tab buttons
        document.querySelectorAll('.auth-tab').forEach(tab => {
            tab.classList.remove('active');
        });
        event.target.classList.add('active');
        
        // Update tab content
        document.querySelectorAll('.auth-tab-content').forEach(content => {
            content.classList.remove('active');
        });
        document.getElementById(`${tabName}-tab`).classList.add('active');
    }
    
    hideAuthForms() {
        const authContainer = document.getElementById('auth-container');
        if (authContainer) {
            authContainer.innerHTML = '';
        }
    }
    
    updateUI() {
        const user = this.getCurrentUser();
        
        if (this.isAuthenticated && user) {
            // Show user info in header
            this.updateHeader(user);
            
            // Show main content
            this.showMainContent();
            
            // Update navigation
            this.updateNavigation();
        } else {
            // Show login form
            this.showLoginForm();
        }
    }
    
    updateHeader(user) {
        const header = document.querySelector('.header');
        if (header) {
            const userInfo = header.querySelector('.user-info') || document.createElement('div');
            userInfo.className = 'user-info';
            userInfo.innerHTML = `
                <div class="user-profile">
                    <span class="user-name">${user.name}</span>
                    <span class="user-plan">${user.plan}</span>
                </div>
                <div class="user-actions">
                    <button class="btn btn-secondary" onclick="threadStormAuth.showProfile()">Profile</button>
                    <button class="btn btn-danger" onclick="threadStormAuth.logout()">Logout</button>
                </div>
            `;
            
            if (!header.querySelector('.user-info')) {
                header.appendChild(userInfo);
            }
        }
    }
    
    showMainContent() {
        const mainContent = document.getElementById('main-content');
        if (mainContent) {
            mainContent.style.display = 'block';
        }
    }
    
    updateNavigation() {
        // Update navigation based on user permissions
        const user = this.getCurrentUser();
        if (user) {
            // Show/hide features based on plan
            const proFeatures = document.querySelectorAll('.pro-feature');
            const businessFeatures = document.querySelectorAll('.business-feature');
            
            proFeatures.forEach(feature => {
                feature.style.display = ['pro', 'business', 'admin'].includes(user.plan) ? 'block' : 'none';
            });
            
            businessFeatures.forEach(feature => {
                feature.style.display = ['business', 'admin'].includes(user.plan) ? 'block' : 'none';
            });
        }
    }
    
    // Form Handlers
    async handleLogin(event) {
        event.preventDefault();
        
        const email = document.getElementById('login-email').value;
        const password = document.getElementById('login-password').value;
        
        try {
            await this.login(email, password);
        } catch (error) {
            // Error already handled in login method
        }
    }
    
    async handleRegister(event) {
        event.preventDefault();
        
        const name = document.getElementById('register-name').value;
        const email = document.getElementById('register-email').value;
        const password = document.getElementById('register-password').value;
        const confirmPassword = document.getElementById('register-confirm-password').value;
        
        if (password !== confirmPassword) {
            this.showNotification('Passwords do not match', 'error');
            return;
        }
        
        try {
            await this.register(email, password, name);
        } catch (error) {
            // Error already handled in register method
        }
    }
    
    // Profile Management
    async showProfile() {
        try {
            const user = await this.apiRequest('/auth/me');
            const userData = await user.json();
            
            this.showModal('Profile', `
                <div class="profile-form">
                    <form id="profile-form" onsubmit="threadStormAuth.handleProfileUpdate(event)">
                        <div class="form-group">
                            <label for="profile-name">Name</label>
                            <input type="text" id="profile-name" value="${userData.name}" required>
                        </div>
                        <div class="form-group">
                            <label for="profile-email">Email</label>
                            <input type="email" id="profile-email" value="${userData.email}" disabled>
                        </div>
                        <div class="form-group">
                            <label for="profile-plan">Plan</label>
                            <input type="text" id="profile-plan" value="${userData.plan}" disabled>
                        </div>
                        <button type="submit" class="btn btn-primary">Update Profile</button>
                    </form>
                    
                    <hr>
                    
                    <h3>Change Password</h3>
                    <form id="password-form" onsubmit="threadStormAuth.handlePasswordChange(event)">
                        <div class="form-group">
                            <label for="current-password">Current Password</label>
                            <input type="password" id="current-password" required>
                        </div>
                        <div class="form-group">
                            <label for="new-password">New Password</label>
                            <input type="password" id="new-password" required minlength="8">
                        </div>
                        <div class="form-group">
                            <label for="confirm-new-password">Confirm New Password</label>
                            <input type="password" id="confirm-new-password" required minlength="8">
                        </div>
                        <button type="submit" class="btn btn-secondary">Change Password</button>
                    </form>
                </div>
            `);
        } catch (error) {
            this.showNotification('Failed to load profile', 'error');
        }
    }
    
    async handleProfileUpdate(event) {
        event.preventDefault();
        
        const name = document.getElementById('profile-name').value;
        
        try {
            const response = await this.apiRequest('/auth/profile', {
                method: 'PUT',
                body: JSON.stringify({ name })
            });
            
            if (response.ok) {
                this.showNotification('Profile updated successfully', 'success');
                this.closeModal();
                // Refresh user data
                await this.verifyToken();
                this.updateUI();
            } else {
                const error = await response.json();
                this.showNotification(error.detail || 'Failed to update profile', 'error');
            }
        } catch (error) {
            this.showNotification('Failed to update profile', 'error');
        }
    }
    
    async handlePasswordChange(event) {
        event.preventDefault();
        
        const currentPassword = document.getElementById('current-password').value;
        const newPassword = document.getElementById('new-password').value;
        const confirmNewPassword = document.getElementById('confirm-new-password').value;
        
        if (newPassword !== confirmNewPassword) {
            this.showNotification('New passwords do not match', 'error');
            return;
        }
        
        try {
            const response = await this.apiRequest('/auth/change-password', {
                method: 'POST',
                body: JSON.stringify({
                    current_password: currentPassword,
                    new_password: newPassword
                })
            });
            
            if (response.ok) {
                this.showNotification('Password changed successfully', 'success');
                this.closeModal();
            } else {
                const error = await response.json();
                this.showNotification(error.detail || 'Failed to change password', 'error');
            }
        } catch (error) {
            this.showNotification('Failed to change password', 'error');
        }
    }
    
    // Utility Methods
    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.innerHTML = `
            <span>${message}</span>
            <button onclick="this.parentElement.remove()">&times;</button>
        `;
        
        const container = document.getElementById('notification-container') || document.body;
        container.appendChild(notification);
        
        // Auto remove after 5 seconds
        setTimeout(() => {
            if (notification.parentElement) {
                notification.remove();
            }
        }, 5000);
    }
    
    showModal(title, content) {
        const modal = document.getElementById('modal');
        const modalBody = document.getElementById('modal-body');
        
        if (modal && modalBody) {
            modalBody.innerHTML = `
                <h2>${title}</h2>
                ${content}
            `;
            modal.style.display = 'block';
        }
    }
    
    closeModal() {
        const modal = document.getElementById('modal');
        if (modal) {
            modal.style.display = 'none';
        }
    }
    
    showForgotPassword() {
        this.showModal('Forgot Password', `
            <p>Enter your email address to receive a password reset link.</p>
            <form onsubmit="threadStormAuth.handleForgotPassword(event)">
                <div class="form-group">
                    <label for="forgot-email">Email</label>
                    <input type="email" id="forgot-email" required>
                </div>
                <button type="submit" class="btn btn-primary">Send Reset Link</button>
            </form>
        `);
    }
    
    async handleForgotPassword(event) {
        event.preventDefault();
        
        const email = document.getElementById('forgot-email').value;
        
        try {
            const response = await fetch(`${this.baseUrl}/auth/forgot-password`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ email })
            });
            
            if (response.ok) {
                this.showNotification('Password reset email sent', 'success');
                this.closeModal();
            } else {
                const error = await response.json();
                this.showNotification(error.detail || 'Failed to send reset email', 'error');
            }
        } catch (error) {
            this.showNotification('Failed to send reset email', 'error');
        }
    }
}

// Initialize authentication when DOM is loaded
let threadStormAuth;
document.addEventListener('DOMContentLoaded', function() {
    threadStormAuth = new ThreadStormAuth();
});
