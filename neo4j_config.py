"""
Neo4j Configuration for Voxel RAG System
"""

# Neo4j Desktop Connection Settings
NEO4J_CONFIG = {
    'uri': 'neo4j://localhost:7687',
    'user': 'neo4j',
    'password': 'voxelpass123',
    'database': 'neo4j'
}

# OpenAI API Settings
OPENAI_CONFIG = {
    'api_key': 'YOUR_API KEY',
    'model': 'gpt-4o-mini',
    'temperature': 0.0,
    'max_tokens': 1000
}

# Color Scheme for Visualization
VISUALIZATION_COLORS = {
    'High': (255, 0, 0),
    'Medium': (255, 255, 0),
    'Low': (0, 255, 0),
    'Default': (100, 100, 100)
}