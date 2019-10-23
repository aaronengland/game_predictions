# dependencies
import pandas as pd
import numpy as np

# define a function
def game_predictions(home_team_array, home_score_array, away_team_array, away_score_array, home_team, away_team, distribution='poisson', outer_weighted_mean='none', inner_weighted_mean='none', weight_home=None, weight_away=None, n_simulations=1000):
    # suppress the SettingWithCopyWarning
    pd.options.mode.chained_assignment = None
    
    # create a df
    # put the arrays into a df
    df = pd.DataFrame({'home_team': home_team_array,
                       'home_score': home_score_array,
                       'away_team': away_team_array,
                       'away_score': away_score_array})
    # get winning team
    df['winning_team'] = df.apply(lambda x: x['home_team'] if x['home_score'] > x['away_score'] else x['away_team'], axis=1)

    # get win pct for each team for weighting later
    # get all teams
    list_all_teams = list(df['home_team']) + list(df['away_team'])
    # get the unique ones
    list_teams_unique = list(dict.fromkeys(list_all_teams))
    # get win pct for each team
    list_win_pct = []
    for team in list_teams_unique:
        # subset to where home team or away team == team
        df_subset = df[(df['home_team'] == team) | (df['away_team'] == team)]
        # see how many times team is in winning_team
        n_wins = list(df_subset['winning_team']).count(team)
        # get number of games
        n_games = df_subset.shape[0]
        # get win pct
        win_pct = n_wins/n_games
        # if we have zero win pct make it .01
        if win_pct == 0:
            win_pct = 0.01
        # append to list
        list_win_pct.append(win_pct)
    # match win_pct with team
    df_win_pct = pd.DataFrame({'team': list_teams_unique,
                               'win_pct': list_win_pct})

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
            # 1. get mean points scored by the home team when they are the home team and points allowed by the home team when they 
            # subset to games where home_team == home_team
            df_home = df[df['home_team'] == home_team]
            # if using all games
            if outer_weighted_mean == 'all_games_weighted':
                # get all the games where the home_team was playing
                df_home = df[(df['home_team'] == home_team) | (df['away_team'] == home_team)]
                # rename the columns because it helps some of the logic later
                df_home.columns = ['home_team','home_pts','away_team','away_pts','winning_team']
                # get points scored by home team (name the col home_score so it will match with the other logic we have)
                df_home['home_score'] = df_home.apply(lambda x: x['home_pts'] if x['home_team'] == home_team else x['away_pts'], axis=1)
                # get the points allowed by the home team
                df_home['away_score'] = df_home.apply(lambda x: x['home_pts'] if x['home_team'] != home_team else x['away_pts'], axis=1)
                # mark games where the home_team is home with a number (i.e., 2)
                df_home['weights'] = df_home.apply(lambda x: weight_home if x['home_team'] == home_team else 1, axis=1)
                # save weights
                list_weights = list(df_home['weights'])
            # if outer_weighted_mean == 'none'
            if outer_weighted_mean == 'none':
                # generate list of 1s for weights
                list_weights = [1 for x in range(df_home.shape[0])]
            # if outer_weighted_mean == 'time'
            elif outer_weighted_mean == 'time':
                # generate list of 1 to n for weights
                list_weights = [x for x in range(1, df_home.shape[0]+1)]
            # outer_weighted_mean == 'opp_win_pct'
            else: # if outer_weighted_mean == 'opp_win_pct':
                # get list of opponents
                list_df_home_opp = list(df_home['away_team'])
                # get win pct for each team in list_df_home_opp so we can use them as weights
                list_weights = []
                for opp in list_df_home_opp:
                    # find index of opp in df_win_pct
                    index_opp = list(df_win_pct['team']).index(opp)
                    # get win pct
                    win_pct = df_win_pct['win_pct'][index_opp]
                    # append to list
                    list_weights.append(win_pct)
            
            # calculate mean of home_score
            home_home_score_mean = np.average(df_home['home_score'], weights=list_weights)
            # get mean of away_score
            home_away_score_mean = np.average(df_home['away_score'], weights=list_weights)
            
            # if distribution == 'poisson'
            if distribution == 'poisson':
                # draw a random number from a poisson distribution for predicted home score
                pred_home_home_score = np.random.poisson(home_home_score_mean, 1)
                # draw a random number from a poisson distribution for predicted away score
                pred_home_away_score = np.random.poisson(home_away_score_mean, 1)
            # if distribution == 'normal'
            else:
                # calculate sd of home_score (for normal distribution)
                home_home_score_sd = np.sqrt(np.average((df_home['home_score']-home_home_score_mean)**2, weights=list_weights))
                # get sd of away_score
                home_away_score_sd = np.sqrt(np.average((df_home['away_score']-home_away_score_mean)**2, weights=list_weights))
                # draw a random number from a normal distribution
                pred_home_home_score = np.random.normal(loc=home_home_score_mean, scale=home_home_score_sd, size=1)
                # draw a random number from a normal distribution
                pred_home_away_score = np.random.normal(loc=home_away_score_mean, scale=home_away_score_sd, size=1)
                
            # 2. repeat the same steps but using the away team
            # subset to games where away_team == away_team
            df_away = df[df['away_team'] == away_team]
            # if using all games
            if outer_weighted_mean == 'all_games_weighted':
                # get all the games where the away_team was playing
                df_away = df[(df['home_team'] == away_team) | (df['away_team'] == away_team)]
                # rename the columns because it helps some of the logic later
                df_away.columns = ['home_team','home_pts','away_team','away_pts','winning_team']
                # get points scored by away team (name the col away_score so it will match with the other logic we have)
                df_away['away_score'] = df_away.apply(lambda x: x['away_pts'] if x['away_team'] == away_team else x['home_pts'], axis=1)
                # get the points allowed by the home team
                df_away['home_score'] = df_away.apply(lambda x: x['away_pts'] if x['away_team'] != away_team else x['home_pts'], axis=1)
                # mark games where the away_team is away with a number (i.e., 2)
                df_away['weights'] = df_away.apply(lambda x: weight_away if x['away_team'] == away_team else 1, axis=1)
                # save weights
                list_weights = list(df_away['weights'])
            # if outer_weighted_mean == 'none'
            elif outer_weighted_mean == 'none':
                # generate list of 1s for weights
                list_weights = [1 for x in range(df_away.shape[0])]
            # if outer_weighted_mean == 'time'
            elif outer_weighted_mean == 'time':
                # generate list of 1 to n for weights
                list_weights = [x for x in range(1, df_away.shape[0]+1)]
            # outer_weighted_mean == 'opp_win_pct'
            else: # if outer_weighted_mean == 'opp_win_pct':
                # get list of opponents
                list_df_away_opp = list(df_away['home_team'])
                # get win pct for each team in list_df_home_opp so we can use them as weights
                list_weights = []
                for opp in list_df_away_opp:
                    # find index of opp in df_win_pct
                    index_opp = list(df_win_pct['team']).index(opp)
                    # get win pct
                    win_pct = df_win_pct['win_pct'][index_opp]
                    # append to list
                    list_weights.append(win_pct)
            
            # calculate mean of away_score
            away_away_score_mean = np.average(df_away['away_score'], weights=list_weights)
            # get mean of home_score
            away_home_score_mean = np.average(df_away['home_score'], weights=list_weights)
            
            # if distribution == 'poisson'
            if distribution == 'poisson':
                # draw a random number from a poisson distribution for predicted away score
                pred_away_away_score = np.random.poisson(away_away_score_mean, 1)
                # draw a random number from a poisson distribution for predicted home score
                pred_away_home_score = np.random.poisson(away_home_score_mean, 1)
            # if distribution == 'normal'
            else:
                # calculate sd of home_score (for normal distribution)
                away_away_score_sd = np.sqrt(np.average((df_away['away_score']-away_away_score_mean)**2, weights=list_weights))
                # get sd of away_score
                away_home_score_sd = np.sqrt(np.average((df_away['home_score']-away_home_score_mean)**2, weights=list_weights))
                # draw a random number from a normal distribution
                pred_away_away_score = np.random.normal(loc=away_away_score_mean, scale=away_away_score_sd, size=1)
                # draw a random number from a normal distribution
                pred_away_home_score = np.random.normal(loc=away_home_score_mean, scale=away_home_score_sd, size=1)
        
            # 3. now let's have the scores meet in the middle
            # if we want a straight avg
            if inner_weighted_mean == 'none':
                list_weights = [1 for x in range(1, 3)]
            # if we want to weight in terms of win pct
            else:
                # get list of teams
                list_matchup_teams = [home_team, away_team]
                # get win pct for each team in list_df_home_opp so we can use them as weights
                list_weights = []
                for opp in list_matchup_teams:
                    # find index of opp in df_win_pct
                    index_opp = list(df_win_pct['team']).index(opp)
                    # get win pct
                    win_pct = df_win_pct['win_pct'][index_opp]
                    # append to list
                    list_weights.append(win_pct)
            
            # home score prediction
            home_score_prediction = np.average([pred_home_home_score[0], pred_away_home_score[0]], weights=list_weights)
            # away score prediction
            away_score_prediction = np.average([pred_home_away_score[0], pred_away_away_score[0]], weights=list_weights)
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
    
    # get winning team
    if prop_home_win >= .5:
        winning_team = home_team
    else:
        winning_team = away_team
    
    # create a dictionary to return objects
    dict_results = {'mean_home_pts': mean_home_score,
                    'mean_away_pts': mean_away_score,
                    'prob_home_win': prop_home_win,
                    'winning_team': winning_team}
    # return dict_results
    return dict_results
