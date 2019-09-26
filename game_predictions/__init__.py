# dependencies
import pandas as pd
import numpy as np

# define a function
def game_predictions(home_team_array, home_score_array, away_team_array, away_score_array, home_team, away_team, n_simulations=1000, weighted_mean=True):
    # put the arrays into a df
    df = pd.DataFrame({'home_team': home_team_array,
                       'home_score': home_score_array,
                       'away_team': away_team_array,
                       'away_score': away_score_array})
    
    # instantiate lists for which to append
    home_score_prediction_list = []
    away_score_prediction_list = []
    # iterate through n_simulations
    for i in range(n_simulations):
        # set equal
        home_score_prediction = 0
        away_score_prediction = 0
        # to make sure there arent ties
        while home_score_prediction == away_score_prediction:
            # 1. get mean points scored by the homne team when they are the home team
            # subset to games where home_team == home_team
            df_home = df[df['home_team'] == home_team]
            # create a list of game number so we can use them as weights
            list_weights = list(np.arange(1,df_home.shape[0]+1))
            # include logic for weighted mean
            if weighted_mean == True:
                # get weighted mean of home_score
                home_score_mean = np.average(df_home['home_score'], weights=list_weights)
            else:
                # get mean of home_score
                home_score_mean = np.mean(df_home['home_score'])
            # generate a random number from a poisson distribution with this number as the lambda
            pred_home_score = np.random.poisson(home_score_mean, 1)
            # 2. get mean points allowed by the home team when they are the home team
            # include logic for weighted mean
            if weighted_mean == True:
                # get weighted mean of away_score
                pred_home_opponent_mean = np.average(df_home['away_score'], weights=list_weights)
            else:
                # get mean of away_score
                pred_home_opponent_mean = np.mean(df_home['away_score'])
            # generate a random number from a poisson distribution with this number as the lambda
            pred_home_opponent_score = np.random.poisson(pred_home_opponent_mean, 1)

            # 3. get mean points scored by the away team when they are away
            # subset to games where away_team == away_team
            df_away = df[df['away_team'] == away_team]
            # create a list of game number so we can use them as weights
            list_weights = list(np.arange(1,df_away.shape[0]+1))
            # include logic for weighted mean
            if weighted_mean == True:
                # get weighted mean of away_score
                away_score_mean = np.average(df_away['away_score'], weights=list_weights)
            else:
                # get mean of away_score
                away_score_mean = np.mean(df_away['away_score'])
            # generate a random number from a poisson distribution with this number as the lambda
            pred_away_score = np.random.poisson(away_score_mean, 1)
            # 4. get mean points allowed by the away team when they are away
            # include logic for weighted mean
            if weighted_mean == True:
                # get weighted mean of home_score
                pred_away_opponent_mean = np.average(df_away['home_score'], weights=list_weights)
            else:
                # get mean of home_score
                pred_away_opponent_mean = np.mean(df_away['home_score'])
            # generate a random number from poisson distribution with this number as the lambda
            pred_away_opponent_score = np.random.poisson(pred_away_opponent_mean, 1)

            # now let's have the scores meet in the middle
            # for the home team, get the average of pred_home_score and pred_away_opponent_score
            home_score_prediction = (pred_home_score[0] + pred_away_opponent_score[0])/2
            # for the away team, get the average of the pred_away_score and 
            away_score_prediction = (pred_away_score[0] + pred_home_opponent_score[0])/2
        # append to lists
        # home
        home_score_prediction_list.append(home_score_prediction)
        # away
        away_score_prediction_list.append(away_score_prediction)
    
    # get the proportion of games where the home team is > away team
    sum_home_wins = 0
    for i in range(len(home_score_prediction_list)):
        if home_score_prediction_list[i] > away_score_prediction_list[i]:
            sum_home_wins += 1
    prop_home_win = sum_home_wins/len(home_score_prediction_list)

    # get mean home score
    mean_home_score = np.mean(home_score_prediction_list)
    # get mean away score
    mean_away_score = np.mean(away_score_prediction_list)

    class Attributes:
        def __init__(self, home_score_prediction_list, away_score_prediction_list, sum_home_wins, prop_home_win, mean_home_score, mean_away_score):
            self.home_score_prediction_list = home_score_prediction_list
            self.away_score_prediction_list = away_score_prediction_list
            self.sum_home_wins = sum_home_wins
            self.prop_home_win = prop_home_win
            self.mean_home_score = mean_home_score
            self.mean_away_score = mean_away_score
    
    # save as returnable object
    x = Attributes(home_score_prediction_list, away_score_prediction_list, sum_home_wins, prop_home_win, mean_home_score, mean_away_score)
    return x
