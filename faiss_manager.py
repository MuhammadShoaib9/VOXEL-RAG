"""
FAISS Manager for Vector Similarity Search
Loads embeddings and creates searchable FAISS index
"""

import faiss
import numpy as np
import json
import os
from typing import List, Dict, Optional, Tuple

class FAISSManager:
    """
    Manage FAISS vector index for voxel similarity search
    """
    
    def __init__(
        self, 
        embedding_file: str = None,
        metadata_file: str = None,
        index_file: str = None
    ):
        """
        Initialize FAISS Manager
        
        Args:
            embedding_file: Path to .npy embeddings file
            metadata_file: Path to .json metadata file
            index_file: Path to save/load FAISS index
        """
        self.embedding_file = embedding_file
        self.metadata_file = metadata_file
        self.index_file = index_file
        
        self.embeddings = None
        self.metadata = None
        self.index = None
        self.dimensions = None
        
        # Load if files provided
        if embedding_file and metadata_file:
            self.load_embeddings_and_metadata()
        
        if index_file and os.path.exists(index_file):
            self.load_index()
    
    def load_embeddings_and_metadata(self):
        """Load embeddings and metadata from disk"""
        
        print(f"\n📂 Loading embeddings from: {self.embedding_file}")
        
        # Load embeddings
        self.embeddings = np.load(self.embedding_file)
        self.dimensions = self.embeddings.shape[1]
        
        print(f"   ✅ Loaded {self.embeddings.shape[0]:,} embeddings")
        print(f"   📐 Dimensions: {self.dimensions}")
        
        # Load metadata
        print(f"\n📂 Loading metadata from: {self.metadata_file}")
        with open(self.metadata_file, 'r') as f:
            self.metadata = json.load(f)
        
        print(f"   ✅ Loaded {len(self.metadata):,} metadata entries")
    
    def create_index(self, index_type: str = 'flat'):
        """
        Create FAISS index from embeddings
        
        Args:
            index_type: Type of FAISS index
                - 'flat': Exact search (IndexFlatIP) - best for <100k vectors
                - 'ivf': Approximate search (IndexIVFFlat) - faster for >100k
        """
        
        if self.embeddings is None:
            raise ValueError("Embeddings not loaded. Call load_embeddings_and_metadata() first.")
        
        print(f"\n🔧 Creating FAISS index...")
        print(f"   Type: {index_type}")
        print(f"   Vectors: {self.embeddings.shape[0]:,}")
        print(f"   Dimensions: {self.dimensions}")
        
        # Normalize embeddings for cosine similarity
        # (FAISS inner product on normalized vectors = cosine similarity)
        embeddings_normalized = self.embeddings.copy()
        faiss.normalize_L2(embeddings_normalized)
        
        if index_type == 'flat':
            # Exact search using Inner Product (cosine similarity on normalized vectors)
            self.index = faiss.IndexFlatIP(self.dimensions)
            self.index.add(embeddings_normalized)
            
        elif index_type == 'ivf':
            # Approximate search with IVF (faster for large datasets)
            nlist = 100  # number of clusters
            quantizer = faiss.IndexFlatIP(self.dimensions)
            self.index = faiss.IndexIVFFlat(quantizer, self.dimensions, nlist)
            
            # Train the index
            print("   🔄 Training IVF index...")
            self.index.train(embeddings_normalized)
            
            # Add vectors
            self.index.add(embeddings_normalized)
            self.index.nprobe = 10  # search 10 nearest clusters
        
        else:
            raise ValueError(f"Unknown index type: {index_type}")
        
        print(f"   ✅ Index created with {self.index.ntotal:,} vectors")
    
    def save_index(self, filepath: str = None):
        """Save FAISS index to disk"""
        
        if self.index is None:
            raise ValueError("No index to save. Call create_index() first.")
        
        filepath = filepath or self.index_file
        
        if not filepath:
            raise ValueError("No filepath provided for saving index")
        
        print(f"\n💾 Saving FAISS index to: {filepath}")
        
        faiss.write_index(self.index, filepath)
        
        file_size = os.path.getsize(filepath) / (1024 * 1024)
        print(f"   ✅ Index saved successfully")
        print(f"   📦 Size: {file_size:.1f} MB")
    
    def load_index(self, filepath: str = None):
        """Load FAISS index from disk"""
        
        filepath = filepath or self.index_file
        
        if not filepath or not os.path.exists(filepath):
            raise ValueError(f"Index file not found: {filepath}")
        
        print(f"\n📂 Loading FAISS index from: {filepath}")
        
        self.index = faiss.read_index(filepath)
        
        print(f"   ✅ Index loaded with {self.index.ntotal:,} vectors")
    
    def search(
        self, 
        query_text: str, 
        top_k: int = 50,
        openai_helper = None
    ) -> List[Dict]:
        """
        Search for similar voxels using natural language query
        
        Args:
            query_text: Natural language search query
            top_k: Number of results to return
            openai_helper: OpenAIHelper instance for generating query embedding
        
        Returns:
            List of dicts with voxel_id, description, score
        """
        
        if self.index is None:
            raise ValueError("Index not loaded. Call create_index() or load_index() first.")
        
        if openai_helper is None:
            # Import here to avoid circular dependency
            from src.utils.embedding_generator import EmbeddingGenerator
            from config.neo4j_config import OPENAI_CONFIG
            
            generator = EmbeddingGenerator(
                api_key=OPENAI_CONFIG['api_key'],
                model='text-embedding-3-small'
            )
            
            query_embedding = generator.generate_embedding(query_text)
        else:
            # Use provided helper
            query_embedding = openai_helper.generate_embedding(query_text)
        
        if query_embedding is None:
            raise ValueError("Failed to generate query embedding")
        
        # Normalize query embedding
        query_embedding = query_embedding.reshape(1, -1).astype('float32')
        faiss.normalize_L2(query_embedding)
        
        # Search
        scores, indices = self.index.search(query_embedding, top_k)
        
        # Compile results
        results = []
        for i, (score, idx) in enumerate(zip(scores[0], indices[0])):
            if idx < len(self.metadata):
                meta = self.metadata[idx]
                results.append({
                    'rank': i + 1,
                    'voxel_id': meta['voxel_id'],
                    'description': meta.get('description', ''),
                    'similarity_score': float(score),
                    'embedding_index': int(idx)
                })
        
        return results
    
    def get_statistics(self) -> Dict:
        """Get index statistics"""
        
        stats = {
            'total_vectors': self.index.ntotal if self.index else 0,
            'dimensions': self.dimensions,
            'index_type': type(self.index).__name__ if self.index else None,
            'embeddings_loaded': self.embeddings is not None,
            'metadata_loaded': self.metadata is not None,
            'index_built': self.index is not None
        }
        
        return stats


# ===================================
# EXAMPLE USAGE
# ===================================
if __name__ == "__main__":
    
    # Test loading and creating index
    manager = FAISSManager(
        embedding_file=r'C:\VoxelExport\voxel_embeddings.npy',
        metadata_file=r'C:\VoxelExport\voxel_metadata.json'
    )
    
    # Create index
    manager.create_index(index_type='flat')
    
    # Save index
    manager.save_index(r'C:\VoxelExport\voxel_faiss.index')
    
    # Test search
    results = manager.search("high moisture clay with poor bearing capacity", top_k=10)
    
    print("\n🔍 Test search results:")
    for r in results[:5]:
        print(f"\n{r['rank']}. {r['voxel_id']} (score: {r['similarity_score']:.3f})")
        print(f"   {r['description'][:100]}...")