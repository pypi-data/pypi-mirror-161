'''Dispatch match markets seeding model'''

from json import dumps

import numpy as np
import pandas as pd

from betting_models.core.allocation import Allocator
from betting_models.core.base_generator import BaseGenerator


class FootballFTRLeagueGenerator(BaseGenerator):
    def __init__(self):
        pass
    
    def _json_encode(self, matchids, leagueid, seeds):
        'Convert seed allocation array into json'
        packet = {}
        packet['LeagueId'] = leagueid
        packet['Lines'] = []
        
        # Loop through all non-zero betting combinations
        lines = np.where(seeds > 0)
        for i in range(lines[0].shape[0]):    
            outcomes = tuple(j[i] for j in lines)
            value = int(seeds[outcomes])  # int required for json encoder
            # Map outcomes to WKW input
            WKW_map = {0:1, 1:0, 2:2}
            WKW_outcomes = list(outcomes)
            WKW_outcomes = tuple(map(WKW_map.get, WKW_outcomes))
            
            zipped = zip(matchids, WKW_outcomes)
            
            line = {}
            line['Predictions'] = []
            line['NumberOfBets'] = value
            
            # For each match bet in line, extract matchid and outcome
            for matchid, WKW_outcome in zipped:
                event = {}
                event['MatchId'] = matchid
                event['Prediction'] = int(WKW_outcome)
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
        matchids, 
        leagueid, 
        random_seed=False
    ):
        'Add first seeding batch to league'
        prob_list = list(map(self.decimal_2_probs, odds_list))

        alloc = Allocator(n_seeds, tol)
        # Get tailed seed bets if random seed specified, otherwise vanilla
        if random_seed:
            _, _, seeds = alloc.gen_tailed_seeds(prob_list, random_seed=random_seed)
        else:
            _, _, seeds = alloc.gen_vanilla_seeds(prob_list)
        json = self._json_encode(matchids, leagueid, seeds)
        fig = self.vis_status(prob_list, seeds)
        return json, fig
