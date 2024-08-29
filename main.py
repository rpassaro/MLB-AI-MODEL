import pandas as pd
from src.Predict.XGBoost_Runner import *
from sbrscrape import Scoreboard
from src.Process_Data.get_today_data import *
from src.Process_Data.update_dataset import *
import warnings
import os
from season_models_tests import szn_model_test

post_format = 2
def get_short_team_name(name):
    if name == "St. Louis Cardinals":
        return "Cardinals"
    elif name == "Boston Red Sox":
        return "Red Sox"
    elif name == "Baltimore Orioles":
        return "Orioles"
    elif name == "Seattle Mariners":
        return "Mariners"
    elif name == "New York Yankees":
        return "Yankees"
    elif name == "Chicago White Sox":
        return "White Sox"
    elif name == "Philadelphia Phillies":
        return "Phillies"
    elif name == "Washington Nationals":
        return "Nationals"
    elif name == "Toronto Blue Jays":
        return "Blue Jays"
    elif name == "Tampa Bay Rays":
        return "Rays"
    elif name == "Cleveland Guardians":
        return "Guardians"
    elif name == "Minnesota Twins":
        return "Twins"
    elif name == "Miami Marlins":
        return "Marlins"
    elif name == "New York Mets":
        return "Mets"
    elif name == "Kansas City Royals":
        return "Royals"
    elif name == "Oakland Athletics":
        return "Athletics"
    elif name == "Houston Astros":
        return "Astros"
    elif name == "Milwaukee Brewers":
        return "Brewers"
    elif name == "Chicago Cubs":
        return "Cubs"
    elif name == "Pittsburgh Pirates":
        return "Pirates"
    elif name == "Texas Rangers":
        return "Rangers"
    elif name == "Los Angeles Angels":
        return "Angels"
    elif name == "San Francisco Giants":
        return "Giants"
    elif name == "Colorado Rockies":
        return "Rockies"
    elif name == "Arizona Diamondbacks":
        return "Diamondbacks"
    elif name == "Detroit Tigers":
        return "Tigers"
    elif name == "Los Angeles Dodgers":
        return "Dodgers"
    elif name == "Cincinnati Reds":
        return "Reds"
    elif name == "Atlanta Braves":
        return "Braves"
    elif name == "San Diego Padres":
        return "Padres"
    else:
        return name

def convert_dataset_to_csv():
    db_path = 'C:/Users/Ryan/Desktop/MLB_AI_Model/Data/dataset.sqlite'

    # Specify the table you want to export to CSV
    table_name = 'dataset'

    # Specify the path for the resulting CSV file
    csv_file_path = 'C:/Users/Ryan/Desktop/MLB_Basic10.csv'

    # Connect to the SQLite database
    conn = sqlite3.connect(db_path)

    # Read the table into a pandas DataFrame
    df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
    df = df[df['Year'] == 2024]

    # Close the connection to the database
    conn.close()

    # Write the DataFrame to a CSV file
    df.to_csv(csv_file_path, index=False)

print("\nUPDATING DATASET")
update_dataset()
print("\nDATASET UPDATED\n")

file_path = "C:/Users/Ryan/Desktop/MLB_Basic10.csv"
if os.path.exists(file_path):
    os.remove(file_path)
convert_dataset_to_csv()

szn_model_test()
print("\n")

warnings.filterwarnings('ignore', category=FutureWarning)

columns = ['OU','Over Open Odds','Home ML Open','Away ML Open','Home_GP','Away_GP','Home_W_PCT','Away_W_PCT','Home_Avg_Score','Away_Avg_Score','Home_Avg_Total_Score','Home_Avg_Total_Score_20','Home_Avg_Total_Score_10','Home_Avg_Total_Score_5','Away_Avg_Total_Score','Away_Avg_Total_Score_20','Away_Avg_Total_Score_10','Away_Avg_Total_Score_5','Home_OU_PCT','Home_OU_PCT_20','Home_OU_PCT_10','Home_OU_PCT_5','Away_OU_PCT','Away_OU_PCT_20','Away_OU_PCT_10','Away_OU_PCT_5','Home_Opp_Avg','Home_Opp_Avg_20','Home_Opp_Avg_10','Home_Opp_Avg_5','Away_Opp_Avg','Away_Opp_Avg_20','Away_Opp_Avg_10','Away_Opp_Avg_5']
data = pd.DataFrame(columns=columns)

