"""
Trading Decision Engine using LangGraph for workflow-based trading decisions
"""

from typing import Annotated, Any, Optional, TypedDict

from langchain.chat_models import ChatOpenAI
from langchain.schema import BaseMessage
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from loguru import logger
from pydantic import BaseModel, Field

from app.core.config import settings
from app.ai.local_ai_manager import local_ai_manager

from .market_analyzer import (
    AdvancedMarketAnalyzer,
)


class TradingState(TypedDict):
    """State for trading decision workflow"""
    messages: Annotated[list[BaseMessage], add_messages]
    symbol: str
    price_history: list[float]
    current_price: float
    user_context: dict[str, Any]
    market_analysis: Optional[dict[str, Any]]
    risk_assessment: Optional[dict[str, Any]]
    trading_recommendation: Optional[dict[str, Any]]
    final_decision: Optional[dict[str, Any]]
    confidence_score: float
    reasoning_steps: list[str]


class TradingDecision(BaseModel):
    """Final trading decision output"""
    action: str = Field(description="Trading action: buy_call, buy_put, hold")
    confidence: float = Field(description="Confidence level (0-1)", ge=0, le=1)
    position_size: float = Field(description="Recommended position size as percentage of balance", ge=0.01, le=0.1)
    time_horizon: str = Field(description="Recommended time horizon: short, medium, long")
    stop_loss: float = Field(description="Stop loss percentage", ge=0.01, le=0.5)
    take_profit: float = Field(description="Take profit percentage", ge=0.01, le=1.0)
    reasoning: str = Field(description="Detailed reasoning for the decision")
    warnings: list[str] = Field(description="Risk warnings and considerations")
    ai_provider: str = Field(description="AI provider used: local, openai, fallback")


