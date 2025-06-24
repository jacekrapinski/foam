import os
import numpy as np
from funkcje import *

print("\n")
print("Creating sigmas......")

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


print("Creating FCI profiles......")
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

print("Creating directories... ")
if not os.path.exists("results"):
    os.mkdir("results")
print("Creating files...")
np.random.seed(157)

N=[25,50,100]
results=[]
j=0

LMH={0.05:"L",0.1:"M",0.2:"H"}
for n in N:
    for sigma in [1,2,3,4,5,6,7,8,9]:
      for sigma_eps in [0.05,0.1,0.2]:
        filename=os.path.join("results",f"{sigma}{LMH[sigma_eps]}{n}.txt")
        print(filename)
        with open(filename,"w") as plik:        
          results=[]
          for s in range(n):
            # Normal distribution with 1 mean and sigma_eps variance
            eps=-1
            while eps<0:
              eps = np.random.normal(1,sigma_eps)
            # Sample Δ (rounding to an integer number, and ensuring )
            Delta = np.random.normal(0,10)
            if Delta<0:
              f=FCI(getSigma(101-int(Delta),sigma),eps)
            else:
              f=FCI(getSigma(101,sigma),eps)
            f=shiftArray(f,int(Delta))
            f=[str(round(i,2)).replace(".",",") for i in f]
            ff=";\t".join(f)
            eps=str(round(eps,2)).replace(".",",")
            wiersz=f"{s};\t{int(Delta)};\t{sigma};\t{eps};\t{ff}\n"
            results.append(wiersz)
            j+=1
          plik.writelines(results)