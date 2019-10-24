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
- `weight_home`: (default = None).
- `weight_away`: (default = None).
- `n_simulations`: (default = 1000).






It uses points scored by the home team when they are the home team [1], points allowed by the away team when they are the away team [2], points scored by the away team when they are the away team [3], and points allowed by the home team when they are the home team [4] to generate predictions for home points scored and away points scored.

[1] <img src="https://latex.codecogs.com/gif.latex?\lambda&space;_{i}&space;=&space;\mu&space;_{HomePointsScored}" title="\lambda _{i} = \mu _{HomePointsScored}" /></a>

[2] <img src="https://latex.codecogs.com/gif.latex?\lambda&space;_{ii}&space;=&space;\mu&space;_{HomePointsAllowed}" title="\lambda _{ii} = \mu _{HomePointsAllowed}" /></a>

[3] <img src="https://latex.codecogs.com/gif.latex?\lambda&space;_{iii}&space;=&space;\mu&space;_{AwayPointsScored}" title="\lambda _{iii} = \mu _{AwayPointsScored}" /></a>

[4] <img src="https://latex.codecogs.com/gif.latex?\lambda&space;_{iv}&space;=&space;\mu&space;_{HomePointsAllowed}" title="\lambda _{iv} = \mu _{HomePointsAllowed}" /></a>

To predict points scored by the home team, a random draw is taken from a Poisson distribution [a] with a lambda of the mean (weighted or unweighted) points scored by the home team when they have been the home team [5]. This value is averaged with a random draw from a Poisson distribution with a lambda of the mean points allowed by the away team when they are the away team [6] [7].

[a]
![alt text](http://mathworld.wolfram.com/images/eps-gif/PoissonDistribution_700.gif)

[5] <img src="https://latex.codecogs.com/gif.latex?\chi&space;{_{i}}&space;=&space;Random_{\lambda&space;_{i}}" title="\chi {_{i}} = Random_{\lambda _{i}}" /></a>

[6] <img src="https://latex.codecogs.com/gif.latex?\chi&space;{_{ii}}&space;=&space;Random_{\lambda&space;_{ii}}" title="\chi {_{ii}} = Random_{\lambda _{ii}}" /></a>

[7] <a href="https://www.codecogs.com/eqnedit.php?latex=\mu&space;_{HomePoints}&space;=&space;\frac{\chi&space;_{i}&space;&plus;&space;\chi&space;_{ii}}{2}" target="_blank"><img src="https://latex.codecogs.com/gif.latex?\mu&space;_{HomePoints}&space;=&space;\frac{\chi&space;_{i}&space;&plus;&space;\chi&space;_{ii}}{2}" title="\mu _{HomePoints} = \frac{\chi _{i} + \chi _{ii}}{2}" /></a>

The same logic is used to predict points scored by the away team. To predict points scored by the away team, a random draw is taken from a Poisson distribution with a lambda of the mean points scored by the away team when they are the away team [8]. This value is averaged with a random draw from a Poisson distribution with a lambda of the mean points allowed by the home team when they are the home team [9] [10].

[8] <img src="https://latex.codecogs.com/gif.latex?\chi&space;_{iii}&space;=&space;Random&space;_{\lambda&space;_{iii}}" title="\chi _{iii} = Random _{\lambda _{iii}}" /></a>

[9] <img src="https://latex.codecogs.com/gif.latex?\chi&space;{_{iv}}&space;=&space;Random_{\lambda&space;_{iv}}" title="\chi {_{iv}} = Random_{\lambda _{iv}}" /></a>

[10] <img src="https://latex.codecogs.com/gif.latex?\mu&space;_{AwayPoints}&space;=&space;\frac{\chi&space;_{iii}&space;&plus;&space;\chi&space;_{iv}}{2}" title="\mu _{AwayPoints} = \frac{\chi _{iii} + \chi _{iv}}{2}" /></a>

This sequence of draws and calculations is repeated for ```n_simulations```. Probability of the home team winning is calculated by the sum of instances where the the predicted points scored by the home team is greater than the predicted points scored by the away team divided by ```n_simulations```[11].

[11] <img src="https://latex.codecogs.com/gif.latex?\mu&space;_{HomeWinProb}&space;=&space;\frac{\sum_{\eta&space;_{simulations}}&space;\mu&space;_{HomePoints}&space;>&space;\mu&space;_{AwayPoints}}{n&space;_{simulations}}" title="\mu _{HomeWinProb} = \frac{\sum_{\eta _{simulations}} \mu _{HomePoints} > \mu _{AwayPoints}}{n _{simulations}}" /></a>

Final predicted points scored by the home and away teams are calculated by taking the mean of the predicted points scored by the home team and away teams, respectively [12] [13].

[12] <img src="https://latex.codecogs.com/gif.latex?PredHomePoints&space;=&space;\frac{\sum_{\eta&space;_{simulations}}&space;\mu&space;_{HomePoints}}{n&space;_{simulations}}" title="PredHomePoints = \frac{\sum_{\eta _{simulations}} \mu _{HomePoints}}{n _{simulations}}" /></a>

[13] <img src="https://latex.codecogs.com/gif.latex?PredAwayPoints&space;=&space;\frac{\sum_{\eta&space;_{simulations}}&space;\mu&space;_{AwayPoints}}{n&space;_{simulations}}" title="PredAwayPoints = \frac{\sum_{\eta _{simulations}} \mu _{AwayPoints}}{n _{simulations}}" /></a>

Arguments:
- ```home_team_array```: array of the home team for each contest
- ```home_score_array```: array of the points scored by the home team for each contest
- ```away_team_array```: array of the away team for each contest
- ```away_score_array```: array of the points scored by the away team for each contest
- ```home_team```: string of the home team for the contest in which to predict
- ```away_team```: string of the home team for the contest in which to predict
- ```n_simulations```: number of draws from the Poisson distribution for each game (default = 1000)
- ```weighted_mean```: a boolean for the user to determine mean points scored/allowed as a weighted average (i.e., more recent games carry more weight; True) or a [regular] average (False; default = True)

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
                                   n_simulations=1000,
                                   weighted_mean=True)

# get distribution of home points
home_points_distribution = game_simulation.home_score_prediction_list

# get distribution of away points
away_points_distribution = game_simulation.away_score_prediction_list

# get the predicted home score
predicted_home_score = game_simulation.mean_home_score

# get the predicted away score
predicted_away_score = game_simulation.mean_away_score

# get the predicted win probability
predicted_win_probability = game_simulation.prop_home_win
```
