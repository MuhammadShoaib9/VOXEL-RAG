"""
Neo4j Database Connector - COMPLETE WITH ALL 50+ ATTRIBUTES + SURFACE + LAYER COMPARISON
Handles all database operations with complete voxel schema
"""

from neo4j import GraphDatabase
import sys

class Neo4jConnector:
    """Connector for Neo4j graph database operations"""
    
    def __init__(self, uri, user, password, database='neo4j'):
        """
        Initialize Neo4j connection
        
        Args:
            uri: Neo4j connection URI
            user: Username
            password: Password
            database: Database name (default: 'neo4j')
        """
        self.uri = uri
        self.user = user
        self.password = password
        self.database = database
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        
        print("Neo4j Connector initialized")
        print("URI:", uri)
        print("User:", user)
        print("Database:", database)
    
    def close(self):
        """Close the Neo4j connection"""
        if self.driver:
            self.driver.close()
            print("Neo4j connection closed")
    
    def test_connection(self):
        """Test the database connection"""
        try:
            with self.driver.session(database=self.database) as session:
                result = session.run("RETURN 1 as test")
                test_value = result.single()["test"]
                
                if test_value == 1:
                    print("✅ Neo4j connection successful")
                    
                    # Get database stats
                    stats_query = """
                    MATCH (v:Voxel)
                    RETURN count(v) as voxel_count
                    """
                    stats = session.run(stats_query).single()
                    
                    if stats:
                        print("   Voxels in database: {:,}".format(stats["voxel_count"]))
                    
                    return True
                else:
                    print("❌ Neo4j connection test failed")
                    return False
        except Exception as e:
            print("❌ Neo4j connection error:", str(e))
            return False
    
    def execute_query(self, query, parameters=None):
        """
        Execute a Cypher query and return results
        
        Args:
            query: Cypher query string
            parameters: Dictionary of query parameters
            
        Returns:
            List of records
        """
        try:
            with self.driver.session(database=self.database) as session:
                result = session.run(query, parameters or {})
                return [record for record in result]
        except Exception as e:
            print("❌ Query execution error:", str(e))
            print("   Query:", query[:200])
            return []
    
    def _node_to_dict(self, node):
        """
        Convert Neo4j node to dictionary with ALL attributes
        
        Args:
            node: Neo4j node object
            
        Returns:
            Dictionary with all node properties
        """
        if node is None:
            return {}
        
        return dict(node)
    
    def get_voxels_by_ids(self, voxel_ids, limit=5000):
        """
        Get voxels by their IDs - RETURNS ALL 50+ ATTRIBUTES
        
        Args:
            voxel_ids: List of voxel IDs
            limit: Maximum voxels to return
            
        Returns:
            Dict with total_count, returned_count, voxels (with ALL attributes)
        """
        
        if not voxel_ids:
            return {'total_count': 0, 'returned_count': 0, 'voxels': []}
        
        query = """
        MATCH (v:Voxel)
        WHERE v.voxel_id IN $voxel_ids
        RETURN v
        LIMIT $limit
        """
        
        params = {
            'voxel_ids': voxel_ids,
            'limit': limit
        }
        
        results = self.execute_query(query, params)
        
        if not results:
            return {'total_count': 0, 'returned_count': 0, 'voxels': []}
        
        voxels = []
        for record in results:
            voxel_dict = self._node_to_dict(record['v'])
            voxels.append(voxel_dict)
        
        return {
            'total_count': len(voxels),
            'returned_count': len(voxels),
            'voxels': voxels
        }
    
    def get_voxels_by_layer_with_count(self, layer, limit=5000):
        """
        Get voxels by layer - RETURNS ALL ATTRIBUTES
        
        Args:
            layer: Layer ID (M1, M2, M3, M4)
            limit: Maximum voxels to return
            
        Returns:
            Dict with total_count, returned_count, voxels (ALL attributes)
        """
        
        count_query = """
        MATCH (v:Voxel)
        WHERE v.mass_id = $layer
        RETURN count(v) as total
        """
        
        count_result = self.execute_query(count_query, {'layer': layer})
        total_count = count_result[0]['total'] if count_result else 0
        
        query = """
        MATCH (v:Voxel)
        WHERE v.mass_id = $layer
        RETURN v
        LIMIT $limit
        """
        
        params = {
            'layer': layer,
            'limit': limit
        }
        
        results = self.execute_query(query, params)
        
        if not results:
            return {
                'total_count': total_count,
                'returned_count': 0,
                'voxels': []
            }
        
        voxels = []
        for record in results:
            voxel_dict = self._node_to_dict(record['v'])
            voxels.append(voxel_dict)
        
        return {
            'total_count': total_count,
            'returned_count': len(voxels),
            'voxels': voxels
        }
    
    def get_high_moisture_voxels_with_count(self, threshold=40.0, limit=5000):
        """
        Get voxels with high moisture - RETURNS ALL ATTRIBUTES
        
        Args:
            threshold: Moisture percentage threshold (default 40%)
            limit: Maximum voxels to return
            
        Returns:
            Dict with total_count, returned_count, voxels (ALL attributes)
        """
        
        count_query = """
        MATCH (v:Voxel)
        WHERE v.moisture_content > $threshold
        RETURN count(v) as total
        """
        
        count_result = self.execute_query(count_query, {'threshold': threshold})
        total_count = count_result[0]['total'] if count_result else 0
        
        query = """
        MATCH (v:Voxel)
        WHERE v.moisture_content > $threshold
        RETURN v
        LIMIT $limit
        """
        
        params = {
            'threshold': threshold,
            'limit': limit
        }
        
        results = self.execute_query(query, params)
        
        if not results:
            return {
                'total_count': total_count,
                'returned_count': 0,
                'voxels': []
            }
        
        voxels = []
        for record in results:
            voxel_dict = self._node_to_dict(record['v'])
            voxels.append(voxel_dict)
        
        return {
            'total_count': total_count,
            'returned_count': len(voxels),
            'voxels': voxels
        }
    
    def get_low_bearing_voxels_with_count(self, threshold=200.0, limit=5000):
        """
        Get voxels with low bearing capacity - RETURNS ALL ATTRIBUTES
        
        Args:
            threshold: Bearing capacity threshold in kPa (default 200)
            limit: Maximum voxels to return
            
        Returns:
            Dict with total_count, returned_count, voxels (ALL attributes)
        """
        
        count_query = """
        MATCH (v:Voxel)
        WHERE v.bearing_capacity < $threshold
        RETURN count(v) as total
        """
        
        count_result = self.execute_query(count_query, {'threshold': threshold})
        total_count = count_result[0]['total'] if count_result else 0
        
        query = """
        MATCH (v:Voxel)
        WHERE v.bearing_capacity < $threshold
        RETURN v
        LIMIT $limit
        """
        
        params = {
            'threshold': threshold,
            'limit': limit
        }
        
        results = self.execute_query(query, params)
        
        if not results:
            return {
                'total_count': total_count,
                'returned_count': 0,
                'voxels': []
            }
        
        voxels = []
        for record in results:
            voxel_dict = self._node_to_dict(record['v'])
            voxels.append(voxel_dict)
        
        return {
            'total_count': total_count,
            'returned_count': len(voxels),
            'voxels': voxels
        }
    
    def get_high_risk_voxels_with_count(self, limit=5000):
        """
        Get high risk voxels - RETURNS ALL ATTRIBUTES
        
        Args:
            limit: Maximum voxels to return
            
        Returns:
            Dict with total_count, returned_count, voxels (ALL attributes)
        """
        
        count_query = """
        MATCH (v:Voxel)
        WHERE v.overall_risk_level = 'High'
        RETURN count(v) as total
        """
        
        count_result = self.execute_query(count_query, {})
        total_count = count_result[0]['total'] if count_result else 0
        
        query = """
        MATCH (v:Voxel)
        WHERE v.overall_risk_level = 'High'
        RETURN v
        LIMIT $limit
        """
        
        params = {'limit': limit}
        
        results = self.execute_query(query, params)
        
        if not results:
            return {
                'total_count': total_count,
                'returned_count': 0,
                'voxels': []
            }
        
        voxels = []
        for record in results:
            voxel_dict = self._node_to_dict(record['v'])
            voxels.append(voxel_dict)
        
        return {
            'total_count': total_count,
            'returned_count': len(voxels),
            'voxels': voxels
        }
    
    def get_voxels_by_material_with_count(self, material, limit=5000):
        """
        Get voxels by material type - RETURNS ALL ATTRIBUTES
        
        Args:
            material: Material type (Clay, Sand, Silt, Gravel, Rock)
            limit: Maximum voxels to return
            
        Returns:
            Dict with total_count, returned_count, voxels (ALL attributes)
        """
        
        count_query = """
        MATCH (v:Voxel)
        WHERE v.material_type = $material
        RETURN count(v) as total
        """
        
        count_result = self.execute_query(count_query, {'material': material})
        total_count = count_result[0]['total'] if count_result else 0
        
        query = """
        MATCH (v:Voxel)
        WHERE v.material_type = $material
        RETURN v
        LIMIT $limit
        """
        
        params = {
            'material': material,
            'limit': limit
        }
        
        results = self.execute_query(query, params)
        
        if not results:
            return {
                'total_count': total_count,
                'returned_count': 0,
                'voxels': []
            }
        
        voxels = []
        for record in results:
            voxel_dict = self._node_to_dict(record['v'])
            voxels.append(voxel_dict)
        
        return {
            'total_count': total_count,
            'returned_count': len(voxels),
            'voxels': voxels
        }
    
    def get_voxels_multi_material(self, materials, limit=5000):
        """
        Get voxels matching multiple materials - RETURNS ALL ATTRIBUTES
        
        Args:
            materials: List of material types
            limit: Maximum voxels to return
            
        Returns:
            Dict with total_count, returned_count, voxels (ALL attributes)
        """
        
        if not materials:
            return {'total_count': 0, 'returned_count': 0, 'voxels': []}
        
        count_query = """
        MATCH (v:Voxel)
        WHERE v.material_type IN $materials
        RETURN count(v) as total
        """
        
        count_result = self.execute_query(count_query, {'materials': materials})
        total_count = count_result[0]['total'] if count_result else 0
        
        query = """
        MATCH (v:Voxel)
        WHERE v.material_type IN $materials
        RETURN v
        LIMIT $limit
        """
        
        params = {
            'materials': materials,
            'limit': limit
        }
        
        results = self.execute_query(query, params)
        
        if not results:
            return {
                'total_count': total_count,
                'returned_count': 0,
                'voxels': []
            }
        
        voxels = []
        for record in results:
            voxel_dict = self._node_to_dict(record['v'])
            voxels.append(voxel_dict)
        
        return {
            'total_count': total_count,
            'returned_count': len(voxels),
            'voxels': voxels
        }
    
    def get_voxels_multi_property(self, properties, logical_op='and', limit=5000):
        """
        Filter voxels by multiple properties - RETURNS ALL ATTRIBUTES
        
        Args:
            properties: List of (property, condition, value) tuples
            logical_op: 'and' or 'or'
            limit: Maximum voxels to return
            
        Returns:
            Dict with total_count, returned_count, voxels (ALL attributes)
        """
        
        if not properties:
            return {'total_count': 0, 'returned_count': 0, 'voxels': []}
        
        conditions = []
        params = {'limit': limit}
        
        for i, (prop, condition, value) in enumerate(properties):
            param_name = 'value' + str(i)
            params[param_name] = value
            
            if prop == 'moisture' or prop == 'moisture_content':
                if condition == 'high':
                    conditions.append('v.moisture_content > $' + param_name)
                elif condition == 'low':
                    conditions.append('v.moisture_content < $' + param_name)
            
            elif prop == 'bearing' or prop == 'bearing_capacity':
                if condition == 'high':
                    conditions.append('v.bearing_capacity > $' + param_name)
                elif condition == 'low':
                    conditions.append('v.bearing_capacity < $' + param_name)
            
            elif prop == 'risk' or prop == 'risk_level':
                conditions.append('v.overall_risk_level = $' + param_name)
        
        if not conditions:
            return {'total_count': 0, 'returned_count': 0, 'voxels': []}
        
        joiner = ' AND ' if logical_op.lower() == 'and' else ' OR '
        where_clause = joiner.join(conditions)
        
        count_query = """
        MATCH (v:Voxel)
        WHERE {}
        RETURN count(v) as total
        """.format(where_clause)
        
        count_result = self.execute_query(count_query, params)
        total_count = count_result[0]['total'] if count_result else 0
        
        query = """
        MATCH (v:Voxel)
        WHERE {}
        RETURN v
        LIMIT $limit
        """.format(where_clause)
        
        results = self.execute_query(query, params)
        
        if not results:
            return {
                'total_count': total_count,
                'returned_count': 0,
                'voxels': []
            }
        
        voxels = []
        for record in results:
            voxel_dict = self._node_to_dict(record['v'])
            voxels.append(voxel_dict)
        
        return {
            'total_count': total_count,
            'returned_count': len(voxels),
            'voxels': voxels
        }
    
    def get_voxels_range_query(self, property_name, operator, value, limit=5000):
        """
        Query voxels with range operators - RETURNS ALL ATTRIBUTES
        
        Args:
            property_name: Property to filter on
            operator: Comparison operator ('>', '<', '>=', '<=', '=')
            value: Threshold value
            limit: Maximum voxels to return
            
        Returns:
            Dict with total_count, returned_count, voxels (ALL attributes)
        """
        
        property_map = {
            'moisture': 'moisture_content',
            'moisture_content': 'moisture_content',
            'bearing': 'bearing_capacity',
            'bearing_capacity': 'bearing_capacity',
            'settlement': 'settlement_potential_mm',
            'settlement_potential': 'settlement_potential_mm'
        }
        
        db_property = property_map.get(property_name.lower(), property_name)
        
        count_query = """
        MATCH (v:Voxel)
        WHERE v.{} {} $value
        RETURN count(v) as total
        """.format(db_property, operator)
        
        count_result = self.execute_query(count_query, {'value': value})
        total_count = count_result[0]['total'] if count_result else 0
        
        query = """
        MATCH (v:Voxel)
        WHERE v.{} {} $value
        RETURN v
        LIMIT $limit
        """.format(db_property, operator)
        
        params = {
            'value': value,
            'limit': limit
        }
        
        results = self.execute_query(query, params)
        
        if not results:
            return {
                'total_count': total_count,
                'returned_count': 0,
                'voxels': []
            }
        
        voxels = []
        for record in results:
            voxel_dict = self._node_to_dict(record['v'])
            voxels.append(voxel_dict)
        
        return {
            'total_count': total_count,
            'returned_count': len(voxels),
            'voxels': voxels
        }
    
    def compare_materials(self, materials, limit=5000):
        """
        Compare multiple materials - RETURNS ALL ATTRIBUTES
        
        Args:
            materials: List of material types to compare
            limit: Maximum voxels per material
            
        Returns:
            Dict with comparison data and sample voxels (ALL attributes)
        """
        
        if not materials:
            return {
                'materials': [],
                'statistics': {},
                'sample_voxels': {}
            }
        
        result = {
            'materials': materials,
            'statistics': {},
            'sample_voxels': {}
        }
        
        for material in materials:
            stats_query = """
            MATCH (v:Voxel)
            WHERE v.material_type = $material
            RETURN count(v) as count,
                   avg(v.moisture_content) as avg_moisture,
                   avg(v.bearing_capacity) as avg_bearing,
                   min(v.moisture_content) as min_moisture,
                   max(v.moisture_content) as max_moisture,
                   min(v.bearing_capacity) as min_bearing,
                   max(v.bearing_capacity) as max_bearing
            """
            
            stats = self.execute_query(stats_query, {'material': material})
            
            if stats:
                result['statistics'][material] = dict(stats[0])
            
            sample_query = """
            MATCH (v:Voxel)
            WHERE v.material_type = $material
            RETURN v
            LIMIT $limit
            """
            
            samples = self.execute_query(sample_query, {'material': material, 'limit': limit})
            
            sample_voxels = []
            for record in samples:
                voxel_dict = self._node_to_dict(record['v'])
                sample_voxels.append(voxel_dict)
            
            result['sample_voxels'][material] = sample_voxels
        
        return result
    
    def get_neighbors_of_voxels(self, voxel_ids, hops=1, limit=5000):
        """
        Get neighboring voxels - RETURNS ALL ATTRIBUTES
        
        Args:
            voxel_ids: List of starting voxel IDs
            hops: Number of hops
            limit: Maximum voxels to return
            
        Returns:
            Dict with total_count, returned_count, voxels (ALL attributes)
        """
        
        if not voxel_ids:
            return {'total_count': 0, 'returned_count': 0, 'voxels': []}
        
        query = """
        MATCH (v:Voxel)-[:NEIGHBOR*1..{}]-(n:Voxel)
        WHERE v.voxel_id IN $voxel_ids AND n.voxel_id <> v.voxel_id
        RETURN DISTINCT n AS v
        LIMIT $limit
        """.format(hops)
        
        params = {
            'voxel_ids': voxel_ids,
            'limit': limit
        }
        
        results = self.execute_query(query, params)
        
        if not results:
            return {'total_count': 0, 'returned_count': 0, 'voxels': []}
        
        voxels = []
        for record in results:
            voxel_dict = self._node_to_dict(record['v'])
            voxels.append(voxel_dict)
        
        return {
            'total_count': len(voxels),
            'returned_count': len(voxels),
            'voxels': voxels
        }
    
    def get_voxels_within_distance(self, voxel_id, max_hops=2, limit=5000):
        """
        Get voxels within graph distance - RETURNS ALL ATTRIBUTES
        
        Args:
            voxel_id: Starting voxel ID
            max_hops: Maximum number of hops
            limit: Maximum voxels to return
            
        Returns:
            Dict with total_count, returned_count, voxels (ALL attributes)
        """
        
        if not voxel_id:
            return {'total_count': 0, 'returned_count': 0, 'voxels': []}
        
        query = """
        MATCH (start:Voxel {voxel_id: $voxel_id})
        MATCH (start)-[:NEIGHBOR*1..{}]-(v:Voxel)
        WHERE v.voxel_id <> start.voxel_id
        RETURN DISTINCT v
        LIMIT $limit
        """.format(max_hops)
        
        params = {
            'voxel_id': voxel_id,
            'limit': limit
        }
        
        results = self.execute_query(query, params)
        
        if not results:
            return {'total_count': 0, 'returned_count': 0, 'voxels': []}
        
        voxels = []
        for record in results:
            voxel_dict = self._node_to_dict(record['v'])
            voxels.append(voxel_dict)
        
        return {
            'total_count': len(voxels),
            'returned_count': len(voxels),
            'voxels': voxels
        }
    
    def expand_zone_from_seed(self, seed_voxel_id, property_name, threshold_similar=10.0, max_expansion=5000):
        """
        Expand zone from seed based on similar property values - RETURNS ALL ATTRIBUTES
        
        Args:
            seed_voxel_id: Starting voxel
            property_name: Property to check
            threshold_similar: Max difference for similarity
            max_expansion: Max voxels in zone
            
        Returns:
            Dict with zone voxels (ALL attributes)
        """
        
        seed_query = """
        MATCH (v:Voxel {voxel_id: $voxel_id})
        RETURN v.{} as seed_value
        """.format(property_name)
        
        seed_result = self.execute_query(seed_query, {'voxel_id': seed_voxel_id})
        
        if not seed_result:
            return {'total_count': 0, 'returned_count': 0, 'voxels': []}
        
        seed_value = seed_result[0]['seed_value']
        
        query = """
        MATCH (seed:Voxel {voxel_id: $voxel_id})
        MATCH (seed)-[:NEIGHBOR*1..3]-(v:Voxel)
        WHERE abs(v.{} - $seed_value) < $threshold
        RETURN DISTINCT v
        LIMIT $limit
        """.format(property_name)
        
        params = {
            'voxel_id': seed_voxel_id,
            'seed_value': seed_value,
            'threshold': threshold_similar,
            'limit': max_expansion
        }
        
        results = self.execute_query(query, params)
        
        if not results:
            return {'total_count': 0, 'returned_count': 0, 'voxels': []}
        
        voxels = []
        for record in results:
            voxel_dict = self._node_to_dict(record['v'])
            voxels.append(voxel_dict)
        
        return {
            'total_count': len(voxels),
            'returned_count': len(voxels),
            'voxels': voxels
        }
    
    def find_path_between_voxels(self, start_id, end_id, max_hops=10):
        """
        Find shortest path between two voxels - RETURNS ALL ATTRIBUTES
        
        Args:
            start_id: Starting voxel ID
            end_id: Ending voxel ID
            max_hops: Maximum path length
            
        Returns:
            Dict with path voxels (ALL attributes)
        """
        
        query = """
        MATCH path = shortestPath(
            (start:Voxel {voxel_id: $start_id})-[:NEIGHBOR*..{}]-(end:Voxel {voxel_id: $end_id})
        )
        UNWIND nodes(path) as v
        RETURN DISTINCT v
        """.format(max_hops)
        
        params = {
            'start_id': start_id,
            'end_id': end_id
        }
        
        results = self.execute_query(query, params)
        
        if not results:
            return {'total_count': 0, 'returned_count': 0, 'voxels': []}
        
        voxels = []
        for record in results:
            voxel_dict = self._node_to_dict(record['v'])
            voxels.append(voxel_dict)
        
        return {
            'total_count': len(voxels),
            'returned_count': len(voxels),
            'voxels': voxels
        }
    
    def get_connected_zones_by_property(self, property_name, operator, threshold, min_zone_size=5, limit=5000):
        """
        Find connected zones with similar property values - RETURNS ALL ATTRIBUTES
        
        Args:
            property_name: Property to check
            operator: Comparison operator
            threshold: Threshold value
            min_zone_size: Minimum voxels in a zone
            limit: Maximum voxels to return
            
        Returns:
            Dict with zones and voxels (ALL attributes)
        """
        
        query = """
        MATCH (v:Voxel)
        WHERE v.{} {} $threshold
        RETURN v
        LIMIT $limit
        """.format(property_name, operator)
        
        params = {
            'threshold': threshold,
            'limit': limit
        }
        
        results = self.execute_query(query, params)
        
        if not results:
            return {'zones': [], 'total_voxels': 0}
        
        voxels = []
        for record in results:
            voxel_dict = self._node_to_dict(record['v'])
            voxels.append(voxel_dict)
        
        zones = {}
        for v in voxels:
            layer = v.get('mass_id', 'Unknown')
            if layer not in zones:
                zones[layer] = []
            zones[layer].append(v)
        
        result_zones = []
        for layer, zone_voxels in zones.items():
            if len(zone_voxels) >= min_zone_size:
                result_zones.append({
                    'zone_id': layer,
                    'size': len(zone_voxels),
                    'voxels': zone_voxels
                })
        
        total_voxels = sum(z['size'] for z in result_zones)
        
        return {
            'zones': result_zones,
            'total_voxels': total_voxels
        }
    
    def get_voxels_by_surface(self, surface_id, position='top', limit=5000):
        """
        Get voxels bounded by a specific surface - RETURNS ALL ATTRIBUTES
        
        Args:
            surface_id: Surface ID (S1, S2, S3, S4, S5)
            position: 'top' or 'bottom' - which surface boundary
            limit: Maximum voxels to return
        
        Returns:
            Dict with total_count, returned_count, voxels (ALL attributes)
        """
        
        if position == 'top':
            property_name = 'top_surface_id'
        elif position == 'bottom':
            property_name = 'bottom_surface_id'
        else:
            property_name = 'top_surface_id'
        
        count_query = """
        MATCH (v:Voxel)
        WHERE v.{} = $surface_id
        RETURN count(v) as total
        """.format(property_name)
        
        count_result = self.execute_query(count_query, {'surface_id': surface_id})
        total_count = count_result[0]['total'] if count_result else 0
        
        query = """
        MATCH (v:Voxel)
        WHERE v.{} = $surface_id
        RETURN v
        LIMIT $limit
        """.format(property_name)
        
        params = {
            'surface_id': surface_id,
            'limit': limit
        }
        
        results = self.execute_query(query, params)
        
        if not results:
            return {
                'total_count': total_count,
                'returned_count': 0,
                'voxels': []
            }
        
        voxels = []
        for record in results:
            voxel_dict = self._node_to_dict(record['v'])
            voxels.append(voxel_dict)
        
        return {
            'total_count': total_count,
            'returned_count': len(voxels),
            'voxels': voxels
        }
    
    def compare_layers(self, layers, limit=5000):
        """
        Compare multiple geological layers - RETURNS ALL ATTRIBUTES
        
        Args:
            layers: List of layer IDs (M1, M2, M3, M4)
            limit: Maximum voxels per layer
        
        Returns:
            Dict with comparison data and sample voxels (ALL attributes)
        """
        
        if not layers:
            return {
                'layers': [],
                'statistics': {},
                'sample_voxels': {}
            }
        
        result = {
            'layers': layers,
            'statistics': {},
            'sample_voxels': {}
        }
        
        for layer in layers:
            stats_query = """
            MATCH (v:Voxel)
            WHERE v.mass_id = $layer
            RETURN count(v) as count,
                   avg(v.moisture_content) as avg_moisture,
                   avg(v.bearing_capacity) as avg_bearing,
                   avg(v.spt_n_value) as avg_spt,
                   min(v.moisture_content) as min_moisture,
                   max(v.moisture_content) as max_moisture,
                   min(v.bearing_capacity) as min_bearing,
                   max(v.bearing_capacity) as max_bearing
            """
            
            stats = self.execute_query(stats_query, {'layer': layer})
            
            if stats:
                result['statistics'][layer] = dict(stats[0])
            
            sample_query = """
            MATCH (v:Voxel)
            WHERE v.mass_id = $layer
            RETURN v
            LIMIT $limit
            """
            
            samples = self.execute_query(sample_query, {'layer': layer, 'limit': limit})
            
            sample_voxels = []
            for record in samples:
                voxel_dict = self._node_to_dict(record['v'])
                sample_voxels.append(voxel_dict)
            
            result['sample_voxels'][layer] = sample_voxels
        
        return result


