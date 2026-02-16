"""System Orchestrator Agent - coordinates all agents and makes final decisions."""

import logging
from typing import Any, Dict, List, Optional

from agrilink.agents.base import AgentResponse, BaseAgent
from agrilink.agents.prompts import get_agent_prompt

logger = logging.getLogger(__name__)


class OrchestratorAgent(BaseAgent):
    """Central orchestrator that coordinates all specialized agents."""

    def __init__(self, **kwargs):
        """Initialize Orchestrator Agent."""
        super().__init__(agent_name="OrchestratorAgent", **kwargs)

    def get_system_prompt(self) -> str:
        """Get system prompt for orchestrator."""
        return get_agent_prompt("orchestrator")

    async def process(self, context: Dict[str, Any]) -> AgentResponse:
        """
        Process and coordinate agent responses.
        
        This method is typically not called directly. Instead, use orchestrate().
        """
        raise NotImplementedError("Use orchestrate() method instead")

    async def orchestrate(
        self,
        agent_responses: List[AgentResponse],
        context: Dict[str, Any],
    ) -> AgentResponse:
        """
        Orchestrate multiple agent responses into a final decision.
        
        Args:
            agent_responses: List of responses from specialized agents
            context: Original request context
            
        Returns:
            Final orchestrated response
        """
        if not agent_responses:
            return self.create_response(
                recommendation="No agent responses available to orchestrate.",
                confidence=0.0,
                reasoning="No input from specialized agents",
                sources=[],
            )
        
        # Filter out low-confidence responses
        valid_responses = [
            r for r in agent_responses
            if r.confidence >= self.settings.minimum_confidence_for_action
        ]
        
        if not valid_responses:
            # All responses below confidence threshold
            return self._create_cautious_response(agent_responses, context)
        
        # Check for conflicts
        if self._has_conflicts(valid_responses):
            return await self._resolve_conflicts(valid_responses, context)
        
        # Synthesize complementary insights
        return await self._synthesize_responses(valid_responses, context)

    def _has_conflicts(self, responses: List[AgentResponse]) -> bool:
        """Check if agent responses conflict with each other."""
        # Simplified conflict detection
        # In production, implement more sophisticated conflict detection
        recommendations = [r.recommendation.lower() for r in responses]
        
        # Check for obvious conflicts (e.g., "buy" vs "sell")
        has_buy = any("buy" in rec for rec in recommendations)
        has_sell = any("sell" in rec for rec in recommendations)
        
        return has_buy and has_sell

    async def _resolve_conflicts(
        self,
        responses: List[AgentResponse],
        context: Dict[str, Any],
    ) -> AgentResponse:
        """Resolve conflicting agent recommendations."""
        logger.warning("Conflicting agent recommendations detected")
        
        # Sort by confidence
        sorted_responses = sorted(responses, key=lambda r: r.confidence, reverse=True)
        
        # Build conflict resolution prompt
        conflict_summary = "\n\n".join([
            f"Agent: {r.agent_name}\n"
            f"Recommendation: {r.recommendation}\n"
            f"Confidence: {r.confidence}\n"
            f"Reasoning: {r.reasoning}"
            for r in sorted_responses
        ])
        
        resolution_prompt = f"""Multiple agents have provided conflicting recommendations. Resolve the conflict and provide a final recommendation.

Agent Responses:
{conflict_summary}

Context: {context}

Provide:
1. Analysis of the conflict
2. Final recommendation (considering confidence levels and reasoning quality)
3. Explanation of resolution
4. Warnings about conflicting viewpoints

Format as:
FINAL_RECOMMENDATION: [clear recommendation]
RESOLUTION_REASONING: [why this resolution]
CONFIDENCE: [0.0 to 1.0]
WARNINGS: [important caveats]
"""
        
        resolution = await self.reason(resolution_prompt)
        
        # Parse resolution
        final_rec = self._extract_section(resolution, "FINAL_RECOMMENDATION")
        reasoning = self._extract_section(resolution, "RESOLUTION_REASONING")
        warnings = self._extract_section(resolution, "WARNINGS")
        confidence_str = self._extract_section(resolution, "CONFIDENCE")
        
        try:
            confidence = float(confidence_str) if confidence_str else 0.5
        except ValueError:
            confidence = 0.5
        
        # Aggregate sources from all agents
        all_sources = []
        for r in responses:
            all_sources.extend(r.sources)
        
        recommendation_text = final_rec or resolution
        if warnings:
            recommendation_text += f"\n\n⚠️ Important Considerations:\n{warnings}"
        
        return self.create_response(
            recommendation=recommendation_text,
            confidence=confidence,
            reasoning=reasoning or "Resolved conflicting agent recommendations",
            sources=all_sources,
            metadata={
                "conflict_resolved": True,
                "num_agents": len(responses),
                "agent_names": [r.agent_name for r in responses],
            },
        )

    async def _synthesize_responses(
        self,
        responses: List[AgentResponse],
        context: Dict[str, Any],
    ) -> AgentResponse:
        """Synthesize complementary agent responses."""
        # Build synthesis prompt
        responses_summary = "\n\n".join([
            f"Agent: {r.agent_name}\n"
            f"Recommendation: {r.recommendation}\n"
            f"Confidence: {r.confidence}\n"
            f"Reasoning: {r.reasoning}"
            for r in responses
        ])
        
        synthesis_prompt = f"""Synthesize the following complementary agent recommendations into a coherent final recommendation.

Agent Responses:
{responses_summary}

Provide:
1. Unified recommendation incorporating all insights
2. Prioritized action items
3. Overall confidence assessment
4. Key considerations

Format as:
UNIFIED_RECOMMENDATION: [synthesized recommendation]
ACTION_ITEMS: [prioritized list]
CONFIDENCE: [0.0 to 1.0]
CONSIDERATIONS: [important points]
"""
        
        synthesis = await self.reason(synthesis_prompt)
        
        # Parse synthesis
        unified_rec = self._extract_section(synthesis, "UNIFIED_RECOMMENDATION")
        action_items = self._extract_section(synthesis, "ACTION_ITEMS")
        considerations = self._extract_section(synthesis, "CONSIDERATIONS")
        confidence_str = self._extract_section(synthesis, "CONFIDENCE")
        
        try:
            confidence = float(confidence_str) if confidence_str else 0.7
        except ValueError:
            # Use average confidence from agents
            confidence = sum(r.confidence for r in responses) / len(responses)
        
        # Aggregate sources
        all_sources = []
        for r in responses:
            all_sources.extend(r.sources)
        
        recommendation_text = unified_rec or synthesis
        if action_items:
            recommendation_text += f"\n\nAction Items:\n{action_items}"
        if considerations:
            recommendation_text += f"\n\nKey Considerations:\n{considerations}"
        
        return self.create_response(
            recommendation=recommendation_text,
            confidence=confidence,
            reasoning="Synthesized from multiple agent insights",
            sources=all_sources,
            metadata={
                "num_agents": len(responses),
                "agent_names": [r.agent_name for r in responses],
                "avg_agent_confidence": sum(r.confidence for r in responses) / len(responses),
            },
        )

    def _create_cautious_response(
        self,
        responses: List[AgentResponse],
        context: Dict[str, Any],
    ) -> AgentResponse:
        """Create a cautious response when all agent confidences are low."""
        avg_confidence = sum(r.confidence for r in responses) / len(responses) if responses else 0.0
        
        recommendation = (
            "Based on available information, I cannot provide a high-confidence recommendation. "
            "The specialized agents have identified the following insights, but with low confidence:\n\n"
        )
        
        for r in responses:
            recommendation += f"- {r.agent_name}: {r.recommendation[:100]}... (confidence: {r.confidence:.2f})\n"
        
        recommendation += (
            "\n⚠️ Recommendation: Gather more information or consult with domain experts "
            "before making critical decisions."
        )
        
        all_sources = []
        for r in responses:
            all_sources.extend(r.sources)
        
        return self.create_response(
            recommendation=recommendation,
            confidence=avg_confidence,
            reasoning="All agent responses below confidence threshold",
            sources=all_sources,
            metadata={
                "cautious_mode": True,
                "num_agents": len(responses),
            },
        )

    def _extract_section(self, text: str, section_name: str) -> str:
        """Extract a section from formatted text."""
        lines = text.split("\n")
        for i, line in enumerate(lines):
            if line.strip().startswith(f"{section_name}:"):
                return line.split(":", 1)[1].strip()
        return ""

    async def handle_event(self, event: Dict[str, Any]) -> Optional[AgentResponse]:
        """Orchestrator typically doesn't handle events directly."""
        return None
