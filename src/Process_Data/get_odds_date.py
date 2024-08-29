import requests
import json

def get_odds_date(date):
    api_key = 'cc6a6fc8a39e1388fe832d260fbda738'
    sport = 'baseball_mlb'
    region = 'us'  # Change depending on your region, e.g., uk, eu, au
    mkt = 'totals,h2h'  # Type of odds you are interested in, e.g., h2h, spreads, totals
    bookmakers = 'fanduel'
    api_date = date + 'T12:00:00Z'


    # Construct the API URL
    url = f'https://api.the-odds-api.com/v4/historical/sports/{sport}/odds/?apiKey={api_key}&regions=us&markets={mkt}&oddsFormat=american&date={api_date}&bookmakers={bookmakers}'

    # Make the request
    response = requests.get(url)
    data = response.json()

    # Check if the request was successful
    if response.status_code != 200:
        print("Failed to retrieve data:", response.status_code, data)
    
    all_odds_data = []
    for temp_game in data['data']:
        odds_data = {}
        odds_data['Home_Team'] = temp_game['home_team']
        odds_data['Away_Team'] = temp_game['away_team']
        for bookmaker in temp_game['bookmakers']:
            for market in bookmaker['markets']:
                if market['key'] == 'h2h':
                    for outcome in market['outcomes']:
                        if outcome['name'] == temp_game['home_team']:
                            odds_data['Home_ML'] = outcome['price']
                        elif outcome['name'] == temp_game['away_team']:
                            odds_data['Away_ML'] = outcome['price']
                if market['key'] == 'totals':
                    for outcome in market['outcomes']:
                        if outcome['name'] == 'Over':
                            odds_data['Over_Line'] = outcome['point']
                            odds_data['Over_Odds'] = outcome['price']
                        elif outcome['name'] == 'Under':
                            odds_data['Under_Line'] = outcome['point']
                            odds_data['Under_Odds'] = outcome['price']
        all_odds_data.append(odds_data)
    return all_odds_data
        