import sqlite3
import pandas as pd
from pysbr import *
from datetime import datetime
import requests
import time
import statistics
from src.Process_Data.get_odds_date import *

def map_team_name_to_abbr(team_name):
    if team_name == 'Arizona Diamondbacks':
        return 'ARI'
    elif team_name == 'Atlanta Braves':
        return 'ATL'
    elif team_name == 'Baltimore Orioles':
        return 'BAL'
    elif team_name == 'Boston Red Sox':
        return 'BOS'
    elif team_name == 'Chicago Cubs':
        return 'CHC'
    elif team_name == 'Chicago White Sox':
        return 'CHW'
    elif team_name == 'Cincinnati Reds':
        return 'CIN'
    elif team_name == 'Cleveland Guardians':
        return 'CLE'
    elif team_name == 'Colorado Rockies':
        return 'COL'
    elif team_name == 'Detroit Tigers':
        return 'DET'
    elif team_name == 'Houston Astros':
        return 'HOU'
    elif team_name == 'Kansas City Royals':
        return 'KC'
    elif team_name == 'Los Angeles Angels':
        return 'LAA'
    elif team_name == 'Los Angeles Dodgers':
        return 'LAD'
    elif team_name == 'Miami Marlins':
        return 'MIA'
    elif team_name == 'Milwaukee Brewers':
        return 'MIL'
    elif team_name == 'Minnesota Twins':
        return 'MIN'
    elif team_name == 'New York Mets':
        return 'NYM'
    elif team_name == 'New York Yankees':
        return 'NYY'
    elif team_name == 'Oakland Athletics':
        return 'OAK'
    elif team_name == 'Philadelphia Phillies':
        return 'PHI'
    elif team_name == 'Pittsburgh Pirates':
        return 'PIT'
    elif team_name == 'San Diego Padres':
        return 'SD'
    elif team_name == 'Seattle Mariners':
        return 'SEA'
    elif team_name == 'San Francisco Giants':
        return 'SF'
    elif team_name == 'St. Louis Cardinals':
        return 'STL'
    elif team_name == 'Tampa Bay Rays':
        return 'TB'
    elif team_name == 'Texas Rangers':
        return 'TEX'
    elif team_name == 'Toronto Blue Jays':
        return 'TOR'
    elif team_name == 'Washington Nationals':
        return 'WAS'
    else:
        return 'Unknown'  # Handling unknown team names

