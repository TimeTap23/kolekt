// ThreadStorm Authentication JavaScript - Development Version
// Shows cyberpunk theme immediately for development

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
        // For development: Show main content immediately
        this.showMainContent();
        
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
            // For development: Show login form but keep main content visible
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
            
            // Store tokens and user info
            this.setTokens(data.access_token, data.refresh_token);
            this.setCurrentUser(data.user);
            this.isAuthenticated = true;
            
            // Setup token refresh
            this.setupTokenRefresh();
            
            // Update UI
            this.updateUI();
            
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
        }
        
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
        
        this.showNotification('Logged out successfully', 'info');
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
            
            return data;
            
        } catch (error) {
            console.error('Token refresh error:', error);
            this.logout();
            throw error;
        }
    }
    
    async verifyToken() {
        try {
            const token = this.getAccessToken();
            if (!token) {
                throw new Error('No access token available');
            }
            
            const response = await fetch(`${this.baseUrl}/auth/me`, {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });
            
            if (!response.ok) {
                throw new Error('Token verification failed');
            }
            
            const data = await response.json();
            this.setCurrentUser(data);
            
            return data;
            
        } catch (error) {
            console.error('Token verification error:', error);
            throw error;
        }
    }
    
    setupTokenRefresh() {
        // Clear existing timer
        if (this.tokenRefreshTimer) {
            clearTimeout(this.tokenRefreshTimer);
        }
        
        // Set up refresh 5 minutes before expiry (25 minutes from now)
        this.tokenRefreshTimer = setTimeout(() => {
            this.refreshToken();
        }, 25 * 60 * 1000); // 25 minutes
    }
    
    // UI Methods
    showLoginForm() {
        const authContainer = document.getElementById('auth-container');
        if (authContainer) {
            authContainer.innerHTML = `
                <div class="auth-form">
                    <h2>ThreadStorm</h2>
                    <div class="auth-tabs">
                        <button class="auth-tab active" onclick="threadStormAuth.showTab('login')">Login</button>
                        <button class="auth-tab" onclick="threadStormAuth.showTab('register')">Register</button>
                    </div>
                    
                    <div id="login-tab" class="auth-tab-content active">
                        <form onsubmit="threadStormAuth.handleLogin(event)">
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
                        <form onsubmit="threadStormAuth.handleRegister(event)">
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
                                <input type="password" id="register-password" required>
                            </div>
                            <div class="form-group">
                                <label for="register-confirm-password">Confirm Password</label>
                                <input type="password" id="register-confirm-password" required>
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
            
            // Hide auth forms
            this.hideAuthForms();
            
            // Update navigation
            this.updateNavigation();
        } else {
            // Show login form but keep main content visible
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
    
    // Utility Methods
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
            
            // Auto-remove after 5 seconds
            setTimeout(() => {
                if (notification.parentElement) {
                    notification.remove();
                }
            }, 5000);
        }
    }
    
    showModal(content) {
        // Simple modal implementation
        const modal = document.createElement('div');
        modal.className = 'modal';
        modal.innerHTML = `
            <div class="modal-content">
                <span class="close" onclick="this.parentElement.parentElement.remove()">&times;</span>
                ${content}
            </div>
        `;
        
        document.body.appendChild(modal);
    }
    
    closeModal() {
        const modal = document.querySelector('.modal');
        if (modal) {
            modal.remove();
        }
    }
}

// Initialize authentication when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    window.threadStormAuth = new ThreadStormAuth();
});
