'''Dispatch racing markets seeding model'''

from json import dumps

import numpy as np

from betting_models.core.allocation import Allocator
from betting_models.core.base_generator import BaseGenerator


class RacingGenerator(BaseGenerator):
    def __init__(self):
        pass
    
    def _json_encode(self, leagueid, raceids, runners, seeds):
        '''Convert seed allocation array into json
        
        Args:
        raceids (iter): Iterable of raceids
        runners (iter): Iterable of runners ordered by raceid
        seeds (np.array): Seeding bet allocation array
        '''
        packet = {}
        packet['LeagueId'] = leagueid
        packet['Lines'] = []
        
        # Loop through all non-zero betting combinations
        lines = np.where(seeds > 0)
        for i in range(lines[0].shape[0]):    
            outcomes = tuple(j[i] for j in lines)
            value = int(seeds[outcomes])  # int required for json encoder
            # Map predicted outcomes to ponies
            event_outcomes = list(outcomes)

            winners = [runners[race][outcome] for race, outcome in enumerate(event_outcomes)]
            zipped = zip(raceids, winners)
            
            line = {}
            line['Predictions'] = []
            line['NumberOfBets'] = value
            
            # For each match bet in line, extract matchid and outcome
            for matchid, winner in zipped:
                event = {}
                event['MatchId'] = matchid
                event['WinnerId'] = winner
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
        raceids, 
        runners, 
    ):
        'Add first seeding batch to league.'
        prob_list = list(map(self.decimal_2_probs, odds_list))

        alloc = Allocator(n_seeds, tol)
        _, _, seeds = alloc.gen_vanilla_seeds(prob_list)
        json = self._json_encode(leagueid, raceids, runners, seeds)
        fig = self.vis_status(prob_list, seeds)
        return json, fig
