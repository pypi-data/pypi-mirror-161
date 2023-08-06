config_dict = dict(
    ResultsModelWiseResults_OLD=dict(lm=["aic", "bic", "centered_tss", "condition_number", "df_model", "df_resid", "ess",
                                        "f_pvalue", "fvalue", "k_constant", "llf", "mse_model", "mse_resid", "mse_total",
                                        "nobs", "rsquared", "rsquared_adj", "scale", "ssr", "uncentered_tss"],
                                     glm=["aic", "bic", "deviance", "df_model", "df_resid",
                                          "k_constant", "llf", "llnull", "null_deviance", "pearson_chi2", "scale",
                                          "nobs"],
                                     gee=["ctol", "df_model", "df_resid", "k_constant", "scale",
                                          "score_norm"]
                                     ),
    ResultsModelWiseResults=dict(lm=["aic", "df_model", "df_resid", "f_pvalue", "fvalue", "mse_model", "mse_resid", "mse_total",
                                     "rsquared", "rsquared_adj", "ssr"],
                                 glm=["aic", "df_model", "df_resid", "deviance", "llf", "llnull", "null_deviance",
                                      "pearson_chi2"],
                                 gee=["ctol", "df_model", "df_resid", "k_constant", "scale",
                                      "score_norm"],
                                 power=["ss"],
                                 pcorr=["r_", "r_prime", "t_", "p_", 'df']
                                 ),
    ResultsModelVariableWiseResults=dict(lm=["bse", "params", "pvalues", "tvalues"],
                                         glm=["bse", "params", "pvalues", "tvalues"],
                                         gee=["bse", "params", "pvalues", "tvalues"],
                                         lme=["bse", "params", "pvalues", "tvalues"]),
    VSVoxelOPS=dict(slice_count="20",
                    version=1.08),

)
