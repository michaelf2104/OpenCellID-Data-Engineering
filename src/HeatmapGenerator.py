import folium
import logging
from folium.plugins import HeatMap
import numpy as np 

# configure logger
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

class HeatmapGenerator:
    @staticmethod
    def generate_heatmap(df, output_file):
        """
        generates a heatmap from a given dataframe
        :param df: pandas dataframe containing 'lat' and 'lon' columns
        :param output_file: path to save the heatmap html file
        """
        if df is None or df.empty:
            logger.error("dataframe is empty. cannot generate heatmap.")
            return

        # create a map centered at the mean location
        center_lat = df["lat"].mean()
        center_lon = df["lon"].mean()
        heatmap_map = folium.Map(location=[center_lat, center_lon], zoom_start=12)

        # prepare data for heatmap
        heat_data = df[["lat", "lon"]].values.tolist()

        # add heatmap layer
        HeatMap(heat_data).add_to(heatmap_map)

        # save the heatmap as an html file
        heatmap_map.save(output_file)
        logger.info(f"heatmap saved to {output_file}")


    @staticmethod
    def generate_circle_heatmap(df, output_file):
        # set center of the map (munich)
        map_center = [48.137154, 11.576124]
        base_map = folium.Map(location=map_center, zoom_start=11)

        for _, row in df.iterrows():
            lat, lon = row["lat"], row["lon"]
            range_in_km = row["range"] / 1000  # convert meters to kilometers
            average_signal = row["averageSignal"]

            # determine circle size based on range
            radius = range_in_km * 100  # example scaling factor

            # create circle marker
            folium.Circle(
                location=[lat, lon],
                radius=radius,
                color='blue',  # color could depend on signal strength
                fill=True,
                fill_color='blue',
                fill_opacity=0.4
            ).add_to(base_map)

        base_map.save(output_file)
        logger.info(f"circle heatmap saved to {output_file}")
