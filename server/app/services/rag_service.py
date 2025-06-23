"""
RAG (Retrieval-Augmented Generation) service for content-aware course generation.
Implements vector storage and retrieval for SOP documents.
"""

import os
import json
import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import hashlib

try:
    import numpy as np
    import faiss
    from sentence_transformers import SentenceTransformer
    from langchain.schema import Document
except ImportError as e:
    logging.warning(f"RAG dependencies not installed: {e}")
    np = None
    faiss = None
    SentenceTransformer = None
    Document = None

from app.services.document_service import document_processor

logger = logging.getLogger(__name__)

class VectorStore:
    """Vector storage and retrieval system using FAISS."""
    
    def __init__(self, embedding_model: str = "all-MiniLM-L6-v2"):
        self.embedding_model_name = embedding_model
        self.embedding_model = None
        self.index = None
        self.documents = []  # Store document chunks with metadata
        self.dimension = 384  # Default for all-MiniLM-L6-v2
        
        if SentenceTransformer:
            try:
                self.embedding_model = SentenceTransformer(embedding_model)
                # Get actual dimension from the model
                test_embedding = self.embedding_model.encode("test")
                self.dimension = len(test_embedding)
                logger.info(f"Initialized embedding model {embedding_model} with dimension {self.dimension}")
            except Exception as e:
                logger.error(f"Failed to load embedding model: {e}")
                self.embedding_model = None
        
        if faiss and self.embedding_model:
            self.index = faiss.IndexFlatIP(self.dimension)  # Inner product (cosine similarity)
            logger.info(f"Initialized FAISS index with dimension {self.dimension}")
    
    def is_available(self) -> bool:
        """Check if vector store is available."""
        return self.embedding_model is not None and self.index is not None
    
    def encode_text(self, text: str) -> np.ndarray:
        """Generate embeddings for text."""
        if not self.embedding_model:
            raise ValueError("Embedding model not available")
        
        embedding = self.embedding_model.encode(text, convert_to_tensor=False)
        # Normalize for cosine similarity
        embedding = embedding / np.linalg.norm(embedding)
        return embedding.astype('float32')
    
    def add_documents(self, documents: List[Dict[str, Any]], source_id: str = None) -> int:
        """Add documents to vector store."""
        if not self.is_available():
            raise ValueError("Vector store not available")
        
        embeddings = []
        
        for doc in documents:
            try:
                # Generate embedding
                embedding = self.encode_text(doc['text'])
                embeddings.append(embedding)
                
                # Store document with metadata
                doc_entry = {
                    'text': doc['text'],
                    'embedding_id': len(self.documents),
                    'source_id': source_id,
                    'chunk_index': doc.get('chunk_index', 0),
                    'word_count': doc.get('word_count', len(doc['text'].split())),
                    'added_at': datetime.utcnow().isoformat(),
                    'metadata': doc.get('metadata', {})
                }
                
                self.documents.append(doc_entry)
                
            except Exception as e:
                logger.error(f"Error processing document chunk: {e}")
                continue
        
        if embeddings:
            # Add to FAISS index
            embeddings_array = np.array(embeddings)
            self.index.add(embeddings_array)
            logger.info(f"Added {len(embeddings)} document chunks to vector store")
        
        return len(embeddings)
    
    def search(self, query: str, k: int = 5, score_threshold: float = 0.3) -> List[Dict[str, Any]]:
        """Search for relevant documents."""
        if not self.is_available():
            raise ValueError("Vector store not available")
        
        if self.index.ntotal == 0:
            return []
        
        try:
            # Generate query embedding
            query_embedding = self.encode_text(query)
            query_embedding = np.array([query_embedding])
            
            # Search
            scores, indices = self.index.search(query_embedding, min(k, self.index.ntotal))
            
            results = []
            for score, idx in zip(scores[0], indices[0]):
                if score >= score_threshold and idx < len(self.documents):
                    doc = self.documents[idx].copy()
                    doc['similarity_score'] = float(score)
                    results.append(doc)
            
            return results
            
        except Exception as e:
            logger.error(f"Error during vector search: {e}")
            return []
    
    def get_stats(self) -> Dict[str, Any]:
        """Get vector store statistics."""
        return {
            "total_documents": len(self.documents),
            "index_size": self.index.ntotal if self.index else 0,
            "dimension": self.dimension,
            "model": self.embedding_model_name,
            "is_available": self.is_available()
        }
    
    def clear(self):
        """Clear all documents and reset index."""
        if self.index:
            self.index.reset()
        self.documents = []
        logger.info("Vector store cleared")

class RAGService:
    """RAG service for content-aware generation."""
    
    def __init__(self):
        self.vector_store = VectorStore()
        self.document_sources = {}  # Track document sources
    
    def is_available(self) -> bool:
        """Check if RAG service is available."""
        return self.vector_store.is_available()
    
    async def index_document(
        self,
        file_path: str,
        file_content: bytes = None,
        source_metadata: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Process and index a document for RAG."""
        
        if not self.is_available():
            raise ValueError("RAG service not available. Install required dependencies.")
        
        try:
            # Process document
            doc_result = await document_processor.process_file(file_path, file_content)
            
            # Generate source ID
            source_id = hashlib.md5(f"{file_path}_{doc_result['content_hash']}".encode()).hexdigest()
            
            # Chunk document
            chunks = document_processor.chunk_text(
                doc_result['text'],
                chunk_size=800,  # Smaller chunks for better retrieval
                overlap=100
            )
            
            # Add to vector store
            added_count = self.vector_store.add_documents(chunks, source_id)
            
            # Store source metadata
            self.document_sources[source_id] = {
                'file_name': doc_result['file_name'],
                'file_size': doc_result['file_size'],
                'word_count': doc_result['word_count'],
                'chunk_count': len(chunks),
                'indexed_chunks': added_count,
                'content_hash': doc_result['content_hash'],
                'indexed_at': datetime.utcnow().isoformat(),
                'metadata': source_metadata or {}
            }
            
            # Extract key terms for metadata
            key_terms = await document_processor.extract_key_terms(doc_result['text'], max_terms=20)
            self.document_sources[source_id]['key_terms'] = key_terms
            
            logger.info(f"Indexed document {file_path}: {added_count} chunks")
            
            return {
                'source_id': source_id,
                'chunks_indexed': added_count,
                'total_chunks': len(chunks),
                'key_terms': key_terms[:10],  # Return top 10 terms
                'document_info': {
                    'file_name': doc_result['file_name'],
                    'word_count': doc_result['word_count'],
                    'char_count': doc_result['char_count']
                }
            }
            
        except Exception as e:
            logger.error(f"Error indexing document {file_path}: {e}")
            raise
    
    async def search_relevant_content(
        self,
        query: str,
        source_ids: List[str] = None,
        max_results: int = 5,
        min_score: float = 0.3
    ) -> List[Dict[str, Any]]:
        """Search for relevant content in indexed documents."""
        
        if not self.is_available():
            return []
        
        try:
            # Search vector store
            results = self.vector_store.search(query, k=max_results, score_threshold=min_score)
            
            # Filter by source IDs if specified
            if source_ids:
                results = [r for r in results if r.get('source_id') in source_ids]
            
            # Enhance results with source metadata
            enhanced_results = []
            for result in results:
                source_id = result.get('source_id')
                if source_id in self.document_sources:
                    result['source_info'] = self.document_sources[source_id]
                enhanced_results.append(result)
            
            return enhanced_results
            
        except Exception as e:
            logger.error(f"Error searching content: {e}")
            return []
    
    async def get_contextual_content(
        self,
        topic: str,
        content_type: str = "general",
        source_ids: List[str] = None,
        max_chunks: int = 3
    ) -> str:
        """Get relevant content chunks for a specific topic."""
        
        # Enhance query based on content type
        enhanced_queries = {
            "vocabulary": f"vocabulary words terms definitions related to {topic}",
            "procedures": f"procedures steps process workflow for {topic}",
            "guidelines": f"guidelines rules requirements standards for {topic}",
            "examples": f"examples cases scenarios instances of {topic}",
            "general": topic
        }
        
        query = enhanced_queries.get(content_type, topic)
        
        # Search for relevant content
        results = await self.search_relevant_content(
            query=query,
            source_ids=source_ids,
            max_results=max_chunks,
            min_score=0.2
        )
        
        if not results:
            return ""
        
        # Combine relevant chunks
        content_pieces = []
        for i, result in enumerate(results[:max_chunks]):
            content_pieces.append(f"--- Context {i+1} (Score: {result['similarity_score']:.2f}) ---")
            content_pieces.append(result['text'])
            content_pieces.append("")
        
        return "\n".join(content_pieces)
    
    async def analyze_document_coverage(self, topics: List[str], source_ids: List[str] = None) -> Dict[str, Any]:
        """Analyze how well indexed documents cover specific topics."""
        
        if not self.is_available():
            return {"coverage": {}, "overall_score": 0.0}
        
        coverage = {}
        total_score = 0.0
        
        for topic in topics:
            results = await self.search_relevant_content(
                query=topic,
                source_ids=source_ids,
                max_results=3,
                min_score=0.2
            )
            
            if results:
                best_score = max(r['similarity_score'] for r in results)
                chunk_count = len(results)
            else:
                best_score = 0.0
                chunk_count = 0
            
            coverage[topic] = {
                "best_score": best_score,
                "relevant_chunks": chunk_count,
                "coverage_level": self._get_coverage_level(best_score, chunk_count)
            }
            
            total_score += best_score
        
        overall_score = total_score / len(topics) if topics else 0.0
        
        return {
            "coverage": coverage,
            "overall_score": overall_score,
            "coverage_summary": self._get_coverage_summary(overall_score)
        }
    
    def _get_coverage_level(self, score: float, chunk_count: int) -> str:
        """Determine coverage level based on score and chunk count."""
        if score >= 0.7 and chunk_count >= 2:
            return "excellent"
        elif score >= 0.5 and chunk_count >= 1:
            return "good"
        elif score >= 0.3:
            return "fair"
        else:
            return "poor"
    
    def _get_coverage_summary(self, overall_score: float) -> str:
        """Get overall coverage summary."""
        if overall_score >= 0.7:
            return "Documents provide excellent coverage of the topics"
        elif overall_score >= 0.5:
            return "Documents provide good coverage with some gaps"
        elif overall_score >= 0.3:
            return "Documents provide partial coverage, additional content may be needed"
        else:
            return "Documents provide limited coverage, significant additional content needed"
    
    def get_indexed_sources(self) -> Dict[str, Any]:
        """Get information about indexed document sources."""
        return {
            "sources": self.document_sources,
            "total_sources": len(self.document_sources),
            "vector_store_stats": self.vector_store.get_stats()
        }
    
    def remove_source(self, source_id: str) -> bool:
        """Remove a document source from the index."""
        if source_id in self.document_sources:
            # Note: FAISS doesn't support efficient deletion, so we mark as removed
            # In production, you might want to rebuild the index periodically
            self.document_sources[source_id]['removed'] = True
            self.document_sources[source_id]['removed_at'] = datetime.utcnow().isoformat()
            logger.info(f"Marked source {source_id} as removed")
            return True
        return False
    
    def clear_all(self):
        """Clear all indexed content."""
        self.vector_store.clear()
        self.document_sources = {}
        logger.info("Cleared all RAG content")

# Global instance
rag_service = RAGService()