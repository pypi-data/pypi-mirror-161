import pandas, re, numpy
import statsmodels.formula.api as smf
import statsmodels.tools.sm_exceptions as sme
from pyVS.pyVoxelStats.pyVoxelStats import pyVoxelStats
import numexpr, copy


class DataMatrix(pyVoxelStats):
    def __init__(self):
        pyVoxelStats.__init__(self)
        self._X = None
        self._Y = None


class Dataset(pyVoxelStats):
    def __init__(self, file_name, file_type='csv', delimiter=',', filter_string=None, string_model_obj=None):
        pyVoxelStats.__init__(self)
        self._file_name = file_name
        self._file_type = file_type
        self._delimiter = delimiter
        self._filter_string = filter_string
        self._data_table_full = self.__load_data()
        self.string_model_obj = string_model_obj
        self._data_table = self.__get_data_table()

    def __load_data_file(self):
        data_set = None
        if self._file_type == 'csv':
            data_set = pandas.read_csv(self._file_name, delimiter=self._delimiter)
        return data_set

    def __filter_data_file(self, data_set):
        return data_set.query(self._filter_string)

    def __load_data(self):
        data_set = self.__load_data_file()
        if self._filter_string:
            filtered_data = self.__filter_data_file(data_set)
        else:
            filtered_data = data_set
        return filtered_data

    def __get_data_table(self, used_vars=None):
        if not used_vars:
            used_vars = self.string_model_obj._used_vars
        return self._data_table_full[used_vars]

    def get_no_subjects(self):
        return len(self._data_table.index)


class StatsModel(pyVoxelStats):
    def __init__(self, type):
        pyVoxelStats.__init__(self)
        self._type = type
        self.mod = None
        self.obs_var_name = None
        self.save_models = False

        try:
            self.model_wise_results_names = [re.sub('\\[|\\]', '', s.strip().replace("'", '')) for s in
                                             self.config['ResultsModelWiseResults'][self._type].split(',')]
        except KeyError:
            self.model_wise_results_names = None
        try:
            self.var_wise_results_names = [re.sub('\\[|\\]', '', s.strip().replace("'", '')) for s in
                                           self.config['ResultsModelVariableWiseResults'][self._type].split(',')]
        except KeyError:
            self.var_wise_results_names = None

    def fit(self, data_frame):
        raise NotImplementedError()

    def predict(self, data_frame):
        raise NotImplementedError()

    def filter_result_statsmodels(self, result, model):
        result_f = {}
        for vard in self.model_wise_results_names:
            if result:
                result_f[vard] = getattr(result, vard)
            else:
                result_f[vard] = 0
        variable_names_in_model_op = model.exog_names
        for vard in self.var_wise_results_names:
            if result:
                result_f[vard] = {name: getattr(result, vard)[name] for name in variable_names_in_model_op}
            else:
                result_f[vard] = {name: 0 for name in variable_names_in_model_op}
        result_f['variable_names_in_model_op'] = variable_names_in_model_op
        result_f['model_wise_results_names'] = self.model_wise_results_names
        result_f['var_wise_results_names'] = self.var_wise_results_names
        if self.save_models:
            result_f['model'] = model
        return result_f


class LM(StatsModel):
    def __init__(self, string_model, weights=None):
        StatsModel.__init__(self, 'lm')
        self.string_model = string_model
        self.weights = weights

    def fit(self, data_frame):
        if self.weights:
            if isinstance(self.weights, str):
                mod = smf.wls(formula=self.string_model._string_model_str, data=data_frame, weights=data_frame[self.weights].values)
            elif isinstance(self.weights, numpy.ndarray) or isinstance(self.weights, float):
                mod = smf.wls(formula=self.string_model._string_model_str, data=data_frame, weights=self.weights)
            else:
                print('Weights either has to be column name, ndarray or a float. Reverting to OLS regression')
                mod = smf.ols(formula=self.string_model._string_model_str, data=data_frame)
        else:
            mod = smf.ols(formula=self.string_model._string_model_str, data=data_frame)
        self.mod = mod
        self.obs_var_name = mod.endog_names
        try:
            res = mod.fit()
        except (sme.PerfectSeparationError, sme.MissingDataError) as e:
            res = None
            # print('Statistics exception; result for the voxel may be set to 0 : ' + str(e))
        return self.filter_result_statsmodels(res, mod)

    def predict(self, data_frame):
        if not self.mod:
            raise Exception('Model is not fitted. Please fit the model prior to using predict')
        else:
            X_vars = copy.deepcopy(self.string_model._used_vars)
            X_vars.remove(self.mod.endog_names)
            data_frame = data_frame[X_vars]
            preds = self.mod.fit().predict(data_frame)
        return preds

