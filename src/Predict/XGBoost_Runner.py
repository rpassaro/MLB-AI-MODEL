import copy

import numpy as np
import pandas as pd
import xgboost as xgb
from colorama import Fore, Style, init, deinit

#MLB

# from src.Utils.Dictionaries import team_index_current
# from src.Utils.tools import get_json_data, to_data_frame, get_todays_games_json, create_todays_games
init()
xgb_uo = xgb.Booster()

models = ["C:/Users/Ryan/Desktop/MLB_AI_Model/Models/XGBoost_55.8_UO-9,2024-08-01,OVER-54.87,UNDER-56.64.json", "C:/Users/Ryan/Desktop/MLB_AI_Model/Models/XGBoost_56.0_UO-9,2024-06-20,OVER-52.52,UNDER-59.49.json", "C:/Users/Ryan/Desktop/MLB_AI_Model/Models/XGBoost_56.2_UO-9,2024-06-20,OVER-53.2,UNDER-59.21.json"]
def predict_games(data):

    all_predictions = []
    
    for model in models:
        
        xgb_uo.load_model(model)
        
        ou_predictions_array = []

        for index, row in data.iterrows():
            # Convert row to 2D numpy array
            row_data = np.array(row).reshape(1, -1)
            dmatrix_data = xgb.DMatrix(row_data)
            
            # Predict and collect predictions
            prediction = xgb_uo.predict(dmatrix_data)
            ou_predictions_array.append(prediction)
        all_predictions.append(ou_predictions_array)
    return all_predictions #ou_predictions_array ALSO GET RID OF FOR LOOP AND JUST HAVE ONE LOAD_MODEL FOR OG
