# Campus Navigation System

## Overview

A Python-based **Campus Navigation System** that helps users find the
shortest path between locations on campus. It integrates with **Google
Maps API** for real distances, durations, and path visualization, while
also supporting algorithms like **Dijkstra** and **Floyd-Warshall**. The
system generates an interactive **map visualization using Folium**.

## Features

-   Add and manage campus locations with latitude/longitude.
-   Fetch real-time walking distances and durations via **Google Maps
    Distance Matrix API**.
-   Retrieve detailed path coordinates via **Google Maps Directions
    API**.
-   Compute shortest paths using:
    -   Dijkstra's Algorithm
    -   Floyd-Warshall Algorithm
-   Generate interactive map visualizations with routes and markers.
-   Save the generated map as an HTML file.

## Requirements

-   Python 3.8+

-   Libraries:

    ``` bash
    pip install googlemaps folium python-dotenv requests polyline
    ```

-   A valid **Google Maps API Key** with:

    -   Distance Matrix API enabled
    -   Directions API enabled

## Setup

1.  Clone or download the repository.

2.  Install dependencies:

    ``` bash
    pip install -r requirements.txt
    ```

3.  Create a `.env` file in the project root:

        GOOGLE_MAPS_API_KEY=your_api_key_here

4.  Run the script:

    ``` bash
    python main.py
    ```

## Output

-   Prints:
    -   Shortest path
    -   Distance in meters
    -   Estimated walking duration
-   Saves:
    -   `campus_navigation.html` → Interactive map with route and
        markers

## Example

Locations in the example: - Library - AB1 - AB3 - Sports Complex -
C-Block

Sample Output:

    Navigation Results:
    Path: Library -> AB1 -> C-Block
    Total Distance: 450 meters
    Walking Duration: 6 mins
    Map visualization saved as 'campus_navigation.html'



<img width="1133" height="869" alt="image" src="https://github.com/user-attachments/assets/fa1baa3d-1cf7-4b07-ba05-12cc7753d0c5" />


## File Structure

    .
    ├── main.py               # Main project file
    ├── .env                  # Environment variables (API key)
    ├── requirements.txt       # Python dependencies
    └── README.md              # Documentation
