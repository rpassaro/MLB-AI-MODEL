import pandas as pd
import sqlite3
import statistics
from datetime import datetime


def get_all_game_data(game_odds_data):    
    conn = sqlite3.connect("C:/Users/Ryan/Desktop/MLB_AI_Model/Data/dataset.sqlite")
    table_name = 'dataset'
    master_data_df = pd.read_sql_query(f"SELECT * FROM {table_name}",conn)
    conn.close()

    todays_date = str(datetime.today())
    todays_date = todays_date[0:4] + todays_date[5:7] + todays_date[8:10]

    home_team = get_right_abbr(game_odds_data[0])
    away_team = get_right_abbr(game_odds_data[1])
    master_data_df = master_data_df[(master_data_df['Year'] == 2024) & (master_data_df['Date'] < int(todays_date))]
    home_team_df = master_data_df[(master_data_df['Home Team'] == home_team) | (master_data_df['Away Team'] == home_team)]
    away_team_df = master_data_df[(master_data_df['Away Team'] == away_team) | (master_data_df['Home Team'] == away_team)]
    home_gp = len(home_team_df)
    away_gp = len(away_team_df)
    ou = game_odds_data[2]
    
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

    game_data = {"OU": [ou], "Over Open Odds": [game_odds_data[3]], "Home ML Open": [game_odds_data[4]], "Away ML Open": [game_odds_data[5]], "Home_GP": [home_gp], "Away_GP": [away_gp], "Home_W_PCT": [home_win_pct], "Away_W_PCT": [away_win_pct], "Home_Avg_Score": [home_avg_score], "Away_Avg_Score": [away_avg_score], "Home_Avg_Total_Score": [home_avg_tot_score], "Home_Avg_Total_Score_20": [home_avg_tot_score_20], "Home_Avg_Total_Score_10": [home_avg_tot_score_10], "Home_Avg_Total_Score_5": [home_avg_tot_score_5], "Away_Avg_Total_Score": [away_avg_tot_score], "Away_Avg_Total_Score_20": [away_avg_tot_score_20], "Away_Avg_Total_Score_10": [away_avg_tot_score_10], "Away_Avg_Total_Score_5": [away_avg_tot_score_5], "Home_OU_PCT": [home_ou_pct], "Home_OU_PCT_20": [home_ou_pct_20], "Home_OU_PCT_10": [home_ou_pct_10], "Home_OU_PCT_5": [home_ou_pct_5], "Away_OU_PCT": [away_ou_pct], "Away_OU_PCT_20": [away_ou_pct_20], "Away_OU_PCT_10": [away_ou_pct_10], "Away_OU_PCT_5": [away_ou_pct_5], "Home_Opp_Avg": [home_opp_avg], "Home_Opp_Avg_20": [home_opp_avg_20], "Home_Opp_Avg_10": [home_opp_avg_10], "Home_Opp_Avg_5": [home_opp_avg_5], "Away_Opp_Avg": [away_opp_avg], "Away_Opp_Avg_20": [away_opp_avg_20], "Away_Opp_Avg_10": [away_opp_avg_10], "Away_Opp_Avg_5": [away_opp_avg_5], "Home_Score_Over_OU_Avg": [home_score_over_ou_avg], "Home_Score_Over_OU_Avg_20": [home_score_over_ou_avg_20], "Home_Score_Over_OU_Avg_10": [home_score_over_ou_avg_10], "Home_Score_Over_OU_Avg_5": [home_score_over_ou_avg_5], "Away_Score_Over_OU_Avg": [away_score_over_ou_avg], "Away_Score_Over_OU_Avg_20": [away_score_over_ou_avg_20], "Away_Score_Over_OU_Avg_10": [away_score_over_ou_avg_10], "Away_Score_Over_OU_Avg_5": [away_score_over_ou_avg_5], "Home_Home_Score_Over_OU_Avg": [home_home_score_over_ou_avg], "Home_Home_Score_Over_OU_Avg_20": [home_home_score_over_ou_avg_20], "Home_Home_Score_Over_OU_Avg_10": [home_home_score_over_ou_avg_10], "Home_Home_Score_Over_OU_Avg_5": [home_home_score_over_ou_avg_5], "Away_Away_Score_Over_OU_Avg": [away_away_score_over_ou_avg], "Away_Away_Score_Over_OU_Avg_20": [away_away_score_over_ou_avg_20], "Away_Away_Score_Over_OU_Avg_10": [away_away_score_over_ou_avg_10], "Away_Away_Score_Over_OU_Avg_5": [away_away_score_over_ou_avg_5]}
    return game_data
    
def get_right_abbr(curr_abbr):
    if curr_abbr == "AZ":
        curr_abbr = "ARI"
    return curr_abbr