from typing import Iterable
from typing import Dict
import pandas as pd
import numpy as np
import pickle, pdb, time, itertools, datetime,hashlib
from copy import copy
from joblib import Parallel, delayed
from ultron.factor.genetic.geneticist.operators import expression_params,calc_factor
from ultron.factor.fitness.weighted import Weighted
from ultron.factor.combine.combine_engine import CombineEngine
from ultron.utilities.utils import check_random_state
from ultron.utilities.jobs import partition_estimators
from ultron.utilities.utils import check_random_state

import warnings
warnings.filterwarnings("ignore")

MAX_INT = np.iinfo(np.int32).max
MIN_INT = np.iinfo(np.int32).min 

class CombineAttr(object):
    def __init__(self, name, method, span, custom_params):
        self._name = name
        self._method = method
        self._span = span
        self._custom_params = custom_params
         
    def log(self):
        print(self._name, self._method, self._span, self._custom_params)
            
class Individual(object):
    def __init__(self, value, stype):
        self._value = value
        self._stype = stype #   1. 函数  2.因子(可用于交叉) 
        
class Program(object):
    def __init__(self, gen, random_state, init_depth, p_point_replace,
                 factor_sets, span_sets, half_sets, weight_limit_sets,
                program=None, parents=None):
        self._gen = gen
        self._random_state = random_state
        self._init_depth = init_depth
        self._p_point_replace = p_point_replace
        self._program = program
        self._parents = parents
        self._raw_fitness = 0
        self._is_valid = True
        self._create_time = datetime.datetime.now()
        self._factor_sets = factor_sets
        self.init_combine_func(span_sets, half_sets, weight_limit_sets)
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
        
    def init_combine_func(self, span_sets, half_sets, weight_limit_sets):
        self._combine_func = []
        hist_func_sets = ['hist_ret_combine','hist_ic_combine']
        max_func_sets = ['max_icir_combine','max_ic_combine']
        hist_method_sets = ['equal','half_life']
        max_method_sets = ['sample','shrunk']
        for name in hist_func_sets:
            for method in hist_method_sets:
                for span in span_sets:
                    for half in half_sets:
                        self._combine_func.append(CombineAttr(name, method, span, half))
        for name in max_func_sets:
            for method in max_method_sets:
                for span in span_sets:
                    for weight in weight_limit_sets:
                        self._combine_func.append(CombineAttr(name, method, span, weight))
    
    def log(self):
        parents = {'method':'gen'} if self._parents is None else self._parents
        name = self._name
        sets = [p._value for p in self._program if p._stype == 2]
        func = [p._value for p in self._program if p._stype == 1][0]
        sets += [func._name, func._method, str(func._span), str(func._custom_params)]
        print('name:%s,raw_fitness:%f, program:%s,create_time:%s,identification:%s' % (
            self._name, self._raw_fitness, sets, self._create_time,self._identification))
    
    def _func_method(self):
        func_sets = [p for p in self._program if p._stype == 1]
        return func_sets[0]._value
        
    def _factors_sets(self):
        return [p._value for p in self._program if p._stype == 2]
    
    def create_identification(self):
        m = hashlib.md5()
        program = [p._value for p in self._program if p._stype == 2]
        func = [p._value for p in self._program if p._stype == 1][0]
        program += [func._name, func._method, str(func._span), str(func._custom_params)]
        program.sort()
        m.update(bytes(''.join(program), encoding='UTF-8'))
        self._identification = m.hexdigest()
        
    def duplicate_removal(self, program):
        #重复的函数剔除，若被正交
        factors_sets = [p._value for p in program if p._stype == 2]
        factors_sets = list(set(factors_sets))
        func_sets = [p for p in program if p._stype == 1]
        new_program = []
        if len(func_sets) == 0:
            combine_func = self._combine_func[np.random.randint(len(self._combine_func))]
            new_program = [Individual(combine_func,1)]
            new_program += [Individual(factor, 2) for factor in factors_sets]
        elif len(func_sets) > 0:
            retain_func = func_sets[np.random.randint(len(func_sets))]
            new_program = [retain_func]
            new_program += [Individual(factor, 2) for factor in factors_sets]
        return new_program
    
    def build_program(self, random_state):
        factors_max = self._init_depth[1] if self._init_depth[1] < len(self._factor_sets) else len(self._factor_sets)
        factors_max_prob = np.random.randint(factors_max) / len(self._factor_sets)
        factors = self._factor_sets[np.random.randint(len(self._factor_sets))]
        combine_func = self._combine_func[np.random.randint(len(self._combine_func))]
        program = [Individual(factors, 2), Individual(combine_func, 1)]
        factors_list = (np.random.uniform(0, 1, (1, len(self._factor_sets))) < factors_max_prob).tolist()
        factors_list = list(set(list(np.array(self._factor_sets)[factors_list])))
        program += [Individual(factor, 2) for factor in factors_list]
        return self.duplicate_removal(program)
    
    
    def get_subtree(self, random_state=None, program=None):
        if program is None:
            program = self._program
        probs = np.array([0.9 if node._value in self._factor_sets else 0.1 for node in program])
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
            if program[node]._value in self._factor_sets:
                replace_node = self._factor_sets[np.random.randint(0,len(self._factor_sets)-1)]
                program[node] = Individual(replace_node,2)
            else:
                replace_node = self._combine_func[np.random.randint(0,len(self._combine_func)-1)]
                program[node] = Individual(replace_node,1)
        return self.duplicate_removal(program), list(mutate)
    
    def evaluation(self, standard_data,  default_value, fitness_method='high_frequency',
                   horizon=2, is_neutralize=0):
        risk_data = standard_data[['trade_date','code'] + self._industry_styles + self._risk_styles]
        mkt_df = standard_data[['closePrice', 'openPrice', 'lowestPrice', 'highestPrice', 'turnoverVol',
                         'turnoverValue', 'trade_date', 'code', 'accumAdjFactor',
                         'chgPct', 'bar30_vwap', 'bar60_vwap']]
        #合成
        func_sets = self._func_method()
        factors_columns = self._factors_sets()
        combine = CombineEngine.create_engine(func_sets._name)
        try:
            if func_sets._name == 'hist_ret_combine' or func_sets._name == 'hist_ic_combine':
                if func_sets._method == 'equal':
                    factors_data, hist_ret = combine(factor_df=standard_data, mret_df=mkt_df, factor_list=factors_columns,
                                                     span=func_sets._span)
                elif func_sets._method == 'half_life':
                    factors_data, hist_ret = combine(factor_df=standard_data, mret_df=mkt_df, factor_list=factors_columns,
                                                         span=func_sets._span, method='half_life', 
                                                     half_life=func_sets._custom_params)
            elif func_sets._name == 'max_icir_combine' or func_sets._name == 'max_ic_combine':
                if func_sets._method == 'sample':
                    factors_data, m_ir_df = combine(factor_df=standard_data, mret_df=mkt_df, factor_list=factors_columns, 
                                                    span=func_sets._span)
                elif func_sets._method == 'shrunk':
                    factors_data, m_ir_df = combine(factor_df=standard_data, mret_df=mkt_df, factor_list=factors_columns,
                                                    span=func_sets._span, method='shrunk', weight_limit=func_sets._custom_params)
                
                
            weight = Weighted.create_weighted(method=fitness_method)
            result =  weight.run(factor_data=factors_data, horizon=horizon,
                               risk_data=risk_data, mkt_df=mkt_df,
                               factor_name='combine', is_neutralize=is_neutralize,
                               default_value=np.iinfo(np.int32))
            raw_fitness = default_value if result['status'] == 0 else abs(result['score'])
            self._raw_fitness = default_value if np.isnan(raw_fitness) else raw_fitness
            self._is_valid = False if self._raw_fitness == default_value else True
        except Exception as e:
            self._raw_fitness = default_value
            self._is_valid  = False
            print(e)

