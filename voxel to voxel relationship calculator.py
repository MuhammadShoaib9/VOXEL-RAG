"""
FIXED: CALCULATE VOXEL NEIGHBORS AND EXPORT
Now creates folder if it doesn't exist
"""

import rhinoscriptsyntax as rs
import csv
import os

print("\n" + "="*70)
print("CALCULATE VOXEL ADJACENCY")
print("="*70)

# Output folder
output_folder = r"C:\VoxelExport"

# CREATE FOLDER IF IT DOESN'T EXIST (FIX!)
if not os.path.exists(output_folder):
    os.makedirs(output_folder)
    print(f"✅ Created folder: {output_folder}")
else:
    print(f"✅ Using existing folder: {output_folder}")

# Distance threshold for adjacency
ADJACENCY_THRESHOLD = 1.5

# ============================================================
# CALCULATE NEIGHBORS
# ============================================================

def calculate_neighbors():
    """Calculate neighbor relationships between voxels"""
    
    print("\n[STEP 1] Collecting all voxels from all layers...")
    
    all_voxels = []
    
    for layer in ['Layer 01', 'Layer 02', 'Layer 03', 'Layer 04']:
        objects = rs.ObjectsByLayer(layer)
        
        if not objects:
            continue
        
        print(f"  {layer}: {len(objects)} voxels")
        
        for obj in objects:
            voxel_id = rs.GetUserText(obj, "voxel_id")
            
            if not voxel_id:
                continue
            
            bbox = rs.BoundingBox(obj)
            if bbox and len(bbox) >= 7:
                cx = (bbox[0].X + bbox[6].X) / 2.0
                cy = (bbox[0].Y + bbox[6].Y) / 2.0
                cz = (bbox[0].Z + bbox[6].Z) / 2.0
                
                all_voxels.append({
                    'voxel_id': voxel_id,
                    'guid': obj,
                    'x': cx,
                    'y': cy,
                    'z': cz
                })
    
    print(f"\n  Total voxels collected: {len(all_voxels)}")
    
    print(f"\n[STEP 2] Calculating neighbors (threshold: {ADJACENCY_THRESHOLD}m)...")
    print("  This may take several minutes for 16K voxels...")
    
    neighbor_relationships = []
    
    for i, voxel in enumerate(all_voxels):
        
        if (i + 1) % 1000 == 0:
            print(f"    Processed {i+1}/{len(all_voxels)} voxels...")
        
        voxel_id = voxel['voxel_id']
        x1, y1, z1 = voxel['x'], voxel['y'], voxel['z']
        
        for j, other in enumerate(all_voxels):
            
            if i == j:
                continue
            
            other_id = other['voxel_id']
            x2, y2, z2 = other['x'], other['y'], other['z']
            
            dx = x2 - x1
            dy = y2 - y1
            dz = z2 - z1
            distance = (dx**2 + dy**2 + dz**2)**0.5
            
            if distance <= ADJACENCY_THRESHOLD:
                
                direction = determine_direction(dx, dy, dz, distance)
                
                neighbor_relationships.append({
                    'from_voxel': voxel_id,
                    'to_voxel': other_id,
                    'direction': direction,
                    'distance': round(distance, 3)
                })
    
    print(f"\n  Found {len(neighbor_relationships)} neighbor relationships")
    
    return neighbor_relationships


def determine_direction(dx, dy, dz, distance):
    """Determine primary direction of neighbor"""
    
    if distance == 0:
        return 'same'
    
    dx_norm = abs(dx) / distance
    dy_norm = abs(dy) / distance
    dz_norm = abs(dz) / distance
    
    if dz_norm > 0.7:
        return 'above' if dz > 0 else 'below'
    elif dx_norm > dy_norm:
        return 'east' if dx > 0 else 'west'
    else:
        return 'north' if dy > 0 else 'south'


def export_neighbors_to_csv(relationships):
    """Export neighbor relationships to CSV"""
    
    csv_file = os.path.join(output_folder, "voxel_neighbors.csv")
    
    print(f"\n[STEP 3] Exporting to: {csv_file}")
    
    # ENSURE FOLDER EXISTS (EXTRA SAFETY)
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    with open(csv_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['from_voxel', 'to_voxel', 'direction', 'distance'])
        writer.writeheader()
        writer.writerows(relationships)
    
    print(f"✅ Neighbor relationships exported!")
    
    return csv_file


# ============================================================
# MAIN EXECUTION
# ============================================================

result = rs.MessageBox(
    "Calculate voxel adjacency relationships?\n\n" +
    "This will:\n" +
    "• Analyze all 16K+ voxels\n" +
    "• Calculate spatial neighbors\n" +
    "• Export to voxel_neighbors.csv\n\n" +
    "Time: 5-10 minutes\n\n" +
    "Continue?",
    buttons=4 | 32,
    title="Calculate Neighbors"
)

if result == 6:
    
    relationships = calculate_neighbors()
    
    csv_file = export_neighbors_to_csv(relationships)
    
    print("\n" + "="*70)
    print("✅ NEIGHBOR CALCULATION COMPLETE!")
    print("="*70)
    print(f"\nResults:")
    print(f"  Total relationships: {len(relationships)}")
    print(f"  Average neighbors per voxel: {len(relationships) / 16116:.1f}")
    print(f"\n  Exported to: {csv_file}")
    print("="*70)
    
    rs.MessageBox(
        f"✅ Neighbor Calculation Complete!\n\n" +
        f"Total relationships: {len(relationships):,}\n" +
        f"Avg neighbors/voxel: {len(relationships) / 16116:.1f}\n\n" +
        f"Exported to:\n{csv_file}",
        title="Complete"
    )
else:
    print("Cancelled")
