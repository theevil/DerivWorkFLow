# DerivWorkFlow - AI-Powered Synthetic Trading Platform

A comprehensive synthetic trading investment platform that integrates with Deriv API for automated trading decisions using AI analysis, real-time monitoring, and intelligent risk management.

## 🚀 Features

### Backend (FastAPI)
- **Authentication**: JWT-based authentication with MongoDB user management
- **Deriv API Integration**: Real-time WebSocket connection to Deriv trading platform
- **AI Analysis Engine**: Technical indicators (RSI, MACD, Bollinger Bands) and signal generation
- **Local AI Support**: Complete local AI integration with Ollama for privacy and cost-free operation
- **Trading Management**: Position tracking, parameter configuration, and risk management
- **Real-time Monitoring**: WebSocket endpoints for live trading data
- **Comprehensive API**: RESTful endpoints for all trading operations

### Frontend (React + TypeScript + Vite)
- **Modern UI**: Mantine-based component library with responsive design
- **Authentication Flow**: Secure login/register with form validation
- **Trading Dashboard**: Real-time position monitoring and performance analytics
- **AI Configuration**: Easy setup for local AI models and OpenAI integration
- **Parameter Configuration**: User-friendly controls for trading parameters
- **Real-time Updates**: Live data updates via WebSocket connections

### Shared Package
- **Type Safety**: Shared TypeScript types across frontend and backend
- **API Contracts**: Consistent interfaces for all API communications

## 🏗️ Architecture

```
DerivWorkFLow/
├── apps/
│   ├── backend/          # FastAPI application
│   │   ├── app/
│   │   │   ├── core/     # Configuration, database, security
│   │   │   ├── models/   # Pydantic models
│   │   │   ├── crud/     # Database operations
│   │   │   ├── routers/  # API endpoints
│   │   │   └── main.py   # Application entry point
│   │   ├── Dockerfile
│   │   └── Pipfile       # Python dependencies (Pipenv)
│   └── frontend/         # React + TypeScript + Vite
│       ├── src/
│       │   ├── components/
│       │   ├── pages/
│       │   ├── stores/   # Zustand state management
│       │   └── lib/      # API client and utilities
│       └── package.json
├── packages/
│   └── shared/           # Shared TypeScript types
├── docker-compose.yml    # Development environment
└── package.json          # Monorepo configuration
```

## 🛠️ Tech Stack

### Backend
- **FastAPI**: Modern, fast web framework for building APIs
- **MongoDB**: NoSQL database with Motor async driver
- **Pipenv**: Python dependency management
- **WebSockets**: Real-time communication
- **JWT**: Secure authentication
- **NumPy**: Technical analysis calculations
- **Loguru**: Advanced logging

### Frontend
- **React 18**: Modern React with hooks
- **TypeScript**: Type-safe JavaScript
- **Vite**: Fast build tool and dev server
- **Mantine**: Modern React components library
- **Zustand**: Lightweight state management
- **React Router**: Client-side routing

### Infrastructure
- **Docker Compose**: Containerized development environment
- **MongoDB**: Database storage
- **WebSocket**: Real-time data streaming
- **Ollama**: Local AI model management

## 🚀 Getting Started

### Prerequisites
- Node.js 18+ and npm
- Python 3.11+
- Docker and Docker Compose
- Git

### 1. Clone the Repository
```bash
git clone <repository-url>
cd DerivWorkFLow
```

### 2. Environment Setup

#### Backend Environment
Create `apps/backend/.env`:
```env
ENVIRONMENT=development
MONGODB_URI=mongodb://mongodb:27017
MONGODB_DB=deriv
SECRET_KEY=your-secret-key-change-in-production
BACKEND_CORS_ORIGINS=["http://localhost:3000"]
```

### 3. Development with Docker (Recommended)

Start all services:
```bash
docker compose up --build
```

This will start:
- MongoDB on port 27017
- Backend API on port 8000
- Frontend on port 3000

### 4. Local Development

#### Install Dependencies
```bash
# Install root dependencies
npm install

# Install shared package dependencies
npm run install:shared

# Install frontend dependencies
npm run install:frontend
```

#### Backend Setup (Alternative to Docker)
```bash
cd apps/backend

# Install Pipenv if not already installed
pip install pipenv

# Install dependencies
pipenv install --dev

# Start development server
pipenv run start
```

