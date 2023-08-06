'''Dispatch match markets seeding model'''

import numpy as np

from .formats import FormatZero, FormatOne


class FootballMatchMarketsGenerator:
    def __init__(self):
        pass

    def dec_2_implied(self, decimal_odds):
        'Convert odds array to implied probability array'
        probs = 1 / decimal_odds
        probs_normalised = probs / np.sum(probs)
        return probs_normalised

    def run(self, num_seeds, tol, dec_odds, format_num,):
        'Choose model format and return seeding bets dataframe'
        if format_num == 0:
            model = FormatZero(num_seeds, tol)
        elif format_num == 1:
            model = FormatOne(num_seeds, tol)
        else:
            raise ValueError('Format number not implemented.')
        
        implied_hda = self.dec_2_implied(dec_odds)
        seeds_df, fig = model.gen_seeds(implied_hda)
        return seeds_df, fig


if __name__ == '__main__':
    
    hda = np.array([1.714, 3.750, 5.71])
    num_seeds = 100
    tol = 50
    format_num = 0
    vis_status = True

    sm = FootballMatchMarketsGenerator(num_seeds, tol)
    seeds_df, fig = sm.run(hda, format_num, vis_status)
    print(seeds_df)
    
    import matplotlib.pyplot as plt
    plt.savefig('c:/users/micha/desktop/test_output.png')
