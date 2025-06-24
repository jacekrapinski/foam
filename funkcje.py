import numpy as np
import pandas as pd
import random
import copy
from itertools import product
import statsmodels
import statsmodels.api as sm
import statsmodels.formula.api as smf
from scipy.stats import norm

from patsy import dmatrix

def Sigma(t,a,b,c,d,e,f):
  return a*np.power(b*t+c,d*t+e)+f

def FCI(sigma,eps):
  fci=[100.0,]
  for i in np.arange(1,len(sigma),1):
    if sigma[i]>0:
      Xt = np.random.normal(loc=0,scale=sigma[i])
      fci.append(max(fci[i-1]-abs(Xt)*eps,0))
    else:
      fci.append(max(fci[i-1],0))
  return fci

def oldFCI(fci_prev,p,sigma,eps):
  dt = np.random.binomial(size=1, n=1, p=p)[0]
  Xt = np.random.normal(loc=0,scale=sigma)
  fci = max((fci_prev-dt * abs(Xt)*eps,0))
  return fci


def shiftArray(a,Delta):
  if Delta>0:
    res=np.hstack(([np.nan]*Delta,a[:len(a)-Delta]))
  elif Delta<0:
    res=a[abs(Delta):]
  else:
    res=a
  return res

def getSigma(x_size,scenario):
  x= np.arange(0,x_size,1)
  if scenario==1:
    sigma = [Sigma(i, 1., 0., 0.5, 0., 1., 0.) for i in x]
  elif scenario==2:
    sigma = [Sigma(i, 1., 0., 1., 0., 1., 0.) for i in x]
  elif scenario==3:
    sigma = [Sigma(i, 1., 0., 1.5, 0., 1., 0.) for i in x]
  elif scenario==4:
    sigma = [Sigma(i, 0.025,0.,1.05,1.,0.,0.) for i in x]
  elif scenario==5:
    sigma = [Sigma(i, 0.05,1.,0.,0.,1.,0.) for i in x]
  elif scenario==6:
    sigma = [Sigma(i, -5.,0.,1.05,-1.,0.,5.) for i in x]
  elif scenario==7:
    sigma = [Sigma(i, 27.5,1.,0.,0.,-1.,0.) for i in x]
  elif scenario==8:
    sigma = [Sigma(i, -0.025,1.,0.,0.,1.,2.5) for i in x]
  elif scenario==9:
    sigma = [Sigma(i, 5.,0.,1.05,-1.,0.,0.) for i in x]
  return sigma

def intervals10(x):
  if x<=10:
    return 1.
  elif 10<x<=20:
    return 12.
  elif 20<x<=30:
    return 23.
  elif 30<x<=40:
    return 34.
  elif 40<x<=50:
    return 45.
  elif 50<x<=60:
    return 55.
  elif 60<x<=70:
    return 66.
  elif 70<x<=80:
    return 77.
  elif 80<x<=90:
    return 88.
  elif x>90:
    return 99.
  

def find_t(fci_array, values):  
  res=[]
  for v in values:    
    closest=np.abs(fci_array - v).argmin()
    if closest==0:
      res.append(int(closest))
      continue
    if closest == res[- 1] or np.isnan(res[- 1]):
        res.append(np.nan)        
    else:
        res.append(int(closest))
  return res

def create_mean_profile():
  x= np.arange(0,101,1)
  sigmas={
    1:[Sigma(i, 1., 0., 0.5, 0., 1., 0.) for i in x],
    2:[Sigma(i, 1., 0., 1., 0., 1., 0.) for i in x],
    3:[Sigma(i, 1., 0., 1.5, 0., 1., 0.) for i in x],
    4:[Sigma(i, 0.025,0.,1.05,1.,0.,0.) for i in x],
    5:[Sigma(i, 0.05,1.,0.,0.,1.,0.) for i in x],
    6:[Sigma(i, -5.,0.,1.05,-1.,0.,5.) for i in x],
    7:[Sigma(i, 27.5,1.,0.,0.,-1.,0.) for i in x],
    8:[Sigma(i, -0.025,1.,0.,0.,1.,2.5) for i in x],
    9:[Sigma(i, 5.,0.,1.05,-1.,0.,0.) for i in x]
    }
  
  fcis={
    1:[100],
    2:[100],
    3:[100],
    4:[100],
    5:[100],
    6:[100],
    7:[100],
    8:[100],
    9:[100]
  }
  for scen in [1,2,3,4,5,6,7,8,9]:
    for i in np.arange(1,101,1):
      fcis[scen].append(fcis[scen][i-1]-np.sqrt(2/np.pi)*sigmas[scen][i])
  
  return fcis

def expectation_epsilon(sigma,sigma_epsilon,previous_fci,epsilon):
  moment = previous_fci/(sigma*epsilon)
  eFCI = np.sqrt(2.0/np.pi)*(previous_fci*np.sqrt(2*np.pi)*(norm.cdf(moment)-0.5) - sigma*epsilon*(1-np.exp(-moment*moment*0.5)))
  return eFCI

def expectation(sigmas,t,sigma_epsilon,previous_fci):
  sum=0
  se2=sigma_epsilon*sigma_epsilon
  zakres=np.arange(0.2,1.81,0.01)
  for i in range(len(zakres)-1):    
    epsilon=zakres[i]
    ex = expectation_epsilon(sigmas[t],sigma_epsilon,previous_fci,epsilon)
    h = ex*1/(np.sqrt(2*np.pi)*sigma_epsilon)*np.exp(-0.5*(epsilon-1)*(epsilon-1)/(se2))  
    epsilon=zakres[i+1]
    ex1 = expectation_epsilon(sigmas[t],sigma_epsilon,previous_fci,epsilon)
    h1 = ex1*1/(np.sqrt(2*np.pi)*sigma_epsilon)*np.exp(-0.5*(epsilon-1)*(epsilon-1)/(se2))  
    m = (h+h1)/2*0.01
    sum+=m
  return sum

def create_mean_profile_with_tail(sigma_epsilon):
  x= np.arange(0,101,1)
  sigmas={
    1:[Sigma(i, 1., 0., 0.5, 0., 1., 0.) for i in x],
    2:[Sigma(i, 1., 0., 1., 0., 1., 0.) for i in x],
    3:[Sigma(i, 1., 0., 1.5, 0., 1., 0.) for i in x],
    4:[Sigma(i, 0.025,0.,1.05,1.,0.,0.) for i in x],
    5:[Sigma(i, 0.05,1.,0.,0.,1.,0.) for i in x],
    6:[Sigma(i, -5.,0.,1.05,-1.,0.,5.) for i in x],
    7:[Sigma(i, 27.5,1.,0.,0.,-1.,0.) for i in x],
    8:[Sigma(i, -0.025,1.,0.,0.,1.,2.5) for i in x],
    9:[Sigma(i, 5.,0.,1.05,-1.,0.,0.) for i in x]
    }
  
  fcis={
    1:[100],
    2:[100],
    3:[100],
    4:[100],
    5:[100],
    6:[100],
    7:[100],
    8:[100],
    9:[100]
  }
  for scen in [1,2,3,4,5,6,7,8,9]:
    for i in np.arange(1,101,1):
      fcis[scen].append(expectation(sigmas[scen],i,sigma_epsilon,fcis[scen][i-1]))
  
  return fcis


def create_seed(combination):  
  p3={5:1,10:2,20:3}
  p2={-10:1,0:2,10:3}
  p1={5:1,7.5:2,10:3}
  seed=p1[combination[2]]+p2[combination[1]]*10+p3[combination[0]]*100  + 27
  return seed