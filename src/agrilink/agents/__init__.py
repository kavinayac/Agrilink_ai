"""Agent system initialization and registry."""

from typing import Dict, Type

# Agent registry will be populated as agents are imported
AGENT_REGISTRY: Dict[str, Type] = {}
