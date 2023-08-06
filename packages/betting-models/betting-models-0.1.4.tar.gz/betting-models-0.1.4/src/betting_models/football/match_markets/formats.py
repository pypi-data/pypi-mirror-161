'''Match markets formats utilities'''

import numpy as np
import pandas as pd

from .market_model_base import MarketModelBase
from .backsolve_lambda import BacksolveLambda
from .score_model import ScoreModel


class FormatZero(MarketModelBase):
    def __init__(self, num_seeds, tol):
        super().__init__(num_seeds, tol)

    def probs_mat(self, implied_hda):
        solver = BacksolveLambda(implied_hda)
        solver.optimise()
        lambda_home, lambda_away = solver.lambdas
        # Generate outcomes_mat from lambdas
        score_model = ScoreModel(lambda_home, lambda_away)
        outcomes_mat = score_model.outcomes_0_mat()        
        return outcomes_mat

    def seeds_2_df(self, seeds_mat):
        lines = np.where(seeds_mat > 0)
        df = pd.DataFrame()
        # Loop through the index of each combination
        for i in range(lines[0].shape[0]):
            outcomes = tuple(j[i] for j in lines)
            dict_ = {
                'homegoals': outcomes[0],
                'awaygoals': outcomes[1],
                'halfgoal': outcomes[2],
                'num_bets': int(seeds_mat[outcomes])
            }
            df = pd.concat([df, pd.DataFrame(dict_, index=[0])], ignore_index=True)
        #df['halfgoal'] = df['halfgoal'].map({0:'Y_Y', 1:'Y_N', 2:'N_Y', 3:'N_N'})
        df['firsthalfgoal'] = False
        df['secondhalfgoal'] = False
        df.loc[df['halfgoal'] == 0, 'firsthalfgoal'] = True
        df.loc[df['halfgoal'] == 1, 'firsthalfgoal'] = True
        df.loc[df['halfgoal'] == 0, 'secondhalfgoal'] = True
        df.loc[df['halfgoal'] == 2, 'secondhalfgoal'] = True
        
        homewin = df['homegoals'] > df['awaygoals']
        draw = df['homegoals'] == df['awaygoals']
        awaywin = df['homegoals'] < df['awaygoals']
        
        # BTTS / OTAAHG / Goal first half / Goal second half column
        df['result'] = np.nan
        df.loc[homewin, 'result'] = 'homewin'
        df.loc[draw, 'result'] = 'draw'
        df.loc[awaywin, 'result'] = 'awaywin'
        df['BTTS'] = (df['homegoals'] > 0) & (df['awaygoals'] > 0)
        df['over_2.5'] = (df['homegoals'] + df['awaygoals']) > 2.5
        
        return df[['homegoals', 'awaygoals', 'result', 'BTTS', 
                'over_2.5', 'firsthalfgoal', 'secondhalfgoal', 'num_bets']]


class FormatOne(MarketModelBase):
    def __init__(self, num_seeds, tol):
        super().__init__(num_seeds, tol)

    def probs_mat(self, implied_hda):
        solver = BacksolveLambda(implied_hda)
        solver.optimise()
        lambda_home, lambda_away = solver.lambdas
        score_model = ScoreModel(lambda_home, lambda_away)
        outcomes_mat = score_model.outcomes_1_mat()
        return outcomes_mat

    def seeds_2_df(self, seeds_mat):
        lines = np.where(seeds_mat > 0)
        df = pd.DataFrame()
        # Loop through the index of each combination
        for i in range(lines[0].shape[0]):
            outcomes = tuple(j[i] for j in lines)
            dict_ = {
                'homegoals': outcomes[0],
                'awaygoals': outcomes[1],
                'htsf': outcomes[2],
                'red_card': outcomes[3],
                'yellow_cards': outcomes[4],
                'halfgoal': outcomes[5],
                'num_bets': int(seeds_mat[outcomes])
            }
            df = pd.concat([df, pd.DataFrame(dict_, index=[0])], ignore_index=True)
        
        # FTR / over 2.5 goals
        homewin = df['homegoals'] > df['awaygoals']
        draw = df['homegoals'] == df['awaygoals']
        awaywin = df['homegoals'] < df['awaygoals']
        df['result'] = np.nan
        df.loc[homewin, 'result'] = 'homewin'
        df.loc[draw, 'result'] = 'draw'
        df.loc[awaywin, 'result'] = 'awaywin'
        df['over_2.5'] = (df['homegoals'] + df['awaygoals']) > 2.5
        
        # Hometeam to score first / Red card / Over 4.5 yellows
        df['htsf'] = df['htsf'].map({0:True, 1:False})
        df['red_card'] = df['red_card'].map({0:True, 1:False}) 
        df['yellow_cards'] = df['yellow_cards'].map({0:True, 1:False})

        # Hometeam clean sheet
        df['clean_sheet'] = df['awaygoals'] == 0

        # Halfgoals
        df['firsthalfgoal'] = False
        df['secondhalfgoal'] = False
        df.loc[df['halfgoal'] == 0, 'firsthalfgoal'] = True
        df.loc[df['halfgoal'] == 1, 'firsthalfgoal'] = True
        df.loc[df['halfgoal'] == 0, 'secondhalfgoal'] = True
        df.loc[df['halfgoal'] == 2, 'secondhalfgoal'] = True
        
        out_cols = [
            'homegoals', 
            'awaygoals', 
            'result', 
            'over_2.5', 
            'htsf', 
            'red_card', 
            'yellow_cards', 
            'clean_sheet', 
            'firsthalfgoal', 
            'secondhalfgoal', 
            'num_bets'
        ]
        
        return df[out_cols]
