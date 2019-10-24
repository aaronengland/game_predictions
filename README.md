# game_predictions

A package to predict points scored for the home team and away team as well as home team win probability based on previous performance.

To install, use: `pip install git+https://github.com/aaronengland/game_predictions.git`

How does it work?

At its core, the algorithm is very simple. It estimates the expected points scored and allowed by the home team as well as expected points scored and allowed by the away team. 

The predicted home score is an average of expected points scored by the home team and expected points allowed by the away team. The predicted away score is an average of expected points scored by the away team and expected points allowed by the away team.

Expected points scored by the home team, allowed by the away team, scored by the away team, and allowed by the home team are determined by setting the model's hyperparameters.

Arguments:
- `home_team_array`: array of the home team for each contest.
- `home_score_array`: array of the points scored by the home team for each contest.
- `away_team_array`: array of the away team for each contest.
- `away_score_array`: array of the points scored by the away team for each contest.
- `home_team`: string of the home team for the contest in which to predict.
- `away_team`: string of the home team for the contest in which to predict.
- `distribution`: distribution from which to draw random numbers (default = 'poisson')
- `outer_weighted_mean`: method in which to calculate mean home team points scored, away points allowed, away points scored, and home points allowed (options: `all_games_weighted`, `none`, `time`, and `opp_win_pct`).
  - `all_games_weighted`: all games involving the teams are used for mean points estimation, but are weighted using `weight_home` and/or `weight_away`. For example, if applying a weight to games where the home team is home, we would set the `weight_home` argument to a number greater than 1.
  - `none`: all games involving the teams are used for mean points estimation, but no weighting will be applied.
  - `time`: all games involving the teams are used for mean points estimation, but more weight is applied to more recent games.
- `opp_win_pct`: all games involving the teams are used for mean points estimation, but more weight is applied to games against teams with a greater win percentage.
- `inner_weighted_mean`: method in which to calculate predicted home points and predicted away points (default = 'none').
  - `none`: no weight applied to the average of points scored and points allowed.
  - `win_pct`: average of points scored and points allowed weighted by each team's win percentage.
- `weight_home`: weight to apply to the games when the home team is the home team (default = None).
- `weight_away`: weight tyo apply to the games when the away team is the away team (default = None).
- `n_simulations`: number of random draws (default = 1000).

Note: if `outer_weighted_mean` is not set to `all_games_weighted`, only games when the `home_team` is home and the `away_team` is away will be used. Thus, for earlyu season contests it is recommended to use `all_games_weighted`.

Returned is a dictionary containing:
- `mean_home_pts`: predicted points for the home team.
- `mean_away_pts`: predicted points for the away team.
- `prob_home_win`: probability of the home team winning.
- `winning_team`: predicted winning team.

Example:
```
# import dependencies
from game_predictions import game_predictions
import pandas as pd

# import data
df = pd.read_csv('data.csv')

# complete simulation(s)
game_simulation = game_predictions(home_team_array=df['home_team'], 
                                   home_score_array=df['home_score'], 
                                   away_team_array=df['away_team'], 
                                   away_score_array=df['away_score'], 
                                   home_team='Name of Home Team', 
                                   away_team='Name of Away Team',
                                   outer_weighted_mean='all_games_weighted',
                                   inner_weighted_mean='none',
                                   weight_home=2,
                                   weight_away=3,
                                   n_simulations=1000)
```
