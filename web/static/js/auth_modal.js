// ThreadStorm Authentication JavaScript - Modal Version
// Uses modal-based authentication with Sign In/Sign Up buttons in header

class KolektAuth {
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
            // Show auth buttons in header
            this.updateUI();
        }
        
        // Check if we're on homepage and user is authenticated - redirect to dashboard
        if (this.isAuthenticated && window.location.pathname === '/') {
            window.location.href = '/dashboard';
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
            
            // Check if registration was successful
            if (!data.success) {
                throw new Error(data.error || 'Registration failed');
            }
            
            // Store tokens and user info for auto-login after registration
            this.setTokens(data.access_token, data.refresh_token);
            this.setCurrentUser(data.user);
            this.isAuthenticated = true;
            
            // Setup token refresh
            this.setupTokenRefresh();
            
            // Update UI and close modal
            this.updateUI();
            this.closeAuthModal();
            
            // Redirect to dashboard after successful registration
            window.location.href = '/dashboard';
            
            this.showNotification('Registration successful! Welcome to Kolekt!', 'success');
            return data;
            
        } catch (error) {
            console.error('Registration error:', error);
            this.showNotification(error.message, 'error');
            throw error;
        }
    }
    
    async login(email, password) {
        try {
            console.log('Attempting login for:', email);
            
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
            
            console.log('Login response status:', response.status);
            const data = await response.json();
            console.log('Login response data:', data);
            
            // Check if login was successful
            if (!data.success) {
                throw new Error(data.error || 'Login failed');
            }
            
            console.log('Login successful, storing tokens...');
            
            // Store tokens and user info
            this.setTokens(data.access_token, data.refresh_token);
            this.setCurrentUser(data.user);
            this.isAuthenticated = true;
            
            // Setup token refresh
            this.setupTokenRefresh();
            
            // Update UI and close modal
            this.updateUI();
            this.closeAuthModal();
            
            console.log('Redirecting to dashboard...');
            
            // Redirect to dashboard after successful login
            window.location.href = '/dashboard';
            
            this.showNotification('Login successful! Welcome back!', 'success');
            return data;
            
        } catch (error) {
            console.error('Login error:', error);
            this.showNotification(error.message, 'error');
            throw error;
        }
    }
    
    async logout() {
        console.log('Logout initiated...');
        
        try {
            const refreshToken = this.getRefreshToken();
            console.log('Refresh token found:', refreshToken ? 'Yes' : 'No');
            
            if (refreshToken) {
                console.log('Calling logout API...');
                const response = await fetch(`${this.baseUrl}/auth/logout`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${this.getAccessToken()}`
                    },
                    body: JSON.stringify({
                        refresh_token: refreshToken
                    })
                });
                
                console.log('Logout API response:', response.status);
                const data = await response.json();
                console.log('Logout API data:', data);
            }
        } catch (error) {
            console.error('Logout error:', error);
        }
        
        // Clear local state
        console.log('Clearing local tokens...');
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
        
        console.log('Redirecting to homepage...');
        // Redirect to homepage after logout
        setTimeout(() => {
            window.location.href = '/';
        }, 1000);
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
    
    // Modal Methods
    showLoginModal() {
        const modalBody = document.getElementById('auth-modal-body');
        if (modalBody) {
            modalBody.innerHTML = `
                <h2>Sign In</h2>
                <form onsubmit="kolektAuth.handleLogin(event)">
                    <div class="form-group">
                        <label for="login-email">Email</label>
                        <input type="email" id="login-email" required>
                    </div>
                    <div class="form-group">
                        <label for="login-password">Password</label>
                        <input type="password" id="login-password" required>
                    </div>
                    <button type="submit" class="btn btn-primary" style="width: 100%; margin-top: 20px;">Sign In</button>
                </form>
                <div class="auth-links">
                    <a href="#" onclick="kolektAuth.showRegisterModal()">Don't have an account? Sign Up</a>
                    <br>
                    <a href="#" onclick="kolektAuth.showForgotPasswordModal()">Forgot Password?</a>
                    <a href="/" style="margin-top: 10px; display: block; text-align: center;">← Back to Home</a>
                </div>
            `;
        }
        this.showAuthModal();
    }
    
    showRegisterModal() {
        const modalBody = document.getElementById('auth-modal-body');
        if (modalBody) {
            modalBody.innerHTML = `
                <h2>Sign Up</h2>
                <form onsubmit="kolektAuth.handleRegister(event)">
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
                    <button type="submit" class="btn btn-primary" style="width: 100%; margin-top: 20px;">Sign Up</button>
                </form>
                <div class="auth-links">
                    <a href="#" onclick="kolektAuth.showLoginModal()">Already have an account? Sign In</a>
                    <a href="/" style="margin-top: 10px; display: block; text-align: center;">← Back to Home</a>
                </div>
            `;
        }
        this.showAuthModal();
    }
    
    showAuthModal() {
        const modal = document.getElementById('auth-modal');
        if (modal) {
            modal.classList.add('show');
        }
    }
    
    closeAuthModal() {
        const modal = document.getElementById('auth-modal');
        if (modal) {
            modal.classList.remove('show');
            modal.style.display = 'none';
            modal.style.opacity = '0';
            modal.style.visibility = 'hidden';
        }
    }
    
    // UI Methods
    updateUI() {
        const user = this.getCurrentUser();
        
        if (this.isAuthenticated && user) {
            // Show user info, hide auth buttons
            this.showUserInfo(user);
            this.hideAuthButtons();
        } else {
            // Show auth buttons, hide user info
            this.showAuthButtons();
            this.hideUserInfo();
        }
    }
    
    showUserInfo(user) {
        const userInfo = document.getElementById('user-info');
        const userName = document.getElementById('user-name');
        const userPlan = document.getElementById('user-plan');
        
        if (userInfo) userInfo.style.display = 'flex';
        if (userName) userName.textContent = user.name || user.email;
        if (userPlan) userPlan.textContent = user.plan || 'Free';
    }
    
    hideUserInfo() {
        const userInfo = document.getElementById('user-info');
        if (userInfo) userInfo.style.display = 'none';
    }
    
    showAuthButtons() {
        const authButtons = document.getElementById('auth-buttons');
        if (authButtons) authButtons.style.display = 'flex';
    }
    
    hideAuthButtons() {
        const authButtons = document.getElementById('auth-buttons');
        if (authButtons) authButtons.style.display = 'none';
    }
    
    // Form Handlers
    async handleLogin(event) {
        event.preventDefault();
        console.log('Login form submitted');
        
        const email = document.getElementById('login-email').value;
        const password = document.getElementById('login-password').value;
        
        console.log('Login credentials:', { email, password: password ? '[HIDDEN]' : '[EMPTY]' });
        
        try {
            await this.login(email, password);
        } catch (error) {
            console.error('Login form error:', error);
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
            // After successful registration, show login modal
            this.showLoginModal();
        } catch (error) {
            // Error already handled in register method
        }
    }
    
    async handleForgotPassword(event) {
        event.preventDefault();
        
        const email = document.getElementById('forgot-email').value;
        
        if (!email) {
            this.showNotification('Please enter your email address', 'error');
            return;
        }
        
        try {
            const response = await fetch(`${this.baseUrl}/auth/forgot-password`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ email })
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.showNotification(data.message, 'success');
                if (data.dev_reset_url) {
                    // In development, show the reset URL
                    this.showNotification(`Development: Reset URL: ${data.dev_reset_url}`, 'info');
                }
                this.closeAuthModal();
            } else {
                this.showNotification(data.error || 'Failed to send reset email', 'error');
            }
        } catch (error) {
            console.error('Forgot password error:', error);
            this.showNotification('An error occurred. Please try again.', 'error');
        }
    }
    
    showForgotPasswordModal() {
        const modalBody = document.getElementById('auth-modal-body');
        if (modalBody) {
            modalBody.innerHTML = `
                <h2>🔐 Forgot Password</h2>
                <p>Enter your email address and we'll send you a link to reset your password.</p>
                <form onsubmit="kolektAuth.handleForgotPassword(event)">
                    <div class="form-group">
                        <label for="forgot-email">Email Address</label>
                        <input type="email" id="forgot-email" name="email" required>
                    </div>
                    <button type="submit" class="btn btn-primary" style="width: 100%; margin-top: 20px;">Send Reset Link</button>
                </form>
                <div class="auth-links">
                    <a href="#" onclick="kolektAuth.showLoginModal()">← Back to Login</a>
                </div>
            `;
        }
        this.showAuthModal();
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
    
    showProfile() {
        // Placeholder for profile functionality
        this.showNotification('Profile feature coming soon!', 'info');
    }
    
    initializeMainApp() {
        // Initialize the main ThreadStorm app functionality
        if (window.kolektApp) {
            console.log('Initializing main app functionality...');
            // The app should already be initialized, but we can trigger any post-login setup
            this.showNotification('Main app features are now available!', 'success');
        } else {
            console.log('KolektApp not found, initializing...');
            // If the app isn't initialized, we can initialize it here
            if (typeof KolektApp !== 'undefined') {
                window.kolektApp = new KolektApp();
            }
        }
        
        // Show a welcome message with available features
        setTimeout(() => {
            this.showNotification('Try clicking on Formatter, Templates, or Analytics to get started!', 'info');
        }, 2000);
    }
}

// Initialize authentication when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    window.kolektAuth = new KolektAuth();
    
    // Close modal when clicking outside
    const authModal = document.getElementById('auth-modal');
    if (authModal) {
        authModal.addEventListener('click', function(event) {
            if (event.target === authModal) {
                kolektAuth.closeAuthModal();
            }
        });
    }
});
