import geopandas as gpd
import pandas as pd
import streamlit as st
import tempfile
import os
import zipfile
from openai import OpenAI
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from dotenv import load_dotenv
import base64

# Load the .env file
load_dotenv()

# Configure the Streamlit app
st.set_page_config(page_title="Shapefile Viewer", layout="wide")
st.title("Shapefile Viewer")

# Initialize session state for GeoDataFrame if not exists
if 'gdf' not in st.session_state:
    st.session_state.gdf = None

# Get the OpenAI API key from environment variables
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    st.error("OpenAI API key not found. Please add it to the .env file.")

# Create two columns for layout
col1, col2 = st.columns(2)

# Sidebar controls
def add_square(color):
    st.sidebar.markdown(
        f"<div style='width: 20px; height: 20px; background-color: {color};'></div>",
        unsafe_allow_html=True
    )

# Add threshold controls to sidebar
st.sidebar.header("Threshold Controls")
add_square("green")
green = st.sidebar.number_input('Green threshold (lower bound)', value=5, min_value=0, max_value=100)

add_square("yellow")
yellow = st.sidebar.number_input('Yellow threshold', value=19, min_value=green, max_value=100)

add_square("orange")
orange = st.sidebar.number_input('Orange threshold', value=39, min_value=yellow, max_value=100)

add_square("red")
red = st.sidebar.number_input("Red threshold", value=59, min_value=orange, max_value=100)

def encode_image_to_base64(image_path):
    """Encode an image to base64."""
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode("utf-8")

def analyze_image_with_gpt(prompt, image_path):
    """Analyze image using GPT-4 Vision."""
    try:
        client = OpenAI(api_key=api_key)
        
        # Read and encode the image
        with open(image_path, "rb") as image_file:
            base64_image = base64.b64encode(image_file.read()).decode('utf-8')
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # Correct model name for GPT-4 Vision
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}",
                                "detail": "high"  # Request high detail analysis
                            }
                        }
                    ]
                }
            ],
            max_tokens=500  # Increased token limit for more detailed analysis
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        st.error(f"Error in image analysis: {str(e)}")
        return "Failed to analyze the image. Please check your OpenAI API key and try again."

def get_color(value):
    """Determine color based on value and thresholds."""
    if value < green:
        return 'green'
    elif value < yellow:
        return 'yellow'
    elif value < orange:
        return 'orange'
    elif value < red:
        return 'red'
    else:
        return 'gray'

# File upload and processing
with col2:
    uploaded_file = st.file_uploader("Upload a Shapefile (.zip)", type=["zip"])
    
    if uploaded_file:
        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                with zipfile.ZipFile(uploaded_file, "r") as z:
                    z.extractall(tmpdir)
                
                shp_files = [f for f in os.listdir(tmpdir) if f.endswith(".shp")]
                if not shp_files:
                    st.error("No .shp file found in the uploaded zip.")
                else:
                    filepath = os.path.join(tmpdir, shp_files[0])
                    st.session_state.gdf = gpd.read_file(filepath)
                    
                    column_t1 = st.selectbox(
                        "Select Shapefile column name:",
                        options=st.session_state.gdf.columns
                    )
                    
                    if 'data' not in st.session_state.gdf.columns:
                        st.session_state.gdf['data'] = 0
                    
                    # Data editor
                    edited_data = st.data_editor(
                        st.session_state.gdf[[column_t1, 'data']],
                        disabled=[column_t1],
                        num_rows='fixed'
                    )
                    
                    # Update GeoDataFrame with edited data
                    st.session_state.gdf['data'] = edited_data['data']
        
        except Exception as e:
            st.error(f"Error processing Shapefile: {str(e)}")
    else:
        st.info("Please upload a valid .zip file containing a .shp file.")

# Map visualization
with col1:
    if st.session_state.gdf is not None:
        # Generate map
        st.session_state.gdf['color'] = st.session_state.gdf['data'].apply(get_color)
        
        # Ensure proper CRS
        if not st.session_state.gdf.crs:
            st.warning("No CRS found. Assuming WGS84.")
            st.session_state.gdf.set_crs("EPSG:4326", inplace=True)
        
        # Convert to Web Mercator for display
        display_gdf = st.session_state.gdf.to_crs(epsg=3857)
        display_gdf['centroid'] = display_gdf.geometry.centroid
        
        # Create the map
        fig, ax = plt.subplots(figsize=(12, 12))  # Adjust figure size for better resolution
        display_gdf.plot(ax=ax, color=display_gdf['color'], edgecolor='black')
        
        # Add annotations
        for idx, row in display_gdf.iterrows():
            ax.annotate(
                text=f"{row[column_t1]}\n{row['data']}%",
                xy=(row.centroid.x, row.centroid.y),
                ha='center',
                size=8
            )
        
        # Customize map appearance
        ax.set_title("Shapefile Data Visualization", fontsize=16, weight='bold')
        ax.set_xticks([])
        ax.set_yticks([])
        
        # Add legend
        legend_elements = [
            Patch(facecolor='green', edgecolor='black', label=f'< {green}%'),
            Patch(facecolor='yellow', edgecolor='black', label=f'{green} - {yellow}%'),
            Patch(facecolor='orange', edgecolor='black', label=f'{yellow} - {orange}%'),
            Patch(facecolor='red', edgecolor='black', label=f'{orange} - {red}%'),
            Patch(facecolor='gray', edgecolor='black', label=f'Other')
        ]
        ax.legend(handles=legend_elements, title='Percentage', loc='lower right', fontsize=10)
        
        # Save the map at high resolution (scaled to fit 2048x2048 square)
        fig_width, fig_height = fig.get_size_inches()
        dpi = max(2048 / (fig_width * 100), 2048 / (fig_height * 100)) * 100  # Scale DPI for 2048px output
        plt.savefig("high_res_map.jpg", dpi=dpi, bbox_inches='tight')  # Save with adjusted DPI
        
        # Display the map
        st.pyplot(fig)
        
        # Close the plot to free memory
        plt.close()
        
        # Analysis section
        st.header("Image Analysis")
        analysis_prompt = """
        Analyze the health data map visualization and provide specific, actionable recommendations for improvement:

Converting yellow regions to green: Suggest targeted interventions or programs to enhance health outcomes in these regions.
Improving red regions to orange: Propose immediate, practical actions to address the most critical health challenges in these areas.
Moving orange regions to yellow: Recommend strategies for gradual and sustainable improvements in these regions.
Consider geographic clusters, regional patterns, and potential correlations between areas. Incorporate recent government interventions at the state level into your analysis, identifying how they can be optimized or expanded. Ensure the response is concise (200 words) and focused on practical solutions.
        """
        
        if st.button("Analyze Map"):
            with st.spinner("Analyzing map data..."):
                try:
                    analysis_result = analyze_image_with_gpt(analysis_prompt, "high_res_map.jpg")
                    st.write("Analysis Results:")
                    st.write(analysis_result)
                except Exception as e:
                    st.error(f"Error during analysis: {str(e)}")
                    st.info("Please ensure your OpenAI API key has access to GPT-4 Vision API")




# It costs around 