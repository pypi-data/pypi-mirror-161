# -*- coding: utf-8 -*-

#import core_helper.helper_general as hg
#hg.set_base_path()

from data_science_helper import helper_general as hg

import lightgbm as lgb 
from scipy.stats import uniform as sp_uniform
import pandas as pd
from sklearn.model_selection import RandomizedSearchCV

from lightgbm import early_stopping
from lightgbm import log_evaluation
import numpy as np
from sklearn.metrics import f1_score
#import general as g
#import core_helper.model.general as g
#import src.Prj_Core.core_helper.model.general as g
from data_science_helper.model import general as g

import time


def get_neg_bagging_fraction_params(y_train=None,params=None,log=0):
    
    N_p = y_train[y_train==1].count()
    N_n = y_train[y_train==0].count()
    #T_minimo= 43000
    T_minimo = get_Total_min_to_train(N_p)
    
    if  log is not None and log>0 :
    
        print("T_minimo : ",T_minimo)
        print("N_p : ",N_p)
        print("N_n : ",N_n)
    
    alpha = (T_minimo-N_p)/N_n
    if params is None:
        params = get_default_params()
        
    params['pos_bagging_fraction'] = 1
    params['neg_bagging_fraction'] = alpha
    params['scale_pos_weight'] = (alpha*N_n)/N_p
    return params


def get_scale_pos_weight_params(y_train=None,params=None,log=0):
    
    N_p = y_train[y_train==1].count()
    N_n = y_train[y_train==0].count()
    
    T_minimo = get_Total_min_to_train(N_p)
    
    if  log is not None and log>0 :
    
        print("T_minimo : ",T_minimo)
        print("N_p : ",N_p)
        print("N_n : ",N_n)
    
    alpha = (T_minimo-N_p)/N_n
    if params is None:
        params = get_default_params()
        
    params['pos_bagging_fraction'] = 1
    params['neg_bagging_fraction'] = 1
    params['scale_pos_weight'] = N_n/N_p

    return params

def get_Total_min_to_train(N_p):
    T_minimo = 10000 
    
    while N_p>=T_minimo:
      T_minimo = T_minimo + 30000

    return T_minimo


def lgb_f1_score(y_hat, data):
    y_true = data.get_label()
    y_hat = np.round(y_hat) # scikits f1 doesn't like probabilities
    return 'f1', f1_score(y_true, y_hat), True


def get_feval(score):     
    if(score=="f1"):
        feval=lgb_f1_score
        
    return feval



def get_pipeline():
    '''
    lgb_pipe = pipeline.Pipeline([
        #
        #  metric="None", first_metric_only=True -> ignora binary_logloss en early_stopping_rounds
        ('clf', lgb.LGBMClassifier(metric="None", first_metric_only=True, importance_type="gain",n_jobs=4))
        ])        

    '''
    lgb_pipe = lgb.LGBMClassifier(metric="None", 
                                  first_metric_only=True, 
                                  importance_type="gain",
                                  use_missing=True,
                                  zero_as_missing=False,
                                  n_jobs=4)
    return lgb_pipe




def get_possible_params():
     
    lgb_param_random = {
        'num_leaves':list(range(7, 50)),
        'feature_fraction':sp_uniform(loc=0.2, scale=0.8),
        'bagging_fraction':sp_uniform(loc=0.2, scale=0.8),   
        'learning_rate': [0.1,0.07,0.05,0.025,0.015,0.01,0.0085,0.007,0.005],
        'max_depth': [-1,1,3,5,10,15],              
    }

    return  lgb_param_random



def get_default_params():
    params = {}    
    params['seed']=1
    params['objective']='binary'
    params['metric']="None" 
    params['seed']=1
        
    return params


def get_default_params_old():
    params = {}    
    params['metric']="None" 
    params['first_metric_only']=True 
    params['importance_type']="gain"
    params['use_missing']=True 
    params['zero_as_missing']=False 
    params['n_jobs']=4
    params['random_state']=1
    params['num_leaves']=15 
    params['feature_fraction']=0.7
    params['bagging_fraction']=0.7
    params['n_estimators']=10000 # optimizacion automatica con : early stopping
    params['objective']="binary" 
    params['bagging_freq']=1
    params['boosting_type']='gbdt'
    params['reg_alpha']=0
    params['reg_lambda']=0
        
    return params


