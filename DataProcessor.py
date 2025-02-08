import pandas as pd
import logging
from HeatMapGenerator import HeatmapGenerator

# configure logger
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

class DataProcessor:
    # predefined bounding boxes for different cities
    REGION_BOUNDS = {
        "München": {"lat_min": 48.061, "lat_max": 48.248, "lon_min": 11.360, "lon_max": 11.722},
        "Berlin": {"lat_min": 52.338, "lat_max": 52.675, "lon_min": 13.088, "lon_max": 13.761},
        "Hamburg": {"lat_min": 53.395, "lat_max": 53.703, "lon_min": 9.732, "lon_max": 10.271}
    }

    def __init__(self, region_name, mnc, provider):
        """
        initializes the data processor with a selected region and mnc filter
        :param region_name: name of the region (e.g., "München", "Berlin", "Hamburg")
        :param mnc: mobile network code to filter the dataset
        """
        if region_name in self.REGION_BOUNDS:
            self.region_bounds = self.REGION_BOUNDS[region_name]
        else:
            raise ValueError(f"unknown region: {region_name}. available options: {list(self.REGION_BOUNDS.keys())}")

        self.mnc = mnc
        self.provider = provider
        logger.info(f"initialized processor for region: {region_name} with mnc: {mnc} known as {provider}")

    def load_and_clean_data(self, file_path):
        """
        loads the csv file and cleans it
        :param file_path: path to the csv file
        :return: cleaned dataframe
        """
        try:
            df = pd.read_csv(file_path)
            logger.info(f"file loaded: {file_path}")
        except Exception as e:
            logger.error(f"error loading file {file_path}: {e}")
            return None

        # add header
        df_with_header = self.add_header(df)
        
        # remove empty rows
        df_cleaned = self.remove_empty_rows(df_with_header)

        # remove duplicates
        df_cleaned = self.remove_duplicates(df_cleaned)

        # filter for selected region
        df_region = self.filter_region(df_cleaned)

        # filter for mcc 262 (germany)
        df_region_mcc = self.filter_for_mcc_262(df_region)

        # keep only relevant columns
        df_relevant_columns = self.filter_relevant_columns(df_region_mcc)

        # filter for selected mnc
        df_final = self.filter_for_mnc(df_relevant_columns)

        df_final.to_csv("final_dataset.csv")
        
        logger.info(f"dataset after cleaning has {len(df_final)} rows.")
        logger.info(f"final dataset has been saved to directory")
    
        self.generate_heatmaps(df_final)

    def generate_heatmaps(self, df):
        """
        generates heatmaps for the given dataframe
        """
        heatmap_generator = HeatmapGenerator()
        logger.warning("Generating visualizations for the given dataset.")
        heatmap_generator.generate_heatmap(df, "../heatmaps/new_heatmap.html")
        heatmap_generator.generate_circle_heatmap(df, "../heatmaps/new_circle_heatmap.html")
        logger.info("heatmaps generated successfully")

    def add_header(self, df):
        """
        assigns the correct column names to the dataframe
        :param df: dataframe without proper headers
        :return: dataframe with correct headers
        """
        columns = [
            "radio", "mcc", "net", "area", "cell", "unit", 
            "lon", "lat", "range", "samples", 
            "changeable", "created", "updated", "averageSignal"
        ]
        df.columns = columns
        return df

    def remove_empty_rows(self, df):
        """
        removes empty rows from the dataframe
        :param df: dataframe to be cleaned
        :return: cleaned dataframe
        """
        before_removal = len(df)
        df_cleaned = df.dropna()
        after_removal = len(df_cleaned)
        logger.info(f"removed empty rows: {before_removal - after_removal}")
        return df_cleaned

    def remove_duplicates(self, df):
        """
        removes duplicate rows from the dataframe
        :param df: dataframe to be checked
        :return: cleaned dataframe without duplicates
        """
        before_removal = len(df)
        df_cleaned = df.drop_duplicates()
        after_removal = len(df_cleaned)
        logger.info(f"removed duplicates: {before_removal - after_removal}")
        return df_cleaned
    
    def filter_region(self, df):
        """
        filters the dataset to only include data within the selected region
        :param df: dataframe to be filtered
        :return: filtered dataframe
        """
        before_filtering = len(df)
        
        df = df[
            (df["lat"] >= self.region_bounds["lat_min"]) & 
            (df["lat"] <= self.region_bounds["lat_max"]) &
            (df["lon"] >= self.region_bounds["lon_min"]) &
            (df["lon"] <= self.region_bounds["lon_max"])
        ]
        after_filtering = len(df)
        logger.info(f"rows remaining after region filtering: {after_filtering}")
        logger.info(f"removed rows: {before_filtering - after_filtering}")
        return df
    
    def filter_for_mcc_262(self, df):
        """
        filters the dataset to only include entries with mcc 262 (germany)
        :param df: dataframe to be filtered
        :return: filtered dataframe
        """
        before_filtering = len(df)
        df = df[df["mcc"] == 262]
        after_filtering = len(df)
        
        logger.info(f"rows remaining after mcc filtering: {after_filtering}")
        logger.info(f"removed rows: {before_filtering - after_filtering}")
        
        if before_filtering == after_filtering:
            logger.info("no incorrect data found.")
        else:
            logger.warning(f"removed {before_filtering - after_filtering} incorrect rows.")
        
        return df
        
    def filter_relevant_columns(self, df):
        """
        keeps only the relevant columns for analysis
        :param df: dataframe to be processed
        :return: dataframe with only relevant columns
        """
        columns_to_keep = ["lon", "lat", "mcc", "range", "net", "cell", "averageSignal"]
        df = df[columns_to_keep]
        return df
    
    def filter_for_mnc(self, df):
        """
        Filters the dataset to only include data for the selected mnc(s).
        :param df: DataFrame to be filtered
        :return: filtered DataFrame
        """
        before_filtering = len(df)
        df = df[df["net"].isin(self.mnc)]
        after_filtering = len(df)

        logger.info(f"rows remaining after mnc filtering: {after_filtering}")
        logger.info(f"removed rows: {before_filtering - after_filtering}")

        return df