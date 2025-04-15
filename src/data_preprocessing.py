import os
import pandas as pd
import numpy as np
from src.logger import get_logger
from src.custom_exception import CustomException
from config.paths_config import *
from utils.common_functions import read_yaml,load_data
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from imblearn.over_sampling import SMOTE

logger = get_logger(__name__)

class DataProccessor:

    def __init__(self, train_path, test_path, processed_dir, config_path):
        self.train_path = train_path
        self.test_path  = test_path
        self.processed_dir = processed_dir 

        self.config = read_yaml(config_path)


        if not os.path.exists(self.processed_dir):
            os.makedirs(self.processed_dir)
    
    def preprocess_data(self,df):
        try:
            logger.info("Starting our Data Processing Step")

            logger.info("Dropping the Columns")
            df.drop(columns=["Booking_ID"], inplace=True)
            df.drop_duplicates(inplace=True)
            
            cat_cols = self.config["data_processing"]["categorical_columns"]
            num_cols = self.config["data_processing"]["numerical_columns"]

            logger.info("Applying Label Encoding")
            label_encoder = LabelEncoder()

            mappings={}

            for column in cat_cols:
                df[column] = label_encoder.fit_transform(df[column])
                mappings[column] = {label: code for label,code in zip(label_encoder.classes_, label_encoder.transform(label_encoder.classes_))}
    
            logger.info("Label Mappings are : ")
            for col,mapping in mappings.items():
                logger.info(f"{col} : {mapping}")

            logger.info("Doing Skewness Handling")

            skewness_threshold = self.config["data_processing"]["skewness_threshold"]
            skewness = df[num_cols].apply(lambda x:x.skew())

            for column in skewness[skewness>skewness_threshold].index:
                df[column] = np.log1p(df[column])

            return df
        except Exception as e:
            logger.error(f"Error During preprocess step {e}")
            raise CustomException("Erorr While Preprocess data")
        
    def balanced_data(self,df):
        try:
            logger.info("Handling Imbalanced data")
            X= df.drop(columns=["booking_status"])
            y= df["booking_status"]

            smote = SMOTE(random_state=42)
            X_resampled ,y_resampled = smote.fit_resample(X,y)

            balanced_df = pd.DataFrame(X_resampled, columns=X.columns)
            balanced_df["booking_status"] = y_resampled

            logger.info("Data Balanced successfully")
            return balanced_df
        except Exception as e:
            logger.error(f"Error During Balancing Data step {e}")
            raise CustomException("Erorr While Balancing data")
        

    def select_features(self,df):
        try:
            logger.info("Starting our feature selection step")
            X= df.drop(columns=["booking_status"])
            y= df["booking_status"]

            model = RandomForestClassifier(random_state=42)
            model.fit(X,y)

            feature_importances = model.feature_importances_

            feature_importances_df = pd.DataFrame({'feature': X.columns, 'importance': model.feature_importances_})
            top_feature_importances_df = feature_importances_df.sort_values(by='importance', ascending=False)

            num_features_to_select = self.config["data_processing"]["no_of_features"]

            top_10_features = top_feature_importances_df['feature'].head(num_features_to_select).values

            logger.info(f" Features selected: {top_10_features}")

            top_10_df = df[top_10_features.tolist() + ["booking_status"]]

            logger.info("Feature Selection completed Succesfully")
            return top_10_df
        except Exception as e:
            logger.error(f"Error During fEATURE selection step {e}")
            raise CustomException("Erorr While selecting the features")

    def save_data(self,df , file_path):
        try:
            logger.info("Saving our data in proessed folder")

            df.to_csv(file_path, index=False)

            logger.info(f"Data saved successfully to {file_path}")
        except Exception as e:
            logger.error(f"Error During saving data step {e}")
            raise CustomException("Erorr While saving the data")

    def process(self):
        try:
            logger.info("Loading data from raw directry")

            train_df = load_data(self.train_path)
            test_df = load_data(self.test_path)

            train_df = self.preprocess_data(train_df)
            test_df = self.preprocess_data(test_df)

            train_df = self.balanced_data(train_df)
            test_df = self.balanced_data(test_df)

            train_df = self.select_features(train_df)
            test_df = test_df[train_df.columns]

            self.save_data(train_df,PROCESSED_TRAIN_DATA_PATH)
            self.save_data(test_df, PROCESSED_TEST_DATA_PATH)

            logger.info("Data Proccessing completed succesfully")
        except Exception as e:
            logger.error(f"Error During Preprocessing pipeline")
            raise CustomException("Erorr While data preprocessing pipeline")
        

if __name__ == "__main__":
    processor = DataProccessor(TRAIN_FILE_PATH,TEST_FILE_PATH,PROCESSED_DIR,CONFIG_PATH)
    processor.process()



