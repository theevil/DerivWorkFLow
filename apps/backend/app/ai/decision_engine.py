"""
Trading Decision Engine using LangGraph for workflow-based trading decisions
"""

import json
from typing import Annotated, Any, Optional, TypedDict

from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema import BaseMessage, HumanMessage, SystemMessage
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from loguru import logger
from pydantic import BaseModel, Field

from app.core.config import settings

from .market_analyzer import (
    AdvancedMarketAnalyzer,
    MarketAnalysisResult,
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
    action: str = Field(description="Final trading action: BUY_CALL, BUY_PUT, HOLD")
    confidence: float = Field(description="Overall confidence (0-1)", ge=0, le=1)
    position_size: float = Field(description="Recommended position size")
    duration: int = Field(description="Recommended duration in seconds")
    risk_level: str = Field(description="Overall risk level: low, medium, high")
    stop_loss_level: Optional[float] = Field(description="Recommended stop loss level")
    take_profit_level: Optional[float] = Field(description="Recommended take profit level")
    reasoning: str = Field(description="Complete reasoning chain")
    validation_checks: list[str] = Field(description="Validation checks performed")
    warnings: list[str] = Field(description="Risk warnings and considerations")


class TradingDecisionEngine:
    """
    Advanced trading decision engine using LangGraph workflows
    """

    def __init__(self):
        """Initialize the trading decision engine"""
        self.market_analyzer = AdvancedMarketAnalyzer()

        # Initialize LLM
        if settings.openai_api_key:
            self.llm = ChatOpenAI(
                model=settings.ai_model,
                temperature=settings.ai_temperature,
                max_tokens=settings.ai_max_tokens,
                openai_api_key=settings.openai_api_key
            )
        else:
            self.llm = None
            logger.warning("OpenAI API key not configured. Decision engine will use fallback logic.")

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
        """Market analysis node"""
        try:
            logger.info(f"Starting market analysis for {state['symbol']}")

            # Perform advanced market analysis
            analysis = await self.market_analyzer.analyze_market_advanced(
                symbol=state["symbol"],
                price_history=state["price_history"],
                current_price=state["current_price"]
            )

            # Convert to dict for state storage
            analysis_dict = analysis.dict()

            # Update state
            state["market_analysis"] = analysis_dict
            state["reasoning_steps"].append(f"Market Analysis: {analysis.reasoning}")

            # Add analysis message
            state["messages"].append(
                HumanMessage(content=f"Market analysis completed for {state['symbol']}: {analysis.recommended_action}")
            )

            logger.info(f"Market analysis completed: {analysis.recommended_action}")

        except Exception as e:
            logger.error(f"Error in market analysis node: {e}")
            state["market_analysis"] = {"error": str(e)}

        return state

    async def _assess_risk_node(self, state: TradingState) -> TradingState:
        """Risk assessment node"""
        try:
            logger.info("Performing risk assessment")

            # Get market analysis
            market_analysis = state.get("market_analysis", {})
            user_context = state["user_context"]

            # Perform risk assessment
            if self.llm and market_analysis and not market_analysis.get("error"):
                risk_assessment = await self._llm_risk_assessment(market_analysis, user_context, state)
            else:
                risk_assessment = self._basic_risk_assessment(market_analysis or {}, user_context, state)

            # Update state
            state["risk_assessment"] = risk_assessment
            state["reasoning_steps"].append(f"Risk Assessment: {risk_assessment.get('summary', 'Basic risk evaluation')}")

            # Add risk message
            state["messages"].append(
                HumanMessage(content=f"Risk assessment: {risk_assessment.get('level', 'unknown')} risk level")
            )

            logger.info(f"Risk assessment completed: {risk_assessment.get('level', 'unknown')} risk")

        except Exception as e:
            logger.error(f"Error in risk assessment node: {e}")
            state["risk_assessment"] = {"error": str(e), "level": "high"}

        return state

    async def _generate_recommendation_node(self, state: TradingState) -> TradingState:
        """Generate trading recommendation node"""
        try:
            logger.info("Generating trading recommendation")

            market_analysis = state.get("market_analysis", {})
            risk_assessment = state.get("risk_assessment", {})
            user_context = state["user_context"]

            # Generate recommendation
            if self.llm and market_analysis and risk_assessment and not any(data.get("error") for data in [market_analysis, risk_assessment]):
                # Convert back to MarketAnalysisResult for LLM processing
                try:
                    analysis_result = MarketAnalysisResult(**market_analysis)
                    recommendation = await self.market_analyzer.get_trading_recommendation(
                        analysis_result, user_context
                    )
                    recommendation_dict = recommendation.dict()
                except Exception as e:
                    logger.warning(f"Error converting to MarketAnalysisResult: {e}")
                    recommendation_dict = self._basic_recommendation(market_analysis or {}, risk_assessment or {}, user_context)
            else:
                recommendation_dict = self._basic_recommendation(market_analysis or {}, risk_assessment or {}, user_context)

            # Update state
            state["trading_recommendation"] = recommendation_dict
            state["reasoning_steps"].append(f"Recommendation: {recommendation_dict.get('reasoning', 'Basic recommendation logic')}")

            # Add recommendation message
            state["messages"].append(
                HumanMessage(content=f"Trading recommendation: {recommendation_dict.get('action', 'HOLD')}")
            )

            logger.info(f"Recommendation generated: {recommendation_dict.get('action', 'HOLD')}")

        except Exception as e:
            logger.error(f"Error in recommendation node: {e}")
            state["trading_recommendation"] = {"action": "HOLD", "error": str(e)}

        return state

    async def _validate_decision_node(self, state: TradingState) -> TradingState:
        """Validate trading decision node"""
        try:
            logger.info("Validating trading decision")

            recommendation = state.get("trading_recommendation", {})
            risk_assessment = state.get("risk_assessment", {})
            user_context = state["user_context"]

            # Perform validation checks
            validation_results = self._perform_validation_checks(recommendation or {}, risk_assessment or {}, user_context)

            # Update confidence based on validation
            confidence = (recommendation or {}).get("confidence", 0.5)
            if validation_results["passed_checks"] < validation_results["total_checks"] * 0.5:
                confidence *= 0.5  # Reduce confidence if many checks failed

            state["confidence_score"] = confidence
            state["reasoning_steps"].append(f"Validation: {validation_results['summary']}")

            # Add validation message
            state["messages"].append(
                HumanMessage(content=f"Validation completed: {validation_results['passed_checks']}/{validation_results['total_checks']} checks passed")
            )

            logger.info(f"Validation completed: {validation_results['passed_checks']}/{validation_results['total_checks']} checks passed")

        except Exception as e:
            logger.error(f"Error in validation node: {e}")
            state["confidence_score"] = 0.3  # Low confidence on error
            state["reasoning_steps"].append(f"Validation error: {str(e)}")

        return state

    async def _finalize_decision_node(self, state: TradingState) -> TradingState:
        """Finalize trading decision node"""
        try:
            logger.info("Finalizing trading decision")

            # Gather all components
            market_analysis = state.get("market_analysis", {})
            risk_assessment = state.get("risk_assessment", {})
            recommendation = state.get("trading_recommendation", {})
            confidence = state.get("confidence_score", 0.5)
            user_context = state["user_context"]

            # Create final decision
            final_decision = self._create_final_decision(
                market_analysis or {}, risk_assessment or {}, recommendation or {},
                confidence, state["reasoning_steps"], user_context
            )

            state["final_decision"] = final_decision

            # Add final message
            state["messages"].append(
                HumanMessage(content=f"Final decision: {final_decision['action']} with {final_decision['confidence']:.2f} confidence")
            )

            logger.info(f"Decision finalized: {final_decision['action']} (confidence: {final_decision['confidence']:.2f})")

        except Exception as e:
            logger.error(f"Error in finalization node: {e}")
            state["final_decision"] = self._emergency_decision()

        return state

    async def _llm_risk_assessment(self, market_analysis: dict, user_context: dict, state: TradingState) -> dict:
        """Perform LLM-based risk assessment"""

        risk_prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content="""You are a risk management expert for synthetic indices trading.

            Analyze the provided market data and user context to assess trading risk.

            Consider:
            - Market volatility and current conditions
            - User's risk tolerance and account size
            - Position sizing relative to account balance
            - Market timing and entry quality
            - Potential drawdown scenarios

            Provide a structured risk assessment with clear reasoning."""),

            HumanMessage(content="""Assess the trading risk for this scenario:

            MARKET ANALYSIS:
            - Trend: {trend}
            - Confidence: {confidence}
            - Risk Level: {risk_level}
            - Recommended Action: {action}

            USER CONTEXT:
            - Account Balance: ${balance}
            - Risk Tolerance: {risk_tolerance}
            - Max Daily Loss: ${max_loss}
            - Experience: {experience}

            CURRENT POSITION:
            - Symbol: {symbol}
            - Current Price: {price}

            Provide risk assessment in JSON format:
            {{
                "level": "low|medium|high",
                "score": 0.0-1.0,
                "factors": ["factor1", "factor2"],
                "warnings": ["warning1", "warning2"],
                "recommendations": ["rec1", "rec2"],
                "summary": "brief summary"
            }}
            """)
        ])

        try:
            formatted_prompt = risk_prompt.format(
                trend=market_analysis.get("trend_direction", "unknown"),
                confidence=market_analysis.get("confidence_score", 0.5),
                risk_level=market_analysis.get("risk_level", "medium"),
                action=market_analysis.get("recommended_action", "hold"),
                balance=user_context.get("account_balance", 1000),
                risk_tolerance=user_context.get("risk_tolerance", "medium"),
                max_loss=user_context.get("max_daily_loss", 50),
                experience=user_context.get("experience_level", "intermediate"),
                symbol=state["symbol"],
                price=state["current_price"]
            )

            response = await self.llm.ainvoke(formatted_prompt.messages)

            # Try to parse JSON response
            risk_data = json.loads(response.content)
            return risk_data

        except Exception as e:
            logger.error(f"Error in LLM risk assessment: {e}")
            return self._basic_risk_assessment(market_analysis, user_context, state)

    def _basic_risk_assessment(self, market_analysis: dict, user_context: dict, state: TradingState) -> dict:
        """Basic risk assessment fallback"""

        # Calculate risk factors
        risk_factors = []
        risk_score = 0.5

        # Market risk
        market_risk = market_analysis.get("risk_level", "medium")
        if market_risk == "high":
            risk_score += 0.2
            risk_factors.append("High market volatility")
        elif market_risk == "low":
            risk_score -= 0.1

        # Confidence risk
        confidence = market_analysis.get("confidence_score", 0.5)
        if confidence < 0.6:
            risk_score += 0.1
            risk_factors.append("Low analysis confidence")

        # Position sizing risk
        account_balance = user_context.get("account_balance", 1000)
        position_size = user_context.get("max_position_size", 100)
        if position_size / account_balance > 0.1:  # More than 10% of account
            risk_score += 0.2
            risk_factors.append("Large position size relative to account")

        # Determine risk level
        if risk_score > 0.7:
            level = "high"
        elif risk_score < 0.4:
            level = "low"
        else:
            level = "medium"

        return {
            "level": level,
            "score": min(1.0, max(0.0, risk_score)),
            "factors": risk_factors,
            "warnings": ["Basic risk assessment only"] if not self.llm else [],
            "recommendations": ["Monitor position closely", "Use appropriate position sizing"],
            "summary": f"Risk level assessed as {level} based on technical factors"
        }

    def _basic_recommendation(self, market_analysis: dict, risk_assessment: dict, user_context: dict) -> dict:
        """Basic recommendation fallback"""

        # Get action from market analysis
        action = market_analysis.get("recommended_action", "hold")
        action_map = {
            "buy_call": "BUY_CALL",
            "buy_put": "BUY_PUT",
            "hold": "HOLD"
        }
        final_action = action_map.get(action, "HOLD")

        # Calculate confidence
        confidence = market_analysis.get("confidence_score", 0.5)
        risk_assessment.get("score", 0.5)

        # Adjust confidence based on risk
        if risk_assessment.get("level") == "high":
            confidence *= 0.7
        elif risk_assessment.get("level") == "low":
            confidence *= 1.1

        confidence = min(1.0, max(0.0, confidence))

        return {
            "action": final_action,
            "confidence": confidence,
            "position_size_multiplier": 1.0,
            "time_horizon": "short",
            "stop_loss_adjustment": 1.0,
            "reasoning": f"Basic recommendation based on market analysis: {action}"
        }

    def _perform_validation_checks(self, recommendation: dict, risk_assessment: dict, user_context: dict) -> dict:
        """Perform validation checks on trading decision"""

        checks = []
        passed = 0

        # Check 1: Confidence threshold
        confidence = recommendation.get("confidence", 0.0)
        if confidence >= settings.ai_confidence_threshold:
            checks.append("✓ Confidence above threshold")
            passed += 1
        else:
            checks.append("✗ Confidence below threshold")

        # Check 2: Risk level acceptable
        risk_level = risk_assessment.get("level", "high")
        user_risk_tolerance = user_context.get("risk_tolerance", "medium")

        risk_compatible = (
            (risk_level == "low") or
            (risk_level == "medium" and user_risk_tolerance in ["medium", "high"]) or
            (risk_level == "high" and user_risk_tolerance == "high")
        )

        if risk_compatible:
            checks.append("✓ Risk level compatible with user tolerance")
            passed += 1
        else:
            checks.append("✗ Risk level exceeds user tolerance")

        # Check 3: Position sizing
        account_balance = user_context.get("account_balance", 1000)
        max_position = user_context.get("max_position_size", 100)

        if max_position <= account_balance * 0.2:  # Max 20% of account
            checks.append("✓ Position size within limits")
            passed += 1
        else:
            checks.append("✗ Position size too large")

        # Check 4: Daily loss limit
        max_daily_loss = user_context.get("max_daily_loss", 50)
        if max_position <= max_daily_loss:
            checks.append("✓ Position within daily loss limit")
            passed += 1
        else:
            checks.append("✗ Position exceeds daily loss limit")

        return {
            "checks": checks,
            "passed_checks": passed,
            "total_checks": len(checks),
            "summary": f"Passed {passed}/{len(checks)} validation checks"
        }

    def _create_final_decision(
        self,
        market_analysis: dict,
        risk_assessment: dict,
        recommendation: dict,
        confidence: float,
        reasoning_steps: list[str],
        user_context: dict
    ) -> dict:
        """Create the final trading decision"""

        # Get base recommendation
        action = recommendation.get("action", "HOLD")

        # Override action if risk is too high
        if risk_assessment.get("level") == "high" and confidence < 0.7:
            action = "HOLD"
            reasoning_steps.append("Action overridden to HOLD due to high risk and low confidence")

        # Calculate position size
        base_size = user_context.get("max_position_size", 50)
        size_multiplier = recommendation.get("position_size_multiplier", 1.0)
        position_size = base_size * size_multiplier * confidence

        # Ensure position size limits
        max_allowed = min(
            user_context.get("account_balance", 1000) * 0.1,  # 10% of account max
            user_context.get("max_daily_loss", 50)  # Daily loss limit
        )
        position_size = min(position_size, max_allowed)

        # Calculate duration (default 5 minutes for synthetic indices)
        duration = 300  # 5 minutes
        time_horizon = recommendation.get("time_horizon", "short")
        if time_horizon == "medium":
            duration = 600  # 10 minutes
        elif time_horizon == "long":
            duration = 900  # 15 minutes

        # Create validation checks list
        validation_checks = self._perform_validation_checks(recommendation, risk_assessment, user_context)

        # Create warnings
        warnings = []
        if risk_assessment.get("level") == "high":
            warnings.append("High risk trade - monitor closely")
        if confidence < 0.6:
            warnings.append("Low confidence signal - consider reducing position size")
        if action != recommendation.get("action", "HOLD"):
            warnings.append("Original recommendation overridden due to risk factors")

        warnings.extend(risk_assessment.get("warnings", []))

        return {
            "action": action,
            "confidence": confidence,
            "position_size": position_size,
            "duration": duration,
            "risk_level": risk_assessment.get("level", "medium"),
            "stop_loss_level": None,  # Could be enhanced with specific levels
            "take_profit_level": None,  # Could be enhanced with specific levels
            "reasoning": " | ".join(reasoning_steps),
            "validation_checks": validation_checks["checks"],
            "warnings": warnings
        }

    def _emergency_decision(self) -> dict:
        """Emergency fallback decision"""
        return {
            "action": "HOLD",
            "confidence": 0.1,
            "position_size": 0,
            "duration": 300,
            "risk_level": "high",
            "stop_loss_level": None,
            "take_profit_level": None,
            "reasoning": "Emergency decision due to system error",
            "validation_checks": ["✗ System error occurred"],
            "warnings": ["System error - manual review required"]
        }

    def _fallback_decision(self, symbol: str, user_context: dict) -> TradingDecision:
        """Complete fallback decision when workflow fails"""
        return TradingDecision(
            action="HOLD",
            confidence=0.2,
            position_size=0,
            duration=300,
            risk_level="high",
            reasoning="Fallback decision due to system limitations",
            validation_checks=["✗ System fallback"],
            warnings=["System operating in limited mode - manual review recommended"]
        )
