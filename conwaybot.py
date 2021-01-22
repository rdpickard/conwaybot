import io
import sys
import time

from PIL import Image, ImageDraw, ImageFont
import numpy

text2 = """
We're renovating our digital infrastructure for 2021. Unfortunately, this means rebuilding our monthly sustainer program from scratch.

https://cwc.im/support

If you are able, please consider signing up to help us cover our costs, or just make a one-time donation.

Thank you!"""

text="""
Hello
Lovely"""

def cord_is_in_region(y, x,
                      region_height_slice_start, region_height_slice_stop,
                      region_width_slice_start, region_width_slice_end):

    if y >= region_height_slice_start and y < region_height_slice_stop and x >= region_width_slice_start and x < region_width_slice_end:
        #print("{}, {} IN [{}:{}, {}:{}]".format(y, x, region_height_slice_start, region_height_slice_stop,region_width_slice_start, region_width_slice_end))
        return True
    else:
        #print("{}, {} OUT [{}:{}, {}:{}]".format(y, x, region_height_slice_start, region_height_slice_stop,region_width_slice_start, region_width_slice_end))
        return False


def find_non_empty_regions_bounded(region_pixel_matrix,
                                   region_y_start, region_y_end, region_x_start, region_x_end):

    region_size_y, region_size_x = region_pixel_matrix.shape

    non_empty_regions = []

    region_width = (region_x_end - region_x_start)
    region_height = (region_y_end - region_y_start)

    if region_height < 1 or region_width < 1:
        raise AttributeError("Bounded region can't have negative height or width")

    if numpy.sum(region_pixel_matrix[region_y_start: region_y_start+int(region_height/2),
                                     region_x_start: region_x_start+int(region_width/2)]) > 0:

        non_empty_regions.append((region_y_start, region_y_start+int(region_height/2),
                                  region_x_start, region_x_start+int(region_width/2)))

    if numpy.sum(region_pixel_matrix[region_y_start+int(region_height/2):region_y_end+1,
                                     region_x_start: region_x_start+int(region_width/2)]) > 0:

        non_empty_regions.append((region_y_start+int(region_height/2), region_y_end,
                                  region_x_start, region_x_start+int(region_width/2)))

    if numpy.sum(region_pixel_matrix[region_y_start: region_y_start+int(region_height/2),
                                     region_x_start+int(region_width/2): region_x_end+1]) > 0:
        non_empty_regions.append((region_y_start, region_y_start+int(region_height/2),
                                  region_x_start+int(region_width/2), region_x_end))

    if numpy.sum(region_pixel_matrix[region_y_start+int(region_height/2):region_y_end+1,
                                     region_x_start+int(region_width/2):region_x_end+1]) > 0:
        non_empty_regions.append((region_y_start+int(region_height/2), region_y_end,
                                  region_x_start+int(region_width/2), region_x_end))

    return non_empty_regions




def find_non_empty_regions(region_pixel_matrix):

    height, width = region_pixel_matrix.shape

    non_empty_regions = []

    if numpy.sum(region_pixel_matrix[0: int(height/2), 0: int(width/2)]) > 2:
        non_empty_regions.append((0, int(height/2), 0, int(width/2)))

    if numpy.sum(region_pixel_matrix[int(height/2):height, 0: int(width/2)]) > 2:
        non_empty_regions.append((int(height/2), height, 0, int(width / 2)))

    if numpy.sum(region_pixel_matrix[0: int(height/2), int(width/2): width]) > 2:
        non_empty_regions.append((0, int(height / 2), int(width / 2), width))

    if numpy.sum(region_pixel_matrix[int(height/2):height, int(width/2): width]) > 2:
        non_empty_regions.append((int(height/2), height, int(width/2), width))

    return non_empty_regions


def find_empty_regions(pixel_matrix):

    height, width = pixel_matrix.shape

    empty_regions = []

    if numpy.sum(pixel_matrix[0: int(height/2), 0: int(width/2)]) < 2:
        empty_regions.append((0, int(height/2), 0, int(width/2)))

    if numpy.sum(pixel_matrix[int(height/2):height, 0: int(width/2)]) < 2:
        empty_regions.append((int(height/2), height, 0, int(width / 2)))

    if numpy.sum(pixel_matrix[0: int(height/2), int(width/2): width]) < 2:
        empty_regions.append((0, int(height / 2), int(width / 2), width))

    if numpy.sum(pixel_matrix[int(height/2):height, int(width/2): width]) < 2:
        empty_regions.append((int(height/2), height, int(width/2), width))

    return empty_regions

images = []

height = 801
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

for i in range(0, 400):

    fstart = time.time()

    x, y = 0, 0

    next_gen_image = Image.new("1", (width, height), 1)
    pixel_matrix = numpy.logical_not(numpy.asarray(cimage))

    depth = 5
    non_empty_regions = [(0, height, 0, width)]

    for _ in range(0, depth):
        non_empty_regions = [item for sublist in list(map(lambda test_region: find_non_empty_regions_bounded(pixel_matrix, *test_region),
                            non_empty_regions)) for item in sublist]

    for region in non_empty_regions:

        for y in range(region[0], region[1]):
            for x in range(region[2], region[3]):

                neighborhood_region = pixel_matrix[max(0, y - 1): y + 2,
                                      max(0, x - 1): x + 2]
                live_neighbors = numpy.sum(neighborhood_region) - pixel_matrix[y, x]

                if pixel_matrix[y,x] == 1 and (live_neighbors == 2 or live_neighbors == 3):
                    next_gen_image.putpixel((x,y), 0)
                elif pixel_matrix[y,x] == 0 and live_neighbors == 3:
                    next_gen_image.putpixel((x, y), 0)

    images.append(next_gen_image.copy())
    cimage = next_gen_image
    print("FRAME {} {}".format(i, time.time()-fstart))

agif = Image.new("1", (width, height), 1)
draw = ImageDraw.Draw(agif)
agif.save('pillow_imagedraw_test3_N.gif',
          save_all=True,
          append_images=map(lambda i: i.convert('P'), images),
          optimize=False, duration=40, loop=0)
