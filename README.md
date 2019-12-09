# game_predictions

A machine learning algorithm to predict points scored for the home team and away team as well as home team win probability based on previous performance.

To install, use: `pip install git+https://github.com/aaronengland/game_predictions.git`

How does it work?

At its core, the algorithm is very simple. It estimates the expected points scored and allowed by the home team as well as expected points scored and allowed by the away team. 

The predicted home score is an average of expected points scored by the home team and expected points allowed by the away team. The predicted away score is an average of expected points scored by the away team and expected points allowed by the away team.

Expected points scored by the home team, allowed by the away team, scored by the away team, and allowed by the home team are determined by setting the model's hyperparameters.

Arguments:
- `df`: data frame returned from `scrape_schedule` algorithm in `nfl_predictions` and `nba_predictions`.
- `home_team`: string of the home team for the contest in which to predict (example: `'New England Patriots'`).
- `away_team`: string of the home team for the contest in which to predict (example: `'New York Jets'`).
- `last_n_games`: integer value for number of games to subset (note: `'all'` will use all games; default = `'all'`).
- `outer_opp_win_pct`: Boolean whether or not to weight games by opponent win percentage (default = `True`).
- `central_tendency`: string of the central tendency in which to use (options: `mean`, `median`; default = `'mean'`).
- `distribution`: distribution from which to draw random numbers (options: `poisson`, `normal`; default = `'poisson'`)
- `inner_opp_win_pct`: Boolean whether or not to calculate predicted home points and predicted away points using win percentage (default = `True`).
- `weight_home`: integer weight to apply to the games when the home team is the home team (default = `1`).
- `weight_away`: integer weight to apply to the games when the away team is the away team (default = `1`).
- `n_simulations`: number of random draws (default = `1000`).

Returned is a dictionary containing:
- `mean_home_pts`: predicted points for the home team.
- `mean_away_pts`: predicted points for the away team.
- `prob_home_win`: probability of the home team winning.
- `winning_team`: predicted winning team.

Example:
```
# import dependencies
from nfl_predictions import scrape_schedule
from game_predictions import game_predictions

# scrape schedulde
df = scrape_schedule(year=2019)

# complete simulation(s)
game_simulation = game_predictions(df=df, 
                                   home_team='Chicago Bears', 
                                   away_team='Philadelphia Eagles',
                                   last_n_games_home='all',
                                   outer_opp_win_pct=True,
                                   central_tendency='mean',
                                   distribution='poisson',
                                   inner_opp_win_pct=True,
                                   weight_home=2,
                                   weight_away=3,
                                   n_simulations=1000)
```
