from typing import Iterable
from typing import Dict
import pandas as pd
import numpy as np
import pickle, pdb, time, itertools, datetime,hashlib
from copy import copy
from joblib import Parallel, delayed
from ultron.factor.genetic.geneticist.operators import expression_params,calc_factor
from ultron.factor.fitness.weighted import Weighted
from ultron.utilities.utils import check_random_state
from ultron.utilities.jobs import partition_estimators
from ultron.utilities.utils import check_random_state

import warnings
warnings.filterwarnings("ignore")

MAX_INT = np.iinfo(np.int32).max
MIN_INT = np.iinfo(np.int32).min  

class Individual(object):
    def __init__(self, name, stype): # 0 行业  1 股票池
        self._name = name
        self._stype = stype
        
class Program(object):
    def __init__(self, gen, random_state, ind_sets, universe_sets, init_depth,
                 p_point_replace, expression, program=None, parents=None):
        self._gen = gen
        self._p_point_replace = p_point_replace
        self._ind_sets = ind_sets
        self._universe_sets = universe_sets
        self._program = program
        self._parents = parents
        self._ind_sets = ind_sets
        self._universe_sets = universe_sets
        self._create_time = datetime.datetime.now()
        self._init_depth = init_depth
        self._expression = expression
        self._raw_fitness = 0
        self._is_valid = True
        self._risk_styles = ['BETA','MOMENTUM','SIZE','EARNYILD','RESVOL','GROWTH','BTOP','LEVERAGE','LIQUIDTY','SIZENL']
        self._industry_styles = ['Bank','RealEstate','Health','Transportation','Mining',
                                 'NonFerMetal','HouseApp','LeiService','MachiEquip','BuildDeco',
                                 'CommeTrade','CONMAT','Auto','Textile','FoodBever','Electronics',
                                 'Computer','LightIndus','Utilities','Telecom','AgriForest','CHEM',
                                 'Media','IronSteel','NonBankFinan','ELECEQP','AERODEF','Conglomerates']
        self._name = 'ultron_' + str(int(time.time() * 1000000 + datetime.datetime.now().microsecond))
        if self._program is None:
            self._program = self.build_program(random_state)
        self.create_identification()
    
    def create_identification(self):
        m = hashlib.md5()
        program = [p._name for p in self._program]
        program.sort()
        m.update(bytes(''.join(program), encoding='UTF-8'))
        self._identification = m.hexdigest()
        
    def industry_features(self):
        return [p._name for p in self._program if p._name in self._industry_styles]
    
    def log(self):
        parents = {'method':'gen'} if self._parents is None else self._parents
        name = self._name
        sets = [p._name for p in self._program]
        print('name:%s,raw_fitness:%f, program:%s,create_time:%s,identification:%s' % (
            self._name, self._raw_fitness, sets, self._create_time,self._identification))
        
    def duplicate_removal(self, program):
        program = [p._name for p in program]
        program = set(program)
        new_program = []
        for p in program: 
            if p in self._ind_sets:
                new_program.append(Individual(p, 0))
            elif p in self._universe_sets:
                new_program.append(Individual(p, 1))
        return new_program
                
    def build_program(self, random_state):
        #构造 深度判断
        ind_max = self._init_depth[1] if self._init_depth[1] < len(self._ind_sets) else len(self._ind_sets)
        universe_max = self._init_depth[1] if self._init_depth[1] < len(self._universe_sets) else len(self._universe_sets)
        ind_max_prob = np.random.randint(ind_max) / len(self._ind_sets)
        universe_max_prob = np.random.randint(universe_max) / len(self._universe_sets)
        univ = self._universe_sets[np.random.randint(len(self._universe_sets))]
        ind = self._ind_sets[np.random.randint(len(self._ind_sets))]
        program = [Individual(univ, 1), Individual(ind, 0)]
        ind_list = (np.random.uniform(0, 1, (1, len(self._ind_sets))) < ind_max_prob).tolist()
        ind_list = list(np.array(self._ind_sets)[ind_list])
        universe_list = (np.random.uniform(0, 1, (1, len(self._universe_sets))) < universe_max_prob).tolist()
        universe_list = list(set(list(np.array(self._universe_sets)[universe_list])))
        program += [Individual(ind, 0) for ind in ind_list] + [Individual(univ, 1) for univ in universe_list]
        return self.duplicate_removal(program)
        
    def get_subtree(self, random_state=None, program=None):
        if program is None:
            program = self._program
        probs = np.array([0.9 if node._name in self._ind_sets else 0.1 for node in program])
        probs = np.cumsum(probs / probs.sum())
        start = np.searchsorted(probs, np.random.uniform())
        end = start if (len(program) - 1) <= start else np.random.randint(start, len(program) - 1)
        return start, end
    
    def reproduce(self):
        return copy(self._program)
    
    def crossover(self, donor, random_state):
        start, end = self.get_subtree(random_state)
        end -= 1
        removed = range(start, end)
        donor_start, donor_end = self.get_subtree(random_state, donor)
        donor_removed = list(set(range(len(donor))) -
                             set(range(donor_start, donor_end)))
        return self.duplicate_removal(self._program[:start] +
                donor[donor_start:donor_end] +
                self._program[end:]), removed, donor_removed
    
    ##树变异        
    def subtree_mutation(self, random_state=None):
        chicken = self.build_program(random_state)
        return self.crossover(chicken, random_state)
    
    ##突变异
    def hoist_mutation(self, random_state):
        start, end = self.get_subtree(random_state)
        subtree = self._program[start:end]
        sub_start, sub_end = self.get_subtree(random_state, subtree)
        hoist = subtree[sub_start:sub_end]
        removed = list(set(range(start, end)) -
                       set(range(start + sub_start, start + sub_end)))
        return self.duplicate_removal(self._program[:start] + hoist + self._program[end:]),removed
    
    def point_mutation(self, random_state):
        program = copy(self._program)
        mutate = np.where(np.random.uniform(size=len(program)) <
                          self._p_point_replace)[0]
        for node in mutate:
            if program[node]._name in self._ind_sets:
                replace_node = self._ind_sets[np.random.randint(0,len(self._ind_sets)-1)]
                program[node] = Individual(replace_node,0)
            elif program[node]._name in self._universe_sets:
                replace_node = self._universe_sets[np.random.randint(0,len(self._universe_sets)-1)]
                program[node] = Individual(replace_node,1)
        return self.duplicate_removal(program), list(mutate)
    
    def _industry_expression(self, industry_styles, name):
        expression = ''
        industry_len = len(industry_styles)
        i = 1
        for industry in industry_styles:
            expression += """({0}[\'{1}\']==1)""".format(name, industry)
            if i <  (industry_len):
                expression += """|"""
            i += 1
        return expression
    
    def optimization_by_formula(self, standard_data, univ_df, expression):
        #print('program:', self._program, isinstance(self._program, list))
        if not isinstance(self._program, list):
            pdb.set_trace()
        universe_codes = [p._name for p in self._program if p._name in self._universe_sets]
        industry_styles = [p._name for p in self._program if p._name in self._ind_sets]
        univ_se = univ_df.set_index(['trade_date','code'])[universe_codes] if len(universe_codes) > 0 else \
                        univ_df.set_index(['trade_date','code'])
        univ_se = univ_se[univ_se>0] # 股票池
        standard_factors = standard_data.copy()
        standard_datadard_factors = standard_factors.set_index(['trade_date','code']).reindex(univ_se.index).reset_index()
        if len(industry_styles) > 0:
            filter_expression = self._industry_expression(industry_styles, 'standard_factors')
            standard_factors = standard_factors[eval(filter_expression)]
        return calc_factor(expression=expression,
                total_data=standard_factors, indexs='trade_date', key='code', name='transformed'
                      ).reset_index().dropna()
    
    def evaluation(self, standard_data, univ_df, default_value, expression, fitness_method='high_frequency',
                   horizon=2, is_neutralize=0):
        risk_data = standard_data[['trade_date','code'] + self._industry_styles + self._risk_styles]
        mkt_df = standard_data[['closePrice', 'openPrice', 'lowestPrice', 'highestPrice', 'turnoverVol',
                         'turnoverValue', 'trade_date', 'code', 'accumAdjFactor',
                         'chgPct', 'bar30_vwap', 'bar60_vwap']]
        factors_data = self.optimization_by_formula(standard_data, univ_df, expression)
        weight = Weighted.create_weighted(method=fitness_method)
        result =  weight.run(factor_data=factors_data, horizon=horizon,
                           risk_data=risk_data, mkt_df=mkt_df,
                           factor_name='transformed', is_neutralize=is_neutralize,
                           default_value=np.iinfo(np.int32))
        raw_fitness = default_value if result['status'] == 0 else abs(result['score'])
        self._raw_fitness = default_value if np.isnan(raw_fitness) else raw_fitness
        self._is_valid = False if self._raw_fitness == default_value else True
    
    
