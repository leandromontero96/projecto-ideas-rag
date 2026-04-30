"""
Impact Analyzer - Extract ROI and business impact metrics from project documents
"""
import logging
import json
import re
from typing import Dict, Optional

from langchain_anthropic import ChatAnthropic

from config import (
    ANTHROPIC_API_KEY,
    LLM_MODEL,
    IMPACT_METRICS_FILE,
    ENABLE_IMPACT_ANALYSIS
)
from schemas import ImpactMetrics

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ImpactAnalyzer:
    """
    Extract and estimate impact metrics:
    - ROI (Return on Investment)
    - Cost savings
    - Time savings
    - Efficiency gains
    - Revenue impact
    - Implementation effort
    """

    def __init__(self):
        self.llm = None
        self.impact_patterns = {}
        self.enabled = ENABLE_IMPACT_ANALYSIS

        # Initialize LLM if available
        if ANTHROPIC_API_KEY and ENABLE_IMPACT_ANALYSIS:
            try:
                self.llm = ChatAnthropic(
                    model=LLM_MODEL,
                    temperature=0.2,
                    anthropic_api_key=ANTHROPIC_API_KEY
                )
                logger.info("LLM initialized for impact analysis")
            except Exception as e:
                logger.warning(f"Could not initialize LLM: {e}")

        self._load_impact_patterns()

    def _load_impact_patterns(self):
        """Load regex patterns for impact metrics from config file"""
        try:
            if IMPACT_METRICS_FILE.exists():
                with open(IMPACT_METRICS_FILE, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    self.impact_patterns = config
                logger.info("Impact metric patterns loaded")
            else:
                logger.warning(f"Impact metrics file not found: {IMPACT_METRICS_FILE}")
                self._load_default_patterns()
        except Exception as e:
            logger.error(f"Error loading impact patterns: {e}")
            self._load_default_patterns()

    def _load_default_patterns(self):
        """Load default patterns as fallback"""
        self.impact_patterns = {
            'roi_patterns': [
                {'pattern': r'(?:roi|return on investment)[:\s]+(\d+(?:\.\d+)?)\s*%', 'unit': 'percentage'}
            ],
            'cost_savings_patterns': [
                {'pattern': r'(?:save|savings?)[:\s]+\$?([\d,]+)', 'unit': 'USD'}
            ],
            'time_savings_patterns': [
                {'pattern': r'(?:save|reduce time)[:\s]+([\d.]+)\s*(?:hours?|hrs?)', 'unit': 'hours'}
            ]
        }

    def extract_impact_metrics(self, content: str) -> ImpactMetrics:
        """
        Extract impact metrics from document content

        Args:
            content: Document text

        Returns:
            ImpactMetrics object with extracted data
        """
        if not self.enabled:
            return ImpactMetrics()

        logger.info("Extracting impact metrics")

        metrics = ImpactMetrics()

        # Extract using regex patterns
        metrics = self._extract_with_regex(content, metrics)

        # Use LLM for additional extraction if regex didn't find much
        if self.llm and not self._has_sufficient_metrics(metrics):
            try:
                llm_metrics = self._extract_with_llm(content)
                metrics = self._merge_metrics(metrics, llm_metrics)
            except Exception as e:
                logger.warning(f"LLM impact extraction failed: {e}")

        logger.info(f"Impact metrics extracted: ROI={metrics.estimated_roi}, Effort={metrics.effort_hours}h")
        return metrics

    def _extract_with_regex(self, content: str, metrics: ImpactMetrics) -> ImpactMetrics:
        """Extract metrics using regex patterns"""

        # ROI patterns
        roi_patterns = self.impact_patterns.get('roi_patterns', [])
        for pattern_config in roi_patterns:
            pattern = pattern_config['pattern']
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                try:
                    roi_value = float(match.group(1))
                    metrics.estimated_roi = roi_value
                    break
                except (ValueError, IndexError):
                    continue
            if metrics.estimated_roi:
                break

        # Cost savings patterns
        cost_patterns = self.impact_patterns.get('cost_savings_patterns', [])
        for pattern_config in cost_patterns:
            pattern = pattern_config['pattern']
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                try:
                    cost_value = match.group(1)
                    metrics.cost_savings = f"${cost_value}"
                    break
                except IndexError:
                    continue
            if metrics.cost_savings:
                break

        # Time savings patterns
        time_patterns = self.impact_patterns.get('time_savings_patterns', [])
        for pattern_config in time_patterns:
            pattern = pattern_config['pattern']
            unit = pattern_config.get('unit', 'hours')
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                try:
                    time_value = match.group(1)
                    metrics.time_savings = f"{time_value} {unit}"
                    break
                except IndexError:
                    continue
            if metrics.time_savings:
                break

        # Effort patterns
        effort_patterns = self.impact_patterns.get('effort_patterns', [])
        for pattern_config in effort_patterns:
            pattern = pattern_config['pattern']
            unit = pattern_config.get('unit', 'hours')
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                try:
                    effort_value = float(match.group(1).replace(',', ''))
                    # Convert to hours
                    if unit == 'days':
                        effort_value *= 8
                    elif unit == 'weeks':
                        effort_value *= 40
                    elif unit == 'months':
                        effort_value *= 160
                    metrics.effort_hours = int(effort_value)
                    break
                except (ValueError, IndexError):
                    continue
            if metrics.effort_hours:
                break

        return metrics

    def _extract_with_llm(self, content: str) -> Dict:
        """Use Claude to extract impact metrics"""

        content_preview = content[:3000]

        prompt = f"""Extract business impact and ROI information from this project description.

Content:
{content_preview}

Extract any available metrics and return ONLY a valid JSON object:
{{
  "estimated_roi": "ROI percentage as number (e.g., 25.5) or null",
  "cost_savings": "Expected cost savings as string (e.g., '$100,000/year') or null",
  "time_savings": "Time savings expected as string (e.g., '50 hours/month') or null",
  "business_value": "Qualitative business value description or null",
  "effort_hours": "Estimated implementation effort in hours as number or null"
}}

Only include fields where you find explicit information. Use null for missing data.
Return ONLY the JSON object."""

        try:
            response = self.llm.invoke(prompt)
            content_str = response.content

            # Extract JSON
            if '```json' in content_str:
                json_match = re.search(r'```json\s*(\{.*?\})\s*```', content_str, re.DOTALL)
                if json_match:
                    content_str = json_match.group(1)
            elif '```' in content_str:
                json_match = re.search(r'```\s*(\{.*?\})\s*```', content_str, re.DOTALL)
                if json_match:
                    content_str = json_match.group(1)

            data = json.loads(content_str)
            logger.info("LLM impact extraction successful")
            return data

        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing error in impact extraction: {e}")
            return {}
        except Exception as e:
            logger.error(f"LLM impact extraction error: {e}")
            raise

    def _has_sufficient_metrics(self, metrics: ImpactMetrics) -> bool:
        """Check if we have enough metrics from regex extraction"""
        count = sum([
            metrics.estimated_roi is not None,
            metrics.cost_savings is not None,
            metrics.time_savings is not None,
            metrics.effort_hours is not None
        ])
        return count >= 2  # At least 2 metrics found

    def _merge_metrics(self, regex_metrics: ImpactMetrics, llm_data: Dict) -> ImpactMetrics:
        """Merge metrics from regex and LLM, preferring regex when available"""

        # ROI
        if regex_metrics.estimated_roi is None and llm_data.get('estimated_roi'):
            try:
                regex_metrics.estimated_roi = float(llm_data['estimated_roi'])
            except (ValueError, TypeError):
                pass

        # Cost savings
        if regex_metrics.cost_savings is None and llm_data.get('cost_savings'):
            regex_metrics.cost_savings = str(llm_data['cost_savings'])

        # Time savings
        if regex_metrics.time_savings is None and llm_data.get('time_savings'):
            regex_metrics.time_savings = str(llm_data['time_savings'])

        # Business value
        if llm_data.get('business_value'):
            regex_metrics.business_value = str(llm_data['business_value'])

        # Effort hours
        if regex_metrics.effort_hours is None and llm_data.get('effort_hours'):
            try:
                regex_metrics.effort_hours = int(llm_data['effort_hours'])
            except (ValueError, TypeError):
                pass

        return regex_metrics

    def calculate_impact_score(self, metrics: ImpactMetrics) -> float:
        """
        Calculate an overall impact score (0-1) based on available metrics

        Args:
            metrics: ImpactMetrics object

        Returns:
            Impact score between 0 and 1
        """
        score = 0.0
        max_score = 0.0

        # ROI contribution (0-0.4)
        if metrics.estimated_roi is not None:
            roi_score = min(metrics.estimated_roi / 100, 0.4)
            score += roi_score
        max_score += 0.4

        # Cost savings contribution (0-0.3)
        if metrics.cost_savings:
            # Simple heuristic: presence of cost savings adds score
            score += 0.3
        max_score += 0.3

        # Time savings contribution (0-0.2)
        if metrics.time_savings:
            score += 0.2
        max_score += 0.2

        # Business value contribution (0-0.1)
        if metrics.business_value:
            score += 0.1
        max_score += 0.1

        # Normalize
        if max_score > 0:
            return score / max_score
        else:
            return 0.0
