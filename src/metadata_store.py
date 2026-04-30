"""
Metadata Store - Persistent storage and retrieval for project metadata
"""
import logging
import json
from pathlib import Path
from typing import Dict, List, Optional, Callable
from datetime import datetime

from config import METADATA_CACHE_DIR
from schemas import ProjectMetadata, ProjectCategory, ComplexityLevel

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MetadataStore:
    """
    Persistent storage for project metadata using JSON files
    - Individual JSON file per project
    - Index file for fast lookup
    - Query capabilities
    """

    def __init__(self, cache_dir: Path = None):
        self.cache_dir = Path(cache_dir) if cache_dir else Path(METADATA_CACHE_DIR)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.index_file = self.cache_dir / "index.json"
        self.index = {}
        self._load_index()

    def _load_index(self):
        """Load the metadata index from disk"""
        if self.index_file.exists():
            try:
                with open(self.index_file, 'r', encoding='utf-8') as f:
                    self.index = json.load(f)
                logger.info(f"Loaded metadata index with {len(self.index)} entries")
            except Exception as e:
                logger.error(f"Error loading index: {e}")
                self.index = {}
        else:
            self.index = {}
            self._save_index()

    def _save_index(self):
        """Save the metadata index to disk"""
        try:
            with open(self.index_file, 'w', encoding='utf-8') as f:
                json.dump(self.index, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving index: {e}")

    def save(self, metadata: ProjectMetadata):
        """
        Save metadata to cache

        Args:
            metadata: ProjectMetadata object to save
        """
        doc_id = metadata.document_id
        file_path = self.cache_dir / f"{doc_id}.json"

        try:
            # Convert to dict and handle datetime serialization
            metadata_dict = metadata.model_dump()

            # Save to file
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(metadata_dict, f, indent=2, default=str)

            # Update index
            self.index[doc_id] = {
                'title': metadata.title,
                'category': metadata.primary_category.value if metadata.primary_category else None,
                'complexity': metadata.complexity_level.value if metadata.complexity_level else None,
                'file': str(file_path),
                'upload_date': metadata.upload_date.isoformat() if metadata.upload_date else None
            }
            self._save_index()

            logger.info(f"Metadata saved: {doc_id}")

        except Exception as e:
            logger.error(f"Error saving metadata {doc_id}: {e}")
            raise

    def get_by_id(self, document_id: str) -> Optional[ProjectMetadata]:
        """
        Retrieve metadata by document ID

        Args:
            document_id: Document ID

        Returns:
            ProjectMetadata object or None if not found
        """
        if document_id not in self.index:
            logger.warning(f"Document not found in index: {document_id}")
            return None

        file_path = Path(self.index[document_id]['file'])

        if not file_path.exists():
            logger.error(f"Metadata file not found: {file_path}")
            return None

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Convert back to ProjectMetadata
            metadata = ProjectMetadata(**data)
            return metadata

        except Exception as e:
            logger.error(f"Error loading metadata {document_id}: {e}")
            return None

    def get_all(self) -> List[ProjectMetadata]:
        """
        Get all metadata entries

        Returns:
            List of ProjectMetadata objects
        """
        all_metadata = []
        for doc_id in self.index.keys():
            metadata = self.get_by_id(doc_id)
            if metadata:
                all_metadata.append(metadata)

        return all_metadata

    def query(self, filter_func: Callable[[ProjectMetadata], bool]) -> List[ProjectMetadata]:
        """
        Query metadata with custom filter function

        Args:
            filter_func: Function that takes ProjectMetadata and returns bool

        Returns:
            List of matching ProjectMetadata objects

        Example:
            # Get all prediction projects
            results = store.query(lambda m: m.primary_category == ProjectCategory.PREDICTION)
        """
        all_metadata = self.get_all()
        return [m for m in all_metadata if filter_func(m)]

    def delete(self, document_id: str) -> bool:
        """
        Delete metadata by document ID

        Args:
            document_id: Document ID to delete

        Returns:
            True if successful, False otherwise
        """
        if document_id not in self.index:
            logger.warning(f"Document not found: {document_id}")
            return False

        try:
            file_path = Path(self.index[document_id]['file'])

            # Delete file
            if file_path.exists():
                file_path.unlink()

            # Remove from index
            del self.index[document_id]
            self._save_index()

            logger.info(f"Metadata deleted: {document_id}")
            return True

        except Exception as e:
            logger.error(f"Error deleting metadata {document_id}: {e}")
            return False

    def update(self, metadata: ProjectMetadata):
        """
        Update existing metadata

        Args:
            metadata: Updated ProjectMetadata object
        """
        # Same as save - will overwrite existing file
        self.save(metadata)

    def clear_all(self) -> bool:
        """
        Clear all metadata from the store

        Returns:
            True if successful
        """
        try:
            # Delete all metadata files
            for doc_id in list(self.index.keys()):
                self.delete(doc_id)

            # Clear index
            self.index = {}
            self._save_index()

            logger.info("All metadata cleared")
            return True

        except Exception as e:
            logger.error(f"Error clearing metadata: {e}")
            return False

    def get_statistics(self) -> Dict:
        """
        Get statistics about stored metadata

        Returns:
            Dictionary with statistics
        """
        all_metadata = self.get_all()

        if not all_metadata:
            return {
                'total_projects': 0,
                'categories': {},
                'complexity_levels': {},
                'technologies': {},
                'avg_word_count': 0
            }

        # Count categories
        category_counts = {}
        for metadata in all_metadata:
            if metadata.primary_category:
                cat = metadata.primary_category.value
                category_counts[cat] = category_counts.get(cat, 0) + 1

        # Count complexity levels
        complexity_counts = {}
        for metadata in all_metadata:
            if metadata.complexity_level:
                level = metadata.complexity_level.value
                complexity_counts[level] = complexity_counts.get(level, 0) + 1

        # Count technologies
        tech_counts = {}
        for metadata in all_metadata:
            for tech in metadata.technologies:
                tech_counts[tech] = tech_counts.get(tech, 0) + 1

        # Get top 10 technologies
        top_technologies = dict(
            sorted(tech_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        )

        # Average word count
        word_counts = [m.word_count for m in all_metadata if m.word_count > 0]
        avg_word_count = sum(word_counts) / len(word_counts) if word_counts else 0

        return {
            'total_projects': len(all_metadata),
            'categories': category_counts,
            'complexity_levels': complexity_counts,
            'top_technologies': top_technologies,
            'avg_word_count': int(avg_word_count)
        }

    def search_by_title(self, query: str) -> List[ProjectMetadata]:
        """
        Search metadata by title (case-insensitive substring match)

        Args:
            query: Search query

        Returns:
            List of matching ProjectMetadata objects
        """
        query_lower = query.lower()
        return self.query(lambda m: query_lower in m.title.lower())

    def filter_by_category(
        self,
        categories: List[ProjectCategory]
    ) -> List[ProjectMetadata]:
        """
        Filter metadata by categories

        Args:
            categories: List of ProjectCategory enums

        Returns:
            List of matching ProjectMetadata objects
        """
        return self.query(
            lambda m: m.primary_category in categories or
            any(cat in m.secondary_categories for cat in categories)
        )

    def filter_by_complexity(
        self,
        complexity_levels: List[ComplexityLevel]
    ) -> List[ProjectMetadata]:
        """
        Filter metadata by complexity levels

        Args:
            complexity_levels: List of ComplexityLevel enums

        Returns:
            List of matching ProjectMetadata objects
        """
        return self.query(lambda m: m.complexity_level in complexity_levels)

    def filter_by_technology(
        self,
        technologies: List[str],
        match_all: bool = False
    ) -> List[ProjectMetadata]:
        """
        Filter metadata by technologies

        Args:
            technologies: List of technology names
            match_all: If True, project must have ALL technologies.
                      If False, project must have ANY technology (default)

        Returns:
            List of matching ProjectMetadata objects
        """
        tech_set = set(t.lower() for t in technologies)

        if match_all:
            # Must have all technologies
            return self.query(
                lambda m: tech_set.issubset(set(t.lower() for t in m.technologies))
            )
        else:
            # Must have at least one technology
            return self.query(
                lambda m: bool(tech_set & set(t.lower() for t in m.technologies))
            )

    def get_by_source_file(self, source_file: str) -> Optional[ProjectMetadata]:
        """
        Get metadata by source file path

        Args:
            source_file: Source file path

        Returns:
            ProjectMetadata or None
        """
        results = self.query(lambda m: m.source_file == source_file)
        return results[0] if results else None
