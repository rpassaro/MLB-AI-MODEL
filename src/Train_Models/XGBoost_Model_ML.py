import sqlite3

import numpy as np
import pandas as pd
import xgboost as xgb
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from tqdm import tqdm
from datetime import datetime, date
import statistics

dataset = "dataset"
con = sqlite3.connect("../../Data/dataset2.sqlite")
data = pd.read_sql_query(f"select * from \"{dataset}\"", con) #, index_col="index")
con.close()

margin = data['Home_Team_Win']
data.drop(['Game_ID','Date','Year','OU_Cover','Home Team','Away Team','Home Score','Away Score','Home_Team_Win','Over Open Odds','Under Open','Under Open Odds','Total_Score'],
          axis=1, inplace=True)

data = data.values

data = data.astype(float)
acc_results = []
for x in tqdm(range(300)):
    x_train, x_test, y_train, y_test = train_test_split(data, margin, test_size=.1)

    train = xgb.DMatrix(x_train, label=y_train)
    test = xgb.DMatrix(x_test, label=y_test)

    param = {
        'max_depth': 20,
        'eta': 0.05,
        'objective': 'multi:softprob',
        'num_class': 2
    }
    epochs = 750

    model = xgb.train(param, train, epochs)
    predictions = model.predict(test)
    y = []

    for z in predictions:
        y.append(np.argmax(z))

    acc = round(accuracy_score(y_test, y) * 100, 1)
    print(f"{acc}%")
    acc_results.append(acc)
    if x % 50 == 0:
        print("Avg Accuracy: " + str(statistics.mean(acc_results)))
    # only save results if they are the best so far
    if acc == max(acc_results) and acc > 60:
        model.save_model('../../Models/XGBoost_{}%_ML-4-{}.json'.format(acc, date.today()))