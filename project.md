# AI Development Prompt: Synthetic Trading Investment Platform

## Technologies Stack

### Frontend
- **Core:** React 18, TypeScript, Vite
- **State Management:** Redux Toolkit, Redux-Saga
- **Caching:** Redis
- **HTTP Client:** Axios
- **Styling:** TailwindCSS, PostCSS
- **Real-time:** WebSocket
- **Charts:** TradingView Lightweight Charts
- **Testing:** Jest, Cypress
- **Build Tools:** ESBuild, SWC
- **Build Tools:** ESBuild, SWC

### Backend
- **Core:** FastAPI, Python 3.11+
- **Database:** MongoDB
- **Cache:** Redis
- **Queue:** Celery
- **AI/ML:** LangChain, LangGraph
- **Real-time:** WebSocket (FastAPI WebSocket)
- **Authentication:** JWT, OAuth2
- **Testing:** Pytest
- **Documentation:** OpenAPI/Swagger

### DevOps & Infrastructure
- **Containerization:** Docker, Docker Compose
- **CI/CD:** GitHub Actions
- **Monitoring:** Prometheus, Grafana
- **Logging:** ELK Stack
- **Cloud:** AWS/Digital Ocean
- **Version Control:** Git, GitHub
- **Infrastructure as Code:** Terraform

### AI/ML Models & Infrastructure
- **Base Models:**
  - GPT-4 (via OpenAI API): Market analysis and pattern recognition
  - LLaMA 2 70B (Local): Trading strategy generation
  - Mistral 7B (Local): Real-time market sentiment analysis
  - MPT-30B (Local): Technical indicator interpretation

- **Specialized Trading Models:**
  - Prophet (Meta): Time series forecasting
  - XGBoost: Price movement prediction
  - LightGBM: Risk assessment
  - Isolation Forest: Anomaly detection
  - LSTM Networks: Pattern recognition
  - Transformer Models: Market sentiment analysis

- **Custom Models:**
  - DerivTradingBERT: Fine-tuned BERT for trading context
  - MarketSentimentGPT: Fine-tuned GPT for market analysis
  - RiskAssessmentLLM: Specialized model for risk evaluation
  - PatternRecognitionVision: CNN for chart pattern recognition

- **Model Training Infrastructure:**
  - Training Framework: PyTorch, TensorFlow
  - Distributed Training: Horovod
  - Experiment Tracking: MLflow
  - Model Registry: DVC
  - Hardware Acceleration: CUDA-enabled GPUs
  - Model Optimization: ONNX Runtime

- **AutoML & Hyperparameter Optimization:**
  - Optuna: Hyperparameter tuning
  - Ray Tune: Distributed hyperparameter search
  - AutoKeras: Neural architecture search
  - Weights & Biases: Experiment tracking

- **Model Deployment & Serving:**
  - TorchServe: Model serving
  - NVIDIA Triton: Inference optimization
  - Redis AI: Model caching
  - KServe: Kubernetes-native serving

- **Model Monitoring & Maintenance:**
  - Model Performance Monitoring
  - Drift Detection
  - Automated Retraining Pipelines
  - A/B Testing Framework
  - Model Versioning and Rollback

- **Feature Engineering Pipeline:**
  - Technical Indicators Generator
  - Market Sentiment Features
  - Historical Pattern Recognition
  - Risk Metrics Calculator
  - Custom Feature Engineering

## Project Overview
Create a comprehensive synthetic trading investment platform that integrates with Deriv API for automated trading decisions using AI analysis, real-time monitoring, and intelligent risk management.

## API and State Management Improvements

### API Client Migration to Axios
- Implement centralized API client using Axios
- Add request/response interceptors for:
  - Authentication token management
  - Error handling
  - Request retries
  - Response caching
- Create API service classes for different domains:
  - Trading operations
  - User management
  - Analytics
  - System configuration

### Redis Integration with Redux Toolkit
- Implement Redis caching layer for:
  - Real-time market data
  - User session management
  - Trading configuration
  - Performance metrics
- Setup Redis pub/sub for real-time updates
- Configure Redis cache invalidation strategies
- Integrate with Redux Toolkit for:
  - Cached data synchronization
  - Optimistic updates
  - Real-time state management

