import geopandas as gpd
import pandas as pd
import streamlit as st
import tempfile
import os
import zipfile
import openai
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from dotenv import load_dotenv
import base64

# Load the .env file
load_dotenv()

# Configure the Streamlit app
st.set_page_config(page_title="Shapefile Viewer", layout="wide")
st.title("Shapefile Viewer")
col1, col2 = st.columns(2)

# Fetch the OpenAI API key from environment variables
openai.api_key = os.getenv("OPENAI_API_KEY")
if not openai.api_key:
    st.error("OpenAI API key not found. Please add it to the .env file.")

# Function to create a square for the legend in the sidebar
def add_square(color):
    st.sidebar.markdown(
        f"<div style='width: 20px; height: 20px; background-color: {color};'></div>",
        unsafe_allow_html=True
    )

# Add squares and sliders for thresholds
add_square("green")
green = st.sidebar.number_input('Select a range of values for Green', value=5, min_value=0, max_value=100)

add_square("yellow")
yellow = st.sidebar.number_input('Select a range of values for Yellow', value=19, min_value=int(green), max_value=100)

add_square("orange")
orange = st.sidebar.number_input('Select a range of values for Orange', value=39, min_value=int(yellow), max_value=100)

add_square("red")
red = st.sidebar.number_input("Select a range of values for Red", value=59, min_value=int(orange), max_value=100)

if "rerun_trigger" not in st.session_state:
    st.session_state.rerun_trigger = False

# Function to encode an image to base64 format
def encode_image_to_base64(image_path):
    """Encode an image to base64."""
    with open(image_path, "rb") as img_file:
        encoded_string = base64.b64encode(img_file.read()).decode("utf-8")
    return encoded_string

# Function to analyze the image using GPT-4
def analyze_image_with_gpt(prompt, image_path):
    """Send an analysis prompt to OpenAI GPT for the map image."""
    image_base64 = encode_image_to_base64(image_path)

    # Sending request to GPT with the image base64 and prompt
    response = openai.Completion.create(
        model="gpt-4",
        prompt=f"Analyze this map data based on the following prompt: {prompt}",
        max_tokens=1000,  # Adjust as needed
        n=1,
        stop=None,
        temperature=0.7,
        # Add image base64 if GPT-4 model accepts image data
        images=[{"data": image_base64}],
    )
    return response['choices'][0]['text']

with col1:
    pass

with col2:
    # File uploader for Shapefiles (only zip files allowed)
    uploaded_file = st.file_uploader("Upload a Shapefile (.zip)", type=["zip"])
    if uploaded_file:
        try:
            # Handle zipped Shapefile upload only
            if uploaded_file.name.endswith(".zip"):
                with tempfile.TemporaryDirectory() as tmpdir:
                    with zipfile.ZipFile(uploaded_file, "r") as z:
                        z.extractall(tmpdir)

                    # Find the .shp file in the zip
                    shp_files = [f for f in os.listdir(tmpdir) if f.endswith(".shp")]
                    if not shp_files:
                        st.error("No .shp file found in the uploaded zip.")
                    else:
                        filepath = os.path.join(tmpdir, shp_files[0])
                        gdf = gpd.read_file(filepath)

            else:
                st.error("Unsupported file format. Please upload a .zip file containing a .shp file.")

            column_t1 = st.selectbox("Select Shapefile column name:", tuple(gdf.columns))
            gdf['data'] = 0
            original_geometry = gdf.geometry
            original_crs = gdf.crs

            # Allow user interaction to edit the 'data' column
            edited_data = st.data_editor(
                gdf[[column_t1, 'data']],
                disabled=[column_t1], num_rows='fixed'
            )

            # Update the GeoDataFrame
            gdf = gpd.GeoDataFrame(
                edited_data,
                geometry=original_geometry,
                crs=original_crs
            )

            if not st.session_state.rerun_trigger and gdf["data"].any():
                st.session_state.rerun_trigger = True
                st.rerun()

        except Exception as e:
            st.error(f"An error occurred while processing the Shapefile: {e}")
    else:
        st.info("Please upload a valid .zip file containing a .shp file.")

# Function to determine color based on value
def get_color(value):
    if value < green:
        return 'green'
    elif green <= value < yellow:
        return 'yellow'
    elif yellow <= value < orange:
        return 'orange'
    elif orange <= value < red:
        return 'red'
    else:
        return 'gray'

with col1:
    if uploaded_file:
        # Generate the map with annotations
        gdf['color'] = gdf['data'].apply(get_color)

        if not gdf.crs:
            st.warning("No CRS found. Assuming WGS84.")
            gdf.set_crs("EPSG:4326")
        elif gdf.crs != "EPSG:4326":
            gdf = gdf.to_crs("EPSG:4326")

        gdf = gdf.to_crs(epsg=3857)
        gdf['centroid'] = gdf.geometry.centroid
        gdf['centroid_x'] = gdf.centroid.x
        gdf['centroid_y'] = gdf.centroid.y

        # Plot the map
        fig, ax = plt.subplots(figsize=(10, 8))
        gdf.plot(ax=ax, color=gdf['color'], edgecolor='black')
        gdf.apply(lambda x: ax.annotate(
            text=f"{x[column_t1]}\n{x['data']}%", 
            xy=(x['centroid_x'], x['centroid_y']),
            ha='center', size=8), axis=1)

        # Add a title to the map
        ax.set_title("Shapefile Data Visualization", fontsize=16, weight='bold')

        legend_elements = [
            Patch(facecolor='green', edgecolor='black', label=f'< {green}%'),
            Patch(facecolor='yellow', edgecolor='black', label=f'{green} - {yellow}%'),
            Patch(facecolor='orange', edgecolor='black', label=f'{yellow} - {orange}%'),
            Patch(facecolor='red', edgecolor='black', label=f'{orange} - {red}%'),
            Patch(facecolor='gray', edgecolor='black', label='Other')
        ]
        ax.legend(handles=legend_elements, title='Percentage', loc='lower right', fontsize=10)
        ax.set_xticks([])
        ax.set_yticks([])

        st.pyplot(fig)
        map_image_path = "Map.jpg"
        plt.savefig(map_image_path, dpi=500)

    # Data Summary
    # st.header("Data Summary")
    # summary = gdf['data'].describe()
    # st.write(summary)

    # Image Analysis and Recommendations
    st.header("Image Analysis")
    analysis_prompt = """
        "Please analyze the health data map and help with the following tasks:
            How can we turn the yellow regions into green? What actions can be taken to improve these areas and bring them closer to the goal (green)?
            For the red regions, which are the most concerning, how can we reduce the values and move them to the orange range? What steps can we take to improve these areas?
            What can be done to help the regions in orange move to yellow? What changes or actions are needed to make these regions less concerning?
            The goal is to get as many regions as possible into the green zone, where lower values are better for health."
        """
    analyze_bt = st.button("Analyze the Map")
if analyze_bt:
    if analysis_prompt:
        # Analyze the image using ChatGPT
        try:
            analysis_result = analyze_image_with_gpt(analysis_prompt, map_image_path)
            st.write("Analysis Result:")
            st.write(analysis_result)

            # Recommendations
            st.header("Recommended Actions")
            st.write("1. Increase resources in regions highlighted in red.")
            st.write("2. Conduct detailed studies in orange regions to identify potential improvement areas.")
            st.write("3. Maintain performance in green and yellow regions.")

            # Option to rerun with new inputs
            if st.button("Rerun Analysis"):
                st.session_state.rerun_trigger = True
                st.rerun()

        except Exception as e:
            st.error(f"An error occurred during image analysis: {e}")
