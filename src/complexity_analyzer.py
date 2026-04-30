"""
Complexity Analyzer - Multi-factor complexity scoring for projects
"""
import logging
import json
import re
from typing import Tuple, Dict
from pathlib import Path

from config import (
    COMPLEXITY_RULES_FILE,
    ENABLE_COMPLEXITY_ANALYSIS
)
from schemas import ComplexityLevel

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ComplexityAnalyzer:
    """
    Analyze project complexity based on multiple factors:
    - Data complexity (volume, variety, velocity)
    - Algorithm complexity (ML models, techniques)
    - Technical skills required
    - Integration complexity
    - Deployment complexity
    """

    def __init__(self):
        self.complexity_factors = {}
        self.complexity_thresholds = {
            'basic': {'min': 0.0, 'max': 0.35},
            'intermediate': {'min': 0.35, 'max': 0.65},
            'advanced': {'min': 0.65, 'max': 1.0}
        }
        self.enabled = ENABLE_COMPLEXITY_ANALYSIS
        self._load_complexity_rules()

    def _load_complexity_rules(self):
        """Load complexity rules from JSON file"""
        try:
            if COMPLEXITY_RULES_FILE.exists():
                with open(COMPLEXITY_RULES_FILE, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    self.complexity_factors = config.get('complexity_factors', {})
                    self.complexity_thresholds = config.get('complexity_thresholds', self.complexity_thresholds)
                logger.info(f"Loaded {len(self.complexity_factors)} complexity factors")
            else:
                logger.warning(f"Complexity rules file not found: {COMPLEXITY_RULES_FILE}")
                self._load_default_rules()
        except Exception as e:
            logger.error(f"Error loading complexity rules: {e}")
            self._load_default_rules()

    def _load_default_rules(self):
        """Load minimal default complexity rules as fallback"""
        self.complexity_factors = {
            'data_complexity': {
                'weight': 0.2,
                'indicators': {
                    'big data': 0.9,
                    'large dataset': 0.7,
                    'real-time': 0.8
                }
            },
            'algorithm_complexity': {
                'weight': 0.3,
                'indicators': {
                    'deep learning': 0.9,
                    'machine learning': 0.6,
                    'linear regression': 0.2
                }
            },
            'technical_skills': {
                'weight': 0.3,
                'indicators': {
                    'cloud': 0.6,
                    'api': 0.5,
                    'database': 0.4
                }
            },
            'integration_complexity': {
                'weight': 0.1,
                'indicators': {
                    'integration': 0.6,
                    'legacy': 0.8
                }
            },
            'deployment_complexity': {
                'weight': 0.1,
                'indicators': {
                    'production': 0.6,
                    'scalability': 0.7
                }
            }
        }

    def analyze_complexity(
        self,
        content: str,
        metadata: Dict = None
    ) -> Tuple[ComplexityLevel, Dict[str, float]]:
        """
        Analyze project complexity

        Args:
            content: Document content
            metadata: Additional metadata (optional)

        Returns:
            Tuple of (ComplexityLevel, factor_scores_dict)
        """
        if not self.enabled:
            return ComplexityLevel.INTERMEDIATE, {}

        logger.info("Analyzing project complexity")

        content_lower = content.lower()

        # Score each factor
        factor_scores = {}
        for factor_name, factor_config in self.complexity_factors.items():
            score = self._score_factor(content_lower, factor_config)
            factor_scores[factor_name] = score

        # Calculate weighted average
        total_score = sum(
            score * self.complexity_factors[factor]['weight']
            for factor, score in factor_scores.items()
        )

        # Map to complexity level
        level = self._score_to_level(total_score)

        logger.info(f"Complexity analysis: {level.value} (score: {total_score:.2f})")

        # Add overall score to factor scores
        factor_scores['overall_score'] = total_score

        return level, factor_scores

    def _score_factor(self, content: str, factor_config: Dict) -> float:
        """
        Score a single complexity factor

        Args:
            content: Document content (lowercased)
            factor_config: Factor configuration with indicators

        Returns:
            Factor score (0.0 to 1.0)
        """
        indicators = factor_config.get('indicators', {})

        if not indicators:
            return 0.0

        matched_scores = []
        for indicator, score in indicators.items():
            # Use word boundary regex for better matching
            pattern = r'\b' + re.escape(indicator.lower()) + r'\b'
            if re.search(pattern, content):
                matched_scores.append(score)

        if not matched_scores:
            return 0.0

        # Return max score (most complex indicator found)
        # Alternative: could use average or weighted combination
        return max(matched_scores)

    def _score_to_level(self, score: float) -> ComplexityLevel:
        """
        Convert numerical score to ComplexityLevel

        Args:
            score: Complexity score (0.0 to 1.0)

        Returns:
            ComplexityLevel enum
        """
        for level_name, thresholds in self.complexity_thresholds.items():
            if thresholds['min'] <= score <= thresholds['max']:
                try:
                    return ComplexityLevel(level_name)
                except ValueError:
                    logger.warning(f"Invalid complexity level: {level_name}")
                    return ComplexityLevel.INTERMEDIATE

        # Fallback
        return ComplexityLevel.INTERMEDIATE

    def get_complexity_explanation(self, factor_scores: Dict[str, float]) -> str:
        """
        Generate human-readable explanation of complexity assessment

        Args:
            factor_scores: Dictionary of factor scores from analyze_complexity

        Returns:
            Explanation string
        """
        explanations = []

        for factor_name, score in factor_scores.items():
            if factor_name == 'overall_score':
                continue

            factor_config = self.complexity_factors.get(factor_name, {})
            description = factor_config.get('description', factor_name.replace('_', ' ').title())

            if score > 0.7:
                level = "High"
            elif score > 0.4:
                level = "Medium"
            else:
                level = "Low"

            explanations.append(f"{description}: {level} ({score:.2f})")

        overall = factor_scores.get('overall_score', 0.0)
        explanations.append(f"\nOverall Complexity Score: {overall:.2f}")

        return "\n".join(explanations)

    def identify_skill_requirements(self, content: str) -> list:
        """
        Identify required skills based on content analysis

        Args:
            content: Document content

        Returns:
            List of required skills
        """
        skills = []
        content_lower = content.lower()

        # Define skill indicators
        skill_indicators = {
            'Machine Learning': ['machine learning', 'ml model', 'predictive model'],
            'Deep Learning': ['deep learning', 'neural network', 'cnn', 'rnn', 'lstm'],
            'Data Engineering': ['etl', 'data pipeline', 'data warehouse', 'airflow'],
            'Cloud Computing': ['aws', 'azure', 'gcp', 'cloud'],
            'SQL': ['sql', 'database', 'postgresql', 'mysql'],
            'Python': ['python', 'pandas', 'numpy'],
            'Data Visualization': ['dashboard', 'tableau', 'power bi', 'visualization'],
            'Statistics': ['statistical', 'hypothesis testing', 'regression'],
            'Big Data': ['spark', 'hadoop', 'big data'],
            'API Development': ['api', 'rest', 'microservices'],
            'DevOps/MLOps': ['docker', 'kubernetes', 'ci/cd', 'mlops']
        }

        for skill, indicators in skill_indicators.items():
            for indicator in indicators:
                if indicator in content_lower:
                    if skill not in skills:
                        skills.append(skill)
                    break

        return skills
