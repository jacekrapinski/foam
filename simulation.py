import os
import sys
import math
import pandas as pd
import numpy as np
from funkcje import intervals10, find_t,create_mean_profile, create_seed
from patsy import dmatrix
import statsmodels.api as sm
import statsmodels.formula.api as smf
from scipy.stats import multivariate_normal, norm
import pickle
from datetime import datetime as dt
from itertools import product
import warnings
from statsmodels.tools.sm_exceptions import ConvergenceWarning
from concurrent.futures import ProcessPoolExecutor
import copy
import traceback
from datetime import datetime as dt
import matplotlib.pyplot as plt

warnings.simplefilter('ignore', ConvergenceWarning)
warnings.simplefilter('ignore', UserWarning)
warnings.simplefilter('ignore',RuntimeWarning)
warnings.simplefilter('ignore',FutureWarning)
def my_dist_func(x, y):
  return np.pow((x - y)/100,2).sum()
# @profile
def single_simulation(parameters):  
  P,b,sigma_p,data,mean_profile=parameters
  np.random.seed(create_seed([P,b,sigma_p]))
  
# RANDOM SEED
  data=[i.replace(",",".").replace("\t","").split(";") for i in data]
  df=pd.DataFrame(data)
  df=df.apply(lambda x: x.astype(float))
  Deltas=df.loc[:,1]  
  sample_times_index=list(range(4,105,P))
  
  fitted_values=[]
  avg_cis=[]
  coverages=[]

  t_start=dt.now()  

  iter = 0
  max_retr=0
  while iter<1000:        
    iter += 1
    print(f"Iteration {iter} in PID {os.getpid()}")
    try:
      result=[]      
      for i, row in df.iterrows():
        r=row[sample_times_index]
        r=list(r)
        r=[np.random.normal(loc=x+b,scale=sigma_p) for x in r]
        r=[intervals10(i) for i in r]
        result.append(r)

      DF=[]
      for nr_wiersza, i in enumerate(result):
        for j,k in enumerate(i):
          t=sample_times_index[j]-4-Deltas[nr_wiersza]
          DF.append([f"object_{nr_wiersza}" ,t, i[j]])
      DF=pd.DataFrame(DF,columns=["object","t","val"]).dropna()      
      DF['T'] = DF['t']
      
      #  Cubic spline with 9 knots at specified quantiles
      knots = DF['t'].quantile([0.2, 0.4, 0.6,0.8]).values      
      
      boundary_knots = [DF['t'].min(), DF['t'].max()]

      spline_basis = dmatrix(f"bs(t, knots=knots, degree=3, include_intercept=False,lower_bound={boundary_knots[0]}, upper_bound={boundary_knots[-1]})", {"t": DF['t']}, return_type='dataframe')      
      
      DF = pd.concat([DF, spline_basis], axis=1)      
            
      knots_str = ", ".join(map(str, knots))
      formula = f"val ~ bs(t, knots=({knots_str}), degree=3, include_intercept=False,lower_bound={boundary_knots[0]}, upper_bound={boundary_knots[-1]})"
      model = smf.gee(formula, data=DF, groups=DF["object"], cov_struct=sm.cov_struct.Autoregressive(dist_func=my_dist_func))     
   
      RES = model.fit()  
      
      new_data1 = pd.DataFrame({"t": np.linspace(DF['t'].min(), DF['t'].max(), 101)})
      new_spline_basis = dmatrix(f"bs(t, knots=knots, degree=3, include_intercept=False,lower_bound={boundary_knots[0]}, upper_bound={boundary_knots[-1]})", {"t": new_data1['t']}, return_type='dataframe')
      # Combine new data with spline basis
      new_data = pd.concat([new_data1, new_spline_basis], axis=1)
      mm=0
      if boundary_knots[0]>0:
        mm=boundary_knots[0]
      new_data1 = pd.DataFrame({"t": np.array(range(math.ceil(mm), 101, 1))})
      new_spline_basis = dmatrix(f"bs(t, knots=knots, degree=3, include_intercept=False,lower_bound={boundary_knots[0]}, upper_bound={boundary_knots[-1]})", {"t": new_data1['t']}, return_type='dataframe')

      new_data = pd.concat([new_data1, new_spline_basis], axis=1)      
          
      X_pred = dmatrix(f"bs(t, knots=knots, degree=3, include_intercept=False, lower_bound={boundary_knots[0]}, upper_bound={boundary_knots[-1]})",{"t": new_data1['t']}, return_type='dataframe')
      predictions = RES.predict(new_data)   
      coef = RES.params.values
      cov = RES.cov_params()
      fe_names = RES.params.index
      cov_fixed = cov.loc[fe_names, fe_names]
      cov = cov_fixed.values          
      se=np.sqrt(np.sum(X_pred.values @ cov * X_pred.values, axis=1))
      
      # 95% CI
      z = norm.ppf(0.975)      
      ci_lower = (predictions - z * se).clip(lower=0,upper=100)
      ci_upper = (predictions + z * se).clip(lower=0,upper=100)      
      avg_ci=np.array((ci_upper-ci_lower)/2)
      
      is_in_ci = (np.array(((ci_lower <= mean_profile[101-len(ci_lower):]))) * np.array(((ci_upper >= mean_profile[101-len(ci_lower):])))).astype(int)
      ci_concat=pd.concat([ci_lower,pd.Series(mean_profile),ci_upper],axis=1)
      pd.set_option('display.max_rows', None)
      fitted_values.append(predictions[FCI_2_eval[int(scenario[0])]].values) # zmienic na times_
      avg_cis.append(avg_ci[FCI_2_eval[int(scenario[0])]])
      coverages.append(is_in_ci[FCI_2_eval[int(scenario[0])]])           

    except Exception as e:
      traceback.print_exc()
      iter-=1
      max_retr+=1
      if max_retr<100:
        continue
      else:
        max_retr=0
        break
        
    

  mean_coverages=np.array(coverages).mean(axis=0)
  mean_cis=np.array(avg_cis).mean(axis=0)
  mean_fitted_values=np.array(fitted_values).mean(axis=0)  
  t_end=dt.now()
  result=f"{scenario}{sigma_p}{b}{P}, {scenario[0]}, {scenario[1]}, {scenario[2:]}, {sigma_p}, {b}, {P}, "+", ".join([f"{FCI_2_eval[int(scenario[0])][j]}, {mean_fitted_values[j]:.2f}, {mean_cis[j]:.2f}, {mean_coverages[j]:.3f}" for j in range(len(mean_coverages))])+f", {(t_end-t_start).total_seconds():.2f}"
  # print(result)
  
  # print(f"Exectution time {(t_end-t_start).total_seconds()}")  
  return result