### Redux Toolkit Optimization
- Implement RTK Query for API calls
- Setup automatic cache management
- Configure selective data persistence
- Implement subscription-based updates
- Add type-safe action creators and reducers
- Setup middleware for:
  - API error handling
  - Analytics tracking
  - State persistence
  - Logging

## Project Implementation Status

|--------------------------------|-------------|----------|-------------------------------------------|
| Component/Feature              | Status      | Progress | Notes                                     |
|--------------------------------|-------------|----------|-------------------------------------------|
| **Frontend Core**              |             |          |                                           |
| Basic UI Structure             | ✅ Complete | 100%     | Base React+TypeScript+Vite implementation |
| Authentication UI              | 🟡 Partial  | 50%      | Basic forms implemented                   |
| Trading Dashboard              | 🟡 Partial  | 30%      | Basic layout only                         |
| Real-time Updates              | ❌ Pending  | 0%       | WebSocket implementation pending          |
| Charts and Visualizations      | ❌ Pending  | 0%       | To be implemented                         |
|--------------------------------|-------------|----------|-------------------------------------------|
| **API & State Management**     |             |          |                                           |
| Axios Integration              | 🟡 Partial  | 40%      | Basic client setup                        |
| API Interceptors               | 🟡 Partial  | 25%      | Auth interceptor implemented              |
| Request Retry Logic            | ❌ Pending  | 0%       | Not started                               |
| API Service Classes            | 🟡 Partial  | 30%      | Basic structure defined                   |
|--------------------------------|-------------|----------|-------------------------------------------|
| **Redis Integration**          |             |          |                                           |
| Redis Cache Setup              | 🟡 Partial  | 35%      | Basic configuration complete              |
| Real-time Data Caching         | ❌ Pending  | 0%       | Not started                               |
| Redis Pub/Sub                  | ❌ Pending  | 0%       | Not started                               |
| Cache Invalidation             | ❌ Pending  | 0%       | Not started                               |
|--------------------------------|-------------|----------|-------------------------------------------|
| **Redux Implementation**       |             |          |                                           |
| RTK Query Setup                | 🟡 Partial  | 40%      | Basic endpoints configured                |
| Cache Management               | 🟡 Partial  | 20%      | Initial setup                             |
| State Persistence              | ❌ Pending  | 0%       | Not started                               |
| Real-time State Sync           | ❌ Pending  | 0%       | Not started                               |
|--------------------------------|-------------|----------|-------------------------------------------|
| **Backend Core**               |             |          |                                           |
| FastAPI Setup                  | ✅ Complete | 100%     | Basic structure implemented               |
| Database Integration           | 🟡 Partial  | 70%      | MongoDB setup complete                    |
| Authentication System          | 🟡 Partial  | 60%      | Basic JWT implementation                  |
| Deriv API Integration          | 🟡 Partial  | 40%      | Basic connection established              |
|--------------------------------|-------------|----------|-------------------------------------------|
| **AI Model Infrastructure**    |             |          |                                           |
| Base Model Integration         | 🟡 Partial  | 15%      | Initial GPT-4 API setup                   |
| LLaMA 2 Local Setup            | ❌ Pending  | 0%       | Environment configuration pending         |
| Mistral 7B Implementation      | ❌ Pending  | 0%       | Not started                               |
| MPT-30B Integration            | ❌ Pending  | 0%       | Not started                               |
|--------------------------------|-------------|----------|-------------------------------------------|
| **Specialized Models**         |             |          |                                           |
| Prophet Time Series            | 🟡 Partial  | 30%      | Basic forecasting implemented             |
| XGBoost Price Prediction       | 🟡 Partial  | 25%      | Initial model training                    |
| LightGBM Risk Assessment       | ❌ Pending  | 0%       | Not started                               |
| LSTM Pattern Recognition       | ❌ Pending  | 0%       | Not started                               |
|--------------------------------|-------------|----------|-------------------------------------------|
| **Custom Models**              |             |          |                                           |
| DerivTradingBERT               | ❌ Pending  | 0%       | Not started                               |
| MarketSentimentGPT             | ❌ Pending  | 0%       | Not started                               |
| RiskAssessmentLLM              | ❌ Pending  | 0%       | Not started                               |
| PatternRecognitionVision       | ❌ Pending  | 0%       | Not started                               |
|--------------------------------|-------------|----------|-------------------------------------------|
| **Training Infrastructure**    |             |          |                                           |
| PyTorch Setup                  | 🟡 Partial  | 40%      | Basic environment configured              |
| TensorFlow Integration         | 🟡 Partial  | 35%      | Initial setup complete                    |
| MLflow Implementation          | 🟡 Partial  | 20%      | Basic tracking setup                      |
| GPU Infrastructure             | ❌ Pending  | 0%       | Hardware selection pending                |
|--------------------------------|-------------|----------|-------------------------------------------|
| **Model Deployment**           |             |          |                                           |
| TorchServe Setup               | ❌ Pending  | 0%       | Not started                               |
| Redis AI Integration           | ❌ Pending  | 0%       | Not started                               |
| Model Monitoring System        | ❌ Pending  | 0%       | Not started                               |
| A/B Testing Framework          | ❌ Pending  | 0%       | Not started                               |
|--------------------------------|-------------|----------|-------------------------------------------|
| **Feature Engineering**        |             |          |                                           |
| Technical Indicators           | 🟡 Partial  | 45%      | Basic indicators implemented              |
| Sentiment Analysis Pipeline    | 🟡 Partial  | 20%      | Initial pipeline setup                    |
| Pattern Recognition Features   | ❌ Pending  | 0%       | Not started                               |
| Custom Feature Pipeline        | ❌ Pending  | 0%       | Not started                               |
| Basic UI Structure             | ✅ Complete | 100%     | Base React+TypeScript+Vite implementation |
| Authentication UI              | 🟡 Partial  | 50%      | Basic forms implemented                   |
| Trading Dashboard              | 🟡 Partial  | 30%      | Basic layout only                         |
| Real-time Updates              | ❌ Pending  | 0%       | WebSocket implementation pending          |
| Charts and Visualizations      | ❌ Pending  | 0%       | To be implemented                         |
|--------------------------------|-------------|----------|-------------------------------------------|
| **Backend Core**               |             |          |                                           |
| FastAPI Setup                  | ✅ Complete | 100%     | Basic structure implemented               |
| Database Integration           | 🟡 Partial  | 70%      | MongoDB setup complete                    |
| Authentication System          | 🟡 Partial  | 60%      | Basic JWT implementation                  |
| Deriv API Integration          | 🟡 Partial  | 40%      | Basic connection established              |
|--------------------------------|-------------|----------|-------------------------------------------|
| **AI Components**              |             |          |                                           |
| Market Analysis Engine         | ❌ Pending  | 0%       | Not started                               |
| Decision System                | ❌ Pending  | 0%       | Not started                               |
| Risk Management System         | ❌ Pending  | 0%       | Not started                               |
|--------------------------------|-------------|----------|-------------------------------------------|
| **Infrastructure**             |             |          |                                           |
| Docker Setup                   | ✅ Complete | 100%     | Basic containerization complete           |
| CI/CD Pipeline                 | ❌ Pending  | 0%       | GitHub Actions to be implemented          |
| Monitoring                     | ❌ Pending  | 0%       | To be implemented                         |
|--------------------------------|-------------|----------|-------------------------------------------|
| **Documentation**              |             |          |                                           |
| API Documentation              | 🟡 Partial  | 30%      | Basic OpenAPI docs                        |
| Setup Instructions             | 🟡 Partial  | 40%      | Basic README available                    |
| User Guide                     | ❌ Pending  | 0%       | Not started                               |
|--------------------------------|-------------|----------|-------------------------------------------|
| **Testing**                    |             |          |                                           |
| Unit Tests                     | 🟡 Partial  | 20%      | Basic test setup only                     |
| Integration Tests              | ❌ Pending  | 0%       | Not started                               |
| E2E Tests                      | ❌ Pending  | 0%       | Not started                               |
|--------------------------------|-------------|----------|-------------------------------------------|
| **Security**                   |             |          |                                           |
| Basic Authentication           | 🟡 Partial  | 50%      | JWT implementation                        |
| 2FA                            | ❌ Pending  | 0%       | Not started                               |
| Security Auditing              | ❌ Pending  | 0%       | Not started                               |
|--------------------------------|-------------|----------|-------------------------------------------|
| **User Management**            |             |          |                                           |
| User Profiles                  | 🟡 Partial  | 40%      | Basic user data structure                 |
| Settings Management            | 🟡 Partial  | 30%      | Basic settings implementation             |
| Role-based Access              | ❌ Pending  | 0%       | Not started                               |
| User Preferences               | ❌ Pending  | 0%       | Not started                               |
|--------------------------------|-------------|----------|-------------------------------------------|
| **Trading Features**           |             |          |                                           |
| Manual Trading                 | ❌ Pending  | 0%       | Not started                               |
| Automated Trading              | ❌ Pending  | 0%       | Not started                               |
| Position Management            | ❌ Pending  | 0%       | Not started                               |
| Order History                  | ❌ Pending  | 0%       | Not started                               |
| Risk Parameters                | ❌ Pending  | 0%       | Not started                               |
|--------------------------------|-------------|----------|-------------------------------------------|
| **Analytics & Reporting**      |             |          |                                           |
| Performance Metrics            | ❌ Pending  | 0%       | Not started                               |
| Trading History Reports        | ❌ Pending  | 0%       | Not started                               |
| Export Functionality           | ❌ Pending  | 0%       | Not started                               |
| Custom Reports                 | ❌ Pending  | 0%       | Not started                               |
|--------------------------------|-------------|----------|-------------------------------------------|
| **Real-time Features**         |             |          |                                           |
| WebSocket Implementation       | 🟡 Partial  | 20%      | Basic setup started                       |
| Live Price Updates             | ❌ Pending  | 0%       | Not started                               |
| Real-time Notifications        | ❌ Pending  | 0%       | Not started                               |
| Live Position Updates          | ❌ Pending  | 0%       | Not started                               |
|--------------------------------|-------------|----------|-------------------------------------------|
| **Mobile Support**             |             |          |                                           |
| Responsive Design              | 🟡 Partial  | 40%      | Basic responsive layout                   |
| Mobile Navigation              | 🟡 Partial  | 30%      | Basic mobile menu                         |
| Touch Interactions             | ❌ Pending  | 0%       | Not started                               |
|--------------------------------|-------------|----------|-------------------------------------------|
| **Data Management**            |             |          |                                           |
| Data Backup System             | ❌ Pending  | 0%       | Not started                               |
| Data Export/Import             | ❌ Pending  | 0%       | Not started                               |
| Historical Data Storage        | 🟡 Partial  | 20%      | Basic schema defined                      |
|--------------------------------|-------------|----------|-------------------------------------------|
| **System Administration**      |             |          |                                           |
| Admin Dashboard                | ❌ Pending  | 0%       | Not started                               |
| User Management Tools          | ❌ Pending  | 0%       | Not started                               |
| System Monitoring Tools        | ❌ Pending  | 0%       | Not started                               |
| Logging System                 | 🟡 Partial  | 30%      | Basic logging implemented                 |
|--------------------------------|-------------|----------|-------------------------------------------|
                                    Legend:
                                    - ✅ Complete: Feature is implemented and working
                                    - 🟡 Partial: Feature is partially implemented or in progress
                                    - ❌ Pending: Feature not started yet

