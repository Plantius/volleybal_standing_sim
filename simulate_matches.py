import pandas as pd
from itertools import product
import numpy as np

# Step 1: Parse CSV files
def read_csv_files(standings_file, past_results_file, remaining_matches_file):
    standings = pd.read_csv(standings_file)
    past_results = pd.read_csv(past_results_file)
    remaining_matches = pd.read_csv(remaining_matches_file)
    return standings, past_results, remaining_matches

# Step 2: Predict match outcomes using historical data
def calculate_win_probabilities(past_results):
    team_stats = {}
    
    for _, row in past_results.iterrows():
        team1, team2 = row['Team thuis'], row['Team uit']
        if row['Uitslag'] is np.nan:
            score1, score2 = [3, 2]
        else:
            score1, score2 = [int(x) for x in row['Uitslag'].split('-')]

        if team1 not in team_stats:
            team_stats[team1] = {'wins': 0, 'games': 0, 'points': 0, '4-0': 0, '3-1': 0, '3-2': 0, '0-4': 0, '1-3': 0, '2-3': 0}
        if team2 not in team_stats:
            team_stats[team2] = {'wins': 0, 'games': 0, 'points': 0, '4-0': 0, '3-1': 0, '3-2': 0, '0-4': 0, '1-3': 0, '2-3': 0}
        
        team_stats[team1]['games'] += 1
        team_stats[team2]['games'] += 1
        team_stats[team1][f'{score1}-{score2}'] += 1
        team_stats[team2][f'{score2}-{score1}'] += 1
        
        if score1 > score2:
            team_stats[team1]['wins'] += 1
            team_stats[team1]['points'] += 5 - score2
            team_stats[team2]['points'] += score2
        else:
            team_stats[team2]['wins'] += 1
            team_stats[team2]['points'] += 5 - score1
            team_stats[team1]['points'] += score1
        
    print(team_stats)
    probabilities = {
        team: stats['wins'] / stats['games']
        for team, stats in team_stats.items()
    }
    
    return probabilities

# Step 3: Predict the most likely outcomes for each match
def predict_match_outcomes(remaining_matches, probabilities):
    outcomes = []
    
    for _, row in remaining_matches.iterrows():
        team1, team2 = row['Team1'], row['Team2']
        prob1 = probabilities.get(team1, 0.5)
        prob2 = probabilities.get(team2, 0.5)
        
        # Normalize probabilities
        prob1, prob2 = prob1 / (prob1 + prob2), prob2 / (prob1 + prob2)
        
        # Likely outcomes based on probabilities
        if prob1 > prob2:
            outcomes.append((team1, team2, '4-0', 5, 0))
        else:
            outcomes.append((team2, team1, '4-0', 5, 0))
    
    return outcomes

# Step 4: Simulate the final standings
def simulate_standings(standings, outcomes):
    standings = standings.set_index('Team')
    
    for winner, loser, score, winner_points, loser_points in outcomes:
        standings.loc[winner, 'Points'] += winner_points
        standings.loc[loser, 'Points'] += loser_points
    
    return standings.sort_values(by='Points', ascending=False)

# Main execution flow
def main():
    standings_file = 'Standen Heren 4e Klasse.csv'
    past_results_file = 'Resultaten.csv'
    remaining_matches_file = 'Wedstrijden.csv'

    standings, past_results, remaining_matches = read_csv_files(
        standings_file, past_results_file, remaining_matches_file
    )

    probabilities = calculate_win_probabilities(past_results)
    print("Probabilities:", probabilities)
    # predicted_outcomes = predict_match_outcomes(remaining_matches, probabilities)

    # final_standings = simulate_standings(standings, predicted_outcomes)
    # print("Final Standings:", final_standings)

# Run the program
if __name__ == "__main__":
    main()