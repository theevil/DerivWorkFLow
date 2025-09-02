# AI Development Prompt: Synthetic Trading Investment Platform

## Project Overview
Create a comprehensive synthetic trading investment platform that integrates with Deriv API for automated trading decisions using AI analysis, real-time monitoring, and intelligent risk management.

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
