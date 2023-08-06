'''Dispatch generic markets seeding model'''

from json import dumps

import numpy as np

from betting_models.core.allocation import Allocator
from betting_models.core.base_generator import BaseGenerator


class GenericGenerator(BaseGenerator):
    def __init__(self):
        pass
    
    def _json_encode(self, leagueid, marketids, outcomes, seeds):
        '''Convert seed allocation array into json
        
        Args:
        marketids (iter): Iterable of marketids
        outcomes (iter): Iterable of outcomes ordered by raceid
        seeds (np.array): Seeding bet allocation array
        '''
        packet = {}
        packet['LeagueId'] = leagueid
        packet['Lines'] = []

        # Loop through all non-zero betting combinations
        lines = np.where(seeds > 0)
        for i in range(lines[0].shape[0]):
            pred_idxs = tuple(j[i] for j in lines)  # Prediction indices
            n_bets = int(seeds[pred_idxs])  # Num bets must be int for json encoder
            # Map preds to markets
            pred_outcomes = [outcomes[market][outcome] for market, outcome in enumerate(list(pred_idxs))]  # TODO: Is enumerate(list()) necessary?
            zipped = zip(marketids, pred_outcomes)
            
            line = {}
            line['Predictions'] = []
            line['NumberOfBets'] = n_bets
            # For each bet in line, extract matchid and outcome
            for marketid, pred_outcome in zipped:
                event = {'MarketId': marketid, 'Outcome': pred_outcome}
                line['Predictions'].append(event)
            # For each betting combination add a line
            packet['Lines'].append(line)
        # JSON encode output
        json = dumps(packet)
        return json
    
    def run(
        self,
        n_seeds, 
        tol, 
        odds_list,
        leagueid,
        marketids, 
        outcomes, 
    ):
        'Add first seeding batch to league.'
        prob_list = list(map(self.decimal_2_probs, odds_list))
        alloc = Allocator(n_seeds, tol)
        _, _, seeds = alloc.gen_vanilla_seeds(prob_list)
        json = self._json_encode(leagueid, marketids, outcomes, seeds)
        fig = self.vis_status(prob_list, seeds)
        return json, fig
