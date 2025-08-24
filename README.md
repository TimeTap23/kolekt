# Kolekt (Kolekt) - Social Media Management Platform

A modern, production-ready social media management platform that allows users to connect and manage multiple social media accounts, create content, and post across platforms seamlessly.

## 🚀 Features

- **Multi-Platform Support**: Connect Threads, Instagram, and Facebook accounts
- **Cross-Platform Posting**: Post content to multiple platforms simultaneously
- **Content Management**: Create, schedule, and manage your social media content
- **Analytics Dashboard**: Track performance across all connected platforms
- **Admin Panel**: Comprehensive admin interface for platform management
- **OAuth Integration**: Secure authentication with social media platforms
- **Production Ready**: Kubernetes deployment with monitoring and scaling

## 🛠 Tech Stack

- **Backend**: FastAPI (Python)
- **Database**: Supabase (PostgreSQL)
- **Frontend**: HTML, CSS, JavaScript
- **Deployment**: Cloud Platform
- **Authentication**: JWT with OAuth 2.0
- **Monitoring**: Prometheus & Grafana

## 📋 Prerequisites

- Python 3.11+
- Docker
- Kubernetes cluster
- Supabase account
- Social media platform developer accounts

## 🚀 Quick Start

### Local Development

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/kolekt.git
   cd kolekt
   ```

2. **Set up environment variables**
   ```bash
   cp env.example .env
   # Edit .env with your credentials
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   python start_kolekt.py
   ```

### Production Deployment

See [KUBERNETES_DEPLOYMENT_GUIDE.md](KUBERNETES_DEPLOYMENT_GUIDE.md) for complete production deployment instructions.

## 🔧 Configuration

### Environment Variables

Required environment variables:

```bash
# Database
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key

# Security
SECRET_KEY=your_secret_key
TOKEN_ENCRYPTION_KEY=your_encryption_key

# Social Media APIs
META_APP_ID=your_meta_app_id
META_APP_SECRET=your_meta_app_secret
THREADS_APP_ID=your_threads_app_id
THREADS_APP_SECRET=your_threads_app_secret
```

## 📚 Documentation

- [Kubernetes Deployment Guide](KUBERNETES_DEPLOYMENT_GUIDE.md)
- [Production OAuth Setup](PRODUCTION_OAUTH_SETUP.md)
- [Admin Dashboard Setup](ADMIN_SETUP.md)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

For support and questions:
- Create an issue in this repository
- Check the documentation in the `/docs` folder
- Review the deployment guides

## 🏗 Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   FastAPI       │    │   Supabase      │
│   (HTML/CSS/JS) │◄──►│   Backend       │◄──►│   Database      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │   Social Media  │
                       │   APIs          │
                       │   (Threads,     │
                       │    Instagram,   │
                       │    Facebook)    │
                       └─────────────────┘
```

## 🔒 Security

- JWT-based authentication
- OAuth 2.0 for social media platforms
- Encrypted token storage
- Rate limiting
- Security headers
- Input validation

---

**Kolekt** - Empowering social media management with modern technology.
