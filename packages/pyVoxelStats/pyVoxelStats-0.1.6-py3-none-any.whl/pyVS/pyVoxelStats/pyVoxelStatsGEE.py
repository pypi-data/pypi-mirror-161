import statsmodels.api as smapi
from pyVS.Util.Masker import Masker
from pyVS.Util.VoxelOperation import VoxelOperation

from pyVS.Util.StatsUtil import Dataset, StringModel
from pyVS.Util.StatsUtil import GEE
from pyVS.pyVoxelStats.pyVoxelStats import pyVoxelStats


class pyVoxelStatsGEE(pyVoxelStats):
    def __init__(self, file_type, model_string, csv_file, mask_file, voxel_variables, family_obj, groups, cov_struct=None,
                 time=None, subset_string=None, multi_variable_operations=None):
        pyVoxelStats.__init__(self, file_type, model_string, csv_file, mask_file, voxel_variables, subset_string,
                              multi_variable_operations)
        self.family_dict = dict(binomial=smapi.families.Binomial, gamma=smapi.families.Gamma, gaussian=smapi.families.Gaussian,
                                poisson=smapi.families.Poisson, inversegaussian=smapi.families.InverseGaussian,
                                negativebinomial=smapi.families.NegativeBinomial)
        self.family_obj = self.get_family(family_obj)
        self.groups = groups
        self.cov_struct = cov_struct
        self.time = time

    def get_family(self, family_obj):
        if type(family_obj) is str:
            return self.family_dict[family_obj]()
        else:
            return family_obj

    def evaluate(self):
        self.string_model_obj = StringModel(self.string_model, self.voxel_vars, self.multi_var_operations)
        self.string_model_obj.add_to_cars(self.groups)
        self.data_set = Dataset(self.data_file, filter_string=self.filter_string,
                                string_model_obj=self.string_model_obj)
        self.masker = Masker(self.file_type, self.mask_file)
        self.stats_model = GEE(self.string_model_obj, self.family_obj, groups = self.groups, covariance_obj=self.cov_struct, time=self.time)
        self.stats_model.save_models = self._save_model
        voxel_op = VoxelOperation(self.string_model_obj, self.data_set, self.masker, self.stats_model)
        try:
            voxel_op.set_up_cluster(clus_json=self.clust_json, profile_name=self.cluster_profile, workers=self.clus_workers,
                                    no_start=self.clus_no_start, clust_sleep_time=self.clust_sleep_time)
            voxel_op.set_up()
            voxel_op.execute()
            self.res = voxel_op.results.get_results()
            self.models = voxel_op.results.get_models()
        finally:
            voxel_op.shut_down_cluster(self.cluster_shut_down)