## End-to-End Test Scenarios and User Stories

### Authentication and User Management

**US001: User Registration** (❌ Pending, High Priority)
- As a new user, I want to create an account
- Test Scenario:
  1. Visit registration page
  2. Fill in valid credentials
  3. Submit form
  4. Verify email received
  5. Confirm account

**US002: User Login** (🟡 Partial, High Priority)
- As a registered user, I want to log in
- Test Scenario:
  1. Visit login page
  2. Enter credentials
  3. Verify successful login
  4. Check dashboard access

**US003: Password Recovery** (❌ Pending, Medium Priority)
- As a user, I want to reset my password
- Test Scenario:
  1. Request password reset
  2. Receive email
  3. Set new password
  4. Verify login with new password

### Trading Operations

**US004: Manual Trading** (❌ Pending, High Priority)
- As a trader, I want to execute manual trades
- Test Scenario:
  1. Access trading interface
  2. Select market
  3. Set parameters
  4. Execute trade
  5. Verify position opened

**US005: Automated Trading** (❌ Pending, High Priority)
- As a trader, I want to set up automated trading
- Test Scenario:
  1. Configure trading parameters
  2. Enable automation
  3. Verify automatic execution
  4. Monitor positions

**US006: Position Management** (❌ Pending, High Priority)
- As a trader, I want to manage open positions
- Test Scenario:
  1. View open positions
  2. Modify stop loss/take profit
  3. Close position
  4. Verify execution

