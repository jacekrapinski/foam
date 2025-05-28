import os
import sys
import pandas as pd
import numpy as np
from funkcje import intervals10, find_t,create_mean_profile, create_seed
from patsy import dmatrix
import statsmodels.formula.api as smf
from scipy.stats import multivariate_normal
import pickle
from datetime import datetime as dt
from itertools import product
import warnings
from statsmodels.tools.sm_exceptions import ConvergenceWarning
from concurrent.futures import ProcessPoolExecutor
import copy
import traceback

warnings.simplefilter('ignore', ConvergenceWarning)
warnings.simplefilter('ignore', UserWarning)
warnings.simplefilter('ignore',RuntimeWarning)


def single_simulation(parameters):  
  P,b,sigma_p,data,mean_profile=parameters
  np.random.seed(create_seed([P,b,sigma_p]))

  data=[i.replace(",",".").replace("\t","").split(";") for i in data]
  df=pd.DataFrame(data)
  df=df.apply(lambda x: x.astype(float))
  Deltas=df.loc[:,1]

  sample_times=list(range(4,105,P))

  fitted_values=[]
  avg_cis=[]
  coverages=[]

  t_start=dt.now()
  for j in range(10):
      #y=list(df.loc[j][4:])
      current_delta=df.loc[j][1]
      #shifted_sample_times=[i-4-current_delta for i in sample_times]        
  #times=[i-4 for i in sample_times]
  iter = 0
  while iter<1000:        
    iter += 1
    print(f"Iteration {iter} in PID {os.getpid()}")
    try:
      result=[]
      for i, row in df.iterrows():
        r=row[sample_times]
        r=list(r)
        r=[np.random.normal(loc=x+b,scale=sigma_p) for x in r]
        r=[intervals10(i) for i in r]
        result.append(r)

      DF=[]
      for nr_wiersza, i in enumerate(result):
        for j,k in enumerate(i):
          t=sample_times[j]-4-Deltas[nr_wiersza]
          DF.append([f"object_{nr_wiersza}" ,t, i[j]])
      DF=pd.DataFrame(DF,columns=["object","t","val"]).dropna()

      DF['T'] = DF['t']
      DF['t'] = (DF['T'] - DF['T'].mean()) / DF['T'].std()
      #  Cubic spline with 9 knots at specified quantiles
      # knots = DF['t'].quantile([0.1, 0.2, 0.3,0.4,0.5,0.6,0.7,0.8,0.9]).values
      knots = DF['t'].quantile([0.2, 0.4, 0.6,0.8]).values
      # print(f'Using following knots: {knots}')
      # knots = DF['t'].quantile([0.1, 0.5,0.9]).values


      boundary_knots = [DF['t'].min(), DF['t'].max()]

      # print(f'Using following boundary knots: {boundary_knots}')
      spline_basis = dmatrix(f"bs(t, knots=knots, degree=3, include_intercept=False,lower_bound={boundary_knots[0]}, upper_bound={boundary_knots[-1]})", {"t": DF['t']}, return_type='dataframe')

      DF = pd.concat([DF, spline_basis], axis=1)
      knots_str = ", ".join(map(str, knots))
      formula = f"val ~ bs(t, knots=[{knots_str}], degree=3, include_intercept=False,lower_bound={boundary_knots[0]}, upper_bound={boundary_knots[-1]})"

      model = smf.mixedlm(formula, data=DF, groups=DF["object"], re_formula="~t")
      RES = model.fit()
      
      new_data1 = pd.DataFrame({"t": np.linspace(DF['t'].min(), DF['t'].max(), 101)})
      new_spline_basis = dmatrix(f"bs(t, knots=knots, degree=3, include_intercept=False,lower_bound={boundary_knots[0]}, upper_bound={boundary_knots[-1]})", {"t": new_data1['t']}, return_type='dataframe')
      
      new_data = pd.concat([new_data1, new_spline_basis], axis=1)
      predictions = RES.predict(new_data)
      X_pred = dmatrix(f"bs(t, knots=knots, degree=3, include_intercept=False, lower_bound={boundary_knots[0]}, upper_bound={boundary_knots[-1]})",{"t": new_data1['t']}, return_type='dataframe')

      coef = RES.fe_params.values
      cov = RES.cov_params()
      fe_names = RES.fe_params.index
      cov_fixed = cov.loc[fe_names, fe_names]
      cov = cov_fixed.values

      simulations = multivariate_normal.rvs(mean=coef, cov=cov, size=1000)
      y_sim = np.dot(simulations, X_pred.T)                                                 
      y_sim = np.where(y_sim < 0, 0, y_sim)

      alpha = 0.05
      ci_lower = np.percentile(y_sim, 100 * (alpha / 2), axis=0,method="linear")
      ci_upper = np.percentile(y_sim, 100 * (1 - alpha / 2), axis=0,method="linear")
      
      
      avg_ci=np.array((ci_upper-ci_lower)/2)
      
      is_in_ci = np.array(((mean_profile > ci_lower) & (mean_profile < ci_upper)).astype(int))
      
      fitted_values.append(predictions[FCI_2_eval[int(scenario[0])]].values) # zmienic na times_
      avg_cis.append(avg_ci[FCI_2_eval[int(scenario[0])]])
      coverages.append(is_in_ci[FCI_2_eval[int(scenario[0])]])      
    except Exception as e:
      traceback.print_exc()
      iter-=1
      continue

  mean_coverages=np.array(coverages).mean(axis=0)
  mean_cis=np.array(avg_cis).mean(axis=0)
  mean_fitted_values=np.array(fitted_values).mean(axis=0)  
  t_end=dt.now()
  result=f"{scenario}{sigma_p}{b}{P}, {scenario[0]}, {scenario[1]}, {scenario[2:]}, {sigma_p}, {b}, {P}, "+", ".join([f"{FCI_2_eval[int(scenario[0])][j]}, {mean_fitted_values[j]:.2f}, {mean_cis[j]:.2f}, {mean_coverages[j]:.3f}" for j in range(len(mean_coverages))])+f", {(t_end-t_start).total_seconds():.2f}"
  print(result)
  
  print(f"Exectution time {(t_end-t_start).total_seconds()}")  
  return result



# MAIN FUNCTION
if __name__ == "__main__":
  all_scenarios=[i.split(".")[0] for i in os.listdir("results")]
  with open("times.pickle","rb") as f:
    FCI_2_eval = pickle.load(f)

  # Parameters:
  sigma_p = 5
  b = 0
  P = 5
  
  
  scenario=sys.argv[1]  
  with open(f"{scenario}") as file:
    data=file.readlines()
  scenario=scenario.split("/")[2].split('.')[0]
  print(scenario)
  mean_profile=create_mean_profile()[int(scenario[0])]
  
  parameter_combinations=[list(p) for p in product([5,10,20], [-10,0,10], [5,7.5,10])]
  for i in range(len(parameter_combinations)):
    parameter_combinations[i].append(copy.deepcopy(data))
    parameter_combinations[i].append(copy.deepcopy(mean_profile))

  np.random.seed(157)
  
  # single_simulation(parameter_combinations[0])
  # exit(0)
  
  with open(f"wyniki/{scenario}.csv","w") as plik:
    with ProcessPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(single_simulation, x) for x in parameter_combinations]
        for f in futures:
            print(f.result())
            plik.write(f.result()+"\n")