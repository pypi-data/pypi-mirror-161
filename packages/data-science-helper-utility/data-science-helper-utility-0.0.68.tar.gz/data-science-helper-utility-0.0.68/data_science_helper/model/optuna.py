# -*- coding: utf-8 -*-
"""
Created on Tue May 31 14:33:24 2022

@author: User
"""

import numpy as np
import pandas as pd
import optuna

from data_science_helper.model import general as g
import data_science_helper.helper_classification_model as hcm
import data_science_helper.model.neg_bagging_fraction__lgb_model as nbf_lgb_model


from sklearn.metrics import  roc_auc_score, average_precision_score 
from sklearn.model_selection import StratifiedKFold   
import lightgbm as lgb 

from optuna.trial import Trial
import gc
import warnings
warnings.filterwarnings("ignore")


from sklearn.model_selection import  StratifiedShuffleSplit
from sklearn.metrics import precision_recall_fscore_support

from lightgbm import early_stopping
from lightgbm import log_evaluation
import statistics
from sklearn.metrics import f1_score


def objective_with_prune(trial: Trial, fast_check=True, X=None,y=None,fn_params=None, list_kpi=[], n_jobs=None, metric=None, num_rounds=None,early_stop=None,log=None,random_state=42):
    folds = 5
    
    kf = StratifiedKFold(n_splits=folds, shuffle=True, random_state=random_state)
    ''' 
    test_size = hcm.get_test_size(X,log)
    if test_size == 0.20:
        kf = StratifiedKFold(n_splits=folds, shuffle=True, random_state=random_state)
        print("StratifiedKFold")
    else:
        kf = StratifiedShuffleSplit(n_splits=folds, test_size=test_size, random_state=random_state)
        print("StratifiedShuffleSplit")
    '''
    X_train = X
    y_train = y    
    
    X_train.reset_index(inplace=True,drop=True)
    y_train.reset_index(inplace=True,drop=True)   
 
    gc.collect()
   
    models = []
    
    list_valid_score = [] 
    list_train_score = []
    
    list_train_precision = []
    list_train_recall = []
    list_train_f1 = []
    list_train_average_precision = []
    list_train_roc_auc = []
    
    list_TP_train = []
    list_FP_train = []
    list_TN_train = []
    list_FN_train = []
    
    #list_TP_train_opt = []
    #list_FP_train_opt = []
    #list_TN_train_opt = []
    #list_FN_train_opt = []
    
    list_valid_precision = []
    list_valid_recall = []
    list_valid_f1 = []
    list_valid_average_precision = []
    list_valid_roc_auc = []
    
    list_TP_valid = []
    list_FP_valid = []
    list_TN_valid = []
    list_FN_valid = []
    
    #list_TP_valid_opt = []
    #list_FP_valid_opt = []
    #list_TN_valid_opt = []
    #list_FN_valid_opt = []
    
    #list_opt_threshold_train = []
    #list_opt_threshold_valid = []
    
    with_bias = False
    
    for train_idx, valid_idx in kf.split(X_train, y_train):
        train_data = X_train.iloc[train_idx,:], y_train[train_idx]
        valid_data = X_train.iloc[valid_idx,:], y_train[valid_idx]

        args = {
                "trial":trial, "train":train_data, "val":valid_data, "fn_params":fn_params, "cat_features":None, 
                "metric":metric,"n_jobs":n_jobs,"num_rounds":num_rounds,"early_stop":early_stop,"log":log,"random_state":random_state
                }

        model, kpi = fit_lgbm_with_pruning(**args)

        models.append(model)
        gc.collect()
        
        
        
        list_train_precision.append(kpi["train/precision"])
        list_train_recall.append(kpi["train/recall"])
        list_train_f1.append(kpi["train/f1"])
        list_train_average_precision.append(kpi["train/average_precision"])
        list_train_roc_auc.append(kpi["train/roc_auc"])  
        
        
         
        
        
        list_TP_train.append(kpi["train/TP"])    
        list_FP_train.append(kpi["train/FP"])  
        list_TN_train.append(kpi["train/TN"])  
        list_FN_train.append(kpi["train/FN"])  
        
        #list_opt_threshold_train.append(kpi["train/opt_threshold_train"]) 
        
        #list_TP_train_opt.append(kpi["train/TP_opt"])    
        #list_FP_train_opt.append(kpi["train/FP_opt"])  
        #list_TN_train_opt.append(kpi["train/TN_opt"])  
        #list_FN_train_opt.append(kpi["train/FN_opt"]) 
        
        list_train_score.append(kpi["train/score"])
        list_valid_score.append(kpi["valid/score"])
        
        list_valid_precision.append(kpi["valid/precision"])
        list_valid_recall.append(kpi["valid/recall"])
        list_valid_f1.append(kpi["valid/f1"])
        list_valid_average_precision.append(kpi["valid/average_precision"])
        list_valid_roc_auc.append(kpi["valid/roc_auc"])        
        
        list_TP_valid.append(kpi["valid/TP"])    
        list_FP_valid.append(kpi["valid/FP"])  
        list_TN_valid.append(kpi["valid/TN"])  
        list_FN_valid.append(kpi["valid/FN"])  
        
        #list_opt_threshold_valid.append(kpi["valid/opt_threshold_valid"]) 
        
        #list_TP_valid_opt.append(kpi["valid/TP_opt"])    
        #list_FP_valid_opt.append(kpi["valid/FP_opt"])  
        #list_TN_valid_opt.append(kpi["valid/TN_opt"])  
        #list_FN_valid_opt.append(kpi["valid/FN_opt"])  
        
        bias = kpi["bias"]
        
        if (bias>0.15 or kpi["train/score"]==0 or kpi["valid/score"]==0  or 
            kpi["train/precision"]==0   or kpi["valid/precision"]==0   or 
            kpi["train/recall"]==0   or kpi["valid/recall"]==0 ):
            with_bias = True
            break
        
        if fast_check:
            break
        
    
    #mean_train_opt_threshold = statistics.mean(list_opt_threshold_train)
    #std_train_opt_threshold = statistics.pstdev(list_opt_threshold_train)
    
    #mean_valid_opt_threshold = statistics.mean(list_opt_threshold_valid)
    #std_valid_opt_threshold = statistics.pstdev(list_opt_threshold_valid)
    
        
    mean_train_score = statistics.mean(list_train_score)
    std_train_score = statistics.pstdev(list_train_score)
            
    mean_valid_score = statistics.mean(list_valid_score)
    std_valid_score = statistics.pstdev(list_valid_score)
    
    
    mean_TP_train = statistics.mean(list_TP_train)
    std_TP_train = statistics.pstdev(list_TP_train)
    mean_FP_train = statistics.mean(list_FP_train)
    std_FP_train = statistics.pstdev(list_FP_train)
    mean_TN_train = statistics.mean(list_TN_train)
    std_TN_train = statistics.pstdev(list_TN_train)
    mean_FN_train = statistics.mean(list_FN_train)
    std_FN_train = statistics.pstdev(list_FN_train)
    
    mean_TP_valid = statistics.mean(list_TP_valid)
    std_TP_valid = statistics.pstdev(list_TP_valid)
    mean_FP_valid = statistics.mean(list_FP_valid)
    std_FP_valid = statistics.pstdev(list_FP_valid)
    mean_TN_valid = statistics.mean(list_TN_valid)
    std_TN_valid = statistics.pstdev(list_TN_valid)
    mean_FN_valid = statistics.mean(list_FN_valid)
    std_FN_valid = statistics.pstdev(list_FN_valid)
    
    
    
    ''' 
    mean_TP_train_opt = statistics.mean(list_TP_train_opt)
    std_TP_train_opt = statistics.pstdev(list_TP_train_opt)
    mean_FP_train_opt = statistics.mean(list_FP_train_opt)
    std_FP_train_opt = statistics.pstdev(list_FP_train_opt)
    mean_TN_train_opt = statistics.mean(list_TN_train_opt)
    std_TN_train_opt = statistics.pstdev(list_TN_train_opt)
    mean_FN_train_opt = statistics.mean(list_FN_train_opt)
    std_FN_train_opt = statistics.pstdev(list_FN_train_opt)
    
    mean_TP_valid_opt = statistics.mean(list_TP_valid_opt)
    std_TP_valid_opt = statistics.pstdev(list_TP_valid_opt)
    mean_FP_valid_opt = statistics.mean(list_FP_valid_opt)
    std_FP_valid_opt = statistics.pstdev(list_FP_valid_opt)
    mean_TN_valid_opt = statistics.mean(list_TN_valid_opt)
    std_TN_valid_opt = statistics.pstdev(list_TN_valid_opt)
    mean_FN_valid_opt = statistics.mean(list_FN_valid_opt)
    std_FN_valid_opt = statistics.pstdev(list_FN_valid_opt)
    '''
    

    mean_train_precision = statistics.mean(list_train_precision)           
    std_train_precision = statistics.pstdev(list_train_precision)
             
    mean_valid_precision = statistics.mean(list_valid_precision)           
    std_valid_precision = statistics.pstdev(list_valid_precision)
    
    mean_train_recall = statistics.mean(list_train_recall)           
    std_train_recall = statistics.pstdev(list_train_recall)
    
    mean_valid_recall = statistics.mean(list_valid_recall)           
    std_valid_recall = statistics.pstdev(list_valid_recall)
    
    mean_train_f1 = statistics.mean(list_train_f1)           
    std_train_f1 = statistics.pstdev(list_train_f1)
    
    mean_valid_f1 = statistics.mean(list_valid_f1)           
    std_valid_f1 = statistics.pstdev(list_valid_f1)
    

    mean_train_average_precision = statistics.mean(list_train_average_precision) 
    std_train_average_precision = statistics.pstdev(list_train_average_precision)
    
    mean_valid_average_precision = statistics.mean(list_valid_average_precision) 
    std_valid_average_precision = statistics.pstdev(list_valid_average_precision)
    
    mean_train_roc_auc = statistics.mean(list_train_roc_auc)           
    std_train_roc_auc = statistics.pstdev(list_train_roc_auc)
    
    mean_valid_roc_auc = statistics.mean(list_valid_roc_auc)           
    std_valid_roc_auc = statistics.pstdev(list_valid_roc_auc)
       
    bias = abs(mean_train_score - mean_valid_score)
    
    result_iter = {
        'trial_number':trial.number,
        'bias': bias,
        'overfitting':with_bias,
        'mean_train_score':mean_train_score,
        'std_train_score':std_train_score,  
        
        'mean_valid_score':mean_valid_score,
        'std_valid_score':std_valid_score,       
          
    }   
    
    if(fast_check):
        split_dic = {}
        key_split = "split_{}".format(1)
        split_dic[key_split] = list_valid_score[0]
        result_iter.update(split_dic)
    else:
        for i in range(folds):
            split_train_dic = {}
            split_valid_dic = {}
            lb_fold = i+1
            
            key_split_train = "split_{}_train_score".format(lb_fold)
            split_train_dic[key_split_train] = list_train_score[i] if with_bias==False else -1
            result_iter.update(split_train_dic)
            
            key_split_valid = "split_{}_valid_score".format(lb_fold)          
            split_valid_dic[key_split_valid] = list_valid_score[i] if with_bias==False else -1
            result_iter.update(split_valid_dic)
        
    
 
    result_kpis = {   
        
        'mean_train_precision':mean_train_precision,
        'std_train_precision':std_train_precision,
        'mean_train_recall':mean_train_recall,
        'std_train_recall':std_train_recall, 
        'mean_train_f1':mean_train_f1,
        'std_train_f1':std_train_f1 ,
        'mean_train_average_precision':mean_train_average_precision,
        'std_train_average_precision':std_train_average_precision,       
        'mean_train_roc_auc':mean_train_roc_auc,
        'std_train_roc_auc':std_train_roc_auc   ,
        
        'mean_TP_train':mean_TP_train   ,
        'std_TP_train':std_TP_train   ,
        'mean_FP_train':mean_FP_train   ,
        'std_FP_train':std_FP_train   ,
        'mean_TN_train':mean_TN_train   ,
        'std_TN_train':std_TN_train   ,
        'mean_FN_train':mean_FN_train   ,
        'std_FN_train':std_FN_train   ,
        

        
        #'mean_train_opt_threshold':mean_train_opt_threshold   ,
        #'std_train_opt_threshold':std_train_opt_threshold   ,
        
        
        #'mean_TP_train_opt':mean_TP_train_opt   ,
        #'std_TP_train_opt':std_TP_train_opt   ,
        #'mean_FP_train_opt':mean_FP_train_opt   ,
        #'std_FP_train_opt':std_FP_train_opt   ,
        #'mean_TN_train_opt':mean_TN_train_opt   ,
        #'std_TN_train_opt':std_TN_train_opt   ,
        #'mean_FN_train_opt':mean_FN_train_opt   ,
        #'std_FN_train_opt':std_FN_train_opt   ,
        
        
        'mean_valid_precision':mean_valid_precision,
        'std_valid_precision':std_valid_precision,
        'mean_valid_recall':mean_valid_recall,
        'std_valid_recall':std_valid_recall, 
        'mean_valid_f1':mean_valid_f1,
        'std_valid_f1':std_valid_f1 ,
        'mean_valid_average_precision':mean_valid_average_precision,
        'std_valid_average_precision':std_valid_average_precision,       
        'mean_valid_roc_auc':mean_valid_roc_auc,
        'std_valid_roc_auc':std_valid_roc_auc   ,
        
        'mean_TP_valid':mean_TP_valid   ,
        'std_TP_valid':std_TP_valid   ,
        'mean_FP_valid':mean_FP_valid   ,
        'std_FP_valid':std_FP_valid   ,
        'mean_TN_valid':mean_TN_valid   ,
        'std_TN_valid':std_TN_valid   ,
        'mean_FN_valid':mean_FN_valid   ,
        'std_FN_valid':std_FN_valid   ,
        
        #'mean_valid_opt_threshold':mean_valid_opt_threshold   ,
        #'std_valid_opt_threshold':std_valid_opt_threshold   ,
        
        
        #'mean_TP_valid_opt':mean_TP_valid_opt   ,
        #'std_TP_valid_opt':std_TP_valid_opt   ,
        #'mean_FP_valid_opt':mean_FP_valid_opt   ,
        #'std_FP_valid_opt':std_FP_valid_opt   ,
        #'mean_TN_valid_opt':mean_TN_valid_opt   ,
        #'std_TN_valid_opt':std_TN_valid_opt   ,
        #'mean_FN_valid_opt':mean_FN_valid_opt   ,
        #'std_FN_valid_opt':std_FN_valid_opt   ,        
        
        
    }
    
    result_iter.update(result_kpis)
  
    list_kpi.append(result_iter)
    return mean_valid_score