def parallel_evolve(n_programs, parents, standard_data, univ_df, seeds, ind_sets, universe_sets, gen, params):
    tournament_size = params['tournament_size']
    init_depth = params['init_depth']
    greater_is_better = params['greater_is_better'] 
    expression = params['expression']
    method_probs = params['method_probs']
    p_point_replace = params['p_point_replace']
    expression = params['expression']
    
    
    programs = []
    def _contenders(tour_parents):
        contenders = random_state.randint(0, len(tour_parents), 2)
        return [tour_parents[p] for p in contenders]
    
    def _tournament(tour_parents):
        contenders = random_state.randint(0, len(tour_parents), tournament_size)
        raw_fitness = [tour_parents[p]._raw_fitness for p in contenders]
        if greater_is_better:
            parent_index = contenders[np.argmax(raw_fitness)]
        else:
            parent_index = contenders[np.argmin(raw_fitness)]
        return tour_parents[parent_index], parent_index
    
    for i in range(n_programs):
        random_state = check_random_state(seeds[i])
        if parents is None:
            program = None
            genome = None
        else:
            method = random_state.uniform()
            parent, parent_index = _tournament(copy(parents))
            ori_parent = copy(parent)
            contenders = _contenders(copy(parents))
            for contender in contenders:
                program, removed, remains = parent.crossover(contender._program, random_state)
                parent = Program(gen=gen, random_state=random_state, ind_sets=ind_sets, universe_sets=universe_sets, 
                                 init_depth=init_depth,p_point_replace=p_point_replace, expression=expression,
                                 program=program, parents=parents)
                
            #新特征种群加入
            if random_state.uniform() < method_probs[2]:
                program = Program(gen=gen, random_state=random_state, ind_sets=ind_sets, universe_sets=universe_sets, 
                                 init_depth=init_depth,p_point_replace=p_point_replace, expression=expression,
                                  program=None)
                program, removed, remains = parent.crossover(program._program, random_state)
                parent = Program(gen=gen, random_state=random_state, ind_sets=ind_sets, universe_sets=universe_sets, 
                                 init_depth=init_depth,p_point_replace=p_point_replace, expression=expression,
                                 program=program)
      
            if method < method_probs[0]: # # crossover
                donor, donor_index = _tournament(copy(parents))
                program, removed, remains = parent.crossover(donor._program, random_state)
                genome = {'method':'Crossover',
                         'parent_idx':parent_index,
                         'parent_nodes':removed,
                         'donor_idx':donor_index,
                         'donor_nodes':remains}
            elif method < method_probs[1]: # subtree_mutation
                program, removed, _ = parent.subtree_mutation(random_state)
                genome = {'method': 'Subtree Mutation',
                          'parent_idx': parent_index,
                          'parent_nodes': removed}
            elif method < method_probs[2]: # hoist_mutation
                program, removed = parent.hoist_mutation(random_state)
                genome = {'method': 'Hoist Mutation',
                          'parent_idx': parent_index,
                          'parent_nodes': removed}
            elif method < method_probs[3]: # point_mutation
                program,mutated = parent.point_mutation(random_state)
                genome = {'method': 'Point Mutation',
                          'parent_idx': parent_index,
                          'parent_nodes': mutated}
            else:
                program = parent.reproduce() # reproduction
                genome = {'method': 'Reproduction',
                          'parent_idx': parent_index,
                          'parent_nodes': []}
                
           
            # 与原始自身进行交叉
            if random_state.uniform() < method_probs[3]:
                program = Program(gen=gen, random_state=random_state, ind_sets=ind_sets, universe_sets=universe_sets, 
                                 init_depth=init_depth,p_point_replace=p_point_replace, expression=expression,
                                  program=program, parents=genome)
                program, removed, remains = program.crossover(ori_parent._program, random_state)
                
        program = Program(gen=gen, random_state=random_state, ind_sets=ind_sets, universe_sets=universe_sets, 
                                 init_depth=init_depth,p_point_replace=p_point_replace, expression=expression,
                          program=program, parents=genome)
        default_value = MIN_INT if greater_is_better else MAX_INT
        program.evaluation(standard_data, univ_df, default_value, expression)
        programs.append(program)
    return programs
    
