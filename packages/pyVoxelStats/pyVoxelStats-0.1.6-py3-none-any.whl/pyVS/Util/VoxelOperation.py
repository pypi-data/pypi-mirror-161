import datetime
import os
import subprocess
import sys
import time
from multiprocessing import Pool

import ipyparallel as ipp
import numexpr
import numpy
import pandas

from pyVS.pyVoxelStats.pyVoxelStats import pyVoxelStats
from pyVS.pyVoxelStats.ShareObj import ShareObj

class VoxelOperation(pyVoxelStats):
    def __init__(self, string_model_obj, dataset_obj, masker_obj, stats_obj):
        pyVoxelStats.__init__(self)
        self.string_model_obj = string_model_obj
        self.dataset_obj = dataset_obj
        self.masker = masker_obj
        self.stats_obj = stats_obj
        self.voxel_var_data_map = {}
        self.operation_dataset = {}
        self.total_voxel_ops = None
        self.results = None
        self.rc = None
        self.par_view = None
        self.number_of_engines = 0

        self.temp_package = None
        self.predictions = None


    def set_up_cluster(self, clus_json=None, profile_name='default', workers=None, no_start=False, clust_sleep_time=10):
        if not pyVoxelStats._no_parallel:
            print('Setting up cluster .....')
            if clus_json:
                self.rc = ipp.Client(clus_json)
            else:
                if not no_start:
                    self.cluster_profile = profile_name
                    p0 = subprocess.Popen(['ipcluster stop --profile={0}'.format(profile_name)], shell=True)
                    time.sleep(5)
                    if workers:
                        str_args = ['ipcluster start --profile={1} -n {0}'.format(workers, profile_name)]
                    else:
                        str_args = ['ipcluster start --profile={0}'.format(profile_name)]
                    p = subprocess.Popen(str_args, shell=True)
                    if profile_name == 'default':
                        time.sleep(clust_sleep_time)
                    else:
                        time.sleep(clust_sleep_time)
                self.rc = ipp.Client(profile=str.encode(profile_name))
            self.par_view = self.rc.direct_view(targets='all')
            self.number_of_engines = len(self.par_view)
            print('Connected to {0} workers. '.format(self.number_of_engines))

    def shut_down_cluster(self, cluster_shut_down):
        if cluster_shut_down:
            if not pyVoxelStats._no_parallel:
                print("Shutting down cluster .....")
                p0 = subprocess.Popen(['ipcluster stop --profile={0}'.format(self.cluster_profile)], shell=True)
                time.sleep(6)
                print("Shutting down cluster complete.")
        else:
            print("Cluster shutdown is skipped")

    def set_up(self):
        print('Setting up voxel operations ... ')
        self.read_voxel_vars()
        self.set_up_data_for_op()

    def read_voxel_vars(self):
        print('File reading ...')
        total_files = 0
        pool = Pool()
        for var in self.string_model_obj._voxel_vars:
            list_of_files = self.dataset_obj._data_table[var]
            image_data_list = pool.map(self.masker.get_data_from_image, list_of_files)
            var_data_list = []
            for image_idx in range(len(image_data_list)):
                masked_data, need_new_ref = self.masker.mask_image_data(image_data_list[image_idx])
                if need_new_ref:
                    self.masker.ref_file = list_of_files[image_idx]
                var_data_list.append(masked_data)
            total_files += len(var_data_list)
            self.voxel_var_data_map[var] = numpy.vstack(var_data_list)
        pool.close()
        pool.join()
        print('Done. Total files read : {0}'.format(total_files))

    def __apply_voxel_ops(self, var_name, var_data):
        if not self.string_model_obj.multi_var_ops:
            return var_data
        data_dict = {var_name : var_data}
        for op in self.string_model_obj.multi_var_ops:
            try:
                ret_data = numexpr.evaluate(op, local_dict=data_dict)
                return ret_data
            except:
                pass
        return var_data

    def set_up_data_for_op(self):
        if not self.voxel_var_data_map:
            print('Voxel Data not read. Cannot continue.')
            return None
        else:
            for var in self.string_model_obj._used_vars:
                if var not in self.string_model_obj._voxel_vars:
                    self.operation_dataset[var] = dict(data=VarDataAccessPointer(self.__apply_voxel_ops(var, self.dataset_obj._data_table[var]), 1),
                                                       shape=self.dataset_obj._data_table[var].shape)
                else:
                    self.operation_dataset[var] = dict(
                        data=VarDataAccessPointer(self.__apply_voxel_ops(var, self.voxel_var_data_map[var]), self.voxel_var_data_map[var].shape[1]),
                        shape=self.voxel_var_data_map[var].shape)
        self.total_voxel_ops = max(
            self.operation_dataset[k]['shape'][1] if len(self.operation_dataset[k]['shape']) > 1 else 1 for k in
            self.operation_dataset)
        self.results = VoxelOpResultsWrapper(self.total_voxel_ops, self.stats_obj)
        self.results.save_model = self._save_model


    def __get_block_from_var_dict(self, block_variable_dict, start_loc):
        vars = list(block_variable_dict.keys())
        blockSize = block_variable_dict[vars[0]].shape[1]
        n_subs = block_variable_dict[vars[0]].shape[0]
        n_formats = ['f8'] * len(vars)
        n_dtype = dict(names=vars, formats=n_formats)
        n_data = numpy.zeros(n_subs, dtype=n_dtype)
        def f(k):
            for var in vars:
                n_data[var][:] = block_variable_dict[var][:, [k]].T
            return dict(data_block=pandas.DataFrame(n_data), location=start_loc + k, stats_obj=self.stats_obj)

        data_block = [f(x) for x in range(blockSize)]
        return data_block

    def __get_data_block(self, blockSize, block_number):
        finished = False
        if (blockSize * block_number) > self.total_voxel_ops:
            finished = True
            return ([], finished)
        elif (blockSize * (block_number + 1) > self.total_voxel_ops) & (
                blockSize * block_number < self.total_voxel_ops):
            block_var_dict = {}
            for var in self.operation_dataset:
                block_var_dict[var] = self.operation_dataset[var]['data'].get_data_block(int(blockSize * block_number),
                                                                                         int(self.total_voxel_ops - 1))
        else:
            block_var_dict = {}
            for var in self.operation_dataset:
                block_var_dict[var] = self.operation_dataset[var]['data'].get_data_block(int(blockSize * block_number),
                                                                                         int((blockSize * (
                                                                                         block_number + 1)) - 1))
        return (self.__get_block_from_var_dict(block_var_dict, int(blockSize * block_number)), finished)

    def __get_data_block_wIdx(self, blockSize, block_number, idx):
        finished = False
        if (blockSize * block_number) > self.total_voxel_ops:
            finished = True
            return ([], [], finished)
        elif (blockSize * (block_number + 1) > self.total_voxel_ops) & (
                        blockSize * block_number < self.total_voxel_ops):
            block_var_dict = {}
            for var in self.operation_dataset:
                block_var_dict[var] = self.operation_dataset[var]['data'].get_data_block_wIdx(int(blockSize * block_number),
                                                                                         int(self.total_voxel_ops - 1), idx)
        else:
            block_var_dict = {}
            for var in self.operation_dataset:
                block_var_dict[var] = self.operation_dataset[var]['data'].get_data_block_wIdx(int(blockSize * block_number),
                                                                                         int((blockSize * (
                                                                                             block_number + 1)) - 1), idx)
        return (self.__get_block_from_var_dict(block_var_dict, int(blockSize * block_number)), finished)

    def __get_data_block_cv(self, blockSize, block_number, train_idx, test_idx):
        train_blk, finished = self.__get_data_block_wIdx(blockSize, block_number, train_idx)
        test_blk, finished = self.__get_data_block_wIdx(blockSize, block_number, test_idx)
        return train_blk, test_blk, finished

    def execute(self):
        print('Execution started ... ')
        ex_st_time = datetime.datetime.now()
        slice_count = int(self.config['VSVoxelOPS']['slice_count'])
        print('Slices - {0}'.format(slice_count))
        blockSize = numpy.ceil(self.total_voxel_ops / slice_count)
        all_results = []
        for art_slice in range(slice_count):
            print('Slice - {0}/{1}'.format(art_slice + 1, slice_count))
            sl_st_time = datetime.datetime.now()
            data_block, finished = self.__get_data_block(blockSize, art_slice)
            d_end_time = datetime.datetime.now()
            if self._debug: print('Block creation time - {0}'.format(d_end_time-sl_st_time))
            if finished:
                print('Analysis complete')
            else:
                pr_st_time = datetime.datetime.now()
                if self._no_parallel:
                    par_results = map(run_par, data_block)
                else:
                    self.par_view.map(os.chdir, [os.getcwd()] * self.number_of_engines)
                    par_results = self.par_view.map_sync(run_par, data_block)
                pr_end_time = datetime.datetime.now()
                all_results.extend(par_results)
                ext_end_time = datetime.datetime.now()
                if self._debug: print('Parallel time - {0}'.format(pr_end_time - pr_st_time))
                if self._debug: print('Extend time - {0}'.format(ext_end_time - pr_end_time))
            sl_end_time = datetime.datetime.now()
            print(' - Time: {0} - Remaining time : {1}'.format((sl_end_time - sl_st_time), (sl_end_time - sl_st_time) * (slice_count - art_slice + 1)))
        self.results.temp_results = all_results
        full_end_time = datetime.datetime.now()
        print('Total execution time {0}'.format((full_end_time - ex_st_time)))

    def cv_execute(self, cv_generator=None, repeats=1):
        if not cv_generator:
            raise Exception('Please provide a scikit learn cross validation generator - Eg: KFold, LOO')
        if repeats > 1:
            print('Please make sure the cv generator uses shuffle when using repeats. ')

        print('Cross validation execution started ...')
        ex_st_time = datetime.datetime.now()
        slice_count = int(self.config['VSVoxelOPS']['slice_count'])
        print('Slices - {0}'.format(slice_count))
        blockSize = numpy.ceil(self.total_voxel_ops / slice_count)

        X = numpy.arange(self.dataset_obj.get_no_subjects())
        all_results = []
        all_preds = []
        all_obs = []
        for rep in range(repeats):
            print('In repeat {0}'.format(rep))
            cv_count = 0
            rep_results = []
            rep_preds = numpy.zeros((self.dataset_obj.get_no_subjects(), self.total_voxel_ops))
            rep_obs = numpy.zeros((self.dataset_obj.get_no_subjects(), self.total_voxel_ops))
            for train_idx, test_idx in cv_generator.split(X):
                cv_count += 1
                print('In CV - {0}'.format(cv_count))
                cv_k_results = []
                for art_slice in range(slice_count):
                    print('Slice - {0}/{1} ; CV - {2} ; Rep - {3}'.format(art_slice + 1, slice_count, cv_count, rep+1))
                    sl_st_time = datetime.datetime.now()
                    train_data_block, test_data_block, finished = self.__get_data_block_cv(blockSize, art_slice, train_idx, test_idx)
                    d_end_time = datetime.datetime.now()
                    if self._debug: print('Block creation time - {0}'.format(d_end_time - sl_st_time))
                    if finished:
                        print('Analysis complete for CV')
                    else:
                        self.par_view.map(os.chdir, [os.getcwd()] * self.number_of_engines)
                        #self.par_view.map(sys.path.append,
                        #                 ['/home/sulantha/PycharmProjects/pyVS'] * self.number_of_engines)
                        #self.par_view.map(sys.path.append,
                        #                  ['/home/sulantha/PycharmProjects/pyVS/Util'] * self.number_of_engines)
                        pr_st_time = datetime.datetime.now()
                        if self._no_parallel:
                            par_results_wPred = map(run_par_cv, train_data_block, test_data_block)
                        else:
                            par_results_wPred = self.par_view.map_sync(run_par_cv, train_data_block, test_data_block)
                        pr_end_time = datetime.datetime.now()
                        par_results, preds, obs = zip(*par_results_wPred)
                        par_results = list(par_results)
                        preds = list(preds)
                        obs = list(obs)
                        cv_k_results.extend(par_results)

                        block_locations = [t_blk_dict['location'] for t_blk_dict in test_data_block]
                        pred_res_counter = 0
                        for test_id in test_idx:
                            rep_preds[test_id, numpy.array(block_locations)] = numpy.array(preds).T[pred_res_counter, :]
                            rep_obs[test_id, numpy.array(block_locations)] = numpy.array(obs).T[pred_res_counter, :]
                            pred_res_counter += 1
                        ext_end_time = datetime.datetime.now()
                        if self._debug: print('Parallel time - {0}'.format(pr_end_time - pr_st_time))
                        if self._debug: print('Extend time - {0}'.format(ext_end_time - pr_end_time))
                    sl_end_time = datetime.datetime.now()
                    print(' - Time: {0} - Remaining time in this CV : {1}'.format((sl_end_time - sl_st_time),
                                                                       (sl_end_time - sl_st_time) * (
                                                                       slice_count - art_slice + 1)))

                rep_results.append(cv_k_results)
                print('CV - {0} Done. '.format(cv_count))
            all_results.append(rep_results)
            all_preds.append(rep_preds)
            all_obs.append(rep_obs)
            print('Rep - {0} Done.'.format(rep+1))

        self.results.temp_results = all_results
        self.predictions = CV_PredsHandler(repeats, all_preds, all_obs[0])
        full_end_time = datetime.datetime.now()
        print('Total execution time {0}'.format((full_end_time - ex_st_time)))

