"""
OpenAI Helper - WITH MASTER PROMPT SYSTEM + CONCISE SYSTEM MESSAGE
Uses 11 task-specific prompts for specialized answers
UPDATED: Now includes system message for ultra-concise outputs
"""

from openai import OpenAI
from src.utils.master_prompts import MasterPrompts

class OpenAIHelper:
    """Helper class for OpenAI GPT interactions with task-specific prompts"""
    
    def __init__(self, api_key, model='gpt-4o-mini'):
        self.client = OpenAI(api_key=api_key)
        self.model = model
        
        # Load master prompts
        self.master_prompts = MasterPrompts()
        
        # System message for conciseness
        self.system_message = """You are a concise geotechnical data assistant.
Your responses MUST be ultra-brief and to-the-point.
Follow the output format examples in the prompt EXACTLY.
Never add extra sections, tables, or verbose explanations unless the prompt specifically requests them.
Adhere strictly to the maximum line limits specified in each prompt."""
        
        print("OpenAI Helper initialized with model:", model)
        print("Master Prompts loaded: 11 task-specific prompts ready")
        print("System message: Concise output mode enabled")
    
    def generate_answer(self, question, voxels, task_type='FILTERING'):
        """
        Generate intelligent answer using task-specific prompt
    
        Args:
            question: User's question
            voxels: List of voxel dictionaries (with ALL 50+ attributes)
            task_type: One of 11 task types (FILTERING, COMPARISON, etc.)
    
        Returns:
            dict with 'answer', 'voxel_ids', and 'tokens'
        """
    
        if not voxels:
            return {
                'answer': "No voxels found.",
                'voxel_ids': [],
                'tokens': {'input': 0, 'output': 0, 'total': 0}
            }
    
        # Get counts
        total_count = len(voxels)
        returned_count = min(total_count, 5000)
    
        # Format voxel data for prompt - WITH ALL ATTRIBUTES
        voxel_data = self._format_voxel_data(voxels[:returned_count])
    
        print(f"\n{'='*60}")
        print("DEBUG: Data being sent to GPT")
        print(f"{'='*60}")
        print(f"Total voxels: {total_count}")
        print(f"First voxel ID: {voxels[0].get('voxel_id') if voxels else 'None'}")
        print(f"First voxel moisture: {voxels[0].get('moisture_content') if voxels else 'None'}")
        print(f"\nVoxel table preview:")
        print(voxel_data[:800])
        print(f"{'='*60}\n")
    
        # Get task-specific prompt
        prompt_template = self.master_prompts.get_prompt(task_type)
    
        # Fill in the prompt template
        prompt = prompt_template.format(
            question=question,
            total_count=total_count,
            returned_count=returned_count,
            voxel_data=voxel_data
        )
    
        print("\n" + "="*60)
        print("GENERATING ANSWER")
        print("="*60)
        print("Task Type:", task_type)
        print("Model:", self.model)
        print("Voxels:", returned_count, "of", total_count)
        print("System message: Concise mode")
    
        try:
            # Call OpenAI API with system message
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": self.system_message
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=2000
            )
        
            answer = response.choices[0].message.content
        
            # Extract voxel IDs from answer
            voxel_ids = self._extract_voxel_ids(answer, voxels)
        
            # ✅ EXTRACT TOKEN COUNTS
            tokens = {
                'input': response.usage.prompt_tokens,
                'output': response.usage.completion_tokens,
                'total': response.usage.total_tokens
            }
        
            print("✅ Answer generated successfully")
            print("   Length:", len(answer), "characters")
            print("   Voxel IDs extracted:", len(voxel_ids))
            print("   Tokens used:", tokens['total'])
        
            return {
                'answer': answer,
                'voxel_ids': voxel_ids,
                'tokens': tokens  # ✅ ADDED
            }
        
        except Exception as e:
            print("❌ Error generating answer:", str(e))
            return {
                'answer': "Error generating answer: " + str(e),
                'voxel_ids': [v.get('voxel_id') for v in voxels[:returned_count]],
                'tokens': {'input': 0, 'output': 0, 'total': 0}  # ✅ ADDED
            }
    
    def _format_voxel_data(self, voxels):
        """
        Format voxel data for prompt - WITH ALL 50+ ATTRIBUTES
        
        For small datasets (≤5 voxels): Show ALL attributes organized by category
        For large datasets (>5 voxels): Show summary table with key attributes
        """
        
        if not voxels:
            return "No voxel data available."
        
        # For small datasets (≤5 voxels), show ALL attributes
        if len(voxels) <= 5:
            lines = []
            for i, v in enumerate(voxels, 1):
                lines.append("\n" + "="*70)
                lines.append("VOXEL #{}: {}".format(i, v.get('voxel_id', 'N/A')))
                lines.append("="*70)
                
                # Group attributes by category
                categories = {
                    'IDENTIFICATION': ['voxel_id', 'project_id'],
                    'MATERIAL': ['material_type', 'material_subtype', 'soil_group', 'texture', 'color'],
                    'POSITION': ['position_x', 'position_y', 'position_z', 'elevation', 'depth_below_surface'],
                    'GEOLOGICAL': ['mass_id', 'mass_name', 'top_surface_id', 'bottom_surface_id'],
                    'PHYSICAL': ['moisture_content', 'density', 'unit_weight', 'porosity', 'saturation', 'permeability'],
                    'STRENGTH': ['bearing_capacity', 'allowable_bearing_pressure', 'spt_n_value', 'friction_angle', 'cohesion', 'undrained_shear_strength'],
                    'SETTLEMENT': ['settlement_potential_mm', 'settlement_risk'],
                    'RISK': ['overall_risk_level', 'overall_risk_score', 'bearing_risk', 'is_problematic', 'is_high_moisture', 'is_low_bearing', 'requires_attention'],
                    'FOUNDATION_RECOMMENDATIONS': ['foundation_suitability', 'recommended_foundation_type', 'excavation_stability', 'ground_improvement_needed', 'dewatering_required'],
                    'CONSOLIDATION': ['liquid_limit', 'plastic_limit', 'plasticity_index'],
                    'METADATA': ['data_source', 'data_quality', 'confidence_level', 'data_version', 'created_date'],
                    'GEOMETRY': ['voxel_volume']
                }
                
                for category, attrs in categories.items():
                    category_data = []
                    for attr in attrs:
                        if attr in v and v[attr] is not None:
                            category_data.append("  {}: {}".format(attr, v[attr]))
                    
                    if category_data:
                        lines.append("\n{}:".format(category))
                        lines.extend(category_data)
            
            return "\n".join(lines)
        
        # For larger datasets (>5 voxels), show summary table + key attributes
        else:
            lines = []
            lines.append("\n" + "="*100)
            lines.append("SHOWING {} OF {} VOXELS (with key attributes)".format(min(len(voxels), 20), len(voxels)))
            lines.append("="*100)
            lines.append("\nKEY ATTRIBUTES TABLE:")
            lines.append("-"*100)
            
            # Table header
            header = "{:<15} {:<12} {:<8} {:<10} {:<8} {:<6} {:<15} {:<15}".format(
                "Voxel_ID", "Material", "Moisture", "Bearing", "Risk", "SPT", "Foundation", "Surfaces(T/B)"
            )
            lines.append(header)
            lines.append("-"*100)
            
            # Table rows
            for v in voxels[:20]:
                # Get values with defaults
                voxel_id = str(v.get('voxel_id', 'N/A'))[:15]
                material = str(v.get('material_type', 'N/A'))[:12]
                moisture = v.get('moisture_content', 0)
                bearing = v.get('bearing_capacity', 0)
                risk = str(v.get('overall_risk_level', 'N/A'))[:8]
                spt = v.get('spt_n_value', 0)
                foundation = str(v.get('foundation_suitability', 'N/A'))[:15]
                top_surf = str(v.get('top_surface_id', 'N/A'))[:5]
                bottom_surf = str(v.get('bottom_surface_id', 'N/A'))[:5]
                surfaces = "{}/{}".format(top_surf, bottom_surf)
                
                # Format row
                row = "{:<15} {:<12} {:<8.1f} {:<10.1f} {:<8} {:<6} {:<15} {:<15}".format(
                    voxel_id,
                    material,
                    float(moisture or 0),
                    float(bearing or 0),
                    risk,
                    int(spt or 0),
                    foundation,
                    surfaces
                )
                lines.append(row)
            
            if len(voxels) > 20:
                lines.append("... and {} more voxels (ALL with full 50+ attributes)".format(len(voxels) - 20))
            
            lines.append("\n" + "="*100)
            lines.append("⚠️ IMPORTANT: Each voxel has 50+ attributes. Key ones shown above in table.")
            lines.append("")
            lines.append("   ALL ATTRIBUTES AVAILABLE including:")
            lines.append("   - Technical Strength: friction_angle, cohesion, undrained_shear_strength")
            lines.append("   - Physical Properties: density, unit_weight, porosity, saturation, permeability")
            lines.append("   - Foundation: recommended_foundation_type, excavation_stability, ground_improvement_needed")
            lines.append("   - Settlement: settlement_potential_mm, settlement_risk")
            lines.append("   - Surfaces: top_surface_id, bottom_surface_id (shown in table)")
            lines.append("   - Consolidation: liquid_limit, plastic_limit, plasticity_index")
            lines.append("   - Position: elevation, depth_below_surface")
            lines.append("   - Metadata: data_source, data_quality, confidence_level")
            lines.append("   - And more! (See VOXEL_SCHEMA in prompt)")
            lines.append("="*100)
            
            return "\n".join(lines)
    
    def _extract_voxel_ids(self, answer, voxels):
        """
        Extract voxel IDs from GPT answer
        
        GPT should end answer with: VOXEL_IDS: v_xxx, v_yyy, v_zzz
        """
        
        import re
        
        # Try to find VOXEL_IDS line in answer
        match = re.search(r'VOXEL_IDS:\s*(.+)', answer, re.IGNORECASE)
        
        if match:
            ids_text = match.group(1)
            # Extract all voxel IDs (format: v_XXX_XXXXX)
            voxel_ids = re.findall(r'v_[A-Z0-9]+_[0-9]+', ids_text)
            
            if voxel_ids:
                print("   Extracted {} voxel IDs from answer".format(len(voxel_ids)))
                return voxel_ids
        
        # Fallback: return all voxel IDs from data
        print("   Using all voxel IDs from query results (GPT didn't list them)")
        return [v.get('voxel_id') for v in voxels if v.get('voxel_id')]
    
    def generate_embedding(self, text):
        """
        Generate embedding for text (for FAISS queries)
        
        Args:
            text: Text to embed
            
        Returns:
            numpy array of embedding
        """
        try:
            response = self.client.embeddings.create(
                model="text-embedding-3-small",
                input=text
            )
            
            import numpy as np
            embedding = np.array(response.data[0].embedding)
            return embedding
            
        except Exception as e:
            print("❌ Error generating embedding:", str(e))
            return None
    
    def test_connection(self):
        """Test OpenAI API connection"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": "Say 'Connected'"}],
                max_tokens=10
            )
            return True
        except Exception as e:
            print("Connection test failed:", str(e))
            return False


# Test the OpenAI helper
if __name__ == "__main__":
    import sys
    sys.path.append(r'C:\RhinoVoxelRAG')
    
    from config.neo4j_config import OPENAI_CONFIG
    
    print("\n" + "="*60)
    print("TESTING OPENAI HELPER - CONCISE EDITION")
    print("="*60)
    
    helper = OpenAIHelper(
        api_key=OPENAI_CONFIG['api_key'],
        model=OPENAI_CONFIG['model']
    )
    
    # Test with sample voxels (simulating full attributes)
    sample_voxels = [
        {
            'voxel_id': 'v_M3_00001',
            'material_type': 'Clay',
            'material_subtype': 'Soft Clay',
            'soil_group': 'CL',
            'moisture_content': 45.5,
            'bearing_capacity': 150.0,
            'allowable_bearing_pressure': 50.0,
            'spt_n_value': 8,
            'friction_angle': 18.5,
            'cohesion': 25.0,
            'overall_risk_level': 'High',
            'foundation_suitability': 'Poor',
            'recommended_foundation_type': 'Deep',
            'top_surface_id': 'S2',
            'bottom_surface_id': 'S3',
            'position_x': 10.5,
            'position_y': 20.3,
            'position_z': -5.2,
            'mass_id': 'M3'
        }
    ]
    
    # Test ATTRIBUTE_RETRIEVAL
    print("\n" + "-"*60)
    print("Test: ATTRIBUTE_RETRIEVAL task (concise output)")
    print("-"*60)
    
    result = helper.generate_answer(
        "What is the top_surface_id of v_M3_00001?",
        sample_voxels,
        'ATTRIBUTE_RETRIEVAL'
    )
    
    print("\nAnswer:")
    print(result['answer'])