import streamlit as st
import geopandas as gpd
import matplotlib.pyplot as plt
from shapely.geometry import Polygon, LineString, MultiPolygon
import zipfile
import os
import tempfile

# Function to calculate side lengths of a polygon
def calculate_side_lengths(polygon):
    sides = []
    coords = list(polygon.exterior.coords)
    for i in range(len(coords) - 1):
        line = LineString([coords[i], coords[i + 1]])
        sides.append(line.length)
    return sides

# Function to add north arrow to the plot
def add_north_arrow(ax, x=0.95, y=0.95, length=0.1):
    ax.annotate('N', xy=(x, y), xytext=(x, y - length),
                arrowprops=dict(facecolor='black', shrink=0.05),
                ha='center', va='center', fontsize=12, xycoords=ax.transAxes)

# Function to plot polygon with side lengths and area
def plot_polygon_with_details(polygon, title):
    fig, ax = plt.subplots()
    x, y = polygon.exterior.xy
    ax.fill(x, y, alpha=0.2, fc='r', ec='none')

    # Plot side lengths
    sides = calculate_side_lengths(polygon)
    coords = list(polygon.exterior.coords)
    for i in range(len(sides)):
        mid_x = (coords[i][0] + coords[i + 1][0]) / 2
        mid_y = (coords[i][1] + coords[i + 1][1]) / 2
        ax.text(mid_x, mid_y, f'{sides[i]:.2f} m', fontsize=9, ha='center')

    # Plot area
    area = polygon.area
    centroid = polygon.centroid
    ax.text(centroid.x, centroid.y, f'Area: {area:.2f} sq.m', fontsize=12, ha='center')

    # Add north arrow
    add_north_arrow(ax)

    # Set title and labels
    ax.set_title(title)
    ax.set_xlabel('Longitude')
    ax.set_ylabel('Latitude')

    # Show lat/lon grid
    ax.grid(True)

    # Display the plot
    st.pyplot(fig)

# Streamlit app
st.title("Polygon Layout Generator")

# File uploader for zipped shapefile
uploaded_file = st.file_uploader("Upload a zipped shapefile", type="zip")

if uploaded_file is not None:
    # Extract the zipped shapefile
    with tempfile.TemporaryDirectory() as tmpdirname:
        with zipfile.ZipFile(uploaded_file, 'r') as zip_ref:
            zip_ref.extractall(tmpdirname)
        
        # Find the shapefile within the extracted files
        shapefile_path = None
        for root, dirs, files in os.walk(tmpdirname):
            for file in files:
                if file.endswith(".shp"):
                    shapefile_path = os.path.join(root, file)
                    break
        
        if shapefile_path is None:
            st.error("No shapefile (.shp) found in the uploaded zip file.")
        else:
            # Read the shapefile
            gdf = gpd.read_file(shapefile_path)
            
            # Reproject to a suitable projected CRS (e.g., UTM)
            gdf = gdf.to_crs(epsg=32633)  # UTM zone 33N as an example; choose appropriate UTM zone

            # Process each polygon in the GeoDataFrame
            for idx, row in gdf.iterrows():
                if isinstance(row.geometry, Polygon):
                    title = row['Bhugwatdar'] if 'Bhugwatdar' in row else f'Polygon {idx + 1}'
                    plot_polygon_with_details(row.geometry, title)
                elif isinstance(row.geometry, MultiPolygon):
                    for polygon in row.geometry:
                        title = row['Bhugwatdar'] if 'Bhugwatdar' in row else f'Polygon {idx + 1}'
                        plot_polygon_with_details(polygon, title)
