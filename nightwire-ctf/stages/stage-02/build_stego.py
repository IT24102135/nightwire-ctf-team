import base64
from PIL import Image
flag = b"NIGHTWIRE{h1dd3n_1n_pl41n_s1ght}"
encoded_flag = base64.b32encode(flag)
binary_data = ''.join([format(b, '08b') for b in encoded_flag]) + '00000000'
img = Image.open('base_image.png').convert('RGB')
pixels = img.load()
width, height = img.size
data_index = 0
for y in range(height):
    for x in range(width):
        if data_index < len(binary_data):
            r, g, b = pixels[x, y]
            # Clear the blue LSB and insert our custom bit
            b = (b & ~1) | int(binary_data[data_index])
            pixels[x, y] = (r, g, b)
            data_index += 1
img.save('html/network_diagram.png')
print("Base32 flag successfully embedded into the blue LSB channel!")
