import pandas as pd
import numpy as np

# Match probability to match result
def prob_mapping(prob):
    thresholds = [
        (0.75, '4-0', 4, 0),
        (0.6, '3-1', 3, 1),
        (0.55, '3-2', 3, 2),
        (0.45, '2-3', 2, 3),
        (0.4, '1-3', 2, 3),
        (0.25, '0-4', 0, 4),
        (0.0, '0-4', 0, 4),
    ]
    for threshold, result, points1, points2 in thresholds:
        if prob >= threshold:
            return result, points1, points2
    return None, 0, 0

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
        if pd.isna(row['Uitslag']):
            score1, score2 = 3, 2
        else:
            score1, score2 = map(int, row['Uitslag'].split('-'))
        
        if team1 not in team_stats:
            team_stats[team1] = {'wins': 0, 'games': 0, 'points': 0, 'results': {}, 'score_dist': {}}
        if team2 not in team_stats:
            team_stats[team2] = {'wins': 0, 'games': 0, 'points': 0, 'results': {}, 'score_dist': {}}
        
        team_stats[team1]['games'] += 1
        team_stats[team2]['games'] += 1
        team_stats[team1]['results'][team2] = team_stats[team1]['results'].get(team2, 0) + (5 - score2)
        team_stats[team2]['results'][team1] = team_stats[team2]['results'].get(team1, 0) + (5 - score1)
        
        score_str = f"{score1}-{score2}"
        team_stats[team1]['score_dist'][score_str] = team_stats[team1]['score_dist'].get(score_str, 0) + 1
        team_stats[team2]['score_dist'][score_str] = team_stats[team2]['score_dist'].get(score_str, 0) + 1
        
        if score1 > score2:
            team_stats[team1]['wins'] += 1
            team_stats[team1]['points'] += 5 - score2
            team_stats[team2]['points'] += score2
        else:
            team_stats[team2]['wins'] += 1
            team_stats[team2]['points'] += 5 - score1
            team_stats[team1]['points'] += score1
    
    probabilities = {
        team: {'results': stats['results'], 'points': stats['points'], 'score_dist': stats['score_dist']}
        for team, stats in team_stats.items()
    }
    return probabilities


# Step 3: Predict the most likely outcomes for each match
def predict_match_outcomes(remaining_matches, probabilities):
    outcomes = []
    chances = []

    for _, row in remaining_matches.iterrows():
        team1, team2 = row['Team thuis'], row['Team uit']
        probs1 = probabilities.get(team1, {}).get('results', {})
        probs2 = probabilities.get(team2, {}).get('results', {})

        old_res1 = probs1.get(team2, 0)
        old_res2 = probs2.get(team1, 0)
        old_total = old_res1 + old_res2
        if old_total == 0:
            winning_chance = 0
        else:
            winning_chance = ((old_res1 - old_res2) / old_total)*.5 + .5

        outcome, points1, points2 = prob_mapping(winning_chance)
        if outcome is None:
            cur_points1 = probabilities.get(team1, {}).get('points', 0)
            cur_points2 = probabilities.get(team2, {}).get('points', 0)
            cur_total = cur_points1 + cur_points2
            if cur_total == 0:
                chance = 0.5
            else:
                chance = ((cur_points1 - cur_points2)/cur_total)*.5 + .5
                
            # print(chance)

            outcome, points1, points2 = prob_mapping(chance)

        outcomes.append((team1, team2, outcome, points1, points2))
    

    return outcomes

# Step 4: Simulate the final standings
def simulate_standings(standings, outcomes):
    standings = standings.set_index('Teamnaam')

    for winner, loser, _, winner_points, loser_points in outcomes:
        if winner in standings.index:
            standings.at[winner, 'Punten'] += winner_points
        if loser in standings.index:
            standings.at[loser, 'Punten'] += loser_points

    return standings.sort_values(by='Punten', ascending=False)

# Main execution flow
def main():
    standings_file = 'Standen Heren 4e Klasse.csv'
    past_results_file = 'Resultaten.csv'
    remaining_matches_file = 'Wedstrijden.csv'

    standings, past_results, remaining_matches = read_csv_files(
        standings_file, past_results_file, remaining_matches_file
    )
    probabilities = calculate_win_probabilities(past_results)
    predicted_outcomes = predict_match_outcomes(remaining_matches, probabilities)
    final_standings = simulate_standings(standings, predicted_outcomes)

    final_standings[['Punten']].to_csv(f"predicted_final_standings_{len(remaining_matches)}_matches_remaining.csv")

# Run the program
if __name__ == "__main__":
    main()