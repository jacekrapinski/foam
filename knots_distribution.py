from scipy.stats import gaussian_kde
from scipy.integrate import cumulative_trapezoid as cumtrapz
import numpy as np
import matplotlib.pyplot as plt
import os
import pickle

def kde_density_knots(x, n_knots):
    x = np.sort(np.asarray(x))
    kde = gaussian_kde(x)
    xs = np.linspace(x.min(), x.max(), 1000)
    cdf = cumtrapz(kde(xs), xs, initial=0)
    cdf /= cdf[-1]  # normalize
    probs = np.linspace(0, 1, n_knots + 2)[1:-1]
    knots = np.interp(probs, cdf, xs)
    return knots

def indices_of_closest(x, knots):
    x = np.asarray(x)
    knots = np.asarray(knots)
    return [np.argmin(np.abs(x - k)) for k in knots]

if __name__=="__main__":

    all_knots={}
    for file in os.listdir("./results"):
        if file.endswith(".txt"):        
            with open(f"results/{file}", "r") as f:
                data = f.readlines()
            data=[i.replace(",",".").replace("\t","").split(";") for i in data]
            data=np.array([i[4:] for i in data]).astype(float)      
            mean_profile_from_data=np.nanmean(data,axis=0)
            data=data.flatten() 
            data = np.sort(data[~np.isnan(data)])
            vals=kde_density_knots(data,4)
            ioc= indices_of_closest(mean_profile_from_data,vals)
            all_knots[file]=list(zip(ioc,vals))
            
            plt.plot(range(101),mean_profile_from_data,label="mean profile")
            plt.scatter(ioc,vals,label="knots")
            plt.title(f"Mean {file[:-4]} profile from data with knots")
            plt.savefig(f"./knots/{file[:-4]}_meanprofile.png",dpi=400)
            plt.close()
    print(all_knots)
    with open('./knots/all_knots.pickle', 'wb') as f:
        pickle.dump(all_knots,f)