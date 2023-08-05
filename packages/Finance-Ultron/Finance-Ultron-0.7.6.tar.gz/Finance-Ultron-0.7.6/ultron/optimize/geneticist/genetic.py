# -*- coding: utf-8 -*-
import numpy as np
from joblib import Parallel, delayed
import warnings, time, itertools, copy, pdb
from ultron.optimize.geneticist.program import Program
from ultron.optimize.geneticist import program
from ultron.utilities.utils import check_random_state
from ultron.utilities.jobs import partition_estimators

warnings.filterwarnings("ignore")

MAX_INT = np.iinfo(np.int32).max
MIN_INT = np.iinfo(np.int32).min


def parallel_evolve(n_programs, parents, features, X, Y, seeds,
                    greater_is_better, gen, params):
    tournament_size = params['tournament_size']
    model_sets = params['model_sets']
    params_sets = params['params_sets']
    init_method = params['init_method']
    method_probs = params['method_probs']
    p_point_replace = params['p_point_replace']
    fitness = params['fitness']
    mode = params['mode']
    n_splits = params['n_splits']

    def _contenders(tour_parents):
        contenders = random_state.randint(0, len(tour_parents), 6)
        return [tour_parents[p] for p in contenders]

    def _tournament(tour_parents, model_name=None):
        if model_name is not None:
            tour_parents = [
                p for p in tour_parents if p._model_name == model_name
            ]
        contenders = random_state.randint(0, len(tour_parents),
                                          tournament_size)
        raw_fitness = [tour_parents[p]._raw_fitness for p in contenders]
        if greater_is_better:
            parent_index = contenders[np.argmax(raw_fitness)]
        else:
            parent_index = contenders[np.argmin(raw_fitness)]
        return tour_parents[parent_index], parent_index

    programs = []
    for i in range(n_programs):
        random_state = check_random_state(seeds[i])
        if parents is None:
            program = None
            genome = None
            p_init_method = init_method
        else:
            method = random_state.uniform()
            parent, parent_index = _tournament(copy.deepcopy(parents))
            ori_parent = copy.deepcopy(parent)

            contenders = _contenders(copy.deepcopy(parents))
            for contender in contenders:
                if contender._model_name != parent._model_name:
                    continue
                program, removed, remains = parent.crossover(
                    contender._program, random_state)
                parent = Program(params_sets=params_sets,
                                 model_sets=model_sets,
                                 random_state=random_state,
                                 method=init_method,
                                 p_point_replace=p_point_replace,
                                 gen=gen,
                                 fitness=fitness,
                                 program=program)
                break
            # 新特征种群
            if random_state.uniform() < method_probs[1]:
                program = Program(params_sets=params_sets,
                                  model_sets=model_sets,
                                  random_state=random_state,
                                  method=init_method,
                                  p_point_replace=p_point_replace,
                                  gen=gen,
                                  fitness=fitness,
                                  model_name=parent._model_name)
                program, removed, remains = parent.crossover(
                    program._program, random_state)
                parent = Program(params_sets=params_sets,
                                 model_sets=model_sets,
                                 random_state=random_state,
                                 method=init_method,
                                 p_point_replace=p_point_replace,
                                 gen=gen,
                                 fitness=fitness,
                                 program=program)

            if method < method_probs[0]:  # crossover
                donor, donor_index = _tournament(copy.deepcopy(parents),
                                                 model_name=parent._model_name)
                program, removed, remains = parent.crossover(
                    donor._program, random_state)
                genome = {
                    'method': 'Crossover',
                    'parent_idx': parent_index,
                    'parent_nodes': removed,
                    'donor_idx': donor_index,
                    'donor_nodes': remains
                }
            elif method < method_probs[1]:  # point_mutation
                program, removed, remains = parent.point_mutation(random_state)
                genome = {
                    'method': 'Point Mutation',
                    'parent_idx': parent_index,
                    'parent_nodes': removed
                }
            else:
                program = parent.reproduce()  # reproduction
                genome = {
                    'method': 'Reproduction',
                    'parent_idx': parent_index,
                    'parent_nodes': []
                }
            # 与原始自身进行交叉
            if random_state.uniform() < method_probs[0]:
                program = Program(params_sets=params_sets,
                                  model_sets=model_sets,
                                  random_state=random_state,
                                  method=init_method,
                                  p_point_replace=p_point_replace,
                                  gen=gen,
                                  fitness=fitness,
                                  program=program)
                program, removed, remains = program.crossover(
                    ori_parent._program, random_state)
            p_init_method = genome['method']
        program = Program(params_sets=params_sets,
                          model_sets=model_sets,
                          random_state=random_state,
                          method=p_init_method,
                          p_point_replace=p_point_replace,
                          gen=gen,
                          fitness=fitness,
                          program=program)
        #default_value = MIN_INT if greater_is_better else MAX_INT
        program.raw_fitness(features=features,
                            X=X,
                            Y=Y,
                            mode=mode,
                            n_splits=n_splits)
        programs.append(program)
    return programs


