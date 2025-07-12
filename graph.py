import streamlit as st
import cv2
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(page_title="Roadside Ditch Graph Visualizer", layout="centered")

st.title("📊 Roadside Ditch Graph Visualizer")
st.write("Upload your graph image. This tool will detect slopes and show X and Y distances on a clean graph.")

uploaded_file = st.file_uploader("Upload Graph Image", type=["jpg", "jpeg", "png"])

if uploaded_file:
    file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
    image = cv2.imdecode(file_bytes, 1)

    st.image(image, caption="Uploaded Graph Image", use_column_width=True)

    # Convert to grayscale & detect edges
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blurred, 50, 150)

    # Find contours (graph line points)
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    slope_points = []
    for cnt in contours:
        for point in cnt:
            x, y = point[0]
            slope_points.append((x, y))

    # Sort points by X value (left to right)
    slope_points = sorted(slope_points, key=lambda p: p[0])

    st.sidebar.subheader("Graph Scale Settings")
    x_min = st.sidebar.number_input("X-axis Min Value", value=0)
    x_max = st.sidebar.number_input("X-axis Max Value", value=45)
    y_min = st.sidebar.number_input("Y-axis Min Value", value=80.0)
    y_max = st.sidebar.number_input("Y-axis Max Value", value=83.5)

    height, width = image.shape[:2]

    x0_pixel = 80       # assuming graph area starts at pixel 80 (left)
    x45_pixel = width - 10   # assuming graph area ends near image width

    pixels_per_meter_x = (x45_pixel - x0_pixel) / (x_max - x_min)

    y80_pixel = height - 80
    y83_5_pixel = 10

    pixels_per_meter_y = (y80_pixel - y83_5_pixel) / (y_max - y_min)

    if len(slope_points) > 1:
        fig, ax = plt.subplots(figsize=(8, 5))

        # Convert pixel points to meter values and plot
        x_vals = []
        y_vals = []
        for (x, y) in slope_points:
 x_meter = round((x - x0_pixel) / pixels_per_meter_x, 2)
            y_meter = round((y80_pixel - y) / pixels_per_meter_y, 2)
            x_vals.append(x_meter)
            y_vals.append(y_meter)

        ax.plot(x_vals, y_vals, marker='o', color='blue', label="Detected Slope")

     
        for i in range(1, len(x_vals)):
            dx = round(abs(x_vals[i] - x_vals[i-1]), 2)
            dy = round(abs(y_vals[i] - y_vals[i-1]), 2)
            mid_x = (x_vals[i] + x_vals[i-1]) / 2
            mid_y = (y_vals[i] + y_vals[i-1]) / 2
            ax.text(mid_x, mid_y, f"ΔX={dx}m\nΔY={dy}m", fontsize=7, color='red', ha='center')

        ax.set_xlabel("X Distance (m)")
        ax.set_ylabel("Y Height (m)")
        ax.set_xlim(x_min, x_max)
        ax.set_ylim(y_min, y_max)
        ax.set_title("Graph Slopes with X and Y Distances")
        ax.grid(True)
        ax.legend()

        st.pyplot(fig)

    else:
        st.warning("No slope points detected in the image.")

else:
    st.info("Please upload a graph image to start.")
