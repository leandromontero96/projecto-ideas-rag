"""
Configuration settings for Project Ideas RAG System
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base paths
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
DOCUMENTS_DIR = DATA_DIR / "documents"
VECTORSTORE_DIR = DATA_DIR / "vectorstore"
METADATA_DIR = DATA_DIR / "metadata"
CONFIG_DIR = BASE_DIR / "config"

# Ensure directories exist
DOCUMENTS_DIR.mkdir(parents=True, exist_ok=True)
VECTORSTORE_DIR.mkdir(parents=True, exist_ok=True)
METADATA_DIR.mkdir(parents=True, exist_ok=True)
CONFIG_DIR.mkdir(parents=True, exist_ok=True)

# API Configuration
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# Vector Store Configuration
CHROMA_PERSIST_DIRECTORY = os.getenv("CHROMA_PERSIST_DIRECTORY", str(VECTORSTORE_DIR))
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "project_ideas_collection")

# Model Configuration
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
LLM_MODEL = os.getenv("LLM_MODEL", "claude-3-5-sonnet-20241022")
LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.3"))
MAX_TOKENS = int(os.getenv("MAX_TOKENS", "2048"))

# Retrieval Configuration
TOP_K_RESULTS = int(os.getenv("TOP_K_RESULTS", "5"))
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "1000"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "200"))

# Metadata Extraction Configuration
ENABLE_METADATA_EXTRACTION = os.getenv("ENABLE_METADATA_EXTRACTION", "true").lower() == "true"
METADATA_CACHE_DIR = os.getenv("METADATA_CACHE_DIR", str(METADATA_DIR))

# Categorization Configuration
ENABLE_AUTO_CATEGORIZATION = os.getenv("ENABLE_AUTO_CATEGORIZATION", "true").lower() == "true"
CATEGORIZATION_CONFIDENCE_THRESHOLD = float(os.getenv("CATEGORIZATION_CONFIDENCE_THRESHOLD", "0.6"))
CATEGORIES_CONFIG_FILE = CONFIG_DIR / "categories.json"
TECHNOLOGIES_CONFIG_FILE = CONFIG_DIR / "technologies.json"

# Complexity Analysis Configuration
ENABLE_COMPLEXITY_ANALYSIS = os.getenv("ENABLE_COMPLEXITY_ANALYSIS", "true").lower() == "true"
COMPLEXITY_RULES_FILE = CONFIG_DIR / "complexity_rules.json"

# Impact Analysis Configuration
ENABLE_IMPACT_ANALYSIS = os.getenv("ENABLE_IMPACT_ANALYSIS", "true").lower() == "true"
IMPACT_METRICS_FILE = CONFIG_DIR / "impact_metrics.json"

# Filtering Configuration
DEFAULT_FILTER_LIMIT = int(os.getenv("DEFAULT_FILTER_LIMIT", "20"))
MAX_FILTER_RESULTS = int(os.getenv("MAX_FILTER_RESULTS", "100"))

# Template Configuration
PROJECT_TEMPLATE_FILE = BASE_DIR / "project_template.md"

# UI Configuration
PROJECTS_PER_PAGE = int(os.getenv("PROJECTS_PER_PAGE", "12"))
CARDS_PER_ROW = int(os.getenv("CARDS_PER_ROW", "3"))

# Supported file types
SUPPORTED_EXTENSIONS = {
    '.pdf', '.txt', '.md', '.docx', '.xlsx', '.csv'
}
