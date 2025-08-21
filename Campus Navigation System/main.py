import sys
from collections import defaultdict
import heapq
import googlemaps
import folium
from datetime import datetime
import polyline
import os
from dotenv import load_dotenv
import requests
import time

class CampusNavigationSystem:
    def __init__(self, google_api_key=None):
        """Initialize the navigation system with Google Maps API integration"""
        self.locations = {}  # Dictionary to store location names and their coordinates
        self.graph = defaultdict(list)  
        self.distances = {}  # Dictionary to store distances between locations
        
        # Initialize Google Maps client if API key is provided
        self.gmaps = None
        if google_api_key:
            self.gmaps = googlemaps.Client(key=google_api_key)
            
    def add_location(self, name, latitude, longitude):
        """Add a new location to the system"""
        self.locations[name] = (latitude, longitude)
        
    def get_google_distance(self, source, destination, mode="walking"):
        """Get distance and duration from Google Maps API"""
        if not self.gmaps:
            raise ValueError("Google Maps API key not provided")
            
        source_coords = self.locations[source]
        dest_coords = self.locations[destination]
        
        result = self.gmaps.distance_matrix(
            origins=[f"{source_coords[0]},{source_coords[1]}"],
            destinations=[f"{dest_coords[0]},{dest_coords[1]}"],
            mode=mode,
            departure_time=datetime.now()
        )
        
        if result['status'] == 'OK':
            element = result['rows'][0]['elements'][0]
            if element['status'] == 'OK':
                return {
                    'distance': element['distance']['value'],  # in meters
                    'duration': element['duration']['value'],  # in seconds
                    'duration_text': element['duration']['text']
                }
        return None
        
    def get_path_coordinates(self, source, destination, mode="walking"):
        """Get detailed path coordinates from Google Maps Directions API"""
        if not self.gmaps:
            raise ValueError("Google Maps API key not provided")
            
        source_coords = self.locations[source]
        dest_coords = self.locations[destination]
        
        directions = self.gmaps.directions(
            origin=f"{source_coords[0]},{source_coords[1]}",
            destination=f"{dest_coords[0]},{dest_coords[1]}",
            mode=mode,
            departure_time=datetime.now()
        )
        
        if directions:
            # Extract the polyline points from the response
            polyline_points = directions[0]['overview_polyline']['points']
            path_coords = polyline.decode(polyline_points)
            return path_coords
        return None

    def add_path_with_google_distance(self, source, destination, mode="walking", bidirectional=True):
        """Add a path between locations using Google Maps distance"""
        result = self.get_google_distance(source, destination, mode)
        if result:
            distance = result['distance']
            self.add_path(source, destination, distance, bidirectional)
            return result
        return None

    def visualize_map(self, path=None, mode="walking"):
        """Create an interactive map visualization using Folium"""
        lats = [coord[0] for coord in self.locations.values()]
        lons = [coord[1] for coord in self.locations.values()]
        center_lat = sum(lats) / len(lats)
        center_lon = sum(lons) / len(lons)
        

        campus_map = folium.Map(location=[center_lat, center_lon], zoom_start=16)

        for name, coords in self.locations.items():
            folium.Marker(
                coords,
                popup=name,
                icon=folium.Icon(color='red', icon='info-sign')
            ).add_to(campus_map)
        
    
        if path and len(path) >= 2:
            # Get coordinates for the path
            path_coords = []
            for i in range(len(path) - 1):
                coords = self.get_path_coordinates(path[i], path[i + 1], mode)
                if coords:
                    path_coords.extend(coords)
            
            if path_coords:
                # Draw the path line
                folium.PolyLine(
                    path_coords,
                    weight=3,
                    color='blue',
                    opacity=0.8
                ).add_to(campus_map)
        
        return campus_map

    # [Previous methods remain the same: floyd_warshall, dijkstra, _build_path, etc.]
    
    def get_shortest_path_with_visualization(self, source, destination, algorithm='dijkstra', mode="walking"):
        """Get the shortest path and create a visualization"""
     
        result = self.get_shortest_path(source, destination, algorithm)
        
   
        map_viz = self.visualize_map(result['path'], mode)
        
        # Get additional information from Google Maps
        google_info = self.get_google_distance(source, destination, mode)
        
        return {
            'path': result['path'],
            'distance': result['distance'],
            'algorithm': result['algorithm'],
            'map': map_viz,
            'google_duration': google_info['duration_text'] if google_info else None
        }


    def floyd_warshall(self):
        """Implement Floyd-Warshall algorithm for APSP"""
        vertices = list(self.locations.keys())
        n = len(vertices)
        dist = [[float('inf')] * n for _ in range(n)]
        next_vertex = [[None] * n for _ in range(n)]
        
        for i in range(n):
            dist[i][i] = 0
            for dest, weight in self.graph[vertices[i]]:
                j = vertices.index(dest)
                dist[i][j] = weight
                next_vertex[i][j] = j
                
        # Floyd-Warshall algorithm
        for k in range(n):
            for i in range(n):
                for j in range(n):
                    if dist[i][k] + dist[k][j] < dist[i][j]:
                        dist[i][j] = dist[i][k] + dist[k][j]
                        next_vertex[i][j] = next_vertex[i][k]
                        
        return dist, next_vertex, vertices
    
    def dijkstra(self, source, destination):
        """Implement Dijkstra's algorithm for single-source shortest path"""
        distances = {loc: float('inf') for loc in self.locations}
        distances[source] = 0
        pq = [(0, source)]
        previous = {loc: None for loc in self.locations}
        
        while pq:
            current_distance, current_vertex = heapq.heappop(pq)
            
            if current_vertex == destination:
                break
                
            if current_distance > distances[current_vertex]:
                continue
                
            for neighbor, weight in self.graph[current_vertex]:
                distance = current_distance + weight
                
                if distance < distances[neighbor]:
                    distances[neighbor] = distance
                    previous[neighbor] = current_vertex
                    heapq.heappush(pq, (distance, neighbor))
                    
        return self._build_path(source, destination, previous), distances[destination]
    
    def _build_path(self, source, destination, previous):
        """Helper function to build the path from source to destination"""
        path = []
        current = destination
        
        while current is not None:
            path.append(current)
            current = previous[current]
            
        return list(reversed(path))
    
    def get_shortest_path(self, source, destination, algorithm='dijkstra'):
        """Get the shortest path between two locations using specified algorithm"""
        if algorithm == 'dijkstra':
            path, distance = self.dijkstra(source, destination)
            return {
                'path': path,
                'distance': distance,
                'algorithm': 'Dijkstra'
            }
        elif algorithm == 'floyd-warshall':
            dist, next_vertex, vertices = self.floyd_warshall()
            i = vertices.index(source)
            j = vertices.index(destination)
            
            path = []
            current = i
            while current != j:
                path.append(vertices[current])
                current = next_vertex[current][j]
            path.append(vertices[j])
            
            return {
                'path': path,
                'distance': dist[i][j],
                'algorithm': 'Floyd-Warshall'
            }
        else:
            raise ValueError("Unsupported algorithm. Use 'dijkstra' or 'floyd-warshall'")
    def add_path(self, source, destination, distance, bidirectional=True):
        """Add a path between two locations with given distance"""
        if source not in self.locations or destination not in self.locations:
            raise ValueError("Both source and destination must be added as locations first")
            
        self.graph[source].append((destination, distance))
        self.distances[(source, destination)] = distance
        
        if bidirectional:
            self.graph[destination].append((source, distance))
            self.distances[(destination, source)] = distance

    def visualize_map(self, path=None, mode="walking"):
        """Create an interactive map visualization using Folium"""
        # Find center point of all locations
        lats = [coord[0] for coord in self.locations.values()]
        lons = [coord[1] for coord in self.locations.values()]
        center_lat = sum(lats) / len(lats)
        center_lon = sum(lons) / len(lons)
        
        # Create the base map
        campus_map = folium.Map(location=[center_lat, center_lon], zoom_start=16)
        
        # Add markers for all locations with different colors for start/end
        for i, (name, coords) in enumerate(self.locations.items()):
            color = 'red'  # default color
            if path:
                if name == path[0]:  # Start point
                    color = 'green'
                elif name == path[-1]:  # End point
                    color = 'red'
                elif name in path:  # Intermediate points
                    color = 'orange'
                    
            folium.Marker(
                coords,
                popup=name,
                icon=folium.Icon(color=color, icon='info-sign')
            ).add_to(campus_map)
        
        # If a path is provided, visualize it
        if path and len(path) >= 2:
            try:
                # Get coordinates for the path
                path_coords = []
                for i in range(len(path) - 1):
                    coords = self.get_path_coordinates(path[i], path[i + 1], mode)
                    if coords:
                        # Add a small delay between API calls to avoid rate limiting
                        if i > 0:
                            time.sleep(0.5)
                        path_coords.extend(coords)
                
                if path_coords:
                    # Draw the path line
                    folium.PolyLine(
                        path_coords,
                        weight=3,
                        color='blue',
                        opacity=0.8,
                        popup='Route'
                    ).add_to(campus_map)
            except Exception as e:
                print(f"Warning: Could not visualize path due to: {str(e)}")
        
        return campus_map

    def get_shortest_path_with_visualization(self, source, destination, algorithm='dijkstra', mode="walking"):
        """Get the shortest path and create a visualization"""
        try:
            # Get the path using the specified algorithm
            result = self.get_shortest_path(source, destination, algorithm)
            
            # Create the visualization
            map_viz = self.visualize_map(result['path'], mode)
            
            # Get additional information from Google Maps
            google_info = self.get_google_distance(source, destination, mode)
            
            return {
                'path': result['path'],
                'distance': result['distance'],
                'algorithm': result['algorithm'],
                'map': map_viz,
                'google_duration': google_info['duration_text'] if google_info else None
            }
        except Exception as e:
            print(f"Error getting shortest path: {str(e)}")
            return None

