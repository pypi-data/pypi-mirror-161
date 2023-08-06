'''Class to find home and away team expected goals (lambdas) in a game'''

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from scipy.optimize import minimize

from .score_model import ScoreModel


class BacksolveLambda:
    def __init__(self, target):
        self.target = target
        self.lambdas = np.zeros(2)
    
    def lambda_mse(self, lambdas):
        lambda_home, lambda_away = lambdas
        model = ScoreModel(lambda_home, lambda_away)
        outcomes_mat = model.scores_mat()
        
        p_draw = np.sum(np.diag(outcomes_mat))
        p_homewin = np.sum(np.tril(outcomes_mat)) - p_draw
        p_awaywin = np.sum(np.triu(outcomes_mat)) - p_draw
        
        curr_probs = np.array([p_homewin, p_draw, p_awaywin])
        mse = np.mean(np.square(curr_probs - self.target))
        return mse
        
    def optimise(self):
        lambdas = self.lambdas
        result = minimize(self.lambda_mse, lambdas, method='BFGS')
        self.lambdas = np.array([result.x[0], result.x[1]])

    def vis_search_space(self, max_l=5, n_iters=20):
        df = pd.DataFrame()
        # Find MSE of a series of home and away lambdas
        for home_l in np.linspace(0, max_l, num=n_iters):
            for away_l in np.linspace(0, max_l, num=n_iters):
                mse = self.lambda_mse((home_l, away_l))
                row = {'home_l': home_l, 'away_l': away_l, 'mse': mse}
                df = pd.concat([df, pd.DataFrame(row, index=[0])], ignore_index=True)
        # Plt package 3D-plot requires bizaare 'meshgrid' format
        Z = df.pivot_table(index='home_l', columns='away_l', values='mse').T.values
        X_unique = np.sort(df.home_l.unique())
        Y_unique = np.sort(df.away_l.unique())
        X, Y = np.meshgrid(X_unique, Y_unique)
        # Plot and show figure
        _ = plt.figure()
        ax = plt.axes(projection='3d')
        ax.contour3D(X, Y, Z, 75, cmap='cool')
        ax.set_xlabel('home_lambda')
        ax.set_ylabel('away_lambda')
        ax.set_zlabel('mse')
        plt.show()
        

if __name__ == '__main__':
    
    def dec_2_implied(decimal_odds):
        'Odds array to probability array'
        probs = 1 / decimal_odds
        probs_normalised = probs / np.sum(probs)
        return probs_normalised
    
    hda = np.array([1.714, 3.750, 5.71])
    target = dec_2_implied(hda)
    
    backsolve = BacksolveLambda(target)
    backsolve.optimise()
    print(backsolve.lambdas)
    