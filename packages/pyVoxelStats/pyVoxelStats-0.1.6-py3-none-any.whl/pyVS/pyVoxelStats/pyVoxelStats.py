import configparser
import os

import pyVS.Util.Params.pyVSParams as pyvsparams

class pyVoxelStats:
    _debug = False
    _no_parallel = False
    _save_model = False

    def __init__(self, file_type=None, model_string=None, csv_file=None, mask_file=None, voxel_variables=None, subset_string=None,
                 multi_variable_operations=None):
        self.config = self.check_config()
        self.string_model = model_string
        self.file_type = file_type
        self.data_file = csv_file
        self.mask_file = mask_file
        self.voxel_vars = voxel_variables
        self.filter_string = subset_string
        self.multi_var_operations = multi_variable_operations

        self.string_model_obj = None
        self.data_set = None

        self.string_model_obj = None
        self.data_set = None
        self.masker = None
        self.stats_model = None

        self.res = None
        self.models = None
        self.preds = None

        self.cluster_profile = 'default'
        self.clus_workers = None
        self.clus_no_start = False
        self.clust_sleep_time = 10
        self.clust_json = None

        self.cluster_shut_down = False

    def set_no_parallel(self, bool_val):
        pyVoxelStats._no_parallel = bool_val

    def enable_save_model(self):
        pyVoxelStats._save_model = True

    def set_debug(self, bool_val):
        pyVoxelStats._debug = bool_val

    def set_new_config(self, config_path):
        config_dict = pyvsparams.config_dict
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        cf = configparser.ConfigParser()
        for k in config_dict.keys():
            cf[k] = config_dict[k]
        with open(config_path, 'w') as configfile:
            cf.write(configfile)
        return cf

    def check_config(self, config_path='{0}/.pyVS/pyVSParams.ini'.format(os.path.expanduser('~'))):
        if os.path.exists(config_path):
            cf = configparser.ConfigParser()
            cf.read(config_path)
            config_dict = pyvsparams.config_dict
            if 'version' not in cf['VSVoxelOPS'] or (
                config_dict['VSVoxelOPS']['version'] > float(cf['VSVoxelOPS']['version'])):
                cf = self.set_new_config(config_path=config_path)
            return cf
        else:
            return self.set_new_config(config_path=config_path)

    def save(self, file_name, result_field, var_name=None):
        if var_name:
            print('Saving - {0} - {1} -> {2} ....'.format(result_field, var_name, file_name))
            self.masker.save_image_from_data(self.res[result_field][var_name], file_name)
        else:
            print('Saving - {0} -> {1} ....'.format(result_field, file_name))
            self.masker.save_image_from_data(self.res[result_field], file_name)
        print('Saving done.')

    def save_image_data(self, file_name, data):
        print('Saving - {0} ...'.format(file_name))
        self.masker.save_image_from_data(data, file_name)

    def set_up_cluster(self, clus_json=None, profile_name='default', workers=None, no_start=False, clust_sleep_time=10):
        self.cluster_profile = profile_name
        self.clus_workers = workers
        self.clus_no_start = no_start
        self.clust_sleep_time = clust_sleep_time
        self.clust_json = clus_json

    def set_shut_down_cluster(self):
        self.cluster_shut_down = True

    def evaluate(self):
        raise NotImplementedError()

    def cv_evaluate(self, cv_generator=None, repeats=1):
        raise NotImplementedError()