def bad():
  seed=dt.now()
  np.random.seed(seed.microsecond)
  with open("bad_rows.txt","r") as f:
    badrows=f.readlines()
  with open("bad_rows_corrected","w") as f:
    for row in badrows:
      r=row.strip().split(",")
      scenario_file=f"./results/{r[0]}.txt"   
      global scenario 
      scenario=scenario_file.split("/")[2].split('.')[0]
      mean_profile=create_mean_profile()[int(scenario[0])]
      with open(f"{scenario_file}") as file:
        data=file.readlines()
      params = [int(r[3]),int(r[2]),float(r[1]),data,mean_profile]
      res=single_simulation(params)
      print(res)
      f.write(res+"\n")
    

# MAIN FUNCTION
if __name__ == "__main__":
  # all()
  with open("times.pickle","rb") as f:
    FCI_2_eval = pickle.load(f)
  all_scenarios=[i.split(".")[0] for i in os.listdir("results")]
  
  # Parameters:
  # sigma_p = 5
  # b = 0
  # P = 20
  scenario=sys.argv[1]  
  # scenario="./results/4H50.txt"  
  with open(f"{scenario}") as file:
    data=file.readlines()
  with open("mean_profiles.pickle","rb") as f:
    all_profiles=pickle.load(f)
  scenario=scenario.split("/")[2].split('.')[0]
  hml={'H':0.2, 'M':0.1, 'L':0.05}
  # mean_profile=create_mean_profile()[int(scenario[0])]
  mean_profile=all_profiles[hml[scenario[1]]][int(scenario[0])]

  # parmeter_combination=(5,0,5,data,mean_profile)
  # result=single_simulation(parmeter_combination)


  parameter_combinations=[list(p) for p in product([5,10,20], [-10,0,10], [5,7.5,10])]
  
  

  for i in range(len(parameter_combinations)):
    parameter_combinations[i].append(copy.deepcopy(data))
    parameter_combinations[i].append(copy.deepcopy(mean_profile))
  
  # print(parameter_combinations)
  # with open(f"wyniki/{scenario}.csv","w") as plik:
  #   for p in parameter_combinations:
  #     result=single_simulation(p)
  #     plik.write(result+"\n")      
  # exit()


  with open(f"wyniki100/{scenario}.csv","w") as plik:
    with ProcessPoolExecutor(max_workers=16) as executor:
        futures = [executor.submit(single_simulation, x) for x in parameter_combinations]
        for f in futures:
            print(f.result())
            plik.write(f.result()+"\n")