def ParGetBlock(i):
    data = {var: ShareObj.block_dict['block_variable_dict'][var][:, i] for var in ShareObj.block_dict['var_names']}
    return dict(data_block=pandas.DataFrame.from_dict(data), location=ShareObj.block_dict['start_loc'] + i,
                stats_obj=ShareObj.block_dict['stats_obj'])

def run_par(data_block):
    loc = data_block['location']
    res = data_block['stats_obj'].fit(data_block['data_block'])
    return ParRes(loc, res)

def run_par_cv(train_data_block, test_data_block):
    loc = train_data_block['location']
    res = train_data_block['stats_obj'].fit(train_data_block['data_block'])
    preds = train_data_block['stats_obj'].predict(test_data_block['data_block'])
    obs_var_name = train_data_block['stats_obj'].obs_var_name
    obs = test_data_block['data_block'][obs_var_name].as_matrix()
    return ParRes(loc, res), preds, obs

class ParRes:
    def __init__(self, loc, res):
        self.loc = loc
        self.res = res

class VarDataAccessPointer:
    def __init__(self, var_data, outer_shape):
        self.var_data = var_data
        self.outer_shape = outer_shape

    def get_data(self, pointer_loc):
        if self.outer_shape == 1:
            return self.var_data.to_numpy(copy=True)
        return self.var_data[:, pointer_loc % self.outer_shape]

    def get_data_block(self, loc_1, loc_2):
        data = [self.get_data(loc) for loc in range(loc_1, loc_2 + 1)]
        return numpy.vstack(data).T

    def get_data_block_wIdx(self, loc_1, loc_2, idx):
        data = [self.get_data(loc) for loc in range(loc_1, loc_2 + 1)]
        return numpy.vstack(data).T[idx]