class RLM(StatsModel):
    def __init__(self, string_model):
        StatsModel.__init__(self, 'rlm')
        self.string_model = string_model

    def fit(self, data_frame):
        mod = smf.rlm(formula=self.string_model._string_model_str, data=data_frame)
        self.mod = mod
        try:
            res = mod.fit()
        except (sme.PerfectSeparationError, sme.MissingDataError) as e:
            res = None
            # print('Statistics exception; result for the voxel may be set to 0 : ' + str(e))
        return self.filter_result_statsmodels(res, mod)


class GLM(StatsModel):
    def __init__(self, string_model, family_obj):
        StatsModel.__init__(self, 'glm')
        self.string_model = string_model
        self.family_obj = family_obj

    def fit(self, data_frame):
        mod = smf.glm(formula=self.string_model._string_model_str, data=data_frame, family=self.family_obj)
        self.mod = mod
        try:
            res = mod.fit()
        except (sme.PerfectSeparationError, sme.MissingDataError) as e:
            res = None
            # print('Statistics exception; result for the voxel may be set to 0 : ' + str(e))
        return self.filter_result_statsmodels(res, mod)


class LME(StatsModel):
    def __init__(self, string_model, groups):
        StatsModel.__init__(self, 'lme')
        self.string_model = string_model
        self.groups = groups

    def fit(self, data_frame):
        mod = smf.gee(formula=self.string_model._string_model_str, data=data_frame, groups=self.groups)
        self.mod = mod
        try:
            res = mod.fit()
        except (sme.PerfectSeparationError, sme.MissingDataError) as e:
            res = None
            # print('Statistics exception; result for the voxel may be set to 0 : ' + str(e))
        return self.filter_result_statsmodels(res, mod)



class GEE(StatsModel):
    def __init__(self, string_model, family_obj, groups, covariance_obj, time):
        StatsModel.__init__(self, 'gee')
        self.string_model = string_model
        self.family_obj = family_obj
        self.covariance_obj = covariance_obj
        self.time = time
        self.groups = groups

    def fit(self, data_frame):
        mod = smf.gee(formula=self.string_model._string_model_str, groups=self.groups, data=data_frame, family=self.family_obj,
                      cov_struct=self.covariance_obj)
        self.mod = mod
        try:
            res = mod.fit()
        except (sme.PerfectSeparationError, sme.MissingDataError) as e:
            res = None
            print('Statistics exception; result for the voxel may be set to 0 : ' + str(e))
        return self.filter_result_statsmodels(res, mod)

