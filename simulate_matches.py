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
            team_stats[team1] = {'wins': 0, 'games': 0, 'points': 0, 'results': {}, '4-0': 0, '3-1': 0, '3-2': 0, '0-4': 0, '1-3': 0, '2-3': 0}
        if team2 not in team_stats:
            team_stats[team2] = {'wins': 0, 'games': 0, 'points': 0, 'results': {}, '4-0': 0, '3-1': 0, '3-2': 0, '0-4': 0, '1-3': 0, '2-3': 0}
        
        if team2 not in team_stats[team1]['results']:
            team_stats[team1]['results'][team2] = 0
        if team1 not in team_stats[team2]['results']:
            team_stats[team2]['results'][team1] = 0

        team_stats[team1]['games'] += 1
        team_stats[team2]['games'] += 1
        team_stats[team1][f'{score1}-{score2}'] += 1
        team_stats[team2][f'{score2}-{score1}'] += 1
        team_stats[team1]['results'][team2] += 5 - score2
        team_stats[team2]['results'][team1] += 5 - score1
        
        if score1 > score2:
            team_stats[team1]['wins'] += 1
            team_stats[team1]['points'] += 5 - score2
            team_stats[team2]['points'] += score2
        else:
            team_stats[team2]['wins'] += 1
            team_stats[team2]['points'] += 5 - score1
            team_stats[team1]['points'] += score1
    probabilities = {
        team: {'results': stats['results'], 
               '4-0':stats['4-0']/stats['games'], '3-1':stats['3-1']/stats['games'], '3-2':stats['3-2']/stats['games'], 
               '0-4':stats['0-4']/stats['games'], '1-3':stats['1-3']/stats['games'], '2-3':stats['2-3']/stats['games']}
        for team, stats in team_stats.items()
    }
    
    return probabilities

# Step 3: Predict the most likely outcomes for each match
def predict_match_outcomes(remaining_matches, probabilities):
    outcomes = []
    teams = []
    chances = []
    for _, row in remaining_matches.iterrows():
        team1, team2 = row['Team thuis'], row['Team uit']
        probs1: dict = probabilities.get(team1, {}).get('results', {})
        probs2: dict = probabilities.get(team2, {}).get('results', {})
        
        old_res1 = probs1.get(team2, 0)
        old_res2 = probs2.get(team1, 0)
        winning_chance = (old_res1 / old_res2 if old_res2 != 0 else 0) - (old_res2 / old_res1 if old_res1 != 0 else 0)
        chances.append(winning_chance)
        teams.append((team1, team2))

        # Normalize probabilities
        # for item1, item2 in zip(probs1.items(), probs2.items()):
            # key, item1 = item1
            # key, item2 = item2
            # probs1[key] = item1 / (item1 + item2) if item1 + item2 != 0 else 0
            # probs2[key] = item2 / (item1 + item2) if item1 + item2 != 0 else 0
        continue
        outcome = 0 
        prev = 0
        for item1, item2 in zip(probs1.items(), probs2.items()):
            key, prob1 = item1
            key, prob2 = item2
            if abs(prob1 - prob2) > prev:
                outcome = key
                prev = abs(prob1 - prob2)
            print(key, abs(prob1 - prob2))
        print(f'{team1} vs. {team2}: {outcome}, {prev}')
    chances = np.array(chances)
    chances = chances/abs(chances).max()*.5 + .5
    print(list(zip(teams, chances)))
        # Likely outcomes based on probabilities
        # if prob1 > prob2:
        #     outcomes.append((team1, team2, '4-0', 5, 0))
        # else:
        #     outcomes.append((team2, team1, '4-0', 5, 0))
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
    print()
    predicted_outcomes = predict_match_outcomes(remaining_matches, probabilities)
    # print(predicted_outcomes)
    # final_standings = simulate_standings(standings, predicted_outcomes)
    # print("Final Standings:", final_standings)

# Run the program
if __name__ == "__main__":
    main()