class VoxelOpResultsWrapper:
    def __init__(self, total_voxel_operations, stats_model):
        self.total_ops = total_voxel_operations
        self.stats_model = stats_model
        self.temp_results = None
        self.__results = None

        self.__models = None

        self.save_model = False


    def modify_temp_result_parallel(self, result):
        self.modify_temp_result(result.res, result.loc)

    def modify_temp_result(self, value, loc):
        self.temp_results.insert(loc, value)

    def get_results(self):
        if not self.__results:
            self.__get_final_voxel_op_result()
        return self.__results

    def get_models(self):
        if not isinstance(self.__models, numpy.ndarray) and self.save_model:
            self.__get_final_voxel_op_result()
        return self.__models

    def get_model_vars_and_params(self):
        model_wise_results_names = None
        var_wise_results_names = None
        model_var_names = None
        result_good = False
        for o in self.temp_results: ## This section was added becuase of a problem arised from the GAM analysis. As we use rpy2, if there is an statical error, the result object is None and do not contain any info to
            # get the variable infomation. So we go through all the results to find the one which is not None to get the relavent information.
            if o.res:
                try:
                    model_var_names = o.res['variable_names_in_model_op']
                except KeyError:
                    model_var_names = None
                result_good = True
                try:
                    model_wise_results_names = o.res['model_wise_results_names']
                    var_wise_results_names = o.res['var_wise_results_names']
                except:
                    model_wise_results_names = self.stats_model.model_wise_results_names
                    var_wise_results_names = self.stats_model.var_wise_results_names
                if model_var_names:
                    var_wise_results_dict = {var_name: set() for var_name in var_wise_results_names}
                    for name in model_var_names:
                        for var_wise_name in var_wise_results_names:
                            if name in o.res[var_wise_name]:
                                var_wise_results_dict[var_wise_name].add(name)
                    var_wise_results_dict = {var_name: list(var_wise_results_dict[var_name]) for var_name in var_wise_results_dict}
                else:
                    var_wise_results_dict = None
                break
        if not result_good:
            return None, None, None, result_good

        if self.stats_model.model_wise_results_names:
            model_wise_results_names = self.stats_model.model_wise_results_names
            var_wise_results_names = self.stats_model.var_wise_results_names
            return model_wise_results_names, var_wise_results_names, model_var_names, var_wise_results_dict, result_good
        return model_wise_results_names, var_wise_results_names, model_var_names, var_wise_results_dict, result_good

    def __get_final_voxel_op_result(self):
        print('Building final results. This may take a while depending on the dimensions of the images. ')
        res_bl_st = datetime.datetime.now()
        model_wise_results_names, var_wise_results_names, model_var_names, var_wise_results_dict, results_good = self.get_model_vars_and_params()
        if results_good:
            builer = ResultBuilder(self.temp_results, self.total_ops, model_wise_results_names, var_wise_results_names, model_var_names, var_wise_results_dict, results_good)
            builer.save_model = self.save_model
            self.__results, self.__models = builer.make_result()
            self.temp_results = None
            print('Final results building finished. ')
        else:
            print('Error in results. None of the results were successful. Check statistical errors. Use no parallel option in VoxelOperation to see the errors at voxel level.')
            self.temp_results = None
            self.results = None
        res_bl_end = datetime.datetime.now()
        print('Time taken to build final results: {0}'.format(res_bl_end-res_bl_st))


