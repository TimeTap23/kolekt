# ThreadStorm Documentation

## Overview

ThreadStorm is a powerful utility for social media thread management, content creation, and data processing. It combines AI-powered content generation with deep research capabilities to help content creators produce engaging, well-researched social media threads.

## Features

### 🧵 Thread Management
- Create, edit, and schedule social media threads
- Support for multiple platforms (Twitter, LinkedIn, Instagram)
- Thread preview and analytics
- Bulk thread operations

### 🤖 AI Content Generation
- AI-powered content creation with customizable voice and style guides
- Multiple content types (threads, articles, blog posts, tweets)
- Style preference customization
- Target audience optimization

### 🔍 Research Tools
- Deep research capabilities with source tracking
- Multiple research types (general, academic, market, trending)
- Automated source credibility assessment
- Key insights extraction

### 📊 Analytics & Insights
- Performance tracking and analytics
- Engagement metrics
- Content optimization suggestions
- A/B testing capabilities

### 🎨 Interactive Interface
- Modern, responsive web interface
- Real-time collaboration features
- Drag-and-drop thread editing
- Mobile-friendly design

## Quick Start

### Prerequisites
- Python 3.11+
- PostgreSQL 13+
- Redis 6+
- Docker (optional)

### Installation

#### Option 1: Local Development
```bash
# Clone the repository
git clone <repository-url>
cd threadstorm

# Set up environment
cp env.example .env
# Edit .env with your configuration

# Install dependencies
make install

# Set up database
make setup-dev

# Run development server
make dev
```

#### Option 2: Docker
```bash
# Clone the repository
git clone <repository-url>
cd threadstorm

# Set up environment
cp env.example .env
# Edit .env with your configuration

# Start services
make setup-docker

# Run application
make docker-run
```

### Configuration

Create a `.env` file with the following variables:

```env
# Application Settings
DEBUG=True
HOST=0.0.0.0
PORT=8000

# Security
SECRET_KEY=your-super-secret-key
DATABASE_URL=postgresql+asyncpg://username:password@localhost:5432/threadstorm
REDIS_URL=redis://localhost:6379

# AI Services
OPENAI_API_KEY=your-openai-api-key
HUGGINGFACE_API_KEY=your-huggingface-api-key

# Optional: Twitter API
TWITTER_API_KEY=your-twitter-api-key
TWITTER_API_SECRET=your-twitter-api-secret
```

## Usage

### Creating a Thread

1. **Navigate to the Dashboard**
   - Open ThreadStorm in your browser
   - Click "Create Thread" or use the quick action card

2. **Configure Thread Settings**
   - Enter thread title and description
   - Select target platform
   - Set voice guide and tone preferences
   - Add hashtags and mentions

3. **Generate Content**
   - Use AI content generation for initial content
   - Edit and refine each thread item
   - Preview the complete thread

4. **Schedule or Publish**
   - Schedule for later publication
   - Publish immediately
   - Save as draft for further editing

### AI Content Generation

1. **Select Content Type**
   - Choose from thread, article, blog post, or single tweet
   - Specify target audience and style preferences

2. **Provide Topic and Context**
   - Enter your topic or subject
   - Add relevant keywords
   - Describe your preferred writing style

3. **Generate and Refine**
   - Generate initial content with AI
   - Review and edit generated content
   - Iterate until satisfied

### Research Tools

1. **Define Research Scope**
   - Enter research topic
   - Select research type (general, academic, market, trending)
   - Set depth level (shallow, medium, deep)

2. **Configure Sources**
   - Specify source types to include
   - Set date range for research
   - Add relevant keywords

3. **Analyze Results**
   - Review gathered sources
   - Extract key insights
   - Generate research summary

## API Reference

### Authentication
All API endpoints require authentication using JWT tokens.

```bash
# Login to get access token
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "password"}'
```

### Threads API

#### Create Thread
```bash
curl -X POST "http://localhost:8000/api/v1/threads" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "My Thread Title",
    "description": "Thread description",
    "platform": "twitter",
    "voice_guide": "Professional but friendly tone"
  }'
```

#### Get Threads
```bash
curl -X GET "http://localhost:8000/api/v1/threads" \
  -H "Authorization: Bearer <token>"
```

### Content Generation API

#### Generate Content
```bash
curl -X POST "http://localhost:8000/api/v1/content/generate" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "content_type": "thread",
    "topic": "AI in content creation",
    "target_audience": "Content creators",
    "style_preferences": "Professional, engaging, educational"
  }'
```

### Research API

#### Start Research
```bash
curl -X POST "http://localhost:8000/api/v1/research" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Machine learning trends",
    "research_type": "general",
    "depth_level": "medium",
    "keywords": ["AI", "ML", "trends"]
  }'
```

## Architecture

### Backend
- **FastAPI**: Modern, fast web framework
- **SQLAlchemy**: ORM for database operations
- **PostgreSQL**: Primary database
- **Redis**: Caching and task queue
- **Celery**: Background task processing

### Frontend
- **HTML/CSS/JavaScript**: Modern web interface
- **Tailwind CSS**: Utility-first CSS framework
- **Font Awesome**: Icon library

### AI Integration
- **OpenAI API**: Content generation
- **Hugging Face**: Text classification and analysis
- **Custom ML models**: Specialized content processing

## Development

### Project Structure
```
threadstorm/
├── src/                    # Core application code
│   ├── core/              # Core functionality
│   ├── api/               # API endpoints
│   ├── models/            # Data models
│   ├── services/          # Business logic
│   └── utils/             # Utility functions
├── web/                   # Web interface
│   ├── static/            # Static assets
│   └── templates/         # HTML templates
├── tests/                 # Test suite
├── docs/                  # Documentation
└── config/                # Configuration files
```

### Running Tests
```bash
make test
```

### Code Formatting
```bash
make format
```

### Linting
```bash
make lint
```

## Deployment

### Production Setup
1. Set up production environment variables
2. Configure database and Redis
3. Set up reverse proxy (Nginx)
4. Configure SSL certificates
5. Set up monitoring and logging

### Docker Deployment
```bash
# Build production image
make prod-build

# Run production services
make prod-run
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions:
- Create an issue on GitHub
- Check the documentation
- Join our community discussions

## Roadmap

### Upcoming Features
- [ ] Advanced analytics dashboard
- [ ] Multi-language support
- [ ] Team collaboration features
- [ ] Advanced AI models integration
- [ ] Mobile application
- [ ] API rate limiting and quotas
- [ ] Advanced scheduling features
- [ ] Content templates marketplace

### Known Issues
- See GitHub issues for current known issues and their status