### Portfolio and Analysis

**US007: Portfolio Overview** (❌ Pending, Medium Priority)
- As a user, I want to see my portfolio status
- Test Scenario:
  1. Access portfolio page
  2. Check balance
  3. View open positions
  4. Verify profit/loss calculations

**US008: Trading History** (❌ Pending, Medium Priority)
- As a user, I want to view my trading history
- Test Scenario:
  1. Access history page
  2. Filter transactions
  3. Export reports
  4. Verify data accuracy

**US009: Performance Analytics** (❌ Pending, Medium Priority)
- As a user, I want to analyze my performance
- Test Scenario:
  1. View performance metrics
  2. Check historical charts
  3. Analyze win/loss ratio
  4. Export analytics

### Risk Management

**US010: Risk Parameters** (❌ Pending, High Priority)
- As a user, I want to set risk parameters
- Test Scenario:
  1. Access risk settings
  2. Configure limits
  3. Set stop losses
  4. Verify enforcement

**US011: Account Limits** (❌ Pending, High Priority)
- As a user, I want to set account limits
- Test Scenario:
  1. Set daily limits
  2. Configure maximum position size
  3. Test limit enforcement
  4. Verify notifications

### AI and Automation

**US012: AI Strategy Configuration** (❌ Pending, High Priority)
- As a trader, I want to configure AI strategies
- Test Scenario:
  1. Access AI settings
  2. Configure parameters
  3. Test strategy
  4. Monitor performance

