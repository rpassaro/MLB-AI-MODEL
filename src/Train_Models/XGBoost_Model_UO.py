import sqlite3

from datetime import datetime, date
import numpy as np
import pandas as pd
import xgboost as xgb
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from tqdm import tqdm
import time
import statistics
import random

dataset = "dataset"
con = sqlite3.connect("../../Data/dataset.sqlite")
data = pd.read_sql_query(f"select * from \"{dataset}\"", con) #, index_col="index")
data = data[(data['Home_GP'] > 20) & (data['Away_GP'] > 20) & (data['Year'] >= 2016) & (data['Home_GP'] < 140) & (data['Away_GP'] < 140)]
print(len(data)) #CHANGED ^
con.close()

OU = data['OU_Cover']
total = data['OU']
dropped_data = ['Game_ID','Date','Year','OU_Cover','Home Team','Away Team','Home Score','Away Score','Home_Team_Win','Total_Score']
data.drop(dropped_data, axis=1, inplace=True)
#Drop GAME_ID and PLAYER_ID
data['OU'] = np.asarray(total)
data = data.values
data = data.astype(float)
acc_results = []
over_results = []
under_results = []

for x in tqdm(range(10000)):
    print(" Normal params, since 2016, 20 < gp < 150, normal dataset + season and 20 game avg")
    x_train, x_test, y_train, y_test = train_test_split(data, OU, test_size=0.1)

    # Create DMatrix for XGBoost
    train = xgb.DMatrix(x_train, label=y_train)
    test = xgb.DMatrix(x_test)

    # Define the parameters for XGBoost
    param = {
        'max_depth': 20,
        'eta': 0.05,
        'objective': 'multi:softprob',
        'num_class': 3
    }
    epochs = 750

    # Train the model
    model = xgb.train(param, train, epochs)

    # Make predictions
    predictions = model.predict(test)
    y_pred = np.argmax(predictions, axis=1)

    # Ensure that the number of predictions matches the number of test samples
    assert x_test.shape[0] == y_pred.shape[0], "Mismatch between number of test samples and predictions"

    # Combine x_test with the predictions
    x_test_with_predictions = x_test.copy()

    # Convert x_test_with_predictions to DataFrame if it's not already one
    if not isinstance(x_test_with_predictions, pd.DataFrame):
        x_test_with_predictions = pd.DataFrame(x_test_with_predictions)

    # Add predictions and actual values to the DataFrame
    x_test_with_predictions['Predicted'] = y_pred
    x_test_with_predictions['Actual'] = y_test.values

    # Convert to DataFrame for easy viewing
    results_df = pd.DataFrame(x_test_with_predictions)

    # Save to CSV
    # if round(accuracy_score(y_test, y_pred) * 100, 1) > 55.5:
    #     results_df.to_csv('C:/Users/Ryan/Desktop/Model_Results/xgboost_predictions_{}%_{}.csv'.format(round(accuracy_score(y_test, y_pred) * 100, 1), x), index=False)

    # Total Accuracy
    total_acc = round(accuracy_score(y_test, y_pred) * 100, 1)

    # Separate Accuracy Calculations
    over_accuracy = (accuracy_score(y_test[y_test == 1], y_pred[y_test == 1]) * 100) if np.any(y_test == 1) else 0
    under_accuracy = (accuracy_score(y_test[y_test == 0], y_pred[y_test == 0]) * 100) if np.any(y_test == 0) else 0

    # Printing and Saving Accuracies
    print(f"Total Accuracy: {total_acc}%")
    print(f"OVER Accuracy: {over_accuracy:.1f}%")
    print(f"UNDER Accuracy: {under_accuracy:.1f}%")
    acc_results.append(total_acc)
    over_results.append(over_accuracy)
    under_results.append(under_accuracy)
    
    if x % 10 == 0:
        print("Accuracy of " + str(x) + " trials")
        print(str(round(statistics.mean(acc_results), 2)) + "%")
        
    # only save results if they are the best so far
    if total_acc > 55.2:
        print("HEREEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEE")
        #MIGHT HAVE TO CHANGE FOLDER LOC
        model.save_model('../../Models_recently_tested/XGBoost_{}_UO-9,{},OVER-{},UNDER-{}.json'.format(total_acc, date.today(), round(over_accuracy,2), round(under_accuracy,2)))
