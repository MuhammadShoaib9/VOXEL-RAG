"""
Rhino Voxel Highlighter
"""

import rhinoscriptsyntax as rs

class VoxelHighlighter:
    """Highlights voxels in Rhino viewport"""
    
    def __init__(self, color_scheme=None):
        self.color_scheme = color_scheme or {
            'High': (255, 0, 0),      # Red
            'Medium': (255, 255, 0),   # Yellow
            'Low': (0, 255, 0),        # Green
            'Default': (100, 100, 100) # Gray
        }
        self.highlighted_objects = []
    
    def find_voxel_by_id(self, voxel_id):
        """Find Rhino object by voxel_id property"""
        all_objects = rs.AllObjects()
        
        if not all_objects:
            return None
        
        for obj_guid in all_objects:
            stored_id = rs.GetUserText(obj_guid, 'voxel_id')
            if stored_id == voxel_id:
                return obj_guid
        
        return None
    
    def highlight_voxel(self, voxel_id, color=(255, 0, 0)):
        """Highlight single voxel with color"""
        obj_guid = self.find_voxel_by_id(voxel_id)
        
        if not obj_guid:
            print("  Voxel", voxel_id, "not found in Rhino")
            return False
        
        rs.ObjectColor(obj_guid, color)
        self.highlighted_objects.append(obj_guid)
        return True
    
    def highlight_voxels(self, voxel_list):
        """
        Highlight multiple voxels
        voxel_list can be:
          - List of voxel_ids: ['v_M1_00001', 'v_M1_00002']
          - List of dicts: [{'voxel_id': 'v_M1_00001', 'overall_risk_level': 'High'}]
        """
        count = 0
        
        for item in voxel_list:
            # Extract voxel_id and risk level
            if isinstance(item, dict):
                voxel_id = item.get('voxel_id')
                risk = item.get('overall_risk_level', 'Default')
                color = self.color_scheme.get(risk, self.color_scheme['Default'])
            else:
                voxel_id = item
                color = (255, 0, 0)  # Default red
            
            if self.highlight_voxel(voxel_id, color):
                count += 1
        
        return count
    
    def clear_all(self):
        """Reset all highlighted voxels to gray"""
        default_color = (200, 200, 200)
        
        for obj_guid in self.highlighted_objects:
            try:
                rs.ObjectColor(obj_guid, default_color)
            except:
                pass
        
        self.highlighted_objects = []
        print("Cleared all highlighting")