class GAM(StatsModel):
    def __init__(self, string_model, family_str, method_str):
        StatsModel.__init__(self, 'gam')
        self.string_model = string_model
        self.family_obj = family_str
        self.method = method_str
        self.model_wise_results_names = []
        self.var_wise_results_names = []

    def fit(self, data_frame):
        import readline
        import rpy2.robjects as r
        from rpy2.robjects.packages import importr
        from rpy2.robjects import pandas2ri
        pandas2ri.activate()
        mgcv = importr('mgcv')
        family = r.r(self.family_obj) if self.family_obj else r.r('gaussian()')
        method_s = self.method if self.method else 'REML'
        opt = r.StrVector(['perf'])
        #ctrl = mgcv.control(maxiter=200)
        try:
            res = mgcv.gam(r.Formula(self.string_model._string_model_str), family=family, data=data_frame, method=method_s)
        except Exception as e:
            res = None
            #print('Statistics exception; result for the voxel may be set to 0 : ' + str(e))
        self.mod = res
        return self.filter_result_gam(res, None)

    def filter_result_gam(self, result, model):
        import rpy2.robjects as r
        if not result:
            return None
        summary = r.r.summary(result)
        model_wise_names = ["deviance", "null.deviance", "df.null", "aic", "scale", "df.residual"]
        model_wise_names_sum = ["dev.expl", "r.sq"]
        vars_in_ptable = list(summary.rx2('p.table').dimnames[0])
        cols_in_ptable = list(summary.rx2('p.table').dimnames[1])
        vars_in_stable = list(summary.rx2('s.table').dimnames[0])
        cols_in_stable = list(summary.rx2('s.table').dimnames[1])
        result_f = {}
        variable_names_in_model_op = vars_in_ptable + vars_in_stable
        for vard in model_wise_names:
            self.model_wise_results_names.append(vard)
            if result:
                result_f[vard] = result.rx2(vard)[0]
            else:
                result_f[vard] = 0
        for vard in model_wise_names_sum:
            self.model_wise_results_names.append(vard)
            if result:
                result_f[vard] = summary.rx2(vard)[0]
            else:
                result_f[vard] = 0
        for vard_idx in range(len(cols_in_ptable)):
            vard_s = 'p.table.{0}'.format(cols_in_ptable[vard_idx])
            self.var_wise_results_names.append(vard_s)
            if result:
                result_f[vard_s] = {vars_in_ptable[name_idx]: summary.rx2('p.table').rx(name_idx+1, True)[vard_idx] for name_idx in range(len(vars_in_ptable))}
            else:
                result_f[vard_s] = {vars_in_ptable[name_idx]: 0 for name_idx in range(len(vars_in_ptable))}
        for vard_idx in range(len(cols_in_stable)):
            vard_s = 's.table.{0}'.format(cols_in_stable[vard_idx])
            self.var_wise_results_names.append(vard_s)
            if result:
                result_f[vard_s] = {vars_in_stable[name_idx]: summary.rx2('s.table').rx(name_idx + 1, True)[vard_idx] for name_idx in range(len(vars_in_stable))}
            else:
                result_f[vard_s] = {vars_in_stable[name_idx]: 0 for name_idx in range(len(vars_in_stable))}
        result_f['variable_names_in_model_op'] = variable_names_in_model_op
        result_f['model_wise_results_names'] = self.model_wise_results_names
        result_f['var_wise_results_names'] = self.var_wise_results_names
        return result_f

class Power(StatsModel):
    def __init__(self, string_model):
        StatsModel.__init__(self, 'power')
        self.string_model = string_model

    def get_expr_string(self, data_frame):
        s = self.string_model._string_model_str
        if 'std' in s:
            s = s.replace('std', str(data_frame[self.string_model._voxel_vars[0]].std()))
        if 'mean' in s:
            s = s.replace('mean', str(data_frame[self.string_model._voxel_vars[0]].mean()))
        if 'var' in s:
            s = s.replace('var', str(data_frame[self.string_model._voxel_vars[0]].var()))
        return s

    def fit(self, data_frame):
        string_expr = self.get_expr_string(data_frame)
        try:
            res = float(numexpr.evaluate(string_expr))
        except:
            res = None
            # print('Statistics exception; result for the voxel may be set to 0 : ' + str(e))
        return self.filter_result_power(res)

    def filter_result_power(self, result):
        result_f = {}
        for vard in self.model_wise_results_names:
            if result:
                result_f[vard] = numpy.clip(result,-5000,5000)
            else:
                result_f[vard] = 0
        result_f['model_wise_results_names'] = self.model_wise_results_names
        return result_f

