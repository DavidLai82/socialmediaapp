# Social Media AI Platform

A sophisticated multi-agent AI platform for social media optimization using CrewAI, FastAPI, and Next.js.

*A social media optimization app powered by AI agents for automated content creation, trend analysis, and cross-platform social media management.*

## 🚀 Features

### Multi-Agent System
- **Social Optimizer Agent**: Main coordinator for all social media activities
- **Traffic Analysis Agent**: Trend detection and viral content prediction
- **Content Writing Agent**: Platform-optimized content generation
- **Video Creation Agent**: Comprehensive video planning and production
- **Script Writing Agent**: Compelling video script creation

### Platform Capabilities
- **Real-time WebSocket Communication**: Live task updates and system monitoring
- **Background Task Processing**: Efficient handling of long-running AI operations
- **Comprehensive Analytics**: Performance monitoring and system health tracking
- **Multi-platform Support**: Twitter, LinkedIn, Instagram, Facebook, TikTok, YouTube
- **Scalable Architecture**: Redis-based task management and caching

## 📋 Prerequisites

Before setting up the application, ensure you have:

- **Python 3.8+** (recommended: Python 3.11)
- **Node.js 18.0+**
- **PostgreSQL 12+**
- **Redis 6.0+**
- **Git** (for version control)

## 🛠 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/DavidLai82/socialmediaapp.git
cd socialmediaapp
```

### 2. Backend Setup

#### Create Virtual Environment
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

#### Install Dependencies
```bash
pip install -r requirements.txt
```

#### Database Setup
```bash
# Start PostgreSQL
sudo systemctl start postgresql  # Linux
brew services start postgresql   # macOS

# Create database
createdb socialmediaai

# Create user
psql socialmediaai
CREATE USER socialmedia_user WITH ENCRYPTED PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE socialmediaai TO socialmedia_user;
\q
```

#### Redis Setup
```bash
# Start Redis
sudo systemctl start redis  # Linux
brew services start redis   # macOS
```

#### Environment Configuration
Create `.env` file in the backend directory:

```env
# Database
DATABASE_URL=postgresql://socialmedia_user:your_password@localhost:5432/socialmediaai

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379

# Security
SECRET_KEY=your-super-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key

# AI Services
OPENAI_API_KEY=your_openai_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key

# Social Media APIs
TWITTER_API_KEY=your_twitter_api_key
TWITTER_API_SECRET=your_twitter_api_secret
LINKEDIN_CLIENT_ID=your_linkedin_client_id
# ... add other API keys as needed
```

### 3. Frontend Setup

#### Install Dependencies
```bash
cd ../frontend
npm install
```

#### Environment Configuration
Create `.env.local` file in the frontend directory:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000
NEXT_PUBLIC_APP_NAME=Social Media AI Platform
```

## 🚀 Running the Application

### Start Backend Services

```bash
# Terminal 1: Start PostgreSQL and Redis (if not already running)
sudo systemctl start postgresql redis

# Terminal 2: Start FastAPI server
cd backend
source venv/bin/activate
python main.py
```

The backend will be available at: http://localhost:8000

### Start Frontend

```bash
# Terminal 3: Start Next.js development server
cd frontend
npm run dev
```

The frontend will be available at: http://localhost:3000

## 📊 API Documentation

Once the backend is running, access the interactive API documentation at:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Key Endpoints

#### Content Generation
```bash
POST /agents/content/generate
```

#### Trend Analysis
```bash
POST /agents/trends/analyze
```

#### Video Creation
```bash
POST /agents/video/create
```

#### System Health
```bash
GET /health
GET /agents/status
```

## 🔧 Configuration

### AI Services
The platform supports multiple AI providers:

- **OpenAI GPT-4**: For general content generation
- **Anthropic Claude**: Alternative AI provider
- **CrewAI**: Multi-agent orchestration

### Social Media Integration
Configure API keys for:

- **Twitter/X**: Content posting and trend analysis
- **LinkedIn**: Professional content optimization
- **Instagram**: Visual content planning
- **Facebook**: Community-focused content
- **TikTok**: Short-form video content
- **YouTube**: Long-form video planning

## 📈 Monitoring and Analytics

### System Health Monitoring
```bash
GET /api/monitoring/health      # Detailed health check
GET /api/monitoring/metrics     # System performance metrics
GET /api/monitoring/agents/status  # Agent system status
```

