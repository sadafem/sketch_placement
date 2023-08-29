import matplotlib.pyplot as plt
import numpy as np


x = np.array(range(1,18))
y = [1, 0.98, 0.81, 0.51, 0.25, 0.11, 0.064, 0.05, 0.049, 0.048, 0.048, 0.047, 0.044, 0.041, 0.035, 0.028, 0.020]

plt.plot(x, y)

plt.xlabel("Memory of each programmable switch (MB)")
plt.ylabel("Placement Failure (%)")
plt.title("Sketch Placement Failure %")
plt.show()


x = [0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
y = [0.047, 0.048, 0.049, 0.05, 0.066, 0.11]
plt.plot(x, y)

plt.xlabel("Load(the percentage of the traffic load to the network capacity)")
plt.ylabel("Placement Failure (%)")
plt.title("Sketch Placement Failure %")
plt.show()