**US013: Market Analysis** (❌ Pending, Medium Priority)
- As a trader, I want to view AI market analysis
- Test Scenario:
  1. Check market indicators
  2. View AI predictions
  3. Analyze recommendations
  4. Verify accuracy

### Settings and Preferences

**US014: Platform Settings** (🟡 Partial, Medium Priority)
- As a user, I want to customize platform settings
- Test Scenario:
  1. Access settings page
  2. Modify preferences
  3. Save changes
  4. Verify persistence

**US015: Notifications** (❌ Pending, Low Priority)
- As a user, I want to manage notifications
- Test Scenario:
  1. Configure alerts
  2. Test different types
  3. Verify delivery
  4. Manage preferences

### Mobile Experience

**US016: Mobile Trading** (❌ Pending, Medium Priority)
- As a user, I want to trade on mobile devices
- Test Scenario:
  1. Access mobile interface
  2. Execute trades
  3. Manage positions
  4. Test responsiveness

**US017: Mobile Notifications** (❌ Pending, Low Priority)
- As a user, I want to receive mobile alerts
- Test Scenario:
  1. Enable push notifications
  2. Test different scenarios
  3. Verify delivery
  4. Check interaction

Test Implementation Notes:
- All E2E tests should be implemented using Cypress
- Each test should include happy path and error scenarios
- Tests should run in CI/CD pipeline
- Mobile tests should cover both Android and iOS
- Performance metrics should be collected during tests
- Test data should be properly managed and cleaned up
- Screenshots should be captured for failures
- Tests should be tagged for selective execution

## Backend Architecture Requirements

### Core Framework Setup
Build a FastAPI-based backend application with the following foundational structure:

**Base Application Structure:**
- Initialize FastAPI with proper CORS configuration for frontend integration
- Implement dependency injection pattern for database connections and external services
- Create modular architecture with separate packages for authentication, trading, analysis, and monitoring
- Set up proper logging and error handling throughout the application
- Implement health check endpoints for monitoring system status

### Database Layer (MongoDB)
Design and implement MongoDB collections for:

**User Management:**
- User profiles with encrypted credentials
- Deriv API tokens and app_id storage with encryption
- User preferences and trading configurations
- Authentication sessions and JWT token management

**Trading Parameters:**
- Flexible profit_top and profit_loss percentages per user
- Dynamic stop-loss configurations with internal profit_loss values
- Market-specific trading thresholds and barriers
- Historical parameter adjustments and their performance outcomes

