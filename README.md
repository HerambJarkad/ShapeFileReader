# 🗺️ Shapefile Viewer with Health Data Analysis

A powerful Streamlit-based web application to visualize and analyze shapefile data (especially health metrics) with customizable color thresholds and GPT-4 Vision-powered insights.

---

## 🚀 Features

- 📂 Upload `.zip` shapefiles containing `.shp` and associated files
- 🎨 Automatically visualize data with color-coded thresholds (Green, Yellow, Orange, Red, Gray)
- ✍️ Inline data editing for easy updates to health metrics
- 🧠 GPT-4 Vision analysis of the generated map with actionable recommendations
- 🗺️ High-resolution choropleth map with labels and legends
- ✅ Supports CRS detection and projection for proper rendering

---

## 📸 Example Use Case

Visualize health data (e.g., district-level malnutrition, vaccination coverage, etc.), modify values, and analyze the map to identify strategic improvements using AI recommendations.

---

## 📦 Installation

### Requirements

- Python 3.8+
- Streamlit
- GeoPandas
- Matplotlib
- OpenAI SDK
- Python-dotenv
- Pandas

### Setup Instructions

```bash
# Clone the repository
git clone https://github.com/yourusername/shapefile-viewer.git
cd shapefile-viewer

# Install dependencies
pip install -r requirements.txt

# Create a .env file and add your OpenAI key
echo "OPENAI_API_KEY=your_openai_key_here" > .env

# Run the app
streamlit run app.py
```
## 🧪 How to Use

1. **Upload a `.zip` Shapefile**: Upload a compressed ZIP file that includes your `.shp` file and associated components (`.shx`, `.dbf`, etc.).
2. **Choose a Column**: Select the shapefile column to use for labeling each region.
3. **Edit the Data**: Use the built-in editor to modify values in the `data` column (e.g., health metric percentages).
4. **Set Thresholds**: Customize thresholds in the sidebar for color coding:
   - Green: Healthy
   - Yellow: Needs attention
   - Orange: Concerning
   - Red: Critical
5. **Visualize the Map**: The app renders a choropleth map with your data, colors, and labels.
6. **Analyze with GPT-4**: Click **“Analyze Map”** to get an AI-powered assessment and actionable health strategy.

---

## 🧠 GPT-4 Vision-Powered Analysis

By leveraging GPT-4 with vision capabilities, the app provides:

- 🎯 **Targeted Interventions** for Yellow → Green conversion
- 🚨 **Immediate Actions** to improve Red zones
- 🧩 **Sustainable Improvements** to move Orange to Yellow
- 🌍 **Regional Pattern Analysis** using map context and clustering
- 🏛️ **Policy Integration** suggesting enhancements to existing government initiatives

All analysis is generated using a high-resolution image of the map and a tailored prompt for concise, strategic recommendations.

---

## 🛠️ Built With

- **[Streamlit](https://streamlit.io/)** – UI framework for interactive apps
- **[GeoPandas](https://geopandas.org/)** – For spatial data processing
- **[Matplotlib](https://matplotlib.org/)** – For custom map plotting
- **[OpenAI GPT-4 Vision](https://platform.openai.com/)** – For intelligent analysis of map visuals
- **[dotenv](https://pypi.org/project/python-dotenv/)** – To manage environment variables
- **[Pandas](https://pandas.pydata.org/)** – For dataframe operations