def update_dataset():
    DATABASE_PATH = "C:/Users/Ryan/Desktop/MLB_AI_Model/Data/dataset.sqlite"
    conn = sqlite3.connect(DATABASE_PATH)
    table_name = 'dataset'
    master_data_df = pd.read_sql_query(f"SELECT * FROM {table_name}",conn)
    conn.close()

    season_url = "http://statsapi.mlb.com/api/v1/schedule/games/?sportId=1&startDate=2024-03-28&endDate=2024-09-29"

    num_tries = 0
    while (True):
        num_tries += 1
        try:
            response = requests.get(season_url)
            break
        except:
            print("Sleeping for {} minutes".format(num_tries ** 2))
            time.sleep(60 * (num_tries ** 2))

    todays_date = int(str(datetime.today())[0:4] + str(datetime.today())[5:7] + str(datetime.today())[8:10])
    data = response.json()
    games = data['dates']
    for date_block in games:
        data_date = date_block['date']
        formatted_date = int(str(data_date)[0:4] + str(data_date)[5:7] + str(data_date)[8:10])
        if formatted_date >= todays_date:
            break
        if len(master_data_df[master_data_df['Date'] == formatted_date]) != 0:
            continue
        
        all_odds = get_odds_date(data_date)
        
        for game in date_block['games']:
            even_total_score = False
            if game['status']['detailedState'] != 'Final':
                continue
            game_id = game['gamePk']
            home_team = map_team_name_to_abbr(game['teams']['home']['team']['name'])
            away_team = map_team_name_to_abbr(game['teams']['away']['team']['name'])
            home_score = game['teams']['home']['score']
            away_score = game['teams']['away']['score']
            home_team_win = 1 if home_score > away_score else 0
            total_score = home_score + away_score
            for temp_game in all_odds:
                if temp_game['Home_Team'] == game['teams']['home']['team']['name']:
                    try:
                        ou = temp_game['Over_Line']
                        over_odds = temp_game['Over_Odds']
                        under_line = temp_game['Under_Line']
                        under_odds = temp_game['Under_Odds']
                        home_ml = temp_game['Home_ML']
                        away_ml = temp_game['Away_ML']
                    except:
                        ou = 8.5
                        over_odds = -110
                        under_line = 8.5
                        under_odds = -110
                        home_ml = -110
                        away_ml = -110
                    if total_score == ou:
                        even_total_score = True
                    ou_cover = 1 if total_score > ou else 0
                    break
            if even_total_score:
                continue
            
            previous_data_df = master_data_df[(master_data_df['Year'] == 2024) & (master_data_df['Date'] < int(todays_date))]
            
            home_team_df = previous_data_df[(previous_data_df['Home Team'] == home_team) | (previous_data_df['Away Team'] == home_team)]
            away_team_df = previous_data_df[(previous_data_df['Away Team'] == away_team) | (previous_data_df['Home Team'] == away_team)]
            home_gp = len(home_team_df)
            away_gp = len(away_team_df)
            
            home_home_df = home_team_df[home_team_df['Home Team'] == home_team]
            away_away_df = away_team_df[away_team_df['Away Team'] == away_team]
            
            home_win_pct = statistics.mean(home_home_df['Home_Team_Win'] == 1) if len(home_home_df != 0) else 0.5
            away_win_pct = 1 - (statistics.mean(away_away_df['Home_Team_Win'] == 1) if len(away_away_df) != 0 else 0.5)
            
            home_avg_score = statistics.mean(home_home_df['Home Score']) if len(home_home_df != 0) else 0
            away_avg_score = statistics.mean(away_away_df['Away Score']) if len(away_away_df != 0) else 0
            
            home_avg_tot_score = statistics.mean(home_home_df['Total_Score']) if len(home_home_df) != 0 else 0
            home_avg_tot_score_20 = statistics.mean(home_home_df['Total_Score'].tail(20)) if len(home_home_df) != 0 else 0
            home_avg_tot_score_10 = statistics.mean(home_home_df['Total_Score'].tail(10)) if len(home_home_df) != 0 else 0
            home_avg_tot_score_5 = statistics.mean(home_home_df['Total_Score'].tail(5)) if len(home_home_df) != 0 else 0
            
            away_avg_tot_score = statistics.mean(away_away_df['Total_Score']) if len (away_away_df) != 0 else 0
            away_avg_tot_score_20 = statistics.mean(away_away_df['Total_Score'].tail(20)) if len (away_away_df) != 0 else 0
            away_avg_tot_score_10 = statistics.mean(away_away_df['Total_Score'].tail(10)) if len (away_away_df) != 0 else 0
            away_avg_tot_score_5 = statistics.mean(away_away_df['Total_Score'].tail(5)) if len (away_away_df) != 0 else 0
            
            home_ou_pct = statistics.mean(home_team_df['OU_Cover']) if len(home_team_df) != 0 else 0.5
            home_ou_pct_20 = statistics.mean(home_team_df['OU_Cover'].tail(20)) if len(home_team_df) != 0 else 0.5
            home_ou_pct_10 = statistics.mean(home_team_df['OU_Cover'].tail(10)) if len(home_team_df) != 0 else 0.5
            home_ou_pct_5 = statistics.mean(home_team_df['OU_Cover'].tail(5)) if len(home_team_df) != 0 else 0.5
            
            away_ou_pct = statistics.mean(away_team_df['OU_Cover']) if len(away_team_df) != 0 else 0.5
            away_ou_pct_20 = statistics.mean(away_team_df['OU_Cover'].tail(20)) if len(away_team_df) != 0 else 0.5
            away_ou_pct_10 = statistics.mean(away_team_df['OU_Cover'].tail(10)) if len(away_team_df) != 0 else 0.5
            away_ou_pct_5 = statistics.mean(away_team_df['OU_Cover'].tail(5)) if len(away_team_df) != 0 else 0.5
            
            home_opp_avg = statistics.mean(home_home_df['Away Score']) if len(home_home_df) != 0 else 3
            home_opp_avg_20 = statistics.mean(home_home_df['Away Score'].tail(20)) if len(home_home_df) != 0 else 3
            home_opp_avg_10 = statistics.mean(home_home_df['Away Score'].tail(10)) if len(home_home_df) != 0 else 3
            home_opp_avg_5 = statistics.mean(home_home_df['Away Score'].tail(5)) if len(home_home_df) != 0 else 3
            
            away_opp_avg = statistics.mean(away_away_df['Home Score']) if len(away_away_df) != 0 else 3
            away_opp_avg_20 = statistics.mean(away_away_df['Home Score'].tail(20)) if len(away_away_df) != 0 else 3
            away_opp_avg_10 = statistics.mean(away_away_df['Home Score'].tail(10)) if len(away_away_df) != 0 else 3
            away_opp_avg_5 = statistics.mean(away_away_df['Home Score'].tail(5)) if len(away_away_df) != 0 else 3
            
            home_score_over_ou_avg = round((len(home_team_df[home_team_df['Total_Score'] > ou]) / len(home_team_df)) if len(home_team_df) != 0 else 0, 2)
            home_score_over_ou_avg_20 = (len(home_team_df.tail(20)[home_team_df.tail(20)['Total_Score'] > ou]) / len(home_team_df.tail(20))) if len(home_team_df) != 0 else 0
            home_score_over_ou_avg_10 = (len(home_team_df.tail(10)[home_team_df.tail(10)['Total_Score'] > ou]) / len(home_team_df.tail(10))) if len(home_team_df) != 0 else 0
            home_score_over_ou_avg_5 = (len(home_team_df.tail(5)[home_team_df.tail(5)['Total_Score'] > ou]) / len(home_team_df.tail(5))) if len(home_team_df) != 0 else 0
            
            away_score_over_ou_avg = round((len(away_team_df[away_team_df['Total_Score'] > ou]) / len(away_team_df)) if len(away_team_df) != 0 else 0, 2)
            away_score_over_ou_avg_20 = (len(away_team_df.tail(20)[away_team_df.tail(20)['Total_Score'] > ou]) / len(away_team_df.tail(20))) if len(away_team_df) != 0 else 0
            away_score_over_ou_avg_10 = (len(away_team_df.tail(10)[away_team_df.tail(10)['Total_Score'] > ou]) / len(away_team_df.tail(10))) if len(away_team_df) != 0 else 0
            away_score_over_ou_avg_5 = (len(away_team_df.tail(5)[away_team_df.tail(5)['Total_Score'] > ou]) / len(away_team_df.tail(5))) if len(away_team_df) != 0 else 0
            
            home_home_score_over_ou_avg = round((len(home_home_df[home_home_df['Total_Score'] > ou]) / len(home_home_df)) if len(home_home_df) != 0 else 0, 2)
            home_home_score_over_ou_avg_20 = (len(home_home_df.tail(20)[home_home_df.tail(20)['Total_Score'] > ou]) / len(home_home_df.tail(20))) if len(home_home_df) != 0 else 0
            home_home_score_over_ou_avg_10 = (len(home_home_df.tail(10)[home_home_df.tail(10)['Total_Score'] > ou]) / len(home_home_df.tail(10))) if len(home_home_df) != 0 else 0
            home_home_score_over_ou_avg_5 = (len(home_home_df.tail(5)[home_home_df.tail(5)['Total_Score'] > ou]) / len(home_home_df.tail(5))) if len(home_home_df) != 0 else 0
            
            away_away_score_over_ou_avg = round((len(away_away_df[away_away_df['Total_Score'] > ou]) / len(away_away_df)) if len(away_away_df) != 0 else 0, 2)
            away_away_score_over_ou_avg_20 = (len(away_away_df.tail(20)[away_away_df.tail(20)['Total_Score'] > ou]) / len(away_away_df.tail(20))) if len(away_away_df) != 0 else 0
            away_away_score_over_ou_avg_10 = (len(away_away_df.tail(10)[away_away_df.tail(10)['Total_Score'] > ou]) / len(away_away_df.tail(10))) if len(away_away_df) != 0 else 0
            away_away_score_over_ou_avg_5 = (len(away_away_df.tail(5)[away_away_df.tail(5)['Total_Score'] > ou]) / len(away_away_df.tail(5))) if len(away_away_df) != 0 else 0
                    
            #Need to make df and then concat, test and should be good
            try:
                game_data = {"Date": [formatted_date], "Year": [int(str(data_date)[0:4])], "Home Team": [home_team], "Home Score": [home_score], "Away Team": [away_team], "Away Score": [away_score], "Home_Team_Win": [home_team_win],"OU": [ou], "Over Open Odds": [over_odds], "Under Open": [under_line], "Under Open Odds": under_odds, "Home ML Open": [home_ml], "Away ML Open": [away_ml], "Total_Score":total_score, "OU_Cover": ou_cover, "Home_GP": [home_gp], "Away_GP": [away_gp], "Home_W_PCT": [home_win_pct], "Away_W_PCT": [away_win_pct], "Home_Avg_Score": [home_avg_score], "Away_Avg_Score": [away_avg_score], "Home_Avg_Total_Score": [home_avg_tot_score], "Home_Avg_Total_Score_20": [home_avg_tot_score_20], "Home_Avg_Total_Score_10": [home_avg_tot_score_10], "Home_Avg_Total_Score_5": [home_avg_tot_score_5], "Away_Avg_Total_Score": [away_avg_tot_score], "Away_Avg_Total_Score_20": [away_avg_tot_score_20], "Away_Avg_Total_Score_10": [away_avg_tot_score_10], "Away_Avg_Total_Score_5": [away_avg_tot_score_5], "Home_OU_PCT": [home_ou_pct], "Home_OU_PCT_20": [home_ou_pct_20], "Home_OU_PCT_10": [home_ou_pct_10], "Home_OU_PCT_5": [home_ou_pct_5], "Away_OU_PCT": [away_ou_pct], "Away_OU_PCT_20": [away_ou_pct_20], "Away_OU_PCT_10": [away_ou_pct_10], "Away_OU_PCT_5": [away_ou_pct_5], "Home_Opp_Avg": [home_opp_avg], "Home_Opp_Avg_20": [home_opp_avg_20], "Home_Opp_Avg_10": [home_opp_avg_10], "Home_Opp_Avg_5": [home_opp_avg_5], "Away_Opp_Avg": [away_opp_avg], "Away_Opp_Avg_20": [away_opp_avg_20], "Away_Opp_Avg_10": [away_opp_avg_10], "Away_Opp_Avg_5": [away_opp_avg_5], "Game_ID": [game_id], "Home_Score_Over_OU_Avg": [home_score_over_ou_avg], "Home_Score_Over_OU_Avg_20": [home_score_over_ou_avg_20], "Home_Score_Over_OU_Avg_10": [home_score_over_ou_avg_10], "Home_Score_Over_OU_Avg_5": [home_score_over_ou_avg_5], "Away_Score_Over_OU_Avg": [away_score_over_ou_avg], "Away_Score_Over_OU_Avg_20": [away_score_over_ou_avg_20], "Away_Score_Over_OU_Avg_10": [away_score_over_ou_avg_10], "Away_Score_Over_OU_Avg_5": [away_score_over_ou_avg_5], "Home_Home_Score_Over_OU_Avg": [home_home_score_over_ou_avg], "Home_Home_Score_Over_OU_Avg_20": [home_home_score_over_ou_avg_20], "Home_Home_Score_Over_OU_Avg_10": [home_home_score_over_ou_avg_10], "Home_Home_Score_Over_OU_Avg_5": [home_home_score_over_ou_avg_5], "Away_Away_Score_Over_OU_Avg": [away_away_score_over_ou_avg], "Away_Away_Score_Over_OU_Avg_20": [away_away_score_over_ou_avg_20], "Away_Away_Score_Over_OU_Avg_10": [away_away_score_over_ou_avg_10], "Away_Away_Score_Over_OU_Avg_5": [away_away_score_over_ou_avg_5]}
            except:
                continue

            game_data_df = pd.DataFrame(game_data)
            master_data_df = pd.concat([master_data_df, game_data_df], ignore_index = True)
    # Replace 'my_database.db' with the path to your SQLite database file
    conn = sqlite3.connect(DATABASE_PATH)
    master_data_df.to_sql('dataset', con=conn, if_exists='replace', index=False)
    conn.commit()
    conn.close()
    #print("Done Updating Data")