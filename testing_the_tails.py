from funkcje import *
import matplotlib.pyplot as plt
import pickle

fcis02=create_mean_profile_with_tail(0.2)
fcis01=create_mean_profile_with_tail(0.1)
fcis005=create_mean_profile_with_tail(0.05)

zapis={0.05:fcis005,0.1:fcis01,0.2:fcis02}
with open("mean_profiles.pickle","wb") as f:
    pickle.dump(zapis,f)
exit()
plt.plot(range(len(differences)),differences)
plt.savefig("differ.png", dpi=600)
print(differences)
print(min(differences))

x= np.arange(0,101,1)
fig, ax= plt.subplots(3,3)
ax[0,0].plot(x,fcis[1],linewidth=0.5)
ax[0,1].plot(x,fcis[2],linewidth=0.5)
ax[0,2].plot(x,fcis[3],linewidth=0.5)
ax[1,0].plot(x,fcis[4],linewidth=0.5)
ax[1,1].plot(x,fcis[5],linewidth=0.5)
ax[1,2].plot(x,fcis[6],linewidth=0.5)
ax[2,0].plot(x,fcis[7],linewidth=0.5)
ax[2,1].plot(x,fcis[8],linewidth=0.5)
ax[2,2].plot(x,fcis[9],linewidth=0.5)


ax[0,0].plot(x,fcis1[1],color="red",linewidth=0.5)
ax[0,1].plot(x,fcis1[2],color="red",linewidth=0.5)
ax[0,2].plot(x,fcis1[3],color="red",linewidth=0.5)
ax[1,0].plot(x,fcis1[4],color="red",linewidth=0.5)
ax[1,1].plot(x,fcis1[5],color="red",linewidth=0.5)
ax[1,2].plot(x,fcis1[6],color="red",linewidth=0.5)
ax[2,0].plot(x,fcis1[7],color="red",linewidth=0.5)
ax[2,1].plot(x,fcis1[8],color="red",linewidth=0.5)
ax[2,2].plot(x,fcis1[9],color="red",linewidth=0.5)

for ax in ax.flat:
    ax.set_ylim(bottom=-5, top=105)
    ax.set_xlim(0, 100)
    for spine in ax.spines.values():
        spine.set_linewidth(0.5)

plt.savefig("fcis.png", dpi=600)