**Transaction Management:**
- Active trades with real-time status tracking
- Complete transaction history with detailed profit/loss calculations
- Trade execution timestamps and market conditions at execution
- Performance metrics and analytics data

**Market Analysis Data:**
- Historical market movements for training AI models
- Real-time market indicators and technical analysis results
- Pattern recognition data and successful trading scenarios
- Market volatility indicators and trend analysis

### Authentication & Security Module
Implement robust authentication system:

**JWT Token Management:**
- Secure token generation with configurable expiration times
- Refresh token mechanism for seamless user experience
- Bearer token validation middleware for all protected endpoints
- Role-based access control for different user privilege levels

**API Security:**
- Rate limiting to prevent abuse
- Request validation and sanitization
- Encrypted storage of sensitive trading credentials
- Audit logging for all trading operations and parameter changes

### Deriv API Integration Module
Create comprehensive integration with Deriv API:

**Market Data Retrieval:**
- Real-time streaming of synthetic indices prices and movements
- Historical data fetching for backtesting and analysis
- Market status monitoring and trading session management
- Connection health monitoring with automatic reconnection logic

**Trading Operations:**
- Manual buy/sell order execution with confirmation mechanisms
- Automated trading based on AI analysis and user-defined parameters
- Position monitoring with real-time profit/loss calculations
- Order history retrieval and transaction status tracking

**Risk Management:**
- Position sizing based on account balance and risk tolerance
- Multi-level stop-loss implementation with trailing stops
- Maximum daily loss limits and circuit breakers
- Portfolio diversification controls across different synthetic indices

### AI Analysis Modules (LangChain & LangGraph)

**Real-Time Market Analysis Engine:**
- Continuous monitoring of synthetic indices using streaming data
- Technical indicator calculations (RSI, MACD, Bollinger Bands, etc.)
- Pattern recognition for identifying trading opportunities
- Market sentiment analysis based on price movements and volatility

**Intelligent Trading Decision System:**
- Multi-factor analysis combining technical indicators with historical patterns
- Dynamic parameter adjustment based on market conditions
- Risk assessment for each potential trade using historical success rates
- Confidence scoring for trading decisions with threshold-based execution

**Adaptive Risk Management:**
- Dynamic stop-loss adjustment based on market volatility
- Profit-taking strategies that adapt to trending vs. ranging markets
- Position sizing optimization based on recent performance and market conditions
- Emergency exit strategies for extreme market conditions

**Historical Learning System:**
- Train models on historical trading data to improve decision accuracy
- Pattern recognition for successful trading scenarios and market conditions
- Backtesting framework for validating new strategies before live deployment
- Continuous learning from new market data and trading outcomes

### Real-Time Monitoring System
Develop always-on monitoring capabilities:

**Active Position Monitoring:**
- WebSocket connections to Deriv for real-time price updates
- Continuous profit/loss calculation for all open positions
- Automated execution of stop-loss and take-profit orders
- Alert system for positions approaching critical thresholds

**Market Opportunity Scanner:**
- Continuous analysis of all available synthetic indices
- Automated detection of trading opportunities based on user-defined criteria
- Queue management for potential trades with priority scoring
- Risk-adjusted opportunity ranking and execution timing

**Performance Analytics:**
- Real-time calculation of portfolio performance metrics
- Daily, weekly, and monthly profit/loss reporting
- Success rate analysis for different trading strategies and market conditions
- Risk-adjusted returns calculation and performance attribution

## Frontend Architecture Requirements (React + TypeScript + Vite)

### Authentication & Security Interface
Create secure user authentication flow:

**Login System:**
- Clean, professional login interface with form validation
- JWT token management with automatic refresh
- Secure storage of authentication tokens
- Password recovery and account management features

**Configuration Management:**
- Secure interface for managing Deriv API tokens and app_id
- Validation of API credentials before saving
- Encrypted local storage of sensitive configuration data
- Clear visual indicators of connection status to trading APIs

### Main Trading Dashboard
Develop comprehensive trading overview:

**Active Positions Display:**
- Real-time table showing all current trades with live profit/loss updates
- Color-coded indicators for winning/losing positions
- Quick action buttons for manual position management
- WebSocket integration for immediate updates without page refresh