class Gentic(object):

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
        self._save_model = save_mode
        self._greater_is_better = greater_is_better
        self._standard_score = standard_score
        self._convergence = convergence
        self._con_time = 0
        self._n_jobs = n_jobs
        self._verbose = verbose

    def filter_programs(self, population):
        ## 保留符合条件的种群(1.种群有效 2.分数优于基准分 3.符合指定个数)
        valid_prorams = np.array(population)[[
            program._is_valid for program in population
        ]]  # 只保留有效种群
        ## 删除重复种群
        identification_dict = {}
        for program in valid_prorams:
            identification_dict[program._identification] = program
        valid_prorams = list(identification_dict.values())
        fitness = [program._raw_fitness for program in valid_prorams]
        if self._standard_score is not None:  #分数筛选且第二代开始
            if self._greater_is_better:
                best_programs = np.array([
                    program for program in valid_prorams
                    if program._raw_fitness > self._standard_score
                ])
            else:
                best_programs = np.array([
                    program for program in valid_prorams
                    if program._raw_fitness < self._standard_score
                ])

        #若不满足分数，则进行排序选出前_tournament_size
        if len(best_programs
               ) < self._tournament_size or self._standard_score is None:
            if self._greater_is_better:
                best_programs = np.array(valid_prorams)[np.argsort(
                    fitness)[-self._tournament_size:]]
            else:
                best_programs = np.array(valid_prorams)[np.argsort(
                    fitness)[:self._tournament_size]]
        return best_programs

    def train(self, features, X, Y, mode, n_splits):
        random_state = check_random_state(self._random_state)
        self._method_probs = np.array(
            [self._p_crossover, self._p_point_mutation])

        self._method_probs = np.cumsum(self._method_probs)
        if self._method_probs[-1] > 1:
            raise ValueError('The sum of p_crossover, '
                             'and p_point_mutation should '
                             'total to 1.0 or less.')
        params = {}
        params['tournament_size'] = self._tournament_size
        params['init_method'] = self.init_method
        params['model_sets'] = self._model_sets
        params['params_sets'] = self._params_sets
        params['method_probs'] = self._method_probs
        params['p_point_replace'] = self._p_point_replace
        params['fitness'] = self._fitness
        params['mode'] = mode
        params['n_splits'] = n_splits

        self._programs = []
        self._best_programs = None
        self._run_details = {
            'generation': [],
            'average_fitness': [],
            'best_fitness': [],
            'generation_time': [],
            'best_programs': []
        }
        prior_generations = len(self._programs)
        n_more_generations = self._generations - prior_generations
        for gen in range(prior_generations, self._generations):
            start_time = time.time()
            if gen == 0:
                parents = None
            else:
                parents = self._programs[gen - 1]
                parents = [parent for parent in parents if parent._is_valid]

            n_jobs, n_programs, starts = partition_estimators(
                self._population_size, self._n_jobs)
            seeds = random_state.randint(MAX_INT, size=self._population_size)
            population = Parallel(n_jobs=n_jobs, verbose=self._verbose)(
                delayed(parallel_evolve)(n_programs[i], parents, features, X,
                                         Y, seeds, self._greater_is_better,
                                         gen, params) for i in range(n_jobs))

            population = list(itertools.chain.from_iterable(population))

            population = [
                program for program in population if program._is_valid
            ]
            if len(population) == 0:
                break

            if self._best_programs is None:
                self._programs.append(population)
            else:
                identification_dict = {}
                valid_prorams = list(
                    np.concatenate([population, self._best_programs]))
                for program in valid_prorams:
                    identification_dict[program._identification] = program
                valid_prorams = list(identification_dict.values())
                self._programs.append(valid_prorams)

            best_programs = self.filter_programs(population)
            if self._best_programs is not None:
                best_programs = np.concatenate(
                    [best_programs, self._best_programs])
                best_programs = self.filter_programs(best_programs)

            self._best_programs = best_programs
            for program in self._best_programs:
                program.log()

            fitness = [program._raw_fitness for program in self._best_programs]
            self._run_details['generation'].append(gen)
            self._run_details['average_fitness'].append(np.mean(fitness))
            generation_time = time.time() - start_time
            self._run_details['generation_time'].append(generation_time)
            self._run_details['best_programs'].append(self._best_programs)
            print(
                'ExpendTime:%f,Generation:%d,Tournament:%d, Fitness Mean:%f,Fitness Max:%f,Fitness Min:%f'
                % (generation_time, gen, len(best_programs), np.mean(fitness),
                   np.max(fitness), np.min(fitness)))

            ##
            if self._save_model is not None:
                self._save_model(gen, self._run_details['best_programs'][-1])
            if self._greater_is_better:
                best_fitness = fitness[np.argmax(fitness)]
                if best_fitness >= self._stopping_criteria:
                    break
            else:
                best_fitness = fitness[np.argmin(fitness)]
                if best_fitness <= self._stopping_criteria:
                    break

            if np.mean(fitness) == MIN_INT or best_fitness == MIN_INT:
                break
            self._run_details['best_fitness'].append(best_fitness)

            # 收敛值判断
            if self._convergence is None or gen == 0:
                continue
            d_value = np.mean(fitness) - self._run_details['average_fitness'][
                gen - 1]
            print('d_value:%f,convergence:%f,con_time:%d' %
                  (d_value, self._convergence, self._con_time))
            if abs(d_value) < self._convergence:
                self._con_time += 1
                if self._con_time > 5:
                    break
            else:
                self._con_time = 0
