"Seeding bet generator base class"

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


class BaseGenerator:
    def __init__(self):
        pass

    def implied_2_tensor(self, implied_probs):
        'Convert implied probabilities list of arrays to n-dimensional tensor.'
        implied_tensor = 1
        for T in implied_probs:
            implied_tensor = np.tensordot(implied_tensor, T, axes=0)
        return implied_tensor

    def decimal_2_probs(self, decimal_odds_arr):
        'Convert decimal odds array to corresponding normalised implied probabilities.'
        probs_arr = 1 / decimal_odds_arr
        normed_probs_arr = probs_arr / np.sum(probs_arr)
        return normed_probs_arr

    def plot_alloc(self, df):
        'Plot betting allocation vs implied probability of outcomes'
        fig, ax = plt.subplots()
        for col in df.columns:    
            ax.plot(df.index, df[col], label=col)
            ax.legend()
            ax.set_title('Seed allocation')
        return fig

    def vis_status(self, prob_list, seeds):
        'Visualises status of seed given batch split, outcome probas etc...'
        n_seeds = np.sum(seeds)
        
        # Plot relative allocation
        seed_alloc = seeds / n_seeds
        implied_probs_tensor = self.implied_2_tensor(prob_list)
        seed_alloc = seed_alloc.reshape((-1,1))
        implied_probs_tensor = implied_probs_tensor.reshape((-1,1))

        data = (implied_probs_tensor, seed_alloc)
        zipped = np.concatenate(data, axis=1)
        cols = ['implied_probability', 'seed_allocation']
        allocation_df = pd.DataFrame(zipped, columns=cols)
        allocation_df.sort_values('implied_probability', ascending=False, inplace=True)
        allocation_df.reset_index(drop=True, inplace=True)
        fig = self.plot_alloc(allocation_df)  # return plot as compatible data
        return fig
