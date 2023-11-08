import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.rc('font', family='Arial')
matplotlib.rc('text', usetex=True)
x = ['0.4', '0.5', '0.6', '0.7', '0.8']
y1 = [0, 0, 50, 90, 100]

# Create a new figure with a specific size (width, height)
#fig, ax = plt.subplots(figsize=(8, 6))

# Plot the data with labels for the legend
plt.bar(x, y1, color='blue')

#ax.set_xticks([0.4, 0.5, 0.6, 0.7, 0.8])

# Set the title and axis labels
plt.title('Feasibility of robust problem')
plt.xlabel('N (confidence level)')
plt.ylabel('Percentage of feasibility for fluctuating rates')

# Display a grid
#ax.grid(True, which='both', linestyle='--', linewidth=0.5)

# Set the legend
#plt.legend(fontsize=12)

# Save the figure in high resolution
#fig.savefig('mem_hash.png', dpi=300, bbox_inches='tight')

# Display the plot
plt.show()