class TradingDecisionEngine:
    """
    Advanced trading decision engine using LangGraph workflows
    """

    def __init__(self):
        """Initialize the trading decision engine"""
        self.market_analyzer = AdvancedMarketAnalyzer()

        # Initialize LLM for OpenAI
        if settings.openai_api_key:
            self.openai_llm = ChatOpenAI(
                model=settings.ai_model,
                temperature=settings.ai_temperature,
                max_tokens=settings.ai_max_tokens,
                openai_api_key=settings.openai_api_key
            )
        else:
            self.openai_llm = None
            logger.warning("OpenAI API key not configured.")

        # Initialize local AI
        self.local_ai_enabled = settings.local_ai_enabled
        if self.local_ai_enabled:
            logger.info("Local AI enabled for decision engine")

        # Build the decision workflow graph
        self.workflow = self._build_decision_workflow()

    def _build_decision_workflow(self) -> StateGraph:
        """Build the LangGraph workflow for trading decisions"""

        # Create the workflow graph
        workflow = StateGraph(TradingState)

        # Add nodes
        workflow.add_node("analyze_market", self._analyze_market_node)
        workflow.add_node("assess_risk", self._assess_risk_node)
        workflow.add_node("generate_recommendation", self._generate_recommendation_node)
        workflow.add_node("validate_decision", self._validate_decision_node)
        workflow.add_node("finalize_decision", self._finalize_decision_node)

        # Add edges
        workflow.add_edge(START, "analyze_market")
        workflow.add_edge("analyze_market", "assess_risk")
        workflow.add_edge("assess_risk", "generate_recommendation")
        workflow.add_edge("generate_recommendation", "validate_decision")
        workflow.add_edge("validate_decision", "finalize_decision")
        workflow.add_edge("finalize_decision", END)

        return workflow.compile()

    async def make_trading_decision(
        self,
        symbol: str,
        price_history: list[float],
        current_price: float,
        user_context: dict[str, Any]
    ) -> TradingDecision:
        """
        Make a comprehensive trading decision using the workflow

        Args:
            symbol: Trading symbol
            price_history: Historical price data
            current_price: Current market price
            user_context: User trading context and preferences

        Returns:
            TradingDecision with comprehensive analysis and recommendation
        """
        try:
            # Initialize state
            initial_state = TradingState(
                messages=[],
                symbol=symbol,
                price_history=price_history,
                current_price=current_price,
                user_context=user_context,
                market_analysis=None,
                risk_assessment=None,
                trading_recommendation=None,
                final_decision=None,
                confidence_score=0.0,
                reasoning_steps=[]
            )

            # Run the workflow
            result = await self.workflow.ainvoke(initial_state)

            # Extract final decision
            if result.get("final_decision"):
                decision_data = result["final_decision"]
                return TradingDecision(**decision_data)
            else:
                # Fallback decision
                return self._fallback_decision(symbol, user_context)

        except Exception as e:
            logger.error(f"Error in trading decision workflow: {e}")
            return self._fallback_decision(symbol, user_context)

    async def _analyze_market_node(self, state: TradingState) -> TradingState:
        """Analyze market conditions"""
        try:
            # Perform market analysis
            market_analysis = await self.market_analyzer.analyze_market_advanced(
                symbol=state["symbol"],
                price_history=state["price_history"],
                current_price=state["current_price"],
                market_context={"timeframe": "5m", "session": "active"}
            )

            # Update state
            state["market_analysis"] = market_analysis.dict()
            state["reasoning_steps"].append(f"Market analysis: {market_analysis.trend_direction} trend with {market_analysis.confidence_score:.2f} confidence")

            return state

        except Exception as e:
            logger.error(f"Error in market analysis node: {e}")
            # Fallback analysis
            state["market_analysis"] = {
                "trend_direction": "sideways",
                "confidence_score": 0.5,
                "risk_level": "medium",
                "recommended_action": "hold",
                "ai_provider": "fallback"
            }
            return state

    async def _assess_risk_node(self, state: TradingState) -> TradingState:
        """Assess trading risk"""
        try:
            market_analysis = state["market_analysis"]
            user_context = state["user_context"]

            # Determine AI provider
            ai_provider = self._determine_ai_provider()

            if ai_provider == "local":
                risk_assessment = await self._assess_risk_with_local_ai(market_analysis, user_context)
            elif ai_provider == "openai":
                risk_assessment = await self._assess_risk_with_openai(market_analysis, user_context)
            else:
                risk_assessment = self._basic_risk_assessment(market_analysis, user_context)

            state["risk_assessment"] = risk_assessment
            state["reasoning_steps"].append(f"Risk assessment: {risk_assessment['risk_level']} risk level")

            return state

        except Exception as e:
            logger.error(f"Error in risk assessment node: {e}")
            state["risk_assessment"] = {
                "risk_level": "medium",
                "risk_score": 0.5,
                "risk_factors": ["Unable to assess risk"],
                "ai_provider": "fallback"
            }
            return state

    async def _generate_recommendation_node(self, state: TradingState) -> TradingState:
        """Generate trading recommendation"""
        try:
            market_analysis = state["market_analysis"]
            risk_assessment = state["risk_assessment"]
            user_context = state["user_context"]

            # Determine AI provider
            ai_provider = self._determine_ai_provider()

            if ai_provider == "local":
                recommendation = await self._generate_recommendation_with_local_ai(
                    market_analysis, risk_assessment, user_context
                )
            elif ai_provider == "openai":
                recommendation = await self._generate_recommendation_with_openai(
                    market_analysis, risk_assessment, user_context
                )
            else:
                recommendation = self._basic_recommendation(market_analysis, risk_assessment, user_context)

            state["trading_recommendation"] = recommendation
            state["reasoning_steps"].append(f"Recommendation: {recommendation['action']} with {recommendation['confidence']:.2f} confidence")

            return state

        except Exception as e:
            logger.error(f"Error in recommendation node: {e}")
            state["trading_recommendation"] = {
                "action": "hold",
                "confidence": 0.5,
                "reasoning": "Unable to generate recommendation",
                "ai_provider": "fallback"
            }
            return state

    async def _validate_decision_node(self, state: TradingState) -> TradingState:
        """Validate the trading decision"""
        try:
            recommendation = state["trading_recommendation"]
            user_context = state["user_context"]

            # Basic validation
            if recommendation["confidence"] < settings.ai_confidence_threshold:
                recommendation["action"] = "hold"
                recommendation["confidence"] = 0.5
                recommendation["reasoning"] += " (Confidence below threshold)"

            # Check user constraints
            max_daily_loss = user_context.get("max_daily_loss", 100)
            if user_context.get("daily_loss", 0) >= max_daily_loss:
                recommendation["action"] = "hold"
                recommendation["reasoning"] += " (Daily loss limit reached)"

            state["trading_recommendation"] = recommendation
            state["reasoning_steps"].append("Decision validated")

            return state

        except Exception as e:
            logger.error(f"Error in validation node: {e}")
            return state

    async def _finalize_decision_node(self, state: TradingState) -> TradingState:
        """Finalize the trading decision"""
        try:
            recommendation = state["trading_recommendation"]
            state["market_analysis"]
            state["user_context"]

            # Calculate position size based on confidence and risk
            base_position_size = 0.02  # 2% base position
            confidence_multiplier = recommendation["confidence"]
            risk_multiplier = 1.0 if state["risk_assessment"]["risk_level"] == "low" else 0.7

            position_size = base_position_size * confidence_multiplier * risk_multiplier
            position_size = max(0.01, min(0.1, position_size))  # Between 1% and 10%

            # Calculate stop loss and take profit
            stop_loss = 0.1 if recommendation["action"] != "hold" else 0.0
            take_profit = 0.2 if recommendation["action"] != "hold" else 0.0

            # Determine time horizon
            time_horizon = "short" if recommendation["action"] != "hold" else "none"

            final_decision = {
                "action": recommendation["action"],
                "confidence": recommendation["confidence"],
                "position_size": position_size,
                "time_horizon": time_horizon,
                "stop_loss": stop_loss,
                "take_profit": take_profit,
                "reasoning": recommendation["reasoning"],
                "warnings": self._generate_warnings(state),
                "ai_provider": recommendation.get("ai_provider", "fallback")
            }

            state["final_decision"] = final_decision
            state["confidence_score"] = recommendation["confidence"]
            state["reasoning_steps"].append("Decision finalized")

            return state

        except Exception as e:
            logger.error(f"Error in finalization node: {e}")
            return state

    def _determine_ai_provider(self) -> str:
        """Determine which AI provider to use"""
        # Check user preference
        if hasattr(settings, 'ai_provider'):
            preferred_provider = getattr(settings, 'ai_provider', 'local')
        else:
            preferred_provider = 'local'

        # Check availability
        if preferred_provider == "local" and self.local_ai_enabled:
            available_models = local_ai_manager.get_available_models()
            if available_models:
                return "local"

        if preferred_provider == "openai" and self.openai_llm:
            return "openai"

        # Fallback logic
        if self.local_ai_enabled and local_ai_manager.get_available_models():
            return "local"
        elif self.openai_llm:
            return "openai"
        else:
            return "fallback"

    async def _assess_risk_with_local_ai(self, market_analysis: dict, user_context: dict) -> dict:
        """Assess risk using local AI"""
        try:
            prompt = f"""
            Assess the trading risk for the following market analysis:

            Market Analysis:
            - Trend: {market_analysis.get('trend_direction', 'unknown')}
            - Confidence: {market_analysis.get('confidence_score', 0.5)}
            - Risk Level: {market_analysis.get('risk_level', 'medium')}

            User Context:
            - Account Balance: ${user_context.get('account_balance', 1000)}
            - Risk Tolerance: {user_context.get('risk_tolerance', 'medium')}
            - Experience: {user_context.get('experience_level', 'intermediate')}

            Provide a risk assessment in JSON format with:
            - risk_level: low/medium/high
            - risk_score: 0.0-1.0
            - risk_factors: list of risk factors
            """

            response = await local_ai_manager.generate_response(
                prompt=prompt,
                temperature=0.1,
                max_tokens=500
            )

            # Parse response
            try:
                import json
                import re
                json_match = re.search(r'\{.*\}', response.content, re.DOTALL)
                if json_match:
                    data = json.loads(json_match.group())
                    data["ai_provider"] = "local"
                    return data
                else:
                    return self._basic_risk_assessment(market_analysis, user_context)
            except:
                return self._basic_risk_assessment(market_analysis, user_context)

        except Exception as e:
            logger.error(f"Error in local AI risk assessment: {e}")
            return self._basic_risk_assessment(market_analysis, user_context)

    async def _assess_risk_with_openai(self, market_analysis: dict, user_context: dict) -> dict:
        """Assess risk using OpenAI"""
        # Implementation for OpenAI risk assessment
        return self._basic_risk_assessment(market_analysis, user_context)

    def _basic_risk_assessment(self, market_analysis: dict, user_context: dict) -> dict:
        """Basic risk assessment without AI"""
        risk_level = market_analysis.get("risk_level", "medium")
        risk_score = 0.5

        if risk_level == "high":
            risk_score = 0.8
        elif risk_level == "low":
            risk_score = 0.2

        return {
            "risk_level": risk_level,
            "risk_score": risk_score,
            "risk_factors": ["Basic risk assessment"],
            "ai_provider": "fallback"
        }

    async def _generate_recommendation_with_local_ai(self, market_analysis: dict, risk_assessment: dict, user_context: dict) -> dict:
        """Generate recommendation using local AI"""
        try:
            prompt = f"""
            Generate a trading recommendation based on:

            Market Analysis:
            - Trend: {market_analysis.get('trend_direction', 'unknown')}
            - Action: {market_analysis.get('recommended_action', 'hold')}
            - Confidence: {market_analysis.get('confidence_score', 0.5)}

            Risk Assessment:
            - Level: {risk_assessment.get('risk_level', 'medium')}
            - Score: {risk_assessment.get('risk_score', 0.5)}

            User Context:
            - Balance: ${user_context.get('account_balance', 1000)}
            - Risk Tolerance: {user_context.get('risk_tolerance', 'medium')}

            Provide recommendation in JSON format with:
            - action: buy_call/buy_put/hold
            - confidence: 0.0-1.0
            - reasoning: detailed explanation
            """

            response = await local_ai_manager.generate_response(
                prompt=prompt,
                temperature=0.1,
                max_tokens=500
            )

            # Parse response
            try:
                import json
                import re
                json_match = re.search(r'\{.*\}', response.content, re.DOTALL)
                if json_match:
                    data = json.loads(json_match.group())
                    data["ai_provider"] = "local"
                    return data
                else:
                    return self._basic_recommendation(market_analysis, risk_assessment, user_context)
            except:
                return self._basic_recommendation(market_analysis, risk_assessment, user_context)

        except Exception as e:
            logger.error(f"Error in local AI recommendation: {e}")
            return self._basic_recommendation(market_analysis, risk_assessment, user_context)

    async def _generate_recommendation_with_openai(self, market_analysis: dict, risk_assessment: dict, user_context: dict) -> dict:
        """Generate recommendation using OpenAI"""
        # Implementation for OpenAI recommendation
        return self._basic_recommendation(market_analysis, risk_assessment, user_context)

    def _basic_recommendation(self, market_analysis: dict, risk_assessment: dict, user_context: dict) -> dict:
        """Basic recommendation without AI"""
        action = market_analysis.get("recommended_action", "hold")
        confidence = market_analysis.get("confidence_score", 0.5)

        # Adjust confidence based on risk
        if risk_assessment.get("risk_level") == "high":
            confidence *= 0.8

        return {
            "action": action,
            "confidence": confidence,
            "reasoning": f"Basic recommendation based on {action} signal",
            "ai_provider": "fallback"
        }

    def _generate_warnings(self, state: TradingState) -> list[str]:
        """Generate warnings for the trading decision"""
        warnings = []

        market_analysis = state["market_analysis"]
        risk_assessment = state["risk_assessment"]

        if market_analysis.get("confidence_score", 0) < 0.6:
            warnings.append("Low confidence in market analysis")

        if risk_assessment.get("risk_level") == "high":
            warnings.append("High risk level detected")

        if not warnings:
            warnings.append("No specific warnings")

        return warnings

    def _fallback_decision(self, symbol: str, user_context: dict[str, Any]) -> TradingDecision:
        """Fallback decision when workflow fails"""
        return TradingDecision(
            action="hold",
            confidence=0.3,
            position_size=0.01,
            time_horizon="none",
            stop_loss=0.0,
            take_profit=0.0,
            reasoning="Fallback decision due to system error",
            warnings=["System error occurred", "Using fallback decision"],
            ai_provider="fallback"
        )