games = Scoreboard(sport="MLB").games
all_games_odds = []
for game in games:
    try:
        all_games_odds.append([game['home_team_abbr'], game['away_team_abbr'], game['total']['fanduel'], game['over_odds']['fanduel'], game['home_ml']['fanduel'], game['away_ml']['fanduel']])
    except:
        print("Missed " + game['home_team_abbr'])
        continue
for temp_game in all_games_odds:
    game_data = get_all_game_data(temp_game)
    game_data_df = pd.DataFrame(game_data)
    data = pd.concat([data, game_data_df], ignore_index = True)
predictions = predict_games(data)

if post_format == 1:
    index = 0
    for game in games:
        ou_prediction = int(np.argmax(predictions[index][0]))
        game_ou = "UNDER" if ou_prediction == 0 else "OVER"
        confidence = predictions[index][0][ou_prediction]
        if game_ou == "UNDER":
            try:
                print("{} vs {}: {} {} {} ({}%)".format(game['home_team'], game['away_team'], game_ou, game['total']['fanduel'], game['under_odds']['fanduel'], round(confidence * 100, 1)))
            except:
                print("No game odds for " + game['home_team'])
                continue
            
        if game_ou == "OVER":
            try:
                print("{} vs {}: {} {} {} ({}%)".format(game['home_team'], game['away_team'], game_ou, game['total']['fanduel'], game['over_odds']['fanduel'], round(confidence * 100, 1)))
            except:
                print("No game odds for " + game['home_team'])
                continue
        index += 1

if post_format == 2:
    index = 0
    for game in games:
        if int(np.argmax(predictions[0][index][0])) != int(np.argmax(predictions[1][index][0])) or int(np.argmax(predictions[0][index][0])) != int(np.argmax(predictions[2][index][0])) or int(np.argmax(predictions[1][index][0])) != int(np.argmax(predictions[2][index][0])):
            index += 1
            continue
        try:
            ou_prediction = int(np.argmax(predictions[0][index][0]))
        except:
            continue
        game_ou = "UNDER" if ou_prediction == 0 else "OVER"
        if game_ou == "UNDER":
            try:
                print("MLB | {} vs {}: {} {} {}".format(get_short_team_name(game['home_team']), get_short_team_name(game['away_team']), game_ou, game['total']['fanduel'], game['under_odds']['fanduel']))
            except:
                print("No game odds for " + game['home_team'])
                continue
            
        if game_ou == "OVER":
            try:
                print("MLB | {} vs {}: {} {} {}".format(get_short_team_name(game['home_team']), get_short_team_name(game['away_team']), game_ou, game['total']['fanduel'], game['over_odds']['fanduel']))
            except:
                print("No game odds for " + game['home_team'])
                continue
        index += 1
    print("\nWe recommend betting 3-5u per pick, straight. \n\n#MLB #DraftKings #BetMGM #sportsbetting #parlay #lockoftheday #freepicks #fanduel #freepicks #locks #Baseball #MLBPicks #SportsbettingX")
    
if post_format == 3:
    index = 0
    for game in games:
        ou_prediction = int(np.argmax(predictions[index][0]))
        game_ou = "UNDER" if ou_prediction == 0 else "OVER"
        confidence = predictions[index][0][ou_prediction]
        if game_ou == "UNDER":
            try:
                print("{} vs {}: {} {} {}".format(get_short_team_name(game['home_team']), get_short_team_name(game['away_team']), game_ou, game['total']['fanduel'], game['under_odds']['fanduel']))
            except:
                print("No game odds for " + game['home_team'])
                continue
            
        if game_ou == "OVER":
            try:
                print("{} vs {}: {} {} {}".format(get_short_team_name(game['home_team']), get_short_team_name(game['away_team']), game_ou, game['total']['fanduel'], game['over_odds']['fanduel']))
            except:
                print("No game odds for " + game['home_team'])
                continue
        index += 1
    print("\nWe recommend betting about 3-4u per pick, straight. \n\n#MLB #DraftKings #BetMGM #sportsbetting #parlay #lockoftheday #freepicks #sportsbetting #fanduel #freepicks #locks #Baseball #MLBPicks #SportsbettingX")