def parallel_evolve(n_programs, parents, standard_data, seeds, factor_sets, span_sets, 
                    half_sets, weight_limit_sets, gen, params):
    tournament_size = params['tournament_size']
    init_depth = params['init_depth']
    greater_is_better = params['greater_is_better'] 
    method_probs = params['method_probs']
    p_point_replace = params['p_point_replace']
    
    programs = []
    def _contenders(tour_parents):
        ctournament_size = tournament_size if tournament_size < 2 else 2
        contenders = random_state.randint(0, len(tour_parents), ctournament_size)
        return [tour_parents[p] for p in contenders]
    
    def _tournament(tour_parents):
        ttournament_size = tournament_size if tournament_size < len(tour_parents) else len(tour_parents)
        contenders = random_state.randint(0, len(tour_parents), ttournament_size)
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
                parent = Program(gen=gen, random_state=random_state, factor_sets=factor_sets, 
                                 span_sets=span_sets, half_sets=half_sets,weight_limit_sets=weight_limit_sets,
                                 init_depth=init_depth,p_point_replace=p_point_replace, 
                                 program=program, parents=parents)
                
            #新特征种群加入
            if random_state.uniform() < method_probs[2]:
                program = Program(gen=gen, random_state=random_state, factor_sets=factor_sets, 
                                  span_sets=span_sets, half_sets=half_sets,weight_limit_sets=weight_limit_sets,
                                  init_depth=init_depth,p_point_replace=p_point_replace, 
                                  program=None)
                program, removed, remains = parent.crossover(program._program, random_state)
                parent = Program(gen=gen, random_state=random_state, factor_sets=factor_sets, 
                                 span_sets=span_sets, half_sets=half_sets,weight_limit_sets=weight_limit_sets,
                                 init_depth=init_depth,p_point_replace=p_point_replace, 
                                 program=program)
      
            if method < 0:#method_probs[0]: # # crossover
                donor, donor_index = _tournament(copy(parents))
                program, removed, remains = parent.crossover(donor._program, random_state)
                genome = {'method':'Crossover',
                         'parent_idx':parent_index,
                         'parent_nodes':removed,
                         'donor_idx':donor_index,
                         'donor_nodes':remains}
            elif method < 0:#method_probs[1]: # subtree_mutation
                program, removed, _ = parent.subtree_mutation(random_state)
                genome = {'method': 'Subtree Mutation',
                          'parent_idx': parent_index,
                          'parent_nodes': removed}
            elif method < 0:#method_probs[2]: # hoist_mutation
                program, removed = parent.hoist_mutation(random_state)
                genome = {'method': 'Hoist Mutation',
                          'parent_idx': parent_index,
                          'parent_nodes': removed}
            elif method < 1:#method_probs[3]: # point_mutation
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
                program = Program(gen=gen, random_state=random_state, factor_sets=factor_sets, 
                                  span_sets=span_sets, half_sets=half_sets,weight_limit_sets=weight_limit_sets,
                                  init_depth=init_depth,p_point_replace=p_point_replace, 
                                  program=program, parents=genome)
                program, removed, remains = program.crossover(ori_parent._program, random_state)
                
        program = Program(gen=gen, random_state=random_state, factor_sets=factor_sets, 
                          span_sets=span_sets, half_sets=half_sets,weight_limit_sets=weight_limit_sets,
                          init_depth=init_depth,p_point_replace=p_point_replace, 
                          program=program, parents=genome)
        default_value = MIN_INT if greater_is_better else MAX_INT
        program.evaluation(standard_data,  default_value)
        print(program._raw_fitness)
        programs.append(program)
    return programs
    
class Gentic(object):
    def __init__(self, factors_sets, span_sets, half_sets, weight_limit_sets=[True, False],
                 random_state=None, population_size=5, tournament_size=2, 
                 generations=MAX_INT,greater_is_better=True,verbose=1,convergence=0.05,
                 init_depth=(5, 6), n_jobs=1, p_crossover=0.9, p_subtree_mutation=0.01,
                 p_hoist_mutation=0.01, p_point_mutation=0.01, p_point_replace=0.5):
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
        self._factors_sets = factors_sets
        self._span_sets = span_sets
        self._half_sets = half_sets
        self._weight_limit_sets = weight_limit_sets
        
    def train(self, standard_data):
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
            population = Parallel(n_jobs=self._n_jobs,
                                  verbose=self._verbose)(
                delayed(parallel_evolve)(n_programs[i], parents, standard_data, seeds, self._factors_sets,
                                         self._span_sets, self._half_sets, self._weight_limit_sets, 
                                         gen, params)
                for i in range(n_jobs))
            
            population = list(itertools.chain.from_iterable(population))
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