### Task Analytics
```bash
GET /api/monitoring/tasks/analytics  # Task execution analytics
GET /tasks/user/{user_id}           # User-specific tasks
```

### WebSocket Events
The platform provides real-time updates via WebSocket:

- Task status updates
- Agent status changes
- System alerts
- Performance metrics

## 🧪 Testing

### Backend Testing
```bash
cd backend
python -m pytest tests/ -v
```

### Frontend Testing
```bash
cd frontend
npm run test
```

### API Testing
Use the provided test scripts or Postman collection:

```bash
# Test content generation
curl -X POST "http://localhost:8000/agents/content/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user",
    "platform": "twitter",
    "topic": "AI trends",
    "brand_voice": "professional",
    "target_audience": "tech enthusiasts",
    "content_type": "post"
  }'
```

## 🏗 Architecture

### Backend Architecture
```
backend/
├── agents/                 # CrewAI agents and tools
│   ├── social_optimizer.py # Main coordinator agent
│   ├── content_tools.py    # Content generation tools
│   ├── social_media_tools.py # Social media integration
│   └── video_tools.py      # Video creation tools
├── api/                    # FastAPI routes
│   ├── websocket_routes.py # WebSocket endpoints
│   └── monitoring_routes.py # System monitoring
├── models/                 # Pydantic schemas
├── utils/                  # Utility modules
├── config/                 # Configuration management
└── main.py                # Application entry point
```

### Frontend Architecture
```
frontend/
├── src/
│   ├── app/               # Next.js 13+ App Router
│   ├── components/        # React components
│   ├── hooks/            # Custom React hooks
│   ├── utils/            # Utility functions
│   └── types/            # TypeScript definitions
└── public/               # Static assets
```

## 🐳 Docker Deployment

### Using Docker Compose
```bash
# Build and start all services
docker-compose up --build

# Start in detached mode
docker-compose up -d

# Stop all services
docker-compose down
```

### Individual Container Builds
```bash
# Backend
docker build -t social-media-ai-backend ./backend

# Frontend
docker build -t social-media-ai-frontend ./frontend
```

## 🔒 Security Considerations

### Environment Variables
- Never commit `.env` files to version control
- Use strong, unique secrets for production
- Rotate API keys regularly

### API Security
- Implement rate limiting
- Use HTTPS in production
- Validate all input data
- Implement proper authentication

### Database Security
- Use encrypted connections
- Regular backups
- Principle of least privilege for database users

## 🛠 Troubleshooting

### Common Issues

#### Backend Won't Start
1. Check Python version: `python --version`
2. Verify virtual environment is activated
3. Ensure PostgreSQL and Redis are running
4. Check environment variables in `.env`

#### Frontend Build Errors
1. Check Node.js version: `node --version`
2. Clear node_modules: `rm -rf node_modules && npm install`
3. Verify environment variables in `.env.local`

#### Agent Initialization Fails
1. Verify AI API keys are set correctly
2. Check internet connectivity
3. Review logs for specific error messages

#### Database Connection Issues
1. Verify PostgreSQL is running
2. Check database credentials
3. Ensure database exists and user has permissions

### Log Files
- Backend logs: `backend/logs/app.log`
- Frontend logs: Browser console and Next.js output
- System logs: Check systemd logs for PostgreSQL and Redis

## 🤝 Contributing

### Development Setup
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

### Code Style
- Backend: Follow PEP 8 for Python code
- Frontend: Follow React and TypeScript best practices
- Use provided linting configurations

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **CrewAI**: Multi-agent orchestration framework
- **FastAPI**: High-performance API framework
- **Next.js**: React framework for production
- **OpenAI & Anthropic**: AI service providers
- **Social Media APIs**: Platform integrations

## 📞 Support

For support and questions:

1. Check the [troubleshooting section](#-troubleshooting)
2. Review [API documentation](http://localhost:8000/docs)
3. Create an issue in the repository
4. Contact the development team

## 🗺 Roadmap

### Upcoming Features
- [ ] Advanced analytics dashboard
- [ ] Multi-user authentication system
- [ ] Content scheduling and automation
- [ ] Mobile application
- [ ] Advanced AI model fine-tuning
- [ ] Enterprise SSO integration

### Version History
- **v1.0.0**: Initial release with core multi-agent functionality
- **v1.1.0**: Enhanced monitoring and analytics (planned)
- **v1.2.0**: Mobile app support (planned)

---

**Built with ❤️ by the Social Media AI Team**