**Portfolio Performance Overview:**
- Current total portfolio value with real-time updates
- Today's profit/loss with percentage change indicators
- Active position count and total invested amount
- Quick performance metrics and key statistics

**Market Status Indicators:**
- Real-time connection status to Deriv API
- Current market session information
- System health indicators for all monitoring modules
- Alert notifications for important system or market events

### Transaction History & Analytics
Build comprehensive reporting interface:

**Detailed Transaction History:**
- Paginated table with complete trade details and outcomes
- Advanced filtering by date range, profit/loss, symbol, and trade type
- Export functionality for detailed reporting and tax purposes
- Visual indicators for AI-initiated vs. manual trades

**Performance Analytics Dashboard:**
- Interactive line charts showing daily profit/loss trends over time
- Win rate statistics with breakdown by trading strategy
- Risk-adjusted return calculations and Sharpe ratio displays
- Comparative performance analysis against market benchmarks

**Advanced Reporting:**
- Monthly and quarterly performance summaries
- Strategy effectiveness analysis with recommendations
- Risk metrics including maximum drawdown and volatility measures
- Tax reporting features with realized gains/losses calculations

### Parameter Configuration Interface
Create intuitive configuration management:

**Trading Parameter Controls:**
- User-friendly sliders and input fields for profit_top and profit_loss percentages
- Visual representation of risk/reward ratios for different parameter combinations
- Preset configuration templates for conservative, moderate, and aggressive strategies
- Real-time impact analysis showing how parameter changes affect potential outcomes

**AI Behavior Settings:**
- Controls for AI analysis sensitivity and decision thresholds
- Market condition overrides for different volatility environments
- Backtesting interface for validating parameter changes before implementation
- Historical performance analysis for different parameter combinations

**Risk Management Configuration:**
- Maximum daily loss limits with automatic trading halt features
- Position sizing rules based on account balance and risk tolerance
- Diversification requirements across different synthetic indices
- Emergency stop mechanisms for extreme market conditions

## Technical Implementation Guidelines

### Development Best Practices
Follow these essential practices throughout development:

**Code Organization:**
- Implement clean architecture principles with clear separation of concerns
- Use dependency injection for better testability and maintainability
- Create comprehensive API documentation using FastAPI's automatic OpenAPI generation
- Implement proper error handling with informative error messages and logging

**Testing Strategy:**
- Unit tests for all business logic and utility functions
- Integration tests for API endpoints and database operations
- Mock external dependencies (Deriv API) for reliable testing
- Performance testing for real-time monitoring and analysis modules

**Monitoring & Observability:**
- Comprehensive logging for all trading operations and system events
- Performance metrics collection for optimization and troubleshooting
- Health checks for all system components and external dependencies
- Alert systems for critical failures and unusual trading patterns

### Security Considerations
Implement robust security throughout:

**Data Protection:**
- Encrypt all sensitive data including API keys and trading credentials
- Secure transmission of all data between frontend and backend
- Regular security audits and vulnerability assessments
- Secure backup and recovery procedures for trading data

**Access Control:**
- Role-based permissions for different user types and administrative functions
- API rate limiting and abuse prevention mechanisms
- Secure session management with proper token expiration
- Audit trails for all user actions and system changes

### Scalability & Performance
Design for growth and reliability:

**Performance Optimization:**
- Database indexing strategy for fast query performance
- Caching mechanisms for frequently accessed data
- Efficient WebSocket management for real-time data streaming
- Load balancing considerations for high-availability deployment

**Monitoring & Maintenance:**
- Automated deployment pipelines with proper testing gates
- Database backup and recovery procedures
- System monitoring and alerting for proactive maintenance
- Performance profiling and optimization tools

## Success Metrics & Validation

Define clear success criteria:

**Trading Performance:**
- Consistent profitability with controlled risk exposure
- High success rate for AI-generated trading decisions
- Effective risk management with minimal large losses
- User satisfaction with system reliability and performance

**Technical Performance:**
- Sub-second response times for all critical trading operations
- 99.9% uptime for real-time monitoring and trading systems
- Accurate real-time data synchronization with minimal latency
- Scalable architecture supporting multiple concurrent users

This comprehensive system should provide a professional-grade synthetic trading platform that combines intelligent automation with user control, ensuring both profitability and risk management while maintaining the flexibility to adapt to changing market conditions.

