"""
Project Categorizer - Hybrid 3-level categorization system
"""
import logging
import json
import re
from typing import Tuple, Dict, List, Optional
from pathlib import Path
from collections import defaultdict

from langchain_anthropic import ChatAnthropic
import numpy as np

from config import (
    ANTHROPIC_API_KEY,
    LLM_MODEL,
    CATEGORIES_CONFIG_FILE,
    CATEGORIZATION_CONFIDENCE_THRESHOLD,
    ENABLE_AUTO_CATEGORIZATION
)
from schemas import ProjectCategory

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ProjectCategorizer:
    """
    Auto-categorize projects using a hybrid 3-level approach:
    1. Keyword-based rules (fast, deterministic)
    2. Embedding similarity (semantic matching) - Optional
    3. Claude API classification (intelligent, context-aware)
    """

    def __init__(self, embeddings=None):
        self.llm = None
        self.embeddings = embeddings
        self.category_keywords = {}
        self.category_descriptions = {}
        self.category_examples = {}
        self.confidence_threshold = CATEGORIZATION_CONFIDENCE_THRESHOLD

        # Initialize LLM if available
        if ANTHROPIC_API_KEY and ENABLE_AUTO_CATEGORIZATION:
            try:
                self.llm = ChatAnthropic(
                    model=LLM_MODEL,
                    temperature=0.2,  # Low temperature for consistent categorization
                    anthropic_api_key=ANTHROPIC_API_KEY
                )
                logger.info("LLM initialized for categorization")
            except Exception as e:
                logger.warning(f"Could not initialize LLM: {e}")

        self._load_category_config()

    def _load_category_config(self):
        """Load category configuration from JSON file"""
        try:
            if CATEGORIES_CONFIG_FILE.exists():
                with open(CATEGORIES_CONFIG_FILE, 'r', encoding='utf-8') as f:
                    config = json.load(f)

                for category, data in config.items():
                    self.category_keywords[category] = data.get('keywords', {})
                    self.category_descriptions[category] = data.get('description', '')
                    self.category_examples[category] = data.get('examples', [])

                logger.info(f"Loaded {len(self.category_keywords)} categories")
            else:
                logger.warning(f"Categories config file not found: {CATEGORIES_CONFIG_FILE}")
                self._load_default_categories()
        except Exception as e:
            logger.error(f"Error loading category config: {e}")
            self._load_default_categories()

    def _load_default_categories(self):
        """Load minimal default categories as fallback"""
        self.category_keywords = {
            'prediction': {'forecast': 1.0, 'predict': 1.0, 'regression': 0.9},
            'classification': {'classification': 1.0, 'classify': 1.0},
            'optimization': {'optimization': 1.0, 'optimize': 1.0},
            'dashboard': {'dashboard': 1.0, 'visualization': 0.8},
            'other': {}
        }

    def categorize(
        self,
        content: str,
        title: str = "",
        use_llm_for_ambiguous: bool = True
    ) -> Tuple[ProjectCategory, float]:
        """
        Categorize a project and return category with confidence score

        Args:
            content: Document content
            title: Project title
            use_llm_for_ambiguous: Use LLM for low-confidence results

        Returns:
            Tuple of (ProjectCategory, confidence_score)
        """
        logger.info(f"Categorizing project: {title[:50]}")

        # Level 1: Keyword-based categorization
        keyword_scores = self._keyword_based_categorization(content, title)

        # Check confidence
        if keyword_scores:
            best_category = max(keyword_scores, key=keyword_scores.get)
            confidence = keyword_scores[best_category]

            # If confidence is high enough, return immediately
            if confidence >= self.confidence_threshold:
                logger.info(f"Keyword categorization: {best_category} (confidence: {confidence:.2f})")
                return ProjectCategory(best_category), confidence

        # Level 2: Embedding-based (if embeddings are available)
        if self.embeddings:
            embedding_scores = self._embedding_based_categorization(content, title)
            # Combine keyword and embedding scores
            combined_scores = self._combine_scores(keyword_scores, embedding_scores)

            if combined_scores:
                best_category = max(combined_scores, key=combined_scores.get)
                confidence = combined_scores[best_category]

                if confidence >= self.confidence_threshold:
                    logger.info(f"Combined categorization: {best_category} (confidence: {confidence:.2f})")
                    return ProjectCategory(best_category), confidence

        # Level 3: LLM categorization for ambiguous cases
        if use_llm_for_ambiguous and self.llm:
            try:
                llm_category, llm_confidence = self._llm_categorization(content, title)
                logger.info(f"LLM categorization: {llm_category} (confidence: {llm_confidence:.2f})")
                return llm_category, llm_confidence
            except Exception as e:
                logger.error(f"LLM categorization failed: {e}")

        # Fallback: Return best from keyword/embedding or 'other'
        if keyword_scores:
            best_category = max(keyword_scores, key=keyword_scores.get)
            confidence = keyword_scores[best_category]
            return ProjectCategory(best_category), confidence
        else:
            return ProjectCategory.OTHER, 0.0

    def _keyword_based_categorization(self, content: str, title: str = "") -> Dict[str, float]:
        """
        Score categories based on keyword presence

        Returns:
            Dict mapping category names to scores (0-1)
        """
        scores = defaultdict(float)
        text = (title + " " + content).lower()

        for category, keywords in self.category_keywords.items():
            for keyword, weight in keywords.items():
                # Count occurrences (with diminishing returns)
                count = len(re.findall(r'\b' + re.escape(keyword) + r'\b', text))
                if count > 0:
                    # Logarithmic scoring to avoid over-weighting repeated keywords
                    score = weight * (1 + np.log(count))
                    scores[category] += score

        # Normalize scores
        if scores:
            total = sum(scores.values())
            if total > 0:
                scores = {k: min(v / total, 1.0) for k, v in scores.items()}

        return dict(scores)

    def _embedding_based_categorization(self, content: str, title: str = "") -> Dict[str, float]:
        """
        Score categories based on embedding similarity
        (Placeholder - requires embeddings to be implemented)

        Returns:
            Dict mapping category names to scores (0-1)
        """
        # This would require computing embeddings for categories and content
        # For now, return empty dict (can be enhanced later)
        return {}

    def _combine_scores(
        self,
        keyword_scores: Dict[str, float],
        embedding_scores: Dict[str, float],
        keyword_weight: float = 0.6
    ) -> Dict[str, float]:
        """
        Combine keyword and embedding scores

        Args:
            keyword_scores: Scores from keyword matching
            embedding_scores: Scores from embedding similarity
            keyword_weight: Weight for keyword scores (embedding gets 1-keyword_weight)

        Returns:
            Combined scores
        """
        combined = defaultdict(float)
        embedding_weight = 1.0 - keyword_weight

        # Add keyword scores
        for category, score in keyword_scores.items():
            combined[category] += score * keyword_weight

        # Add embedding scores
        for category, score in embedding_scores.items():
            combined[category] += score * embedding_weight

        return dict(combined)

    def _llm_categorization(self, content: str, title: str = "") -> Tuple[ProjectCategory, float]:
        """
        Use Claude for intelligent categorization

        Returns:
            Tuple of (ProjectCategory, confidence)
        """
        # Limit content to avoid token limits
        content_preview = content[:3000]

        # Build category descriptions
        category_descriptions = "\n".join([
            f"- {cat.value}: {self.category_descriptions.get(cat.value, '')}"
            for cat in ProjectCategory
        ])

        prompt = f"""Categorize this data analyst project idea into ONE primary category.

Title: {title}

Content preview:
{content_preview}

Available categories:
{category_descriptions}

Analyze the project and return ONLY a valid JSON object:
{{
  "category": "category_name",
  "confidence": 0.95,
  "reasoning": "brief explanation (max 50 words)"
}}

Choose the single best category that matches the primary focus of the project.
Return ONLY the JSON object."""

        try:
            response = self.llm.invoke(prompt)
            content_str = response.content

            # Extract JSON from response
            if '```json' in content_str:
                json_match = re.search(r'```json\s*(\{.*?\})\s*```', content_str, re.DOTALL)
                if json_match:
                    content_str = json_match.group(1)
            elif '```' in content_str:
                json_match = re.search(r'```\s*(\{.*?\})\s*```', content_str, re.DOTALL)
                if json_match:
                    content_str = json_match.group(1)

            result = json.loads(content_str)

            category_name = result.get('category', 'other')
            confidence = float(result.get('confidence', 0.5))

            # Validate category
            try:
                category = ProjectCategory(category_name)
            except ValueError:
                logger.warning(f"Invalid category from LLM: {category_name}, defaulting to OTHER")
                category = ProjectCategory.OTHER
                confidence = 0.5

            return category, confidence

        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing error in LLM categorization: {e}")
            return ProjectCategory.OTHER, 0.0
        except Exception as e:
            logger.error(f"LLM categorization error: {e}")
            raise

    def get_secondary_categories(
        self,
        content: str,
        title: str = "",
        primary_category: Optional[ProjectCategory] = None,
        max_secondary: int = 2
    ) -> List[ProjectCategory]:
        """
        Identify secondary categories for a project

        Args:
            content: Document content
            title: Project title
            primary_category: Already identified primary category (to exclude)
            max_secondary: Maximum number of secondary categories

        Returns:
            List of secondary ProjectCategory objects
        """
        keyword_scores = self._keyword_based_categorization(content, title)

        # Remove primary category if specified
        if primary_category and primary_category.value in keyword_scores:
            del keyword_scores[primary_category.value]

        # Get top N secondary categories with reasonable confidence
        secondary = []
        sorted_categories = sorted(keyword_scores.items(), key=lambda x: x[1], reverse=True)

        for cat_name, score in sorted_categories[:max_secondary]:
            if score >= 0.3:  # Threshold for secondary categories
                try:
                    secondary.append(ProjectCategory(cat_name))
                except ValueError:
                    continue

        return secondary

    def get_category_info(self, category: ProjectCategory) -> Dict:
        """Get information about a category"""
        cat_value = category.value
        return {
            'name': cat_value,
            'description': self.category_descriptions.get(cat_value, ''),
            'examples': self.category_examples.get(cat_value, []),
            'keywords': list(self.category_keywords.get(cat_value, {}).keys())
        }
