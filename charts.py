# import matplotlib.pyplot as plt
# import numpy as np


# x = np.array(range(1,18))
# y = [1, 0.98, 0.81, 0.51, 0.25, 0.11, 0.064, 0.05, 0.049, 0.048, 0.048, 0.047, 0.044, 0.041, 0.035, 0.028, 0.020]

# plt.plot(x, y)

# plt.xlabel("Memory of each programmable switch (MB)")
# plt.ylabel("Placement Failure (%)")
# plt.title("Sketch Placement Failure %")
# plt.show()


# x = [0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
# y = [0.047, 0.048, 0.049, 0.05, 0.066, 0.11]
# plt.plot(x, y)

# plt.xlabel("Load(the percentage of the traffic load to the network capacity)")
# plt.ylabel("Placement Failure (%)")
# plt.title("Sketch Placement Failure %")
# plt.show()
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.rc('font', family='Arial')
matplotlib.rc('text', usetex=True)
x = [4, 8, 12, 16, 20, 24]
y1 = [0.58, 0.58, 0.58, 0.58, 0.58, 0.58]
y2 = [0.35, 0.20, 0.16, 0.16, 0.16, 0.16]
y3 = [0.35, 0.21, 0.12, 0.06, 0.01, 0]
y4 = [0.35, 0.32, 0.32, 0.32, 0.32, 0.32]
y5 = [0.48, 0.48, 0.48, 0.48, 0.48, 0.48]


# Create a new figure with a specific size (width, height)
fig, ax = plt.subplots(figsize=(8, 6))

# Plot the data with labels for the legend
ax.plot(x, y1, label='Max hash capacity /10', color='blue', linewidth=2)
ax.plot(x, y5, label='Max hash capacity /5', color='black', linewidth=2)
ax.plot(x, y4, label='Max hash capacity /2', color='orange', linewidth=2)
ax.plot(x, y2, label='Max hash capacity', color='red', linewidth=2)
ax.plot(x, y3, label='Max hash capacity * 10', color='green', linewidth=2)


ax.set_xticks([4, 8, 12, 16, 20, 24])

# Set the title and axis labels
ax.set_title('Sketch Placement Failure (1 GB Bandwidth and fixed rate)', fontsize=12, fontweight='bold')
ax.set_xlabel('Switch Memory (MB)', fontsize=12)
ax.set_ylabel('Percentage of placement failure', fontsize=14)

# Display a grid
ax.grid(True, which='both', linestyle='--', linewidth=0.5)

# Set the legend
ax.legend(fontsize=12)

# Save the figure in high resolution
fig.savefig('mem_hash.png', dpi=300, bbox_inches='tight')

# Display the plot
plt.show()