## Additional Requirements and Improvements

### GitHub and CI/CD Integration
As this is a GitHub-based project, implement comprehensive GitHub Actions workflows:

**GitHub Actions Workflows:**
- Automated testing pipeline for all pull requests
- Continuous Integration checks for code quality and style
- Security scanning for dependencies and vulnerabilities
- Automated deployment to staging and production environments
- Docker image building and publishing pipeline

**Repository Management:**
- Branch protection rules for main/production branches
- Required code review process
- Automated version tagging and release notes generation
- Issue and pull request templates
- Automated dependency updates with Dependabot

### Version Control and Deployment
**Version Management:**
- Semantic versioning for all releases
- Changelog automation and maintenance
- Feature flag system for gradual rollouts
- Automated rollback procedures
- Environment-specific configuration management

**Deployment Strategy:**
- Blue-green deployment support
- Canary releases for risk mitigation
- Infrastructure as Code (IaC) for all environments
- Automated environment provisioning
- Deployment health checks and validation

### Documentation
**Developer Documentation:**
- Comprehensive API documentation with OpenAPI/Swagger
- Contributing guidelines and code style guide
- Development environment setup instructions
- Architecture decision records (ADRs)
- Component interaction diagrams

**User Documentation:**
- User guides and tutorials
- API integration documentation for third parties
- Troubleshooting guides
- FAQs and knowledge base
- Video tutorials and walkthroughs

### Disaster Recovery and Business Continuity
**Backup Systems:**
- Automated daily backups with retention policies
- Cross-region data replication
- Point-in-time recovery capabilities
- Regular backup restoration testing
- Data integrity validation procedures

**Disaster Recovery:**
- Detailed recovery procedures and playbooks
- Recovery time objective (RTO) definitions
- Recovery point objective (RPO) specifications
- Regular disaster recovery drills
- Incident response procedures

### Advanced Monitoring
**System Metrics:**
- Real-time performance dashboards
- Resource utilization monitoring
- Application performance monitoring (APM)
- Custom metric collection and analysis
- Trend analysis and capacity planning

**Operational Monitoring:**
- Centralized logging system
- Error tracking and analysis
- User behavior analytics
- System health dashboards
- Proactive alert system

### Enhanced Security
**Authentication and Authorization:**
- Two-factor authentication (2FA)
- Single sign-on (SSO) integration
- Password policy enforcement
- Session management and control
- Role-based access control (RBAC)

**Security Measures:**
- Regular security audits
- Penetration testing schedule
- Automated security scanning
- Suspicious activity detection
- Security incident response plan

### Scalability and Performance
**Database Optimization:**
- Database sharding strategy
- Read replicas for performance
- Query optimization and monitoring
- Index strategy and maintenance
- Connection pooling configuration

**Architecture Scalability:**
- Microservices architecture considerations
- Load balancing configuration
- Auto-scaling policies
- Cache strategy and implementation
- API rate limiting and throttling

### External Integrations
**Notification Systems:**
- Email notification service
- SMS alert system
- Push notifications
- Webhook integrations
- Third-party analytics integration

### Comprehensive Testing
**Advanced Testing:**
- Load and stress testing
- Performance benchmark testing
- Security penetration testing
- A/B testing framework
- Chaos engineering tests

### User Features
**User Management:**
- User tier system (Basic, Premium, Enterprise)
- Referral and affiliate program
- Customer support system
- User feedback collection
- Account management features

### Compliance and Regulation
**Regulatory Requirements:**
- Data protection compliance (GDPR, etc.)
- Financial regulations compliance
- Privacy policy and terms of service
- Audit trails and logging
- Regular compliance reporting

### Analytics and Reporting
**Enhanced Analytics:**
- Custom report generation
- Advanced ROI metrics
- Market benchmark comparisons
- Performance attribution analysis
- Risk analytics dashboard

### Mobile and Accessibility
**Mobile Support:**
- Progressive Web App (PWA)
- Native mobile applications
- Responsive design implementation
- Cross-platform compatibility
- Offline functionality

**Accessibility:**
- WCAG 2.1 compliance
- Screen reader compatibility
- Keyboard navigation support
- Color contrast compliance
- Accessibility testing and validation
