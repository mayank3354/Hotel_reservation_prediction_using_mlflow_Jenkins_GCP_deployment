import os
import pandas as pd
from google.cloud import storage
from sklearn.model_selection import train_test_split
from src.logger import get_logger
from src.custom_exception import CustomException
from config.paths_config import *
from utils.common_functions import read_yaml

logger = get_logger(__name__)


class DataIngestion:
    def __init__(self, config):
        self.config = config["data_ingestion"]
        self.bucket_name = self.config["bucket_name"]
        self.bucket_file_name = self.config["bucket_file_name"]
        self.train_test_ratio = self.config["train_ratio"]

        os.makedirs(RAW_DIR, exist_ok=True)

        logger.info(f"Data ingestion started with {self.bucket_name} and file is {self.bucket_file_name}")

    def download_csv_from_gcp(self):
        try:
            client = storage.Client()
            bucket = client.bucket(self.bucket_name)
            blob = bucket.blob(self.bucket_file_name)
            blob.download_to_filename(RAW_FILE_PATH)
            logger.info(f"File {self.bucket_file_name} downloaded successfully")
        except Exception as e:
            logger.error(f"Error in downloading file {self.bucket_file_name}: {e}")
            raise CustomException("Error in downloading file", e)
        
    def split_data(self):
        try:
            df = pd.read_csv(RAW_FILE_PATH)
            train_df, test_df = train_test_split(df, test_size=1 - self.train_test_ratio, random_state=42)
            train_df.to_csv(TRAIN_FILE_PATH, index=False)
            test_df.to_csv(TEST_FILE_PATH, index=False)
            logger.info(f"Data split into train and test successfully")
        except Exception as e:
            logger.error(f"Error in splitting data: {e}")
            raise CustomException("Error in splitting data", e)
        
    def initiate_data_ingestion(self):
        try:
            logger.info("data ingestion started")
            self.download_csv_from_gcp()
            self.split_data()

            logger.info(f"Data ingestion completed")
        except CustomException as ce:
            logger.error(f"Custom Exception: {str(ce)}")
        finally:
            logger.info("Data ingestion completed")

if __name__ == "__main__":

    data_ingestion = DataIngestion(config=read_yaml(CONFIG_PATH))
    data_ingestion.initiate_data_ingestion()
