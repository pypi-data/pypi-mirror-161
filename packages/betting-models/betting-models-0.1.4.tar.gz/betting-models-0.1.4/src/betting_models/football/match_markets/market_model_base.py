'''Base class for various match market format models'''

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from ...core.allocation import Allocator


class MarketModelBase:
    def __init__(self, num_seeds, tol):
        self.num_seeds = num_seeds
        self.tol = tol
    
    def optimise(self, target):
        'Optimise seeding bet allocation within bounding constraints'
        seeds = (target * 0).astype(int)
        #seeds = np.floor(target * self.lower_bound) maths/code is wrong here??
        if np.sum(seeds) == 0:
            allocation = seeds
        else:
            allocation = seeds / np.sum(seeds)
        deltas = allocation - target
        abs_delta = np.sum(abs(deltas))
        n_seeds = np.sum(seeds)
        # Cache information
        master_seed = seeds.copy()  # explicitly seperate from seeds (tentative)
        cache = (abs_delta, n_seeds, master_seed)

        while n_seeds < self.num_seeds:  # set a non-zero abs_delta if n_seeds = 0
            # Find min value location in deltas, if tie pick first value
            min_delta = np.amin(deltas)
            index = np.where(deltas == min_delta)
            if np.count_nonzero(deltas == min_delta) > 1:
                # Wrangle due to bizarre output from np.where
                index = tuple(i[0] for i in index)
            seeds[index] += 1
            n_seeds = np.sum(seeds)
            allocation = seeds / n_seeds            
            deltas = allocation - target
            abs_delta = np.sum(abs(deltas))
            # If improvement in allocation update cache
            if (abs_delta <= cache[0]) or (n_seeds < self.lower_bound):
                master_seed = seeds.copy()
                cache = (abs_delta, n_seeds, master_seed)
        # Return cached optimal seeding bets
        return cache

    def probs_mat(self, *args):
        raise NotImplementedError

    def seeds_mat(self, prob_mat):
        _, _, seeding_mat = self.optimise(prob_mat)
        return seeding_mat

    def seeds_2_df(self, *args):
        raise NotImplementedError

    def aggregate_seeds(self, df):
        ignore = ['num_bets', 'homegoals', 'awaygoals']
        cols = [i for i in df.columns if i not in ignore]
        return df.groupby(cols, as_index=False)['num_bets'].sum()

    def gen_seeds(self, implied_hda):
        'Return optimal seeding bets dataframe given implied HDA probs'
        probs_mat = self.probs_mat(implied_hda)
        alloc = Allocator(self.num_seeds, self.tol)
        _, _, seeds_mat = alloc.optimise(probs_mat)
        fig = self.print_status(probs_mat, seeds_mat)
        seeds_df = self.seeds_2_df(seeds_mat)
        seeds_df = self.aggregate_seeds(seeds_df)
        seeds_df.sort_values('num_bets', ascending=False, inplace=True)
        seeds_df.reset_index(drop=True, inplace=True)
        return seeds_df, fig

    def df_2_json(self, *args):
        raise NotImplementedError('Functionality to be added in future.')

    def plot_allocation(self, df):        
        'Plot betting allocation vs implied probability of outcomes'
        fig, ax = plt.subplots()
        for col in df.columns[:2]:
            ax.plot(df.index, df[col], label=col)
        ax2 = ax.twinx()
        ax2.plot(df.index, df[df.columns[2]], color='g', label=df.columns[2])
        ax.legend(bbox_to_anchor=(0.95, 0.75))
        ax2.legend(bbox_to_anchor=(0.95, 0.85))
        ax.set_title('Seed allocation')
        return fig

    def print_status(self, implied_probs_tensor, seeds):
        'Visualises status of seed given batch split, outcome probas etc...'
        n_seeds = np.sum(seeds)
        # Plot relative allocation
        seed_alloc = seeds / n_seeds
        seed_alloc = seed_alloc.reshape((-1,1))
        implied_probs_tensor = implied_probs_tensor.reshape((-1,1))
        data = (implied_probs_tensor, seed_alloc)
        zipped = np.concatenate(data, axis=1)
        
        cols = ['implied_probability', 'overall_seed_allocation']
        allocation_df = pd.DataFrame(zipped, columns=cols)
        allocation_df.sort_values('implied_probability', ascending=False, inplace=True)
        allocation_df.reset_index(drop=True, inplace=True)
        allocation_df['cumulative_prob'] = allocation_df['implied_probability'].cumsum()
        fig = self.plot_allocation(allocation_df)       
        # Info printouts
        print(f'Total seeds overall: {n_seeds}')
        return fig
