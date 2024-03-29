# dependencies
import pandas as pd
import numpy as np
import wquantiles as weighted

# define a function
def game_predictions(df, home_team, away_team, last_n_games='all', outer_opp_win_pct=True, central_tendency='mean', distribution='poisson', inner_opp_win_pct=True, weight_home=1, weight_away=1, n_simulations=1000):
    # suppress the SettingWithCopyWarning
    pd.options.mode.chained_assignment = None
    # drop unplayed games
    df = df.dropna(subset=['home_score'])
    
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
    
    # -------------------------------------------------------------------------

    # 1. get all the games where the home_team was playing
    df_home = df[(df['home_team'] == home_team) | (df['away_team'] == home_team)]
    
    # to prevent errors
    # get n_rows
    n_rows = df_home.shape[0]
    if (last_n_games != 'all') and last_n_games > n_rows:
        last_n_games = n_rows
    # use last n_games
    if last_n_games == 'all':
        df_home = df_home
    else:
        df_home = df_home.iloc[-last_n_games:]
    
    # rename the columns because it helps some of the logic later
    df_home.rename(columns={'home_score':'home_pts', 'away_score':'away_pts'}, inplace=True)
    # get points scored by home team (name the col home_score so it will match with the other logic we have)
    df_home['home_score'] = df_home.apply(lambda x: x['home_pts'] if x['home_team'] == home_team else x['away_pts'], axis=1)
    # get the points allowed by the home team
    df_home['away_score'] = df_home.apply(lambda x: x['home_pts'] if x['home_team'] != home_team else x['away_pts'], axis=1)
    # mark games where the home_team is home with a number (i.e., 2)
    df_home['weights'] = df_home.apply(lambda x: weight_home if x['home_team'] == home_team else 1, axis=1)
    
    # if we choose to weight each game by the opponents win %
    if outer_opp_win_pct == True:
        # get the name of the opponent
        df_home['opponent_name'] = df_home.apply(lambda x: x['home_team'] if x['away_team'] == home_team else x['away_team'], axis=1)
        # merge with df_win_pct to get opponent win %
        df_home = pd.merge(left=df_home, right=df_win_pct, left_on='opponent_name', right_on='team', how='left')
        # multiply 'weights' by 'win_pct'
        df_home['weights'] = df_home['weights'] * df_home['win_pct']
        
    # save weights
    list_weights = list(df_home['weights'])
    # some logic to catch errors
    if np.sum(list_weights) == 0:
        list_weights = [1 for x in list_weights]
    
    # get the central tendency number
    if central_tendency == 'mean':
        # calculate mean of home_score
        home_home_score_avg = np.average(df_home['home_score'], weights=list_weights)
        # get mean of away_score
        home_opponent_score_avg = np.average(df_home['away_score'], weights=list_weights)
    else:
        # calculate median home_score
        home_home_score_avg = weighted.median(df_home['home_score'], weights=list_weights)
        # get median of away_score
        home_opponent_score_avg = weighted.median(df_home['away_score'], weights=list_weights)
        
    # if distribution == 'poisson'
    if distribution == 'poisson':
        # draw a random number from a poisson distribution for predicted home score
        list_pred_home_home_score = list(np.random.poisson(home_home_score_avg, n_simulations))
        # draw a random number from a poisson distribution for predicted away score
        list_pred_home_opponent_score = list(np.random.poisson(home_opponent_score_avg, n_simulations))
    # if distribution == 'normal'
    else:
        # calculate sd of home_score (for normal distribution)
        home_home_score_sd = np.sqrt(np.average((df_home['home_score']-home_home_score_avg)**2, weights=list_weights))
        # get sd of away_score
        home_opponent_score_sd = np.sqrt(np.average((df_home['away_score']-home_opponent_score_avg)**2, weights=list_weights))
        # draw a random number from a normal distribution
        list_pred_home_home_score = list(np.random.normal(loc=home_home_score_avg, scale=home_home_score_sd, size=n_simulations))
        # draw a random number from a normal distribution
        list_pred_home_opponent_score = list(np.random.normal(loc=home_opponent_score_avg, scale=home_opponent_score_sd, size=n_simulations))
    
    # -------------------------------------------------------------------------
    
    # 2. repeat the same steps but using the away team
    # get all the games where the away_team was playing
    df_away = df[(df['home_team'] == away_team) | (df['away_team'] == away_team)]
    
    # to prevent errors
    # get n_rows
    n_rows = df_away.shape[0]
    if (last_n_games != 'all') and (last_n_games > n_rows):
        last_n_games = n_rows
    # use last n_games
    if last_n_games == 'all':
        df_away = df_away
    else:
        df_away = df_away.iloc[-last_n_games:]

    # rename the columns because it helps some of the logic later
    df_away.rename(columns={'home_score':'home_pts', 'away_score':'away_pts'}, inplace=True)
    # get points scored by away team (name the col away_score so it will match with the other logic we have)
    df_away['away_score'] = df_away.apply(lambda x: x['away_pts'] if x['away_team'] == away_team else x['home_pts'], axis=1)
    # get the points allowed by the home team
    df_away['home_score'] = df_away.apply(lambda x: x['away_pts'] if x['away_team'] != away_team else x['home_pts'], axis=1)
    # mark games where the away_team is away with a number (i.e., 2)
    df_away['weights'] = df_away.apply(lambda x: weight_away if x['away_team'] == away_team else 1, axis=1)
    
    # if we choose to weight each game by the opponents win %
    if outer_opp_win_pct == True:
        # get the name of the opponent
        df_away['opponent_name'] = df_away.apply(lambda x: x['away_team'] if x['home_team'] == away_team else x['home_team'], axis=1)
        # merge with df_win_pct to get opponent win %
        df_away = pd.merge(left=df_away, right=df_win_pct, left_on='opponent_name', right_on='team', how='left')
        # multiply 'weights' by 'win_pct'
        df_away['weights'] = df_away['weights'] * df_away['win_pct']
    
    # save weights
    list_weights = list(df_away['weights'])
    # some logic to catch errors
    if np.sum(list_weights) == 0:
        list_weights = [1 for x in list_weights]
     
    # get the central tendency number
    if central_tendency == 'mean':
        # calculate mean of home_score
        away_away_score_avg = np.average(df_away['away_score'], weights=list_weights)
        # get mean of away_score
        away_opponent_score_avg = np.average(df_away['home_score'], weights=list_weights)
    else: # i.e., median
        # calculate median home_score
        away_away_score_avg = weighted.median(df_away['away_score'], weights=list_weights)
        # get median of away_score
        away_opponent_score_avg = weighted.median(df_away['home_score'], weights=list_weights)
         
    # if distribution == 'poisson'
    if distribution == 'poisson':
        # draw a random number from a poisson distribution for predicted away score
        list_pred_away_away_score = list(np.random.poisson(away_away_score_avg, n_simulations))
        # draw a random number from a poisson distribution for predicted home score
        list_pred_away_opponent_score = list(np.random.poisson(away_opponent_score_avg, n_simulations))
    # if distribution == 'normal'
    else:
        # calculate sd of home_score (for normal distribution)
        away_away_score_sd = np.sqrt(np.average((df_away['away_score']-away_away_score_avg)**2, weights=list_weights))
        # get sd of away_score
        away_opponent_score_sd = np.sqrt(np.average((df_away['home_score']-away_opponent_score_avg)**2, weights=list_weights))
        # draw a random number from a normal distribution
        list_pred_away_away_score = list(np.random.normal(loc=away_away_score_avg, scale=away_away_score_sd, size=n_simulations))
        # draw a random number from a normal distribution
        list_pred_away_opponent_score = list(np.random.normal(loc=away_opponent_score_avg, scale=away_opponent_score_sd, size=n_simulations))
    
    # -------------------------------------------------------------------------
    
    # put into a df
    df_predictions = pd.DataFrame({'pred_home_home_score': list_pred_home_home_score,
                                   'pred_home_opponent_score': list_pred_home_opponent_score,
                                   'pred_away_away_score': list_pred_away_away_score,
                                   'pred_away_opponent_score': list_pred_away_opponent_score})
    
    # -------------------------------------------------------------------------
    
    # 3. now let's have the scores meet in the middle
    # if we want a straight avg
    if inner_opp_win_pct == False:
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
        # logic to avoid errors
        if np.sum(list_weights) == 0:
            list_weights = [1, 1]
    
    # home score prediction
    df_predictions['pred_home_score'] = df_predictions.apply(lambda x: np.average([x['pred_home_home_score'], x['pred_away_opponent_score']], weights=list_weights), axis=1)
    # away score prediction
    df_predictions['pred_away_score'] = df_predictions.apply(lambda x: np.average([x['pred_home_opponent_score'], x['pred_away_away_score']], weights=list_weights), axis=1)
    
    # creat a col 1/0 to deal with ties
    df_predictions['rand_binomial'] = np.random.binomial(1, 0.5, n_simulations)
    
    # create col == 1 if home team wins
    # define function
    def did_home_win(pred_home_score, pred_away_score, rand_binomial):
        if pred_home_score > pred_away_score:
            return 1
        elif pred_home_score < pred_away_score:
            return 0
        elif pred_home_score == pred_away_score and rand_binomial == 1:
            return 1
        else:
            return 0
    
    # get sum of games where home team won
    sum_home_wins = np.sum(df_predictions.apply(lambda x: did_home_win(pred_home_score=x['pred_home_score'], pred_away_score=x['pred_away_score'], rand_binomial=x['rand_binomial']), axis=1))
    # get the proportion of games where the home team is > away team
    prop_home_win = sum_home_wins/n_simulations

    # get mean home score
    mean_home_score = round(np.mean(df_predictions['pred_home_score']), 3)
    # get mean away score
    mean_away_score = round(np.mean(df_predictions['pred_away_score']), 3)
    
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