def lgb_f1_score(y_hat, data):
    y_true = data.get_label()
    y_hat = np.round(y_hat) # scikits f1 doesn't like probabilities
    return 'f1', f1_score(y_true, y_hat), True


def fit_lgbm_with_pruning(trial=None, train=None, val=None, fn_params=None, cat_features=None,metric=None,n_jobs=1, num_rounds=None,early_stop=None,log=None,random_state=None ):
    """Train Light GBM model"""    
    X_train, y_train = train
    X_valid, y_valid = val
    
    train_params ,  dataset_params = fn_params(trial)
        
    nb_f = nbf_lgb_model.get_neg_bagging_fraction_params(y_train,{},log)
    
    train_params.update(nb_f)
    
    params_config = {"seed": random_state, "n_jobs":n_jobs,"objective":'binary' , "metric": metric}

    train_params.update(params_config)
    


    d_train = lgb.Dataset(X_train, label=y_train, categorical_feature=cat_features, params=dataset_params)
    d_valid = lgb.Dataset(X_valid, label=y_valid, categorical_feature=cat_features, params=dataset_params)

    watchlist = [d_train,d_valid]    

    
    pruning_callback_t = optuna.integration.LightGBMPruningCallback(trial, metric, valid_name="data_train")    
    pruning_callback_v = optuna.integration.LightGBMPruningCallback(trial, metric, valid_name="data_valid")

    model = lgb.train(train_params,                 
                      num_boost_round = num_rounds,
                      train_set=d_train,
                      valid_names = ['data_train','data_valid'],
                      valid_sets=watchlist,
                      feval=lgb_f1_score,
                      callbacks=[log_evaluation(log),pruning_callback_t,pruning_callback_v,early_stopping(early_stop)]
                     )
    
    train_best_score = model.best_score['data_train'][metric]
    valid_best_score = model.best_score['data_valid'][metric]

    # predictions
    
    y_pred_prob_train = model.predict(X_train, num_iteration=model.best_iteration)   
    y_pred_prob_valid = model.predict(X_valid, num_iteration=model.best_iteration) 
    
    print('best_score== : ', model.best_score)
    
    y_pred_train = np.rint(y_pred_prob_train)    
    #opt_threshold_train  = g.get_opt_threshold(y_train,y_pred_prob_train)
    
    
    y_pred_valid = np.rint(y_pred_prob_valid)    
    #opt_threshold_valid  = g.get_opt_threshold(y_valid,y_pred_prob_valid)
    #print("11111111111111")
    #print(y_train.shape)
    #print("11111111111111")

    TP_train, FP_train, TN_train, FN_train = perf_measure(y_train.values,y_pred_train)    
    #y_pred_train_opt = (y_pred_prob_train > opt_threshold_train).astype(int)
    #TP_train_opt, FP_train_opt, TN_train_opt, FN_train_opt = perf_measure(y_train.values,y_pred_train_opt)
    
    TP_valid, FP_valid, TN_valid, FN_valid = perf_measure(y_valid.values,y_pred_valid)
    #y_pred_valid_opt = (y_pred_prob_valid > opt_threshold_valid).astype(int)
    #TP_valid_opt, FP_valid_opt, TN_valid_opt, FN_valid_opt = perf_measure(y_valid.values,y_pred_valid_opt)

    
    train_average_precision = average_precision_score(y_train, y_pred_prob_train)
    valid_average_precision = average_precision_score(y_valid, y_pred_prob_valid)
    
    
    precision_t, recall_t, f1_t, support_t = precision_recall_fscore_support(y_train, y_pred_train ,average="binary",pos_label=1)    
    precision, recall, f1, support = precision_recall_fscore_support(y_valid, y_pred_valid ,average="binary",pos_label=1)
    
    roc_auc_t = roc_auc_score(y_train, y_pred_prob_train) 
    roc_auc = roc_auc_score(y_valid, y_pred_prob_valid) 
    

    bias = train_best_score - valid_best_score    
 
    kpi = {'train/average_precision': train_average_precision,  
           'train/precision': precision_t,
           'train/recall': recall_t,
           'train/f1': f1_t,
           'train/roc_auc': roc_auc_t,        
           'train/TP': TP_train,   
           'train/FP': FP_train,   
           'train/TN': TN_train,   
           'train/FN': FN_train,   
           
           #'train/opt_threshold_train': opt_threshold_train,  
           
           
           #'train/TP_opt': TP_train_opt,   
           #'train/FP_opt': FP_train_opt,   
           #'train/TN_opt': TN_train_opt,   
           #'train/FN_opt': FN_train_opt,  
           'train/score': train_best_score,
           'valid/score': valid_best_score,
           
           'valid/average_precision': valid_average_precision,
           'valid/precision': precision,
           'valid/recall': recall,
           'valid/f1': f1,
           'valid/roc_auc': roc_auc,
           'valid/TP': TP_valid,   
           'valid/FP': FP_valid,   
           'valid/TN': TN_valid,   
           'valid/FN': FN_valid,   
           
           #'valid/TP_opt': TP_valid_opt,   
           #'valid/FP_opt': FP_valid_opt,   
           #'valid/TN_opt': TN_valid_opt,   
           #'valid/FN_opt': FN_valid_opt,  
           
           #'valid/opt_threshold_valid': opt_threshold_valid, 
           
           'bias':bias
          }
    return model, kpi


