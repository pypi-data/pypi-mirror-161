from pyVS.Util.Masker import Masker
from pyVS.Util.VoxelOperation import VoxelOperation

from pyVS.Util.StatsUtil import Dataset, StringModel
from pyVS.Util.StatsUtil import LM
from pyVS.pyVoxelStats.pyVoxelStats import pyVoxelStats


class pyVoxelStatsLM(pyVoxelStats):
    def __init__(self, file_type, model_string, csv_file, mask_file, voxel_variables, subset_string=None,
                 multi_variable_operations=None, weights=None):
        pyVoxelStats.__init__(self, file_type, model_string, csv_file, mask_file, voxel_variables, subset_string,
                              multi_variable_operations)
        self.weights = weights

    def evaluate(self):
        self.string_model_obj = StringModel(self.string_model, self.voxel_vars, self.multi_var_operations)
        if self.weights and isinstance(self.weights, str):
            self.string_model_obj.add_extra_used_vars(self.weights)
        self.data_set = Dataset(self.data_file, filter_string=self.filter_string,
                                string_model_obj=self.string_model_obj)
        self.masker = Masker(self.file_type, self.mask_file)
        self.stats_model = LM(self.string_model_obj, self.weights)
        self.stats_model.save_models = self._save_model
        voxel_op = VoxelOperation(self.string_model_obj, self.data_set, self.masker, self.stats_model)
        try:
            voxel_op.set_up_cluster(clus_json=self.clust_json, profile_name=self.cluster_profile,
                                    workers=self.clus_workers,
                                    no_start=self.clus_no_start, clust_sleep_time=self.clust_sleep_time)
            voxel_op.set_up()
            voxel_op.execute()
            self.res = voxel_op.results.get_results()
            self.models = voxel_op.results.get_models()
        finally:
            voxel_op.shut_down_cluster(self.cluster_shut_down)

    def cv_evaluate(self, cv_generator=None, repeats=1):
        self.string_model_obj = StringModel(self.string_model, self.voxel_vars, self.multi_var_operations)
        self.data_set = Dataset(self.data_file, filter_string=self.filter_string,
                                string_model_obj=self.string_model_obj)
        self.masker = Masker(self.file_type, self.mask_file)
        self.stats_model = LM(self.string_model_obj)

        voxel_op = VoxelOperation(self.string_model_obj, self.data_set, self.masker, self.stats_model)
        try:
            voxel_op.set_up_cluster(clus_json=self.clust_json, profile_name=self.cluster_profile, workers=self.clus_workers,
                                    no_start=self.clus_no_start, clust_sleep_time=self.clust_sleep_time)
            voxel_op.set_up()
            voxel_op.cv_execute(cv_generator=cv_generator, repeats=repeats)
            #self.res = voxel_op.results.get_results()
            self.preds = voxel_op.predictions
            #self.models = voxel_op.results.get_models()
        finally:
            voxel_op.shut_down_cluster(self.cluster_shut_down)
