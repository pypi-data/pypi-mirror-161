'''Poisson + Binomial game score outcomes model class'''

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import poisson, binom

from . import config


class ScoreModel:
    def __init__(self, lambda_h, lambda_a, precision=11):
        self.lh = lambda_h
        self.la = lambda_a
        self.prec = precision
    
    @staticmethod
    def p_goals(n_goals, lambd):
        return poisson.pmf(n_goals, lambd)

    def p_scoreline(self, goals_home, goals_away):    
        p_goals_home = ScoreModel.p_goals(goals_home, self.lh)
        p_goals_away = ScoreModel.p_goals(goals_away, self.la)
        return p_goals_home * p_goals_away

    @staticmethod
    def p_halfgoals(n, p=0.47):
        # If no goal N_N must occur else N_N = 0
        if n == 0:
            return np.array([0, 0, 0, 1])
        N_N = 0
        # x <= k = 0; (FHG/SHG) (N/Y)  ONLY FHG
        Y_N = binom.pmf(n, n, p)
        # x == k = n:  ONLY SHG
        N_Y = binom.pmf(0, n, p)
        # FHG AND SHG
        Y_Y = 1 - (Y_N + N_Y)
        return np.array([Y_Y, Y_N, N_Y, N_N])

    def halfgoals_mat(self):
        p_mat = np.zeros((self.prec, self.prec, 4))
        for goals_home in range(self.prec):
            for goals_away in range(self.prec):
                tot_goals = goals_home + goals_away
                p_goal_combos = ScoreModel.p_halfgoals(tot_goals)
                p_mat[goals_home, goals_away, :] = p_goal_combos
        return p_mat
    
    def scores_mat(self, plot=False):
        # Make grid of possible outcomes
        df = pd.DataFrame()
        p_mat = np.zeros((self.prec, self.prec))
        for goals_home in range(self.prec):
            for goals_away in range(self.prec):    
                p_curr_score = self.p_scoreline(goals_home, goals_away)
                p_mat[goals_home, goals_away] = p_curr_score
                info = {
                    'home_goals': goals_home, 
                    'away_goals': goals_away, 
                    'p_score': p_curr_score
                }
                df = pd.concat([df, pd.DataFrame(info, index=[0])], ignore_index=True)
        if plot:
            self.plot_heatmap(p_mat)
        return p_mat

    def outcomes_0_mat(self):
        # Explode goal outcomes, cartesian product scores array to (prec, prec, 4)
        scores_mat = self.scores_mat()
        hg_mat = self.halfgoals_mat()
        outcomes_mat = np.expand_dims(scores_mat, scores_mat.ndim) * hg_mat
        return outcomes_mat

    def htsf_mat(self):
        p_mat = np.zeros((self.prec, self.prec, 2))
        for goals_home in range(self.prec):
            for goals_away in range(self.prec):
                tot_goals = goals_home + goals_away
                if tot_goals > 0:
                    p_htsf = goals_home / tot_goals
                    vec = [p_htsf, (1 - p_htsf)]
                else:
                    vec = [0, 1]
                p_mat[goals_home, goals_away, :] = vec
        return p_mat

    def red_card(self):
        p_mat = np.zeros((self.prec, self.prec, 2))
        vec = [config.PROB_RED, 1 - config.PROB_RED]
        p_mat += vec
        return p_mat

    def yellow_cards(self):
        p_mat = np.zeros((self.prec, self.prec, 2))
        vec = [config.PROB_CO_YELLOWS, 1 - config.PROB_CO_YELLOWS]
        p_mat += vec
        return p_mat

    @staticmethod
    def pseudo_cartesian(arr_1, arr_2):
        shape = arr_1.shape  # (n1, n2, k, k)
        arr_1  = np.expand_dims(arr_1, arr_1.ndim)  # (n1, n2, k, k, 1)
        dims = shape[2:]
        # (n1, n2, j) -> (n1, n2, k, k, j)
        for dim in dims:
            arr_2  = np.stack((arr_2,) * dim, axis=-2)
        return arr_1 * arr_2  # (n1, n2, k, k, j)

    def outcomes_1_mat(self):
        out_mat = self.scores_mat()
        markets = [
            self.htsf_mat(), 
            self.red_card(), 
            self.yellow_cards(),
            self.halfgoals_mat()
        ]
        for mkt_mat in markets:
            out_mat = ScoreModel.pseudo_cartesian(out_mat, mkt_mat)
        return out_mat

    def plot_heatmap(self, p_mat):
        # Plot result
        _, ax = plt.subplots()
        sns.heatmap(p_mat, cmap="YlGnBu", annot=True, ax=ax)
        ax.set_ylabel('Hometeam')
        ax.set_xlabel('Awayteam')
        plt.show()


if __name__ == '__main__':
    
    lambda_h = 1.5
    lambda_a = 0.5
    model = ScoreModel(lambda_h, lambda_a, precision=5)
    
    p_mat = model.outcomes_1_mat()
    print(np.sum(p_mat))
    print(p_mat.shape)
    