def perf_measure(y_actual, y_hat):
    
    TP = 0
    FP = 0
    TN = 0
    FN = 0
    
    for i in range(len(y_hat)): 
        
        if y_actual[i]==y_hat[i]==1:
           TP += 1
        if y_hat[i]==1 and y_actual[i]!=y_hat[i]:
           FP += 1
        if y_actual[i]==y_hat[i]==0:
           TN += 1
        if y_hat[i]==0 and y_actual[i]!=y_hat[i]:
           FN += 1

    return(TP, FP, TN, FN)
  

def lgb_model_optuna(X_train=None, y_train=None,n_trials=2,fast_check=True,fn_params=None, 
                      n_jobs=None, metric=None, num_rounds=None,early_stop=None,log=None,random_state=42):
    
    if log == 0:
        optuna.logging.set_verbosity(optuna.logging.ERROR)
    
    list_kpi_ = []
    sampler = optuna.samplers.RandomSampler(seed=random_state)
    pruner=optuna.pruners.MedianPruner(n_warmup_steps=5)
    study = optuna.create_study(pruner=pruner,sampler=sampler,direction="maximize")


    func = lambda trial: objective_with_prune(trial,fast_check=fast_check, X=X_train, y=y_train,fn_params=fn_params, list_kpi=list_kpi_,
                                              n_jobs=n_jobs, metric=metric, num_rounds=num_rounds,early_stop=early_stop,log=log,
                                              random_state=random_state)
    
    study.optimize(func, n_trials=n_trials, n_jobs=n_jobs)

    best_params = study.best_params
    result = pd.DataFrame(list_kpi_)
    
    
    trials_dataframe = study.trials_dataframe()

    return result, best_params, study.best_value , trials_dataframe