class ResultBuilder:
    def __init__(self, temp_results, total_ops, model_wise_results_names, var_wise_results_names, model_var_names, var_wise_results_dict, results_good):
        self.temp_results = temp_results
        self.total_ops = total_ops
        self.model_wise_results_names = list(set(model_wise_results_names)) if model_wise_results_names else None
        self.var_wise_results_names= list(set(var_wise_results_names)) if var_wise_results_names else None
        self.model_var_names = list(set(model_var_names)) if model_var_names else None
        self.var_wise_results_dict = var_wise_results_dict
        self.results_good = results_good
        self.save_model = False

    def value_to_record(self, value):
        tup = ()
        if self.model_wise_results_names:
            tup = tup + tuple(value.res[var] for var in self.model_wise_results_names)
        if self.var_wise_results_names:
            tup = tup + tuple(tuple(value.res[var][name] for name in self.var_wise_results_dict[var]) for var in self.var_wise_results_dict)
        return tup

    def make_result(self):
        self.temp_results.sort(key=lambda x: x.loc, reverse=False)
        dtype = []
        if self.model_wise_results_names:
            for var in self.model_wise_results_names:
                dtype.append(("{0}".format(var), "f8"))
        if self.var_wise_results_names:
            for var in self.var_wise_results_dict:
                dtype.append(("{0}".format(var), [("{0}".format(name), "f8") for name in self.var_wise_results_dict[var]]))
        print('Outputs: Model wise: {0}'.format(self.model_wise_results_names))
        print('Outputs:  Variable wise: {0}'.format(self.var_wise_results_names))
        print('Variables names in model: Model wise: {0}'.format(self.model_var_names))
        arr = numpy.fromiter(map(self.value_to_record, self.temp_results), dtype=dtype, count=self.total_ops)
        models = None
        if self.save_model:
            models = numpy.array([t_res.res['model'] for t_res in self.temp_results])
        return arr, models

    def make_result_p(self, obj, res):
        i = obj.loc
        result = obj.res
        if  self.model_wise_results_names:
            for var in self.model_wise_results_names:
                res[var][i] = result[var]
        if  self.var_wise_results_names:
            for var in self.var_wise_results_names:
                for name in self.model_var_names:
                    try:
                        res[var][name][i] = result[var][name]
                    except KeyError as e:
                        ##TODO Add a debug check
                        pass

        return None

class CV_PredsHandler:
    def __init__(self, n_repeats, predictions, obs_data):
        self.n_repeats = n_repeats
        self.preds = numpy.array(predictions)
        self.obs_data = numpy.array(obs_data)

    def get_predictions(self):
        return self.preds

    def get_mean_prediction(self):
        return numpy.mean(self.preds, 0)

    def get_error_pred(self):
        return self.preds - self.obs_data

    def get_rmse(self):
        return numpy.sqrt(numpy.mean(numpy.square(self.get_mean_prediction() - self.obs_data), axis=0))
