"""Signal Extraction Layer (SEL) - Core Schema Definitions"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum

class SignalCategory(str, Enum):
    """Categories for different types of signals"""
    # YouTube/Money Lab categories
    REVENUE_MECHANIC = "revenue-mechanic"
    SERVICE_OFFERING = "service-offering"
    STACK = "stack"
    OUTBOUND = "outbound"
    PRICING = "pricing"
    SELF_PUBLISHING = "self-publishing"
    TOOL_REFERENCE = "tool-reference"
    
    # RSS categories
    TOOLS_MENTIONED = "tools-mentioned"
    PRICING_DATA = "pricing-data"
    VENDOR_MOVES = "vendor-moves"
    REGULATORY = "regulatory"
    MARKET_STATS = "market-stats"
    
    # Paperclip/Agent categories
    DECISION = "decision"
    LESSON_LEARNED = "lesson-learned"
    GOTCHA = "gotcha"
    REUSABLE_PATTERN = "reusable-pattern"
    FINDING = "finding"
    ANOMALY = "anomaly"
    BLOCKER = "blocker"
    SURPRISE = "surprise"
    
    # KB categories
    FRAMEWORK = "framework"
    FORMULA = "formula"
    CLAIM = "claim"
    METHODOLOGY = "methodology"
    
    # Discord/Activity categories
    PATTERN = "pattern"
    RECURRING_QUESTION = "recurring-question"
    SWARM_BLOCKER = "swarm-blocker"

class SourceRef(BaseModel):
    """Reference to the source of a signal"""
    kind: str = Field(..., description="Source type: youtube, rss, paperclip, agent_heartbeat, kb, discord")
    identifier: str = Field(..., description="Unique identifier in source system")
    url: Optional[str] = None
    path: Optional[str] = None
    location_hint: Optional[str] = None  # e.g., timestamp, section header

class Signal(BaseModel):
    """Core Signal abstraction - a structured insight extracted from any source"""
    
    id: str = Field(..., description="Deterministic from source + chunk hash")
    category: str = Field(..., description="Signal category")
    sub_tags: List[str] = Field(default_factory=list)
    
    # Content
    quote: str = Field(..., description="Exact source content")
    paraphrase: str = Field(..., description="Concise paraphrase/extraction")
    
    # Quality metrics
    confidence: float = Field(default=0.8, ge=0.0, le=1.0)
    parent_score: Optional[float] = None  # Source-specific scorer output
    
    # Provenance
    source: SourceRef
    extracted_by: str = Field(..., description="Agent/tool that extracted")
    extracted_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Optional enrichment
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "yt-abc123-revenue-mechanic-0",
                "category": "revenue-mechanic",
                "sub_tags": ["saas", "b2b"],
                "quote": "We charge $500/month for the enterprise tier",
                "paraphrase": "Pricing model: $500/month enterprise SaaS tier",
                "confidence": 0.92,
                "source": {
                    "kind": "youtube",
                    "identifier": "yt_video_id_123",
                    "url": "https://youtube.com/watch?v=...",
                    "location_hint": "12:34"
                },
                "extracted_by": "money_lab_extractor_v1"
            }
        }

def generate_signal_id(source_kind: str, source_id: str, category: str, chunk_idx: int = 0) -> str:
    """Generate deterministic signal ID"""
    import hashlib
    content = f"{source_kind}:{source_id}:{category}:{chunk_idx}"
    return f"sig-{hashlib.sha256(content.encode()).hexdigest()[:16]}"
