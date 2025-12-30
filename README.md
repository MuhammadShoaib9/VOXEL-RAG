# VOXEL-GRAPH-VECTOR-RAG

Natural Language Interface for Subsurface Digital Twins using Retrieval-Augmented Generation (RAG) and Large Language Models (LLMs).

##  Overview

This system enables natural language querying, reasoning, and visualization of voxel-based subsurface digital twins. It integrates hybrid RAG (Graph + Vector search) with LLMs to automatically extract, fuse, and interpret spatially distributed underground semantics.

**Key Features:**
-  Natural language querying (no SQL/Cypher expertise required)
-  Hybrid RAG combining Neo4j graph traversal + FAISS vector search
-  Interactive 3D voxel-level visualization in Rhino
-  9 task types: Attribute retrieval, Filtering, Reasoning, Computation, Classification, Summarization, Comparison, Proximity, Visualization

##  Repository Contents

### **1. Source Code**
- `neo4j_connector.py` - Neo4j graph database operations
- `faiss_manager.py` - FAISS vector search manager
- `master_prompts.py` - task-specific prompt templates with anti-hallucination constraints (It can be modified and adopted for other tasks user defined)
- `openai_helper.py` - OpenAI GPT integration (if you need other ai helper, please contact muhammadshoaib5308@gmail.com)
- `neo4j_config.py` - Database and API configuration template
- `rhino_highlighter.py` - 3D voxel highlighting in Rhino (only configuration with red highlighting is upload here. this can be modified for other scenario with more colors)
- `voxel to voxel relationship calculator.py` - Graph relationship generator
- `voxel_metadata.json` - Voxel metadata structure

### **2. Evaluation Dataset**
- `Q&A_Dataset_400.xlsx` - **400 question-answer pairs** across 9 task categories
  - Attribute Retrieval (50 queries, 12.5%)
  - Filtering (40 queries, 10%)
  - Reasoning (45 queries, 11.25%)
  - Computation (40 queries, 10%)
  - Classification (45 queries, 11.25%)
  - Summarization (50 queries, 12.5%)
  - Comparison (40 queries, 10%)
  - Proximity (40 queries, 10%)
  - Visualization (50 queries, 12.5%)

### **3. Ground Truth Data**
- `Ground truth with 4 consistent layers.zip` - Ground truth model in RHino geometries

### **4. Neo4j Database**
- `neo4j-2025-12-29T03-39-58.dump` - Complete Neo4j database dump (16,116 voxels with 50+ attributes each, this data can be used as a practice to demonstrate the developed system inside RHino3D)

## Quick Start

### **Prerequisites**
- Python 3.8+
- Neo4j Database 5.x
- Rhino 3D 7/8 (for visualization)
- API keys: OpenAI, Anthropic, etc. (We can use here OpenAI for demonstration. While, any AI model can be used and file should be prepared accordingly). 

### **Installation**
```bash
# Clone repository
git clone https://github.com/MuhammadShoaib9/VOXEL-GRAPH-VECTOR-RAG.git
cd VOXEL-GRAPH-VECTOR-RAG

# Install dependencies
pip install neo4j==5.14.0 faiss-cpu==1.7.4 numpy pandas openai anthropic
```

### **Configuration**

1. **Configure Neo4j:**
   - Install Neo4j Desktop from https://neo4j.com/download/
   - Create new database
   - Import database dump: `neo4j-2025-12-29T03-39-58.dump`

2. **Configure API Keys:**
   - Open `neo4j_config.py`
   - Replace placeholders with your credentials:
```python
   NEO4J_CONFIG = {
       'uri': 'bolt://localhost:7687',
       'user': 'neo4j',
       'password': 'Voxelpass123',   # this can be used for my created database for demonstration. 
       'database': 'neo4j'
   }
   
   OPENAI_CONFIG = {
       'api_key': 'YOUR_OPENAI_API_KEY_HERE'  # Replace this with your open_Ai key
   }
```

### **Basic Usage**
```python
from neo4j_connector import Neo4jConnector
from openai_helper import OpenAIHelper
from faiss_manager import FAISSManager

# Initialize components
neo4j = Neo4jConnector(uri="bolt://localhost:7687", 
                       user="neo4j", 
                       password="your_password")

gpt = OpenAIHelper(api_key="your_openai_key")

# Query example
question = "Find voxels with high moisture content in layer M3"
voxels = neo4j.get_high_moisture_voxels_with_count(threshold=40.0)
answer = gpt.generate_answer(question, voxels['voxels'], 'FILTERING')

print(answer['answer'])
```

## 📦 Project Data Files

Some of the file needed for demonstration are upload. While some large files are **available upon request** via email:

- **Rhino 3D Voxel Model** (.3dm file, uploaded)
- **Neo4j Knowledge Graph** (complete database, uploaded)
- **FAISS Vector Index** (.index file, request via email)
- **Voxel Embeddings** (.npy file, request via email)
- **Complete Metadata** (.json file, uploaded)

📧 **Contact:** muhammadshoaib5308@gmail.com


## 🏗️ System Architecture
```
User Query (Natural Language)
    ↓
Query Router (Task Classification)
    ↓
Hybrid Retrieval ← Neo4j Graph + FAISS Vector Search
    ↓
Task-Specific Prompt Template (9 types)
    ↓
LLM (GPT-4o)
    ↓
Natural Language Answer + Voxel IDs
    ↓
3D Visualization in Rhino
```

## 📚 Voxel Attribute Schema for the upload demostration example

Each voxel contains comprehensive geotechnical properties:

**Identification:** voxel_id, project_id

**Material:** material_type, soil_group, texture, color

**Position:** position_x/y/z, elevation, depth_below_surface

**Geological:** mass_id, top_surface_id, bottom_surface_id

**Physical:** moisture_content, density, porosity, permeability

**Strength:** bearing_capacity, spt_n_value, friction_angle, cohesion

**Risk Assessment:** overall_risk_level, settlement_potential_mm, is_problematic

**Foundation:** foundation_suitability, recommended_foundation_type, ground_improvement_needed


## 🤝 Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## 📄 License

This project is licensed under the MIT License.


Special thanks to all contributors and domain experts who participated in the evaluation.
