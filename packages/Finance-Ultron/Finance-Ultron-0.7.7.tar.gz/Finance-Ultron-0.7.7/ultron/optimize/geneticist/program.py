# -*- coding: utf-8 -*-
import numpy as np
import datetime, time, pdb, hashlib, json, copy
from ultron.optimize.model.modelbase import load_module
from ultron.optimize.geneticist.fitness import model_fitness
from ultron.utilities.utils import NumpyEncoder

import warnings

warnings.filterwarnings("ignore")


class Program(object):

    def __init__(self,
                 params_sets,
                 model_sets,
                 method,
                 random_state,
                 p_point_replace,
                 gen,
                 fitness,
                 model_name=None,
                 params=None,
                 program=None,
                 parents=None):
        self._id = str(
            int(time.time() * 1000000 + datetime.datetime.now().microsecond))
        self._init_method = method
        self._random_state = random_state
        self._p_point_replace = p_point_replace
        self._gen = gen
        self._fitness = fitness
        self._program = program
        self._parents = parents
        self._raw_fitness = None
        self._create_time = datetime.datetime.now()
        if self._program is None:
            self._program = self.build_program(random_state, params_sets,
                                               model_sets, model_name)
        else:
            self._program = self.reset_program(program)
        self._params = self._program['params']
        self._model_name = self._program['model_name']
        self._params_sets = params_sets[self._model_name]
        self._name = self._model_name + '_' + self._id
        self.create_identification()
        self._is_valid = True

    def reset_program(self, program):
        return program

    def build_program(self, random_state, params_sets, model_sets, model_name):
        ### 选择模型
        if model_name is None:
            model_name = random_state.randint(len(model_sets))
            model_name = model_sets[model_name]
        ##获取模型对应参数集
        model_params_sets = params_sets[model_name]
        params = {}
        for key in model_params_sets.keys():
            params[key] = random_state.choice(model_params_sets[key])
        #self._model = load_module(self._model_name)(**params)
        return {'model_name': model_name, 'params': params}

    def log(self):
        print("name:{0},gen:{1},params:{2},fitness:{3},method:{4},token:{5}".
              format(self._name, self._gen, self._params, self._raw_fitness,
                     self._init_method, self._identification))

    def create_identification(self):
        m = hashlib.md5()
        try:
            token = self.transform()
        except Exception as e:
            #ID为key
            token = self._name
        if token is None:
            token = self._name
        m.update(bytes(token, encoding='UTF-8'))
        self._identification = m.hexdigest()

    def transform(self):
        return json.dumps(self._program, cls=NumpyEncoder)

    def get_subtree(self, random_state, program=None):
        if program is None:
            program = self._program
        params = program['params']
        # Choice of crossover points follows Koza's (1992) widely used approach
        # of choosing functions 90% of the time and leaves 10% of the time.
        probs = np.array([
            0.9 if params[node] in self._params_sets[node] else 0.1
            for node in params.keys()
        ])
        probs = np.cumsum(probs / probs.sum())
        start = np.searchsorted(probs, random_state.uniform())
        end = start
        while len(list(params.keys())[start:]) > end - start:
            end += 1
        return start, end

    def reproduce(self):
        return copy.deepcopy(self._program)

    def point_mutation(self, random_state):
        program = copy.deepcopy(self._program)
        mutate = np.where(
            random_state.uniform(
                size=len(program['params'])) < self._p_point_replace)[0]
        removed = [
            list(self._program['params'].keys())[node] for node in mutate
        ]
        remain = list(set(self._program['params'].keys()) - set(removed))
        for key in removed:
            program['params'][key] = random_state.choice(
                self._params_sets[key])
        return program, removed, remain

    def crossover(self, donor, random_state):
        start, end = self.get_subtree(random_state)
        removed = list(self._program['params'].keys())[start:end]
        remain = list(set(self._program['params'].keys()) - set(removed))
        program = copy.deepcopy(self._program)
        for key in removed:
            program['params'][key] = donor['params'][key]
        return program, removed, remain

    def raw_fitness(self, features, X, Y, mode, n_splits):
        if self._fitness is None:
            raw_fitness = model_fitness(features=features,
                                        model_name=self._model_name,
                                        X=X,
                                        Y=Y,
                                        mode=mode,
                                        n_splits=n_splits,
                                        params=self._params)
        else:
            raw_fitness = self._fitness(features=features,
                                        model_name=self._model_name,
                                        X=X,
                                        Y=Y,
                                        params=self._params)
        self._raw_fitness = raw_fitness