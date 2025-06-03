import Rhino.Geometry as rg
import random
from System.Drawing import Color

# === INPUTS ===
# breps: list of Breps (geometry input)
# colorCount: number of distinct colors to cycle through
# seed: optional integer to randomize reproducibly

random.seed(seed)

# Make sure breps is a list
if not isinstance(breps, list):
    breps = [breps]

# Generate distinct colors
colors_list = []
for _ in range(colorCount):
    r = random.randint(50, 255)
    g = random.randint(50, 255)
    b = random.randint(50, 255)
    color = Color.FromArgb(r, g, b)
    colors_list.append(color)

# Assign colors to breps
output_breps = []
output_colors = []

for i, brep in enumerate(breps):
    clr = colors_list[i % colorCount]
    output_breps.append(brep)
    output_colors.append(clr)

# === OUTPUT ===
a = output_breps     # Connect to 'Custom Preview' geometry input
colors = output_colors  # Connect to 'Custom Preview' shader input