class Pcorr(StatsModel):
    def __init__(self, string_model, var_y, var_x):
        StatsModel.__init__(self, 'pcorr')
        self.string_model = string_model
        self.var_y = var_y
        self.var_x = var_x

    def fit(self, data_frame):
        import patsy
        dmatrices  = patsy.dmatrices(self.string_model._string_model_str, data_frame)
        y = dmatrices[0]
        x = dmatrices[1]
        col_indxs = x.design_info.column_name_indexes
        var_x_idx = col_indxs[self.var_x]
        C = numpy.hstack([y, x])

        dof = C.shape[0] - 2 - (C.shape[1] - 2 - 1)  ### n-2-k k = number of variables except the two in question, -1 to remove intercept
        try:
            res = self.parr_corr_idx(C, 0+1, var_x_idx+1+1) ## We added the y column at the beginning. So, we have to increase the index
        except:
            res=None

        return self.filter_results_pcorr(res, dof)

    def parr_corr_idx(self, C, i, j):
        from scipy import stats, linalg
        i = i - 1
        j = j - 1

        C = numpy.asarray(C)
        p = C.shape[1]
        idx = numpy.ones(p, dtype=numpy.bool)
        idx[i] = False
        idx[j] = False
        beta_i = linalg.lstsq(C[:, idx], C[:, j])[0]
        beta_j = linalg.lstsq(C[:, idx], C[:, i])[0]

        res_j = C[:, j] - C[:, idx].dot(beta_i)
        res_i = C[:, i] - C[:, idx].dot(beta_j)

        corr = stats.pearsonr(res_i, res_j)[0]
        return corr

    def partial_corr(self, C):
        from scipy import stats, linalg
        C = numpy.asarray(C)
        p = C.shape[1]
        P_corr = numpy.zeros((p, p), dtype=numpy.float)
        for i in range(p):
            P_corr[i, i] = 1
            for j in range(i + 1, p):
                idx = numpy.ones(p, dtype=numpy.bool)
                idx[i] = False
                idx[j] = False
                beta_i = linalg.lstsq(C[:, idx], C[:, j])[0]
                beta_j = linalg.lstsq(C[:, idx], C[:, i])[0]

                res_j = C[:, j] - C[:, idx].dot(beta_i)
                res_i = C[:, i] - C[:, idx].dot(beta_j)

                corr = stats.pearsonr(res_i, res_j)[0]
                P_corr[i, j] = corr
                P_corr[j, i] = corr

        return P_corr

    def filter_results_pcorr(self, pcorr, dof):
        import scipy
        result_f = {}
        if pcorr:
            result_f['df'] = dof
            result_f['r_'] = pcorr
            result_f['r_prime'] = numpy.arctan(pcorr)
            result_f['t_'] = pcorr * numpy.sqrt((dof) / (1 - pcorr * pcorr))
            result_f['p_'] = (1 - scipy.special.stdtr(dof, numpy.abs(result_f['t_']))) * 2
        else:
            result_f['df'] = dof
            result_f['r_'] = 0
            result_f['r_prime'] = 0
            result_f['t_'] = 0
            result_f['p_'] = 0
        result_f['model_wise_results_names'] = self.model_wise_results_names
        return result_f

class StringModel(pyVoxelStats):
    def __init__(self, string_model_str, voxel_vars, multi_var_ops=None):
        pyVoxelStats.__init__(self)
        self._string_model_str = string_model_str
        self._voxel_vars = voxel_vars
        self._used_vars = self.__get_used_vars(self._string_model_str)
        self.multi_var_ops = multi_var_ops

    def __get_used_vars(self, string_model):
        all_strings = re.findall(r"[.Cs\(\w\)\w']+", string_model)
        all_strings = [re.sub(r'C\(([\w]+)\)', r'\1', st) for st in all_strings]
        all_strings = [re.sub(r's\(([\w]+)\)', r'\1', st) for st in all_strings]
        unique_vars = set(all_strings)
        return list(unique_vars)

    def add_to_cars(self, string):
        strs = self.__get_used_vars(string)
        for s in strs:
            if s not in self._used_vars:
                self._used_vars.append(s)

    def add_extra_used_vars(self, var_name):
        if isinstance(var_name, str):
            self._used_vars.append(var_name)
