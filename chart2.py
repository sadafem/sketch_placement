import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.rc('font', family='Arial')
matplotlib.rc('text', usetex=True)
x = [0.5,0.6,0.7,0.8]
y1 = [0.35, 0.39, 0.42, 0.45]
y2 = [0.36, 0.42, 0.47, 0.52]
y3 = [0.36, 0.44, 0.51, 0.57]



# Create a new figure with a specific size (width, height)
fig, ax = plt.subplots(figsize=(8, 6))

# Plot the data with labels for the legend
ax.plot(x, y1, label='alpha = 0.3', color='blue', linewidth=2)
ax.plot(x, y2, label='alpha = 0.6', color='red', linewidth=2)
ax.plot(x, y3, label='alpha = 0.9', color='green', linewidth=2)



ax.set_xticks([0.5,0.6,0.7,0.8])

# Set the title and axis labels
ax.set_title('Sketch Placement Failure (10 GB Bandwidth and non-fixed rate)', fontsize=12, fontweight='bold')
ax.set_xlabel(r'$\epsilon$', fontsize=16)
ax.set_ylabel('Percentage of placement failure', fontsize=14)

# Display a grid
ax.grid(True, which='both', linestyle='--', linewidth=0.5)

# Set the legend
ax.legend(fontsize=12)

# Save the figure in high resolution
fig.savefig('n.png', dpi=300, bbox_inches='tight')

# Display the plot
plt.show()
