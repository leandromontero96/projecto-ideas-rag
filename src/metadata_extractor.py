"""
Metadata Extractor - Intelligent metadata extraction from project documents
"""
import logging
import json
import re
import uuid
from typing import Dict, List, Optional
from pathlib import Path
from datetime import datetime

from langchain_anthropic import ChatAnthropic
from langchain.schema import Document

from config import (
    ANTHROPIC_API_KEY,
    LLM_MODEL,
    TECHNOLOGIES_CONFIG_FILE,
    ENABLE_METADATA_EXTRACTION
)
from schemas import ProjectMetadata, ImpactMetrics

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MetadataExtractor:
    """
    Extract structured metadata from project idea documents using:
    1. Claude API for intelligent extraction
    2. Regex patterns for technology detection
    3. Keyword extraction
    """

    def __init__(self):
        self.llm = None
        self.tech_patterns = {}
        self.technologies_config = {}

        if ANTHROPIC_API_KEY and ENABLE_METADATA_EXTRACTION:
            try:
                self.llm = ChatAnthropic(
                    model=LLM_MODEL,
                    temperature=0.3,  # Lower temperature for more consistent extraction
                    anthropic_api_key=ANTHROPIC_API_KEY
                )
                logger.info("LLM initialized for metadata extraction")
            except Exception as e:
                logger.warning(f"Could not initialize LLM: {e}")

        self._load_technology_patterns()

    def _load_technology_patterns(self):
        """Load technology patterns from config file"""
        try:
            if TECHNOLOGIES_CONFIG_FILE.exists():
                with open(TECHNOLOGIES_CONFIG_FILE, 'r', encoding='utf-8') as f:
                    self.technologies_config = json.load(f)
                    self._build_technology_patterns()
                logger.info("Technology patterns loaded")
            else:
                logger.warning(f"Technologies config file not found: {TECHNOLOGIES_CONFIG_FILE}")
        except Exception as e:
            logger.error(f"Error loading technology patterns: {e}")

    def _build_technology_patterns(self):
        """Build regex patterns for technology detection"""
        self.tech_patterns = {}

        for category, tech_list in self.technologies_config.items():
            for tech in tech_list:
                name = tech['name']
                aliases = tech.get('aliases', [])

                # Build pattern for main name and aliases
                all_names = [name] + aliases
                # Escape special regex characters and create pattern
                escaped_names = [re.escape(n) for n in all_names]
                pattern = r'\b(?:' + '|'.join(escaped_names) + r')\b'

                self.tech_patterns[name] = {
                    'pattern': re.compile(pattern, re.IGNORECASE),
                    'category': category
                }

    def extract_metadata(
        self,
        document: Document,
        file_path: str = "",
        file_type: str = ""
    ) -> ProjectMetadata:
        """
        Extract all metadata from a document

        Args:
            document: LangChain Document object
            file_path: Path to source file
            file_type: File extension/type

        Returns:
            ProjectMetadata object with extracted information
        """
        logger.info(f"Extracting metadata from document: {file_path}")

        content = document.page_content
        source_metadata = document.metadata

        # Generate unique ID
        doc_id = str(uuid.uuid4())[:8]

        # Extract structured data using LLM if available
        llm_data = {}
        if self.llm:
            try:
                llm_data = self._extract_with_llm(content)
            except Exception as e:
                logger.warning(f"LLM extraction failed: {e}")

        # Detect technologies
        tech_data = self._detect_technologies(content)

        # Extract keywords (simple word frequency for now)
        keywords = self._extract_keywords(content)

        # Count words and estimate pages
        word_count = len(content.split())
        total_pages = source_metadata.get('total_pages', 0)

        # Build metadata object
        metadata = ProjectMetadata(
            document_id=doc_id,
            title=llm_data.get('title', source_metadata.get('title', 'Untitled Project')),
            source_file=file_path or source_metadata.get('source', ''),
            file_type=file_type or source_metadata.get('file_type', 'unknown'),
            upload_date=datetime.now(),
            summary=llm_data.get('summary'),
            description=content[:500] if not llm_data.get('summary') else None,
            technologies=tech_data['all_technologies'],
            programming_languages=tech_data.get('programming_languages', []),
            frameworks=tech_data.get('ml_frameworks', []),
            tools=tech_data.get('visualization', []) + tech_data.get('data_tools', []),
            business_domain=llm_data.get('business_domain'),
            industry=llm_data.get('industry'),
            use_cases=llm_data.get('use_cases', []),
            keywords=keywords[:20],  # Limit to top 20
            word_count=word_count,
            total_pages=total_pages,
            custom_fields={
                'llm_extracted': bool(llm_data),
                'extraction_date': datetime.now().isoformat()
            }
        )

        # Extract impact metrics if effort is mentioned
        if 'estimated_effort' in llm_data:
            effort_str = llm_data.get('estimated_effort', '')
            effort_hours = self._parse_effort_to_hours(effort_str)
            metadata.impact_metrics.effort_hours = effort_hours

        logger.info(f"Metadata extraction complete for {doc_id}")
        return metadata

    def _extract_with_llm(self, content: str) -> Dict:
        """Use Claude API to extract structured information"""

        # Limit content to avoid token limits
        content_preview = content[:4000]

        prompt = f"""Analyze this project idea document and extract structured information.

Document:
{content_preview}

Extract and return ONLY a valid JSON object with these fields (use null if information is not available):
{{
  "title": "Project title (string)",
  "summary": "2-3 sentence summary (string)",
  "business_domain": "Business area like finance, healthcare, retail, manufacturing, etc. (string)",
  "industry": "Specific industry sector (string)",
  "use_cases": ["List of specific use cases (array of strings)"],
  "estimated_effort": "Estimated hours/days/weeks for implementation (string)",
  "expected_impact": "Expected business impact description (string)"
}}

Return ONLY the JSON object, no additional text or explanation."""

        try:
            response = self.llm.invoke(prompt)
            content_str = response.content

            # Try to extract JSON from response
            # Sometimes Claude returns markdown code blocks
            if '```json' in content_str:
                json_match = re.search(r'```json\s*(\{.*?\})\s*```', content_str, re.DOTALL)
                if json_match:
                    content_str = json_match.group(1)
            elif '```' in content_str:
                json_match = re.search(r'```\s*(\{.*?\})\s*```', content_str, re.DOTALL)
                if json_match:
                    content_str = json_match.group(1)

            # Parse JSON
            data = json.loads(content_str)
            logger.info("LLM extraction successful")
            return data

        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing error: {e}")
            logger.error(f"Response was: {content_str[:200]}")
            return {}
        except Exception as e:
            logger.error(f"LLM extraction error: {e}")
            return {}

    def _detect_technologies(self, content: str) -> Dict[str, List[str]]:
        """Detect technologies mentioned in content using regex patterns"""

        detected = {
            'all_technologies': [],
            'programming_languages': [],
            'ml_frameworks': [],
            'data_tools': [],
            'visualization': [],
            'databases': [],
            'cloud_platforms': [],
            'etl_orchestration': []
        }

        content_lower = content.lower()

        for tech_name, tech_info in self.tech_patterns.items():
            pattern = tech_info['pattern']
            category = tech_info['category']

            if pattern.search(content):
                detected['all_technologies'].append(tech_name)

                # Categorize
                if category in detected:
                    detected[category].append(tech_name)

        # Remove duplicates
        for key in detected:
            detected[key] = list(set(detected[key]))

        logger.info(f"Detected {len(detected['all_technologies'])} technologies")
        return detected

    def _extract_keywords(self, content: str, top_n: int = 30) -> List[str]:
        """
        Extract keywords from content using simple word frequency
        (Can be enhanced with KeyBERT or YAKE in the future)
        """
        # Simple approach: extract meaningful words
        words = re.findall(r'\b[a-z]{4,}\b', content.lower())

        # Filter stop words (basic list)
        stop_words = {
            'this', 'that', 'with', 'from', 'have', 'will', 'would', 'could',
            'should', 'their', 'there', 'about', 'which', 'these', 'those',
            'when', 'where', 'what', 'been', 'were', 'said', 'each', 'also',
            'into', 'than', 'them', 'some', 'your', 'only', 'such', 'just',
            'like', 'more', 'very', 'even', 'most', 'many', 'much', 'between',
            'through', 'during', 'before', 'after', 'above', 'below'
        }

        # Count word frequency
        word_freq = {}
        for word in words:
            if word not in stop_words:
                word_freq[word] = word_freq.get(word, 0) + 1

        # Sort by frequency and get top N
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        keywords = [word for word, freq in sorted_words[:top_n]]

        return keywords

    def _parse_effort_to_hours(self, effort_str: str) -> Optional[int]:
        """Convert effort string to hours"""
        if not effort_str:
            return None

        effort_str = effort_str.lower()

        # Extract number
        num_match = re.search(r'(\d+(?:\.\d+)?)', effort_str)
        if not num_match:
            return None

        num = float(num_match.group(1))

        # Determine unit
        if 'hour' in effort_str:
            return int(num)
        elif 'day' in effort_str:
            return int(num * 8)  # Assuming 8-hour days
        elif 'week' in effort_str:
            return int(num * 40)  # Assuming 40-hour weeks
        elif 'month' in effort_str:
            return int(num * 160)  # Assuming ~160 hours per month
        else:
            # Default to hours
            return int(num)

    def get_technology_categories(self) -> Dict:
        """Return available technology categories"""
        return {
            cat: [tech['name'] for tech in techs]
            for cat, techs in self.technologies_config.items()
        }