def get_best_value_nob(result_,nob_group="0.0-0.15"):
    #result_ = result.copy()
    labels = ["{0} - {1}".format(i, i + 0.1) for i in np.linspace(0,1,10,endpoint=True)] #, labels=labels
    labels = ["0.0-0.15","0.15-0.2","0.2-0.3","0.3-0.4","0.4-0.5","0.5-0.6","0.6-0.7","0.7-0.8","0.8-0.9","0.9-1.0"]
    intervalos = [0. , 0.15, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1. ]    
    result_["bias_group"] = pd.cut(result_.bias, intervalos, right=False, labels=labels)
    #result_["bias_group"] = pd.cut(result_.bias, np.linspace(0,1,11,endpoint=True), right=False, labels=labels)
    final_result = result_[(result_.bias_group==nob_group) & (result_.overfitting==False)].sort_values(by=['mean_valid_score'], ascending=False)
    best_value_nob = final_result['mean_valid_score'].iloc[0]
    return best_value_nob

def get_params_by_trial_number(trials_dataframe_,trial_number):

    best_trial_nob = trials_dataframe_[trials_dataframe_.number==trial_number].copy()
    cls_to_delete = ["number","value","datetime_start","datetime_complete","duration","state"]
    best_trial_nob.drop(columns=cls_to_delete, inplace=True)

    best_trial_nob.columns = best_trial_nob.columns.str.replace('params_', '')
    best_params_nob = best_trial_nob.to_dict(orient='records')[0]

    return best_params_nob


def get_best_trial_number_nob(result_,nob_group="0.0-0.15"):
    #result_ = result.copy()
    labels = ["{0} - {1}".format(i, i + 0.1) for i in np.linspace(0,1,10,endpoint=True)] #, labels=labels
    labels = ["0.0-0.15","0.15-0.2","0.2-0.3","0.3-0.4","0.4-0.5","0.5-0.6","0.6-0.7","0.7-0.8","0.8-0.9","0.9-1.0"]
    intervalos = [0. , 0.15, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1. ]    
    result_["bias_group"] = pd.cut(result_.bias, intervalos, right=False, labels=labels)
    #result_["bias_group"] = pd.cut(result_.bias, np.linspace(0,1,11,endpoint=True), right=False, labels=labels)
    final_result = result_[(result_.bias_group==nob_group) & (result_.overfitting==False)].sort_values(by=['mean_valid_score'], ascending=False)
    if len(final_result)==0:
        final_result = result_[result_.overfitting==False].sort_values(by=['mean_valid_score'], ascending=False)
        if len(final_result)==0:
            return None
        else:
            trial_number = final_result['trial_number'].iloc[0]        
            return trial_number
    else:
        trial_number = final_result['trial_number'].iloc[0]
        return trial_number


def get_kpis_by_trial_number(res,trial_number):

    result_ = res[res.trial_number==trial_number].copy()
    if len(result_)==0:
        return None
    result_dic = result_.to_dict(orient='records')[0]
    return result_dic