#### Frontend Setup
```bash
# Start frontend development server
npm run dev
```

## 📚 API Documentation

Once the backend is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Key Endpoints

#### Authentication
- `POST /api/v1/auth/register` - User registration
- `POST /api/v1/auth/token` - User login

#### Trading
- `GET/POST/PUT /api/v1/trading/parameters` - Trading parameters management
- `GET/POST /api/v1/trading/positions` - Position management
- `GET /api/v1/trading/stats` - Trading statistics
- `GET /api/v1/trading/signals` - AI trading signals

#### Deriv Integration
- `POST /api/v1/deriv/token` - Set Deriv API token
- `WS /api/v1/ws/deriv/{user_id}` - Real-time trading WebSocket

## 🤖 AI Features

### Technical Analysis
- **RSI (Relative Strength Index)**: Momentum oscillator
- **MACD**: Moving Average Convergence Divergence
- **Bollinger Bands**: Volatility indicator
- **Trend Analysis**: Market direction detection
- **Volatility Calculation**: Risk assessment

### Signal Generation
- **Multi-factor Analysis**: Combines multiple technical indicators
- **Confidence Scoring**: Signal reliability assessment
- **Position Sizing**: Dynamic amount calculation based on confidence
- **Duration Optimization**: Adaptive trade duration based on market conditions

### Risk Management
- **Stop Loss**: Automated loss protection
- **Take Profit**: Profit target management
- **Daily Loss Limits**: Maximum exposure controls
- **Position Sizing**: Risk-adjusted trade amounts

## 🔧 Configuration

### Trading Parameters
- **Profit Top**: Target profit percentage
- **Profit Loss**: Stop loss percentage
- **Stop Loss**: Maximum stop loss
- **Take Profit**: Take profit percentage
- **Max Daily Loss**: Maximum daily loss amount
- **Position Size**: Base position size in USD

### AI Configuration
- **Local AI**: Use local models with Ollama (recommended for microtransactions)
- **OpenAI**: Use OpenAI models (requires API key)
- **Hybrid**: Combine both local and OpenAI models
- **Model Selection**: Choose from Phi-3 Mini, Gemma 2B, Llama 3.1, Mistral 7B
- **Temperature**: Control model creativity (0.1-0.3 recommended for trading)
- **Confidence Threshold**: Minimum confidence for signal execution

### Deriv API Setup
1. Create a Deriv account at https://deriv.com
2. Generate an API token in your account settings
3. Note your App ID
4. Configure in the application settings

### Local AI Setup
For detailed instructions on setting up local AI models, see [LOCAL_AI_SETUP.md](LOCAL_AI_SETUP.md).

## 🧪 Testing

### Backend Tests
```bash
cd apps/backend
pipenv run test
```

### Frontend Tests
```bash
cd apps/frontend
npm test
```

## 📦 Deployment

### Production Build
```bash
# Build frontend
npm run build

# Backend is containerized and ready for deployment
```

### Environment Variables
Ensure all production environment variables are set:
- `SECRET_KEY`: Strong secret key for JWT
- `MONGODB_URI`: Production MongoDB connection string
- `ENVIRONMENT`: Set to "production"

## 🔒 Security

- **JWT Authentication**: Secure token-based authentication
- **Password Hashing**: bcrypt for secure password storage
- **API Rate Limiting**: Prevents abuse
- **CORS Configuration**: Controlled cross-origin requests
- **Input Validation**: Pydantic models for request validation
- **Encrypted Storage**: Sensitive credentials encrypted in database

## 📊 Monitoring

- **Health Checks**: `/health` endpoint for system monitoring
- **Logging**: Comprehensive logging with Loguru
- **Error Handling**: Graceful error handling and user feedback
- **Performance Metrics**: Trading statistics and analytics

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## ⚠️ Disclaimer

This software is for educational and research purposes only. Trading involves substantial risk of loss and is not suitable for all investors. Past performance is not indicative of future results. Always trade responsibly and only with funds you can afford to lose.

## 🆘 Support

For support and questions:
1. Check the documentation
2. Review existing issues
3. Create a new issue with detailed information
4. Join our community discussions

---

**Built with ❤️ for the trading community**