def modelar(X_train=None,y_train=None,X_test=None,y_test=None,params=None,metric=None,num_rounds=None,early_stop=None,log=None,random_state=42,api="train_api",strategy="",url=None):
    start = time.time()
    model = None
    
    print("strategy: ",strategy)
    if (strategy=="neg_bagging_fraction__lgb_model"):
        params = get_neg_bagging_fraction_params(y_train,params)
        
    if (strategy=="scale_pos_weight__lgb_model"):
        params = get_scale_pos_weight_params(y_train,params)

    
    if api=="train_api":

        model = lgb_model_train(X_train,y_train,X_test,y_test,params=params,metric=metric,num_rounds=num_rounds,early_stop=early_stop,log=log)
        y_prob_uno_train = model.predict(X_train, num_iteration=model.best_iteration) 
        y_prob_uno_test  = model.predict(X_test, num_iteration=model.best_iteration) 
        
    elif api=="skl_api":
        model = lgb_model_skl(X_train,y_train,X_test,y_test,params=params,metric=metric)  
        
        predicted_probas_train = model.predict_proba(X_test) 
        y_prob_uno_train = predicted_probas_train[:,1]
        
        predicted_probas_test = model.predict_proba(X_test) 
        y_prob_uno_test = predicted_probas_test[:,1]
        
    if url is not None:
        g.save_model(model,url)
        g.save_json(params,url+"/params.json")
    
    
    if model is None:
        raise Exception("Modelo no implementado")
    
    return model , y_prob_uno_train, y_prob_uno_test 


def lgb_model_skl(X_train,y_train,X_test,y_test,metric='average_precision',params=None):

    fn_eval = g.get_fn_eval(metric)
    fit_params = get_fit_params(X_train,y_train,X_test,y_test,fn_eval)
  
                       
    model = lgb.LGBMClassifier(**params)
    print('---------- definicion del modelo ----------------')
    print(model)
    print('-------------------------------------------------')
    
    model.fit(X_train,y_train,**fit_params)
   
    return model


def lgb_model_train(X_train,y_train,X_test,y_test,params=None,metric='average_precision',num_rounds=None,early_stop=None,log=None):

    
    feval = get_feval(metric)
    
    if 'max_bin' in params:
        
        max_bin=params['max_bin']  
        print("Estableciendo max_bin : ",max_bin)
        del params['max_bin']
        d_train = lgb.Dataset(X_train, label=y_train, categorical_feature=[], params={"max_bin":max_bin})
        d_valid = lgb.Dataset(X_test, label=y_test, categorical_feature=[], params={"max_bin":max_bin})
    else:
        d_train = lgb.Dataset(X_train, label=y_train, categorical_feature=[])
        d_valid = lgb.Dataset(X_test, label=y_test, categorical_feature=[])
        

    

    watchlist = [d_train,d_valid]
    
    print("--------------- lgb_model_train params -------------------")
    print(params)
    print("--------------- lgb_model_train params -------------------")
    model = lgb.train(params,       
                  num_boost_round = num_rounds,
                  train_set=d_train,
                  valid_names = ['data_train','data_valid'],
                  feval=feval,
                  valid_sets=watchlist,
                  callbacks=[log_evaluation(log),early_stopping(early_stop)]
                 )
    
    return model


def lgb_model_rscv(X_train, y_train, X_test, y_test,score_rs='average_precision', params=None, param_dist=None,n_iter=None,n_jobs = None):
    
    print("++++++++++++++++++++++++ INICIO - ESTIMAR MODELO ++++++++++++++++++++++++")   
    fn_eval = g.get_fn_eval(score_rs)
    fit_params = get_fit_params(X_train,y_train,X_test,y_test,fn_eval)          

    cv_ = g.get_kfold()          
    model = lgb.LGBMClassifier(**params)       
    print("------------------  n_jobs= ",n_jobs," -------------------")    
    print('------------------------ params -------------')
    print(params)
    print('------------------------------------------------')
    
    print('RandomizedSearchCV -> Multiples Hyperparametros')
    grid_obj = RandomizedSearchCV(estimator=model,
                                  param_distributions=param_dist,
                                  cv=cv_,
                                  n_iter=n_iter,
                                  refit=False,
                                  return_train_score=False,
                                  scoring = score_rs,
                                  n_jobs = n_jobs,
                                  verbose= True,          
                                  random_state=375)

    print('------------X_train-------------')
    print(X_train.shape)
    print(y_train.value_counts())
    print('---------------------------------')
    grid_obj.fit(X_train, y_train,**fit_params)

    #estimator = grid_obj.best_estimator_
    
    estimator = lgb.LGBMClassifier(**params)
    estimator.set_params(**grid_obj.best_params_) 
    estimator.fit(X_train,y_train,**fit_params)
    
    results = pd.DataFrame(grid_obj.cv_results_)
    best_params = grid_obj.best_params_  
    
    print('------------mejores hyperparametros-------------')
    print(best_params)
    print('------------------------------------------------')
    print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++") 
    return results, estimator , best_params

def get_fit_params(X_train,y_train,X_test, y_test,fn_eval):
 
    fit_params={"early_stopping_rounds":800, 
                "eval_metric" : fn_eval, 
                "eval_set" : [(X_train,y_train),(X_test,y_test)],
                'eval_names': ['train','test'],
                #"eval_set" : [(X_train,y_train)],
                #'eval_names': ['train'],               
                'verbose': 200,
                'feature_name': 'auto', # that's actually the default
                'categorical_feature': 'auto' # that's actually the default
               }    
    return fit_params