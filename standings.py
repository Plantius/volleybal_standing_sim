import csv
from collections import defaultdict

# Load current standings
def load_standings(filename):
    standings = {}
    with open(filename, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            team = row['Teamnaam']
            standings[team] = {
                'Wedstrijden': int(row['Wedstrijden']),
                'Punten': int(row['Punten']),
                'Sets voor': int(row['Sets voor']),
                'Sets tegen': int(row['Sets tegen']),
                'Punten voor': int(row['Punten voor']),
                'Punten tegen': int(row['Punten tegen'])
            }
    return standings

# Load remaining matches
def load_matches(filename):
    matches = []
    with open(filename, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            matches.append((row['Team thuis'], row['Team uit']))
    return matches

# Load previous results to calculate team performance
def load_previous_results(filename):
    team_performance = defaultdict(lambda: {'matches_played': 0, 'sets_won': 0, 'sets_lost': 0, 'points_won': 0, 'points_lost': 0})
    with open(filename, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            home_team = row['Team thuis']
            away_team = row['Team uit']
            set_scores = row['Setstanden'].split(", ")
            home_sets_won = 0
            away_sets_won = 0
            for score in set_scores:
                home_points, away_points = map(int, score.split("-"))
                if home_points > away_points:
                    home_sets_won += 1
                else:
                    away_sets_won += 1
                team_performance[home_team]['points_won'] += home_points
                team_performance[home_team]['points_lost'] += away_points
                team_performance[away_team]['points_won'] += away_points
                team_performance[away_team]['points_lost'] += home_points

            team_performance[home_team]['matches_played'] += 1
            team_performance[away_team]['matches_played'] += 1
            team_performance[home_team]['sets_won'] += home_sets_won
            team_performance[home_team]['sets_lost'] += away_sets_won
            team_performance[away_team]['sets_won'] += away_sets_won
            team_performance[away_team]['sets_lost'] += home_sets_won

    return team_performance

# Simulate a match based on historical performance
def simulate_match(standings, home_team, away_team, team_performance):
    # Calculate average sets won and lost per match for each team
    home_avg_sets_won = team_performance[home_team]['sets_won'] / team_performance[home_team]['matches_played']
    home_avg_sets_lost = team_performance[home_team]['sets_lost'] / team_performance[home_team]['matches_played']
    away_avg_sets_won = team_performance[away_team]['sets_won'] / team_performance[away_team]['matches_played']
    away_avg_sets_lost = team_performance[away_team]['sets_lost'] / team_performance[away_team]['matches_played']

    # Predict the outcome based on average performance
    if home_avg_sets_won > away_avg_sets_won:
        # Home team is stronger
        if home_avg_sets_lost < 1.5:  # Likely to win 3-0 or 3-1
            if home_avg_sets_won > 3:
                result = (3, 0)  # 3-0 win
            else:
                result = (3, 1)  # 3-1 win
        else:
            result = (3, 2)  # 3-2 win
    else:
        # Away team is stronger
        if away_avg_sets_lost < 1.5:  # Likely to win 3-0 or 3-1
            if away_avg_sets_won > 3:
                result = (0, 3)  # 0-3 loss
            else:
                result = (1, 3)  # 1-3 loss
        else:
            result = (2, 3)  # 2-3 loss

    # Update standings based on the predicted result
    home_sets_won, away_sets_won = result
    if home_sets_won > away_sets_won:
        if home_sets_won == 3 and away_sets_won == 0:
            standings[home_team]['Punten'] += 5
        elif home_sets_won == 3 and away_sets_won == 1:
            standings[home_team]['Punten'] += 4
            standings[away_team]['Punten'] += 1
        elif home_sets_won == 3 and away_sets_won == 2:
            standings[home_team]['Punten'] += 3
            standings[away_team]['Punten'] += 2
    else:
        if away_sets_won == 3 and home_sets_won == 0:
            standings[away_team]['Punten'] += 5
        elif away_sets_won == 3 and home_sets_won == 1:
            standings[away_team]['Punten'] += 4
            standings[home_team]['Punten'] += 1
        elif away_sets_won == 3 and home_sets_won == 2:
            standings[away_team]['Punten'] += 3
            standings[home_team]['Punten'] += 2

    standings[home_team]['Wedstrijden'] += 1
    standings[away_team]['Wedstrijden'] += 1
    standings[home_team]['Sets voor'] += home_sets_won
    standings[home_team]['Sets tegen'] += away_sets_won
    standings[away_team]['Sets voor'] += away_sets_won
    standings[away_team]['Sets tegen'] += home_sets_won

# Calculate final standings
def calculate_final_standings(standings, matches, team_performance):
    for home_team, away_team in matches:
        simulate_match(standings, home_team, away_team, team_performance)
    return standings

# Save final standings to CSV
def save_standings(standings, filename):
    with open(filename, mode='w', encoding='utf-8', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Ranking', 'Teamnaam', 'Wedstrijden', 'Punten', 'Sets voor', 'Sets tegen', 'Punten voor', 'Punten tegen'])
        sorted_standings = sorted(standings.items(), key=lambda x: x[1]['Punten'], reverse=True)
        for rank, (team, data) in enumerate(sorted_standings, start=1):
            writer.writerow([rank, team, data['Wedstrijden'], data['Punten'], data['Sets voor'], data['Sets tegen'], data['Punten voor'], data['Punten tegen']])

# Main function
def main():
    standings = load_standings('Standen Heren 4e Klasse.csv')
    matches = load_matches('Wedstrijden.csv')
    team_performance = load_previous_results('Resultaten.csv')
    final_standings = calculate_final_standings(standings, matches, team_performance)
    save_standings(final_standings, 'Finale Standen.csv')
    print("Final standings calculated and saved to 'Finale Standen.csv'.")

if __name__ == "__main__":
    main()