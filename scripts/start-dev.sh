#!/bin/bash

# Development startup script for Social Media AI Platform

echo "🚀 Starting Social Media AI Platform in Development Mode"
echo "======================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to check if a service is running
check_service() {
    if pgrep -f "$1" > /dev/null; then
        echo -e "${GREEN}✓${NC} $2 is running"
        return 0
    else
        echo -e "${RED}✗${NC} $2 is not running"
        return 1
    fi
}

# Function to start a service
start_service() {
    echo -e "${YELLOW}Starting $1...${NC}"
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        sudo systemctl start $2
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        brew services start $2
    fi
    sleep 2
}

echo
echo "📋 Checking prerequisites..."

# Check Python
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    echo -e "${GREEN}✓${NC} Python $PYTHON_VERSION found"
else
    echo -e "${RED}✗${NC} Python 3 not found. Please install Python 3.8+"
    exit 1
fi

# Check Node.js
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    echo -e "${GREEN}✓${NC} Node.js $NODE_VERSION found"
else
    echo -e "${RED}✗${NC} Node.js not found. Please install Node.js 18+"
    exit 1
fi

echo
echo "🔍 Checking services..."

# Check and start PostgreSQL
if ! check_service "postgres" "PostgreSQL"; then
    echo -e "${YELLOW}Starting PostgreSQL...${NC}"
    start_service "PostgreSQL" "postgresql"
    if ! check_service "postgres" "PostgreSQL"; then
        echo -e "${RED}Failed to start PostgreSQL. Please start it manually.${NC}"
        exit 1
    fi
fi

# Check and start Redis
if ! check_service "redis" "Redis"; then
    echo -e "${YELLOW}Starting Redis...${NC}"
    start_service "Redis" "redis"
    if ! check_service "redis" "Redis"; then
        echo -e "${RED}Failed to start Redis. Please start it manually.${NC}"
        exit 1
    fi
fi

echo
echo "📦 Setting up backend..."

# Navigate to backend directory
cd "$(dirname "$0")/../backend" || exit 1

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Creating virtual environment...${NC}"
    python3 -m venv venv
fi

# Activate virtual environment
echo -e "${YELLOW}Activating virtual environment...${NC}"
source venv/bin/activate

# Install/upgrade dependencies
echo -e "${YELLOW}Installing Python dependencies...${NC}"
pip install --upgrade pip
pip install -r requirements.txt

# Check environment file
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}Creating .env file from template...${NC}"
    cat > .env << EOL
# Database Configuration
DATABASE_URL=postgresql://socialmedia_user:SecurePassword123!@localhost:5432/socialmediaai

# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379

# Security
SECRET_KEY=dev-secret-key-change-in-production
JWT_SECRET_KEY=dev-jwt-secret-key-change-in-production

# AI Services (Add your API keys)
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Application Settings
DEBUG=True
ENVIRONMENT=development
EOL
    echo -e "${RED}⚠️  Please update the .env file with your API keys before starting the server${NC}"
fi

echo
echo "🌐 Setting up frontend..."

# Navigate to frontend directory
cd "../frontend" || exit 1

# Install Node.js dependencies
if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}Installing Node.js dependencies...${NC}"
    npm install
fi

# Check frontend environment file
if [ ! -f ".env.local" ]; then
    echo -e "${YELLOW}Creating frontend .env.local file...${NC}"
    cat > .env.local << EOL
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000
NEXT_PUBLIC_APP_NAME=Social Media AI Platform
NEXT_PUBLIC_APP_VERSION=1.0.0
EOL
fi

echo
echo "✅ Setup complete!"
echo
echo "🚀 To start the application:"
echo "   1. Backend:  cd backend && source venv/bin/activate && python main.py"
echo "   2. Frontend: cd frontend && npm run dev"
echo
echo "📱 Access points:"
echo "   • Frontend:  http://localhost:3000"
echo "   • Backend:   http://localhost:8000" 
echo "   • API Docs:  http://localhost:8000/docs"
echo
echo "⚠️  Don't forget to:"
echo "   • Add your AI API keys to backend/.env"
echo "   • Create PostgreSQL database and user"
echo "   • Configure social media API keys (optional)"

# Make the script executable
chmod +x "$0"