# Example usage
def main():
    # Load environment variables
    load_dotenv()
    
    # Get Google Maps API key from environment variable
    google_api_key = os.getenv('GOOGLE_MAPS_API_KEY')
    if not google_api_key:
        raise ValueError("Please set GOOGLE_MAPS_API_KEY environment variable")
    
    # Create navigation system with Google Maps integration
    nav = CampusNavigationSystem(google_api_key=google_api_key)
    
    nav.add_location("Library", 12.84110599237612, 80.15400444094736)
    nav.add_location("AB1", 12.843796745138429, 80.15343701194637)
    nav.add_location("AB3", 12.843657497393256, 80.15461098415642)
    nav.add_location("Sports Complex", 12.842119747419215, 80.15497014400945)
    nav.add_location("C-Block", 12.842861329573648, 80.15737319822169)
    
    # Add paths with real distances from Google Maps
    for source, dest in [
        ("Library", "AB1"),
        ("AB1", "AB3"),
        ("AB3", "Sports Complex"),
        ("Sports Complex", "C-Block"),
        ("Library", "AB3"),
        ("AB1", "C-Block")
    ]:
        nav.add_path_with_google_distance(source, dest)
    
    # Find and visualize shortest path
    result = nav.get_shortest_path_with_visualization(
        "Library",
        "C-Block",
        algorithm='dijkstra',
        mode="walking"
    )
    
    # Save the map visualization
    result['map'].save("campus_navigation.html")
    
    # Print results
    print("\nNavigation Results:")
    print(f"Path: {' -> '.join(result['path'])}")
    print(f"Total Distance: {result['distance']} meters")
    print(f"Walking Duration: {result['google_duration']}")
    print(f"Map visualization saved as 'campus_navigation.html'")

if __name__ == "__main__":
    main()