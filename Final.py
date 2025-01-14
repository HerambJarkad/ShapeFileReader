import geopandas as gpd
import pandas as pd
import streamlit as st
import tempfile
import os
import zipfile
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
# Title of the app
st.set_page_config(page_title="ShapeFile Viewer",layout="wide")
st.title("Shapefile Viewer")
col1, col2 = st.columns(2)
# Function to create a square
def add_square(color):
    st.sidebar.markdown(
        f"<div style='width: 20px; height: 20px; background-color: {color};'></div>",
        unsafe_allow_html=True
    )

# Add squares and sliders
add_square("green")
green = st.sidebar.number_input(
    'Select a range of values for Green',
    value=5,min_value=0,max_value=100)

add_square("yellow")
yellow = st.sidebar.number_input(
    'Select a range of values for Yellow',
    value=19,min_value=int(green), max_value=100,
)

add_square("orange")
orange = st.sidebar.number_input(
    'Select a range of values for Orange',
    value=39,min_value=int(yellow), max_value=100,
)

add_square("red")
red = st.sidebar.number_input(
    "Select a range of values for Red",
    value=59,min_value=int(orange), max_value=100,
)


if "rerun_trigger" not in st.session_state:
    st.session_state.rerun_trigger = False

with col1:
    pass
with col2:
    # File uploader Shape File-------------------------------------------------------------------1

    uploaded_file = st.file_uploader("Upload a Shapefile (.zip)", type=["zip"])
    if (uploaded_file):
        try:
            # Temporary directory for handling files
            with tempfile.TemporaryDirectory() as tmpdir:
                # Handling zipped Shapefiles
                with zipfile.ZipFile(uploaded_file, "r") as z:
                    z.extractall(tmpdir)
                # Find the .shp file
                shp_files = [f for f in os.listdir(tmpdir) if f.endswith(".shp")]
                if not shp_files:
                    st.error("No .shp file found in the uploaded zip.")
                else:
                    filepath = os.path.join(tmpdir, shp_files[0])
                    gdf = gpd.read_file(filepath)
                    # st.write(gdf.head())
                    column_t1 = st.selectbox(
                            "Select Shape file column name:",
                        tuple(gdf.columns))
                    gdf['data']=0
                    original_geometry = gdf.geometry
                original_crs = gdf.crs
                title_map = st.text_input("Enter the title of the map")
                # Use st.data_editor for user interaction
                edited_data = st.data_editor(
                    gdf[[column_t1, 'data']],
                    disabled=[column_t1],num_rows='fixed'
                )
                # Number_letter = st.number_input("Enter the no of Letter:",value=None ,min_value=None,max_value=10,step=1)
                # Reconstruct the GeoDataFrame with the original geometry and CRS
                gdf = gpd.GeoDataFrame(
                    edited_data,
                    geometry=original_geometry,
                    crs=original_crs
                )
                # Trigger rerun if data is updated
                if not st.session_state.rerun_trigger and gdf["data"].any():
                    st.session_state.rerun_trigger = True
                    st.rerun()

        except Exception as e:
            st.error(f"An error occurred while processing the Shapefile: {e}")
    else:
        st.info("Please upload a valid Shapefile (.zip).")

    # Update = st.button("Update")

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
        if(uploaded_file):
            # if Update:
                gdf['color'] = gdf['data'].apply(get_color) 
            # Check and set CRS
                if not gdf.crs:
                    st.warning("No CRS found. Assuming WGS84.")
                    gdf.set_crs("EPSG:4326")
                elif gdf.crs != "EPSG:4326":
                    gdf = gdf.to_crs("EPSG:4326")

                gdf = gdf.to_crs(epsg=3857)
                # Calculate centroids
                gdf['centroid'] = gdf.geometry.centroid

                # Accessing centroid coordinates
                gdf['centroid_x'] = gdf.centroid.x
                gdf['centroid_y'] = gdf.centroid.y

                # Now you can annotate the map
                fig, ax = plt.subplots(figsize=(10, 8))
                gdf.plot(ax=ax, color=gdf['color'], edgecolor='black')
                gdf.apply(lambda x: ax.annotate(
                    text=f"{x[column_t1]}\n{x['data']}%",  # Print only the name
                    xy=(x['centroid_x'], x['centroid_y']),
                    ha='center', size=8), axis=1)
                legend_elements = [
                    Patch(facecolor='green', edgecolor='black', label=f'< {green}%'),
                    Patch(facecolor='yellow', edgecolor='black', label=f'{green} - {yellow}%'),
                    Patch(facecolor='orange', edgecolor='black', label=f'{yellow} - {orange}%'),
                    Patch(facecolor='red', edgecolor='black', label=f'{orange} - {red}%'),
                    Patch(facecolor='gray', edgecolor='black', label='Other')
                    ]
                ax.legend(handles=legend_elements, title='Percentage', loc='lower right', fontsize=10)
                
                # ax.set_xlabel('')
                ax.set_xticks([])
                ax.set_yticks([])
                ax.set_title(title_map,fontsize=16, weight='bold')
                st.pyplot(fig)
                plt.savefig("Map.jpg",dpi=500)
                # st.rerun()


