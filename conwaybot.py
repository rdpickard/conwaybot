import io
import sys
import time

from PIL import Image, ImageDraw, ImageFont
import numpy

text = """
Hello 
Lovely"""

images = []

height = 800
width = 800
font_size = 96

# create an image
start_image = Image.new("1", (width, height), 1)

# get a font
fnt = ImageFont.truetype("fonts/FreeMono.ttf", font_size)
# get a drawing context
d = ImageDraw.Draw(start_image)

# draw multiline text
d.multiline_text((10, 10), text, font=fnt)
cimage = start_image
for i in range(1, 45):
    images.append(cimage)

for i in range(0, 45):

    fstart = time.time()

    x, y = 0, 0

    next_gen_image = Image.new("1", (width, height), 1)
    pixel_matrix = numpy.logical_not(numpy.asarray(cimage))

    for y in range(0, height):
        for x in range(0, width):
            region = pixel_matrix[max(0, y - 1): y + 2,
                                  max(0, x - 1): x + 2]
            live_neighbors = numpy.sum(region) - pixel_matrix[y, x]

            if pixel_matrix[y,x] == 1 and (live_neighbors == 2 or live_neighbors == 3):
                next_gen_image.putpixel((x,y), 0)
            elif pixel_matrix[y,x] == 0 and live_neighbors == 3:
                next_gen_image.putpixel((x, y), 0)

    images.append(next_gen_image.copy())
    cimage = next_gen_image
    print("FRAME {} {}".format(i, time.time()-fstart))

agif = Image.new("1", (width, height), 1)
draw = ImageDraw.Draw(agif)
agif.save('pillow_imagedraw.gif',
          save_all=True,
          append_images=map(lambda i: i.convert('P'), images),
          optimize=False, duration=40, loop=0)