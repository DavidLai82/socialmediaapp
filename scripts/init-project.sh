#!/bin/bash

# Project initialization script for GitHub deployment

echo "🚀 Initializing Social Media AI Platform for GitHub"
echo "=================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get the project directory
PROJECT_DIR="$(dirname "$0")/.."
cd "$PROJECT_DIR" || exit 1

echo
echo -e "${BLUE}📋 Project Structure:${NC}"
echo "├── backend/          FastAPI + CrewAI multi-agent system"
echo "├── frontend/         Next.js + TypeScript React app"
echo "├── scripts/          Development and deployment scripts"
echo "├── docs/            Documentation and guides"
echo "└── docker-compose.yml  Container orchestration"

echo
echo -e "${YELLOW}🔧 Initializing Git repository...${NC}"

# Initialize git if not already done
if [ ! -d ".git" ]; then
    git init
    echo -e "${GREEN}✓${NC} Git repository initialized"
else
    echo -e "${GREEN}✓${NC} Git repository already exists"
fi

# Create initial commit
echo -e "${YELLOW}📝 Creating initial commit...${NC}"

# Add all files
git add .

# Check if there are any changes to commit
if git diff --staged --quiet; then
    echo -e "${YELLOW}ℹ️${NC} No changes to commit"
else
    git commit -m "Initial commit: Social Media AI Platform

🚀 Features:
- Multi-agent system with CrewAI
- FastAPI backend with async support
- Next.js frontend with TypeScript
- Redis task queue and caching
- PostgreSQL database
- WebSocket real-time updates
- Docker containerization
- Comprehensive monitoring

🤖 Agents:
- Social Optimizer (coordinator)
- Traffic Analyst (trends)
- Content Writer (generation)
- Video Creator (planning)
- Script Writer (video scripts)

💼 Ready for production deployment!"

    echo -e "${GREEN}✓${NC} Initial commit created"
fi

echo
echo -e "${BLUE}📚 Next steps for GitHub deployment:${NC}"
echo
echo "1. Create GitHub repository:"
echo "   https://github.com/new"
echo
echo "2. Add remote origin:"
echo -e "   ${YELLOW}git remote add origin https://github.com/YOUR_USERNAME/social-media-ai-platform.git${NC}"
echo
echo "3. Push to GitHub:"
echo -e "   ${YELLOW}git branch -M main${NC}"
echo -e "   ${YELLOW}git push -u origin main${NC}"
echo
echo "4. Set up environment variables:"
echo "   - Copy .env.example to .env"
echo "   - Add your API keys (OpenAI, Anthropic, Social Media APIs)"
echo
echo "5. Local development:"
echo -e "   ${YELLOW}./scripts/start-dev.sh${NC}"
echo
echo "6. Docker deployment:"
echo -e "   ${YELLOW}docker-compose up --build${NC}"
echo

echo -e "${GREEN}🎉 Project ready for GitHub! ${NC}"
echo -e "${BLUE}📖 See README.md for detailed setup instructions${NC}"

# Make scripts executable
chmod +x scripts/*.sh
echo -e "${GREEN}✓${NC} Scripts made executable"