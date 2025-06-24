import os
import numpy as np
from funkcje import find_t, Sigma
import pickle

print("\n")
print("Creating times......")


FCI_2_eval = [100,90,80,70,60,50,40,30,20,10,0]

x= np.arange(0,101,1)
sigma_1 = [Sigma(i, 1., 0., 0.5, 0., 1., 0.) for i in x]
sigma_2 = [Sigma(i, 1., 0., 1., 0., 1., 0.) for i in x]
sigma_3 = [Sigma(i, 1., 0., 1.5, 0., 1., 0.) for i in x]
sigma_4 = [Sigma(i, 0.025,0.,1.05,1.,0.,0.) for i in x]
sigma_5 = [Sigma(i, 0.05,1.,0.,0.,1.,0.) for i in x]
sigma_6 = [Sigma(i, -5.,0.,1.05,-1.,0.,5.) for i in x]
sigma_7 = [Sigma(i, 27.5,1.,0.,0.,-1.,0.) for i in x]
sigma_8 = [Sigma(i, -0.025,1.,0.,0.,1.,2.5) for i in x]
sigma_9 = [Sigma(i, 5.,0.,1.05,-1.,0.,0.) for i in x]

fci1=[100]
fci2=[100]
fci3=[100]
fci4=[100]
fci5=[100]
fci6=[100]
fci7=[100]
fci8=[100]
fci9=[100]

for i in np.arange(1,101,1):
  fci1.append(fci1[i-1]-np.sqrt(2/np.pi)*sigma_1[i])
  fci2.append(fci2[i-1]-np.sqrt(2/np.pi)*sigma_2[i])
  fci3.append(fci3[i-1]-np.sqrt(2/np.pi)*sigma_3[i])
  fci4.append(fci4[i-1]-np.sqrt(2/np.pi)*sigma_4[i])
  fci5.append(fci5[i-1]-np.sqrt(2/np.pi)*sigma_5[i])
  fci6.append(fci6[i-1]-np.sqrt(2/np.pi)*sigma_6[i])
  fci7.append(fci7[i-1]-np.sqrt(2/np.pi)*sigma_7[i])
  fci8.append(fci8[i-1]-np.sqrt(2/np.pi)*sigma_8[i])
  fci9.append(fci9[i-1]-np.sqrt(2/np.pi)*sigma_9[i])

fci1=np.array(fci1)
fci1=np.where(fci1<0,0,fci1)
fci2=np.array(fci2)
fci2=np.where(fci2<0,0,fci2)
fci3=np.array(fci3)
fci3=np.where(fci3<0,0,fci3)
fci4=np.array(fci4)
fci4=np.where(fci4<0,0,fci4)
fci5=np.array(fci5)
fci5=np.where(fci5<0,0,fci5)
fci6=np.array(fci6)
fci6=np.where(fci6<0,0,fci6)
fci7=np.array(fci7)
fci7=np.where(fci7<0,0,fci7)
fci8=np.array(fci8)
fci8=np.where(fci8<0,0,fci8)
fci9=np.array(fci9)
fci9=np.where(fci9<0,0,fci9)


T={
1:[i for i in find_t(fci1,FCI_2_eval) if not np.isnan(i)],
2:[i for i in find_t(fci2,FCI_2_eval) if not np.isnan(i)],
3:[i for i in find_t(fci3,FCI_2_eval) if not np.isnan(i)],
4:[i for i in find_t(fci4,FCI_2_eval) if not np.isnan(i)],
5:[i for i in find_t(fci5,FCI_2_eval) if not np.isnan(i)],
6:[i for i in find_t(fci6,FCI_2_eval) if not np.isnan(i)],
7:[i for i in find_t(fci7,FCI_2_eval) if not np.isnan(i)],
8:[i for i in find_t(fci8,FCI_2_eval) if not np.isnan(i)],
9:[i for i in find_t(fci9,FCI_2_eval) if not np.isnan(i)],}

print(T)
with open("times.pickle","wb") as f:
  pickle.dump(T,f)
print(fci2)
