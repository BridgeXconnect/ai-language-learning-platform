"""
RAG (Retrieval-Augmented Generation) service for content-aware course generation.
Uses OpenAI embeddings with FAISS for efficient vector search.
"""

import logging
import numpy as np
import faiss
import asyncio
from typing import List, Dict, Any, Optional
from openai import OpenAI
import os
from pathlib import Path

logger = logging.getLogger(__name__)

# RAG service is now available
RAG_AVAILABLE = True

class VectorStore:
    """Vector storage for document embeddings using FAISS."""
    
    def __init__(self, dimension: int = 1536):  # OpenAI embedding dimension
        self.dimension = dimension
        self.index = None
        self.documents = []
        self.embeddings = []
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self._initialize_index()
        logger.info(f"VectorStore initialized with dimension {dimension}")
    
    def _initialize_index(self):
        """Initialize FAISS index for vector similarity search."""
        try:
            self.index = faiss.IndexFlatL2(self.dimension)
            logger.info("FAISS index initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize FAISS index: {e}")
            raise
    
    async def encode_text(self, text: str) -> Optional[List[float]]:
        """Encode text to vector embedding using OpenAI."""
        try:
            response = self.client.embeddings.create(
                model="text-embedding-3-small",
                input=text
            )
            embedding = response.data[0].embedding
            logger.debug(f"Successfully encoded text of length {len(text)}")
            return embedding
        except Exception as e:
            logger.error(f"Failed to encode text: {e}")
            return None
    
    async def add_document(self, doc_id: str, content: str, metadata: Dict[str, Any] = None):
        """Add a document to the vector store."""
        try:
            # Get embedding for the document
            embedding = await self.encode_text(content)
            if embedding is None:
                return False
            
            # Store document and metadata
            doc_data = {
                'id': doc_id,
                'content': content,
                'metadata': metadata or {}
            }
            
            # Add to FAISS index
            embedding_array = np.array([embedding], dtype=np.float32)
            self.index.add(embedding_array)
            
            # Store document data
            self.documents.append(doc_data)
            self.embeddings.append(embedding)
            
            logger.info(f"Added document {doc_id} to vector store")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add document {doc_id}: {e}")
            return False
    
    async def search(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """Search for similar documents."""
        try:
            if self.index.ntotal == 0:
                logger.warning("No documents in vector store")
                return []
            
            # Get query embedding
            query_embedding = await self.encode_text(query)
            if query_embedding is None:
                return []
            
            # Search for similar documents
            query_array = np.array([query_embedding], dtype=np.float32)
            distances, indices = self.index.search(query_array, min(k, self.index.ntotal))
            
            # Prepare results
            results = []
            for i, (distance, idx) in enumerate(zip(distances[0], indices[0])):
                if idx < len(self.documents):
                    doc = self.documents[idx]
                    results.append({
                        'document': doc,
                        'score': float(distance),
                        'rank': i + 1
                    })
            
            logger.info(f"Found {len(results)} similar documents for query")
            return results
            
        except Exception as e:
            logger.error(f"Failed to search documents: {e}")
            return []
    
    def get_stats(self) -> Dict[str, Any]:
        """Get vector store statistics."""
        return {
            'total_documents': len(self.documents),
            'index_size': self.index.ntotal if self.index else 0,
            'dimension': self.dimension,
            'initialized': self.index is not None
        }

class RAGService:
    """RAG service for document retrieval and generation."""
    
    def __init__(self):
        self.vector_store = VectorStore()
        self.documents_loaded = False
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        logger.info("RAG service initialized successfully")
    
    async def load_documents(self):
        """Load documents into the vector store."""
        try:
            # Load sample educational content
            sample_documents = [
                {
                    'id': 'intro_programming',
                    'content': 'Programming fundamentals include variables, data types, control structures, and functions. Understanding these concepts is essential for any programming language.',
                    'metadata': {'category': 'programming', 'level': 'beginner'}
                },
                {
                    'id': 'python_basics',
                    'content': 'Python is a high-level programming language known for its simplicity and readability. It uses indentation to define code blocks and has a rich ecosystem of libraries.',
                    'metadata': {'category': 'python', 'level': 'beginner'}
                },
                {
                    'id': 'web_development',
                    'content': 'Web development involves creating websites and web applications using HTML, CSS, and JavaScript. Modern frameworks like React, Vue, and Angular make development more efficient.',
                    'metadata': {'category': 'web', 'level': 'intermediate'}
                },
                {
                    'id': 'data_structures',
                    'content': 'Data structures are ways of organizing and storing data efficiently. Common structures include arrays, lists, stacks, queues, trees, and graphs.',
                    'metadata': {'category': 'computer_science', 'level': 'intermediate'}
                },
                {
                    'id': 'algorithms',
                    'content': 'Algorithms are step-by-step procedures for solving problems. Important algorithm categories include sorting, searching, graph algorithms, and dynamic programming.',
                    'metadata': {'category': 'computer_science', 'level': 'advanced'}
                }
            ]
            
            # Add documents to vector store
            for doc in sample_documents:
                await self.vector_store.add_document(
                    doc['id'], 
                    doc['content'], 
                    doc['metadata']
                )
            
            self.documents_loaded = True
            logger.info(f"Successfully loaded {len(sample_documents)} documents")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load documents: {e}")
            return False
    
    async def generate_contextual_response(self, query: str, context_limit: int = 3) -> str:
        """Generate a response using RAG."""
        try:
            # Ensure documents are loaded
            if not self.documents_loaded:
                await self.load_documents()
            
            # Retrieve relevant documents
            relevant_docs = await self.vector_store.search(query, k=context_limit)
            
            # Build context from retrieved documents
            context = ""
            if relevant_docs:
                context_parts = []
                for doc_result in relevant_docs:
                    doc = doc_result['document']
                    context_parts.append(f"[{doc['metadata'].get('category', 'unknown')}] {doc['content']}")
                context = "\n\n".join(context_parts)
            
            # Generate response with context
            system_prompt = """You are an AI language learning assistant. Use the provided context to give accurate, helpful responses about programming and computer science topics. If the context doesn't contain relevant information, provide a general helpful response."""
            
            user_prompt = f"""Context information:
{context}

User question: {query}

Please provide a comprehensive answer based on the context and your knowledge."""
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=500,
                temperature=0.7
            )
            
            generated_response = response.choices[0].message.content
            logger.info(f"Generated contextual response for query: {query[:50]}...")
            
            return generated_response
            
        except Exception as e:
            logger.error(f"Failed to generate contextual response: {e}")
            # Fallback to regular AI service
            from app.domains.ai.services.core import ai_service
            return await ai_service.generate_response(query)
    
    async def add_document_to_store(self, content: str, metadata: Dict[str, Any] = None) -> bool:
        """Add a new document to the vector store."""
        try:
            # Generate unique ID
            doc_id = f"doc_{len(self.vector_store.documents) + 1}"
            
            # Add to vector store
            success = await self.vector_store.add_document(doc_id, content, metadata)
            
            if success:
                logger.info(f"Successfully added document {doc_id} to store")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to add document to store: {e}")
            return False
    
    async def search_relevant_content(self, query: str, source_ids: List[str] = None, max_results: int = 5, min_score: float = 0.0) -> List[Dict[str, Any]]:
        """Search for relevant content in the vector store."""
        try:
            results = await self.vector_store.search(query, k=max_results)
            
            # Filter by min_score if provided
            if min_score > 0.0:
                results = [r for r in results if r['score'] >= min_score]
            
            # Filter by source_ids if provided
            if source_ids:
                results = [r for r in results if r['document']['id'] in source_ids]
            
            return results
            
        except Exception as e:
            logger.error(f"Failed to search relevant content: {e}")
            return []
    
    async def index_document(self, file_path: str, file_content: str, source_metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """Index a document in the vector store."""
        try:
            # Generate document ID from file path
            doc_id = f"doc_{file_path}_{len(self.vector_store.documents) + 1}"
            
            # Add document to vector store
            success = await self.vector_store.add_document(doc_id, file_content, source_metadata)
            
            if success:
                return {
                    'success': True,
                    'document_id': doc_id,
                    'chunks_indexed': 1,
                    'message': f'Successfully indexed document: {file_path}'
                }
            else:
                return {
                    'success': False,
                    'document_id': None,
                    'chunks_indexed': 0,
                    'message': f'Failed to index document: {file_path}'
                }
                
        except Exception as e:
            logger.error(f"Failed to index document {file_path}: {e}")
            return {
                'success': False,
                'document_id': None,
                'chunks_indexed': 0,
                'message': f'Error indexing document: {str(e)}'
            }
    
    async def get_contextual_content(self, query: str, max_results: int = 3) -> str:
        """Get contextual content for a query."""
        try:
            results = await self.vector_store.search(query, k=max_results)
            
            if not results:
                return ""
            
            # Build context from results
            context_parts = []
            for result in results:
                doc = result['document']
                context_parts.append(f"[{doc['metadata'].get('category', 'document')}] {doc['content']}")
            
            return "\n\n".join(context_parts)
            
        except Exception as e:
            logger.error(f"Failed to get contextual content: {e}")
            return ""
    
    def get_indexed_sources(self) -> List[Dict[str, Any]]:
        """Get list of indexed sources."""
        try:
            sources = []
            for doc in self.vector_store.documents:
                sources.append({
                    'id': doc['id'],
                    'metadata': doc['metadata'],
                    'content_preview': doc['content'][:100] + "..." if len(doc['content']) > 100 else doc['content']
                })
            return sources
            
        except Exception as e:
            logger.error(f"Failed to get indexed sources: {e}")
            return []
    
    def remove_source(self, source_id: str) -> bool:
        """Remove a source from the vector store."""
        try:
            # Find the document index
            doc_index = None
            for i, doc in enumerate(self.vector_store.documents):
                if doc['id'] == source_id:
                    doc_index = i
                    break
            
            if doc_index is not None:
                # Remove from documents list
                self.vector_store.documents.pop(doc_index)
                self.vector_store.embeddings.pop(doc_index)
                
                # Rebuild FAISS index
                self.vector_store._initialize_index()
                if self.vector_store.embeddings:
                    embeddings_array = np.array(self.vector_store.embeddings, dtype=np.float32)
                    self.vector_store.index.add(embeddings_array)
                
                logger.info(f"Successfully removed source: {source_id}")
                return True
            else:
                logger.warning(f"Source not found: {source_id}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to remove source {source_id}: {e}")
            return False
    
    def clear_all(self) -> bool:
        """Clear all documents from the vector store."""
        try:
            self.vector_store.documents.clear()
            self.vector_store.embeddings.clear()
            self.vector_store._initialize_index()
            self.documents_loaded = False
            
            logger.info("Successfully cleared all documents from vector store")
            return True
            
        except Exception as e:
            logger.error(f"Failed to clear vector store: {e}")
            return False
    
    def is_available(self) -> bool:
        """Check if RAG service is available."""
        return RAG_AVAILABLE and self.vector_store.index is not None
    
    def get_status(self) -> Dict[str, Any]:
        """Get RAG service status."""
        return {
            'available': RAG_AVAILABLE,
            'documents_loaded': self.documents_loaded,
            'vector_store_initialized': self.vector_store.index is not None,
            'document_count': len(self.vector_store.documents),
            'status': 'ACTIVE - RAG service operational'
        }

# Global RAG service instance
rag_service = RAGService()