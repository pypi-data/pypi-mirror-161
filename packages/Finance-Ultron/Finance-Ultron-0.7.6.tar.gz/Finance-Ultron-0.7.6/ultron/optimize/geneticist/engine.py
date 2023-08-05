# -*- coding: utf-8 -*-
import numpy as np
from ultron.optimize.geneticist.genetic import Gentic

MAX_INT = np.iinfo(np.int32).max
MIN_INT = np.iinfo(np.int32).min


class Engine(object):

    def __init__(
            self,
            model_sets,
            params_sets,
            population_size=2000,
            generations=MAX_INT,
            tournament_size=20,
            n_jobs=1,
            p_crossover=0.9,
            p_point_mutation=0.01,
            p_subtree_mutation=0.00,
            p_hoist_mutation=0.00,
            p_point_replace=0.8,
            stopping_criteria=0.0,
            fitness=None,
            save_model=None,
            random_state=None,
            greater_is_better=True,  #True 倒序， False 正序
            convergence=None,
            standard_score=0.9,  # None代表 根据tournament_size保留种群  standard_score保留种群
            verbose=1):

        self._population_size = population_size
        self._generations = MAX_INT if generations == 0 else generations
        self._tournament_size = tournament_size
        self._stopping_criteria = stopping_criteria
        self.init_method = 'full'
        self._model_sets = model_sets
        self._params_sets = params_sets
        self._p_crossover = p_crossover
        self._p_subtree_mutation = p_subtree_mutation
        self._p_hoist_mutation = p_hoist_mutation
        self._p_point_mutation = p_point_mutation
        self._p_point_replace = p_point_replace
        self._random_state = random_state
        self._fitness = fitness
        self._save_model = save_model
        self._greater_is_better = greater_is_better
        self._standard_score = standard_score
        self._convergence = convergence
        self._con_time = 0
        self._n_jobs = n_jobs
        self._verbose = verbose

    def run_gentic(self, features, X, Y, mode, n_splits):
        gentic = Gentic(
            model_sets=self._model_sets,
            params_sets=self._params_sets,
            population_size=self._population_size,
            generations=MAX_INT,
            tournament_size=self._tournament_size,
            n_jobs=self._n_jobs,
            p_crossover=self._p_crossover,
            p_point_mutation=self._p_point_mutation,
            p_point_replace=self._p_point_replace,
            stopping_criteria=self._stopping_criteria,
            fitness=self._fitness,
            save_mode=self._save_model,
            random_state=self._random_state,
            greater_is_better=self._greater_is_better,  #True 倒序， False 正序
            convergence=self._convergence,
            standard_score=self.
            _standard_score,  # None代表 根据tournament_size保留种群  standard_score保留种群
            verbose=self._verbose)
        gentic.train(features=features, X=X, Y=Y, mode=mode, n_splits=n_splits)
        result = gentic._run_details
        raw_fitness = 0 if len(
            result['best_programs']) == 0 else result['best_fitness'][-1]
        # del gentic 主动释放内存
        return raw_fitness

    def train(self, features, X, Y, mode, n_splits):
        raw_fitness = 0
        while raw_fitness < self._stopping_criteria:
            raw_fitness = self.run_gentic(features,
                                          X=X,
                                          Y=Y,
                                          mode=mode,
                                          n_splits=n_splits)
