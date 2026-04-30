"""
Pydantic models for Project Ideas RAG System metadata
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum


class ComplexityLevel(str, Enum):
    """Project complexity levels"""
    BASIC = "basic"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class ProjectCategory(str, Enum):
    """Project categories for data analyst projects"""
    PREDICTION = "prediction"
    CLASSIFICATION = "classification"
    COMPUTER_VISION = "computer_vision"
    NLP = "nlp"
    OPTIMIZATION = "optimization"
    DASHBOARD = "dashboard"
    DATA_ENGINEERING = "data_engineering"
    EXPLORATORY_ANALYSIS = "exploratory_analysis"
    ANOMALY_DETECTION = "anomaly_detection"
    TIME_SERIES = "time_series"
    RECOMMENDATION = "recommendation"
    CLUSTERING = "clustering"
    A_B_TESTING = "a_b_testing"
    ETL = "etl"
    OTHER = "other"


class ImpactMetrics(BaseModel):
    """Impact and ROI metrics"""
    estimated_roi: Optional[float] = Field(None, description="Estimated ROI as percentage")
    cost_savings: Optional[str] = Field(None, description="Expected cost savings")
    time_savings: Optional[str] = Field(None, description="Expected time savings")
    business_value: Optional[str] = Field(None, description="Qualitative business value")
    implementation_cost: Optional[str] = Field(None, description="Estimated implementation cost")
    effort_hours: Optional[int] = Field(None, description="Estimated effort in hours")

    class Config:
        json_schema_extra = {
            "example": {
                "estimated_roi": 25.5,
                "cost_savings": "$100,000/year",
                "time_savings": "50 hours/month",
                "business_value": "Improved customer retention",
                "effort_hours": 160
            }
        }


class ProjectMetadata(BaseModel):
    """Complete metadata for a project idea document"""

    # Core identifiers
    document_id: str = Field(..., description="Unique document identifier")
    title: str = Field(..., description="Project title")
    source_file: str = Field(..., description="Source file path")
    file_type: str = Field(..., description="File type/extension")
    upload_date: datetime = Field(default_factory=datetime.now, description="Upload timestamp")

    # Content summary
    summary: Optional[str] = Field(None, description="Project summary (2-3 sentences)")
    description: Optional[str] = Field(None, description="Detailed description")

    # Auto-categorization
    primary_category: Optional[ProjectCategory] = Field(None, description="Main project category")
    secondary_categories: List[ProjectCategory] = Field(default_factory=list, description="Additional categories")
    confidence_score: float = Field(0.0, ge=0.0, le=1.0, description="Categorization confidence (0-1)")

    # Technology stack
    technologies: List[str] = Field(default_factory=list, description="All technologies mentioned")
    programming_languages: List[str] = Field(default_factory=list, description="Programming languages")
    frameworks: List[str] = Field(default_factory=list, description="ML/Data frameworks")
    tools: List[str] = Field(default_factory=list, description="Tools and platforms")

    # Complexity analysis
    complexity_level: Optional[ComplexityLevel] = Field(None, description="Project complexity")
    complexity_factors: Dict[str, Any] = Field(default_factory=dict, description="Complexity factor scores")
    skill_requirements: List[str] = Field(default_factory=list, description="Required skills")

    # Impact estimation
    impact_metrics: ImpactMetrics = Field(default_factory=ImpactMetrics, description="Impact and ROI metrics")

    # Business context
    business_domain: Optional[str] = Field(None, description="Business domain (e.g., finance, healthcare)")
    industry: Optional[str] = Field(None, description="Industry sector")
    use_cases: List[str] = Field(default_factory=list, description="Specific use cases")

    # Search and filtering
    keywords: List[str] = Field(default_factory=list, description="Extracted keywords")
    tags: List[str] = Field(default_factory=list, description="User-defined tags")

    # Content statistics
    total_pages: int = Field(0, description="Total pages in document")
    word_count: int = Field(0, description="Total word count")

    # Custom fields
    custom_fields: Dict[str, Any] = Field(default_factory=dict, description="Additional custom metadata")

    class Config:
        json_schema_extra = {
            "example": {
                "document_id": "proj_001",
                "title": "Customer Churn Prediction Model",
                "source_file": "churn_prediction.pdf",
                "file_type": "pdf",
                "summary": "ML model to predict customer churn using historical data",
                "primary_category": "prediction",
                "confidence_score": 0.92,
                "technologies": ["Python", "scikit-learn", "Pandas"],
                "complexity_level": "intermediate",
                "impact_metrics": {
                    "estimated_roi": 30.0,
                    "cost_savings": "$500,000/year",
                    "effort_hours": 200
                }
            }
        }


class FilterCriteria(BaseModel):
    """Criteria for filtering project ideas"""
    categories: List[ProjectCategory] = Field(default_factory=list, description="Filter by categories")
    technologies: List[str] = Field(default_factory=list, description="Filter by technologies")
    tech_match_mode: str = Field("any", description="Technology match mode: 'any' or 'all'")
    complexity_levels: List[ComplexityLevel] = Field(default_factory=list, description="Filter by complexity")
    min_roi: Optional[float] = Field(None, description="Minimum ROI percentage")
    max_effort_hours: Optional[int] = Field(None, description="Maximum effort in hours")
    keywords: List[str] = Field(default_factory=list, description="Keyword search")
    business_domain: Optional[str] = Field(None, description="Filter by business domain")

    class Config:
        json_schema_extra = {
            "example": {
                "categories": ["prediction", "classification"],
                "technologies": ["Python", "TensorFlow"],
                "tech_match_mode": "any",
                "complexity_levels": ["intermediate"],
                "min_roi": 20.0
            }
        }


class SearchResult(BaseModel):
    """Search result with metadata and relevance score"""
    document_id: str
    metadata: ProjectMetadata
    content_preview: str = Field(..., description="Preview of document content")
    relevance_score: float = Field(0.0, ge=0.0, le=1.0, description="Relevance score (0-1)")

    class Config:
        json_schema_extra = {
            "example": {
                "document_id": "proj_001",
                "content_preview": "This project aims to predict customer churn...",
                "relevance_score": 0.87
            }
        }