class Gentic(object):
    
    def __init__(self, ind_sets, universe_sets, random_state=None, population_size=5, tournament_size=2, 
                 generations=MAX_INT,greater_is_better=True,verbose=1,convergence=0.05,
                 init_depth=(5, 6), n_jobs=1, p_crossover=0.9, p_subtree_mutation=0.01,
                 p_hoist_mutation=0.01, p_point_mutation=0.01, p_point_replace=0.05):
        self._random_state = random_state
        self._generations = MAX_INT if generations == 0 else generations
        self._population_size = population_size
        self._tournament_size = tournament_size
        self._init_depth = init_depth
        self._n_jobs = n_jobs
        self._greater_is_better = greater_is_better
        self._p_crossover = p_crossover
        self._p_subtree_mutation = p_subtree_mutation
        self._p_hoist_mutation = p_hoist_mutation
        self._p_point_mutation = p_point_mutation
        self._p_point_replace = p_point_replace
        self._convergence = convergence
        self._verbose = verbose
        self._ind_sets = ind_sets
        self._universe_sets = universe_sets
        
    def train(self, standard_data, univ_df, expression):
        random_state = check_random_state(self._random_state)
        self._method_probs = np.array([self._p_crossover,
                                       self._p_subtree_mutation,
                                       self._p_hoist_mutation,
                                       self._p_point_mutation])
        
        self._method_probs = np.cumsum(self._method_probs)
        
        if self._method_probs[-1] > 1:
            raise ValueError('The sum of p_crossover, p_subtree_mutation, '
                             'p_hoist_mutation and p_point_mutation should '
                             'total to 1.0 or less.')
            
        if (isinstance(self._init_depth, tuple) and len(self._init_depth) != 2):
            raise ValueError('init_depth should be a tuple with length two.')
        
        if (isinstance(self._init_depth, tuple) and (self._init_depth[0] > self._init_depth[1])):
            raise ValueError('init_depth should be in increasing numerical '
                             'order: (min_depth, max_depth).')
            
        params = {}
        params['tournament_size'] = self._tournament_size
        params['p_point_replace'] = self._p_point_replace
        params['init_depth'] = self._init_depth
        params['greater_is_better'] = self._greater_is_better
        params['expression'] = expression
        params['method_probs'] = self._method_probs
        params['p_point_replace'] = self._p_point_replace
        
        count_time = 0
        iteration_best_programs = None
        self._programs = []
        run_details = {'generation': [],
                             'average_fitness': [],
                             'best_fitness': [],
                             'generation_time': [],
                             'best_programs':[]}
        
        prior_generations = len(self._programs)
        n_more_generations = self._generations - prior_generations
        for gen in range(prior_generations, self._generations):
            start_time = time.time()
            if gen == 0:
                parents = None
            else:
                parents = self._programs[gen - 1]
                
            n_jobs, n_programs, starts = partition_estimators(
                self._population_size, self._n_jobs)
            
            seeds = random_state.randint(MAX_INT, size=self._population_size)
            population = Parallel(n_jobs=n_jobs,
                                  verbose=self._verbose)(
                delayed(parallel_evolve)(n_programs[i], parents, standard_data, univ_df, seeds,
                                         self._ind_sets, self._universe_sets, gen, params)
                for i in range(n_jobs))
            population = list(itertools.chain.from_iterable(population))
            #有效性判断
            population = [p for p in population if p._is_valid]
            
            self._programs.append(population)
                
            if iteration_best_programs is not None:
                programs = np.concatenate([population,iteration_best_programs])
            else:
                programs = population
                
             
            fitness = [program._raw_fitness for program in programs]
            if self._greater_is_better:
                iteration_best_programs = np.array(programs)[np.argsort(fitness)[-self._tournament_size:]]
            else:
                iteration_best_programs = np.array(programs)[np.argsort(fitness)[:self._tournament_size:]]
            
            fitness = [program._raw_fitness for program in iteration_best_programs]
            
            for program in iteration_best_programs:
                program.log()
                
            run_details['generation'].append(gen)
            run_details['average_fitness'].append(np.mean(fitness))
            generation_time = time.time() - start_time
            run_details['generation_time'].append(generation_time)
            run_details['best_programs'].append(iteration_best_programs)
            print(np.mean(fitness))
            
            if gen ==0:
                continue
             
            d_value = np.mean(fitness) - run_details['average_fitness'][gen - 1]
            print('d_value:%f,convergence:%f,count:%d,con_time:%d' % (d_value, self._convergence,
                                                                      len(iteration_best_programs), count_time))
            if abs(d_value) < self._convergence:
                count_time += 1
                if count_time > 3:
                    break
            else:
                count_time = 0
            
        return run_details