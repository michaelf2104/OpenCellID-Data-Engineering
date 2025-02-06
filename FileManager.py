import pandas as pd

class FileManager:
    @staticmethod
    def load_previous_snapshot(file_path):
        try:
            return pd.read_csv(file_path)
        except FileNotFoundError:
            print("No previous dataset found.")
            return None
