import numpy as np
import matplotlib.pyplot as plt

LAMBDA = [1, 2, 4, 8, 16, 32, 64, 128, 256, 512]

mins = []
maxs = []
means = []
stds = []
for l in LAMBDA:
    file = open(f"rtt_{l}.txt", "r")
    file_content = file.readlines()
    last_line = file_content[-1].split(" = ")[1].split(" ")[0].split("/")
    mins.append(float(last_line[0]))
    means.append(float(last_line[1]))
    maxs.append(float(last_line[2]))
    stds.append(float(last_line[3]))
    file.close()

# calculate %95 confidence interval
errors = 1.96 * np.array(stds) / np.sqrt(100)

plt.plot(LAMBDA, mins, label="min", color="lightblue")
plt.plot(LAMBDA, maxs, label="max", color="lightblue")
plt.fill_between(LAMBDA, mins, maxs, color="lightblue", alpha=0.2)
plt.errorbar(LAMBDA, means, yerr=errors, label="mean", color="lightblue", fmt='.', capsize=4, capthick=1, ecolor="lightblue")
plt.xlabel("Delay (exponential distribution ms)")
xtickslabel = [str(l) for l in LAMBDA]
xtickslabel[0] = ""
xtickslabel[1] = ""
xtickslabel[2] = ""
plt.xticks(LAMBDA, xtickslabel)
plt.ylabel("RTT (ms)")
plt.legend()

plt.show()