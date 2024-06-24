from PIL import Image

# Define your custom palette
palette = [
    [0, 128, 0],  # Green
    [0, 64, 128],  # Dark Blue
    [0, 128, 128],  # Teal
    [0, 64, 0],  # Dark Green
    [0, 64, 64], # Dark Teal
    [128, 128, 0], # Yellow
    # Add more colors as needed
]

# Define the size of the image
size = (400, 300)

# Create a new image with the size and fill it with a solid color
# Here, we're using the first color in the palette as the fill color
new_image = Image.new('RGB', size, color=tuple(palette[0]))

# Convert the image to 'P' mode (8-bit pixels, mapped to any other mode using a color palette)
new_image = new_image.convert('P')

# Create a flat list of the palette for use with putpalette
flat_palette = [value for color in palette for value in color]

# Apply the palette to the image
new_image.putpalette(flat_palette)
new_image.show()