if __name__ == "__main__":
    sys.path.append(r'C:\RhinoVoxelRAG')
    
    from config.neo4j_config import NEO4J_CONFIG
    
    print("\n" + "="*60)
    print("TESTING NEO4J CONNECTOR (ALL ATTRIBUTES + NEW METHODS)")
    print("="*60)
    
    connector = Neo4jConnector(
        uri=NEO4J_CONFIG['uri'],
        user=NEO4J_CONFIG['user'],
        password=NEO4J_CONFIG['password'],
        database=NEO4J_CONFIG.get('database', 'neo4j')
    )
    
    if connector.test_connection():
        print("\n✅ Connection successful!")
        
        print("\n" + "-"*60)
        print("TEST: Get voxel by ID (ALL attributes)")
        print("-"*60)
        result = connector.get_voxels_by_ids(['v_M4_02351'], limit=1)
        
        if result['voxels']:
            voxel = result['voxels'][0]
            print("Voxel ID:", voxel.get('voxel_id'))
            print("Attributes found:", len(voxel))
            print("\nSample attributes:")
            for key in list(voxel.keys())[:10]:
                print("  {}: {}".format(key, voxel[key]))
        
        print("\n" + "-"*60)
        print("TEST: Get voxels by surface S3")
        print("-"*60)
        result = connector.get_voxels_by_surface('S3', 'top', limit=5)
        print("Found {} voxels with top_surface_id = S3".format(result['total_count']))
        
        print("\n" + "-"*60)
        print("TEST: Compare layers M3 and M4")
        print("-"*60)
        result = connector.compare_layers(['M3', 'M4'], limit=5)
        print("Layers compared:", result['layers'])
        for layer in result['layers']:
            if layer in result['statistics']:
                print("{}: {} voxels".format(layer, result['statistics'][layer].get('count', 0)))
    
    connector.close()