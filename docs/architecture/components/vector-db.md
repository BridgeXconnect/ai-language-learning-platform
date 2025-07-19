# Vector Database Architecture

## Overview
The Vector Database component stores and manages embeddings for SOP documents, enabling efficient semantic search and RAG operations in the Course Generation Engine.

## Core Features
- Embedding storage and retrieval
- Semantic similarity search
- Multi-tenant isolation
- Version control for embeddings
- Batch processing support

## Technologies
- Milvus/Pinecone as primary vector store
- AWS OpenSearch with vector engine as fallback
- Redis for metadata caching
- S3 for backup storage

## Collection Schema
```python
# Collection definition
collection_schema = {
    "name": "sop_embeddings",
    "fields": [
        {
            "name": "id",
            "type": "VARCHAR(100)",
            "is_primary": True
        },
        {
            "name": "request_id",
            "type": "VARCHAR(100)",
            "index": True
        },
        {
            "name": "embedding",
            "type": "FLOAT_VECTOR",
            "dim": 1536  # OpenAI embedding dimension
        },
        {
            "name": "text_chunk",
            "type": "VARCHAR(8192)"
        },
        {
            "name": "metadata",
            "type": "JSON"
        },
        {
            "name": "created_at",
            "type": "TIMESTAMP"
        }
    ],
    "indexes": [
        {
            "name": "embedding_index",
            "field_name": "embedding",
            "index_type": "IVF_FLAT",
            "metric_type": "L2",
            "params": {"nlist": 1024}
        }
    ]
}
```

## API Interface
```python
class VectorDBService:
    async def store_embeddings(
        self, 
        request_id: str, 
        embeddings: List[float], 
        text_chunks: List[str],
        metadata: Dict[str, Any]
    ) -> List[str]

    async def search_similar(
        self,
        query_embedding: List[float],
        request_id: str,
        limit: int = 5,
        score_threshold: float = 0.7
    ) -> List[Dict[str, Any]]

    async def delete_embeddings(
        self,
        request_id: str
    ) -> bool

    async def get_metadata(
        self,
        vector_ids: List[str]
    ) -> Dict[str, Dict[str, Any]]
```

## Performance Optimization
- Index type: IVF_FLAT for balance of speed/accuracy
- Batch processing for bulk operations
- Caching frequently accessed metadata
- Regular index optimization
- Load balancing across nodes

## Monitoring Metrics
- Query latency (p95, p99)
- Index size and growth rate
- Cache hit/miss ratio
- Search quality metrics
- Resource utilization

## Backup Strategy
- Daily snapshots to S3
- Incremental backups every 6 hours
- Metadata backup in PostgreSQL
- 30-day retention policy

## Security Measures
- Network isolation
- Access control per collection
- Encryption at rest
- Audit logging
- Regular security scans 