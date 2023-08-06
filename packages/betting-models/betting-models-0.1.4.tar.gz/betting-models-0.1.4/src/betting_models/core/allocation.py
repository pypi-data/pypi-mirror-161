"Generic betting allocation utility for markets with mutually exclusive event outcomes"

import time

from copy import deepcopy
from random import shuffle

import numpy as np


class Allocator:
    def __init__(self, n_seeds, tolerance=0):
        self.outcome_probs = None
        self.n_seeds = n_seeds
        self.lower_bound = n_seeds - tolerance

    def _largest_indices(self, arr, n):
        'Returns the n largest indices from a numpy array in a list of lists'
        flat = arr.flatten()
        indices = np.argpartition(flat, -n)[-n:]
        indices = indices[np.argsort(-flat[indices])]
        output = np.unravel_index(indices, arr.shape)
        
        # Wrangle output into list of lists format
        event_outcomes_list = []
        for i in range(n):
            outcome_set = [idx[i] for idx in output]
            event_outcomes_list.append(outcome_set)
        
        return event_outcomes_list

    def optimise(self, target):
        'Optimise seeding bet allocation within bounding constraints'
        seeds = (target * 0).astype(int)
        #seeds = np.floor(target * self.lower_bound) For some reason your maths/code is wrong here
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
        
        list_ = []
        timeout = time.time() + 180

        while n_seeds < self.n_seeds:  # set a non-zero abs_delta if n_seeds = 0
            if time.time() > timeout:
                raise ValueError('Optimiser timed out, check target allocation input.')
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
            list_.append(abs_delta)
            # If improvement in allocation update cache
            if (abs_delta <= cache[0]) or (n_seeds < self.lower_bound):
                master_seed = seeds.copy()
                cache = (abs_delta, n_seeds, master_seed)
        # Return cached optimal seeding bets
        return cache

    def _compound_probs(self, probs_list):
        "Generate compound probabilities array from individual events"
        probs_arr = 1
        for T in probs_list:
            probs_arr = np.tensordot(probs_arr, T, axes=0)
        return probs_arr

    def gen_vanilla_seeds(self, prob_list):
        'Return near-optimal league seeds within tolerance in tensor format'
        target_alloc = self._compound_probs(prob_list)
        result = self.optimise(target_alloc)
        return result

    def gen_tailed_seeds(self, prob_list, lb_cutoff_proba=0.20, 
                             ub_cutoff_proba=0.99, random_seed=False):
        'Returns league seeds with cadence bets from beyond cutoff most likely outcomes'
        target_alloc = self._compound_probs(prob_list)
        n_outcomes = target_alloc.size
        ordered_idxs = self._largest_indices(target_alloc, n_outcomes)
        adjusted_target = target_alloc.copy()
        
        # If random state specified, generate random numbers based on this
        if random_seed:
            np.random.seed(random_seed)

        # Gen random uniform iterator
        randoms = iter(np.random.uniform(size=n_outcomes))
        prob_cumsum = 0
        
        for _, idx in enumerate(ordered_idxs):
            # Count cumulative probability of most likely outcomes    
            prob = target_alloc[tuple(idx)]
            prob_cumsum += prob
            # UB/LB adjustment
            if prob_cumsum < lb_cutoff_proba:
                adjusted_target[tuple(idx)] = 0
            elif prob_cumsum > ub_cutoff_proba:
                adjusted_target[tuple(idx)] = -1
            else:
                # Implieds tail extension
                optimal_bet = self.n_seeds * target_alloc[tuple(idx)]
                # If its optimal placing over 1 bet, keep this as target
                if optimal_bet >= 1:
                    continue
                # If coinflip true allocate a bet, else don't
                coinflip = next(randoms) < optimal_bet
                divisor = 1 / optimal_bet
                
                if coinflip == True:
                    adjusted_target[tuple(idx)] *= divisor
                else:
                    adjusted_target[tuple(idx)] = 0
                
        # Optimise on new target
        result = self.optimise(adjusted_target)
        return result        

    def gen_bounded_seeds(self, prob_list, lb_cutoff=10, ub_cutoff=5000, random_seed=False):
        'Not implemented (may not be working), different way of executing the tailed strategy'
        target_alloc = self._compound_probs(prob_list)
        n_outcomes = target_alloc.size
        #if n_outcomes < ub_cutoff:
        ordered_idxs = self._largest_indices(target_alloc, n_outcomes)
        adjusted_target = target_alloc.copy()
        
        # If random state specified, generate random numbers based on this
        if random_seed:
            np.random.seed(random_seed)
        # Gen random uniform iterator
        randoms = iter(np.random.uniform(size=ub_cutoff))
        
        for index, idx in enumerate(ordered_idxs):
            # Hogg adjustment
            if index <= lb_cutoff:
                adjusted_target[tuple(idx)] = 0
            elif index >= ub_cutoff:
                adjusted_target[tuple(idx)] = -1
            else:
                # Implieds tail extension
                optimal_bet = self.n_seeds * target_alloc[tuple(idx)]
                # If its optimal placing over 1 bet, keep this as target
                if optimal_bet >= 1:
                    continue
                # If coinflip true allocate a bet, else don't
                coinflip = next(randoms) < optimal_bet
                divisor = 1 / optimal_bet
                
                if coinflip == True:
                    adjusted_target[tuple(idx)] *= divisor
                else:
                    adjusted_target[tuple(idx)] = 0
        # Optimise on new target
        result = self.optimise(adjusted_target)
        
        return result
