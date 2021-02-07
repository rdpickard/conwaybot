import sys
import argparse
import os

import conwaybot
from PIL import Image, ImageDraw, ImageFont

parser = argparse.ArgumentParser()
parser.add_argument('number_of_generations', type=int)
parser.add_argument('seed_image_path', type=str)
parser.add_argument('output_image_path', type=str)
args = parser.parse_args()

if not os.path.exists(args.seed_image_path):
    raise AttributeError("No such file at path '{}'".format(args.seed_image_path))
if not os.path.isfile(args.seed_image_path):
    raise AttributeError("path doesn't point to a file '{}'".format(args.seed_image_path))
if not os.access(args.seed_image_path, os.R_OK):
    raise AttributeError("No read access on file '{}'".format(args.seed_image_path))

seed_image = Image.open(args.seed_image_path)
gray = seed_image.convert('L')
bw = gray.point(lambda x: 0 if x<128 else 255, '1')

frames, frame_render_times = conwaybot.simulate_conway_generations_from_image(bw, args.number_of_generations)
conwaybot.images_to_animated_gif(args.output_image_path,
                                 [frames[0]] * 45 + frames)

sys.exit()
