import io
import sys
import os
import time
import hashlib

from PIL import Image, ImageDraw, ImageFont
import numpy
import tweepy


def cord_is_in_region(y, x,
                      region_height_slice_start, region_height_slice_stop,
                      region_width_slice_start, region_width_slice_end):
    if y >= region_height_slice_start and y < region_height_slice_stop and x >= region_width_slice_start and x < region_width_slice_end:
        # print("{}, {} IN [{}:{}, {}:{}]".format(y, x, region_height_slice_start, region_height_slice_stop,region_width_slice_start, region_width_slice_end))
        return True
    else:
        # print("{}, {} OUT [{}:{}, {}:{}]".format(y, x, region_height_slice_start, region_height_slice_stop,region_width_slice_start, region_width_slice_end))
        return False


def find_non_empty_regions_bounded(region_pixel_matrix,
                                   region_y_start, region_y_end, region_x_start, region_x_end):
    region_size_y, region_size_x = region_pixel_matrix.shape

    non_empty_regions = []

    region_width = (region_x_end - region_x_start)
    region_height = (region_y_end - region_y_start)

    if region_height < 1 or region_width < 1:
        raise AttributeError("Bounded region can't have negative height or width")

    if numpy.sum(region_pixel_matrix[region_y_start: region_y_start + int(region_height / 2),
                 region_x_start: region_x_start + int(region_width / 2)]) > 0:
        non_empty_regions.append((region_y_start, region_y_start + int(region_height / 2),
                                  region_x_start, region_x_start + int(region_width / 2)))

    if numpy.sum(region_pixel_matrix[region_y_start + int(region_height / 2):region_y_end + 1,
                 region_x_start: region_x_start + int(region_width / 2)]) > 0:
        non_empty_regions.append((region_y_start + int(region_height / 2), region_y_end,
                                  region_x_start, region_x_start + int(region_width / 2)))

    if numpy.sum(region_pixel_matrix[region_y_start: region_y_start + int(region_height / 2),
                 region_x_start + int(region_width / 2): region_x_end + 1]) > 0:
        non_empty_regions.append((region_y_start, region_y_start + int(region_height / 2),
                                  region_x_start + int(region_width / 2), region_x_end))

    if numpy.sum(region_pixel_matrix[region_y_start + int(region_height / 2):region_y_end + 1,
                 region_x_start + int(region_width / 2):region_x_end + 1]) > 0:
        non_empty_regions.append((region_y_start + int(region_height / 2), region_y_end,
                                  region_x_start + int(region_width / 2), region_x_end))

    return non_empty_regions


def find_non_empty_regions(region_pixel_matrix):
    height, width = region_pixel_matrix.shape

    non_empty_regions = []

    if numpy.sum(region_pixel_matrix[0: int(height / 2), 0: int(width / 2)]) > 2:
        non_empty_regions.append((0, int(height / 2), 0, int(width / 2)))

    if numpy.sum(region_pixel_matrix[int(height / 2):height, 0: int(width / 2)]) > 2:
        non_empty_regions.append((int(height / 2), height, 0, int(width / 2)))

    if numpy.sum(region_pixel_matrix[0: int(height / 2), int(width / 2): width]) > 2:
        non_empty_regions.append((0, int(height / 2), int(width / 2), width))

    if numpy.sum(region_pixel_matrix[int(height / 2):height, int(width / 2): width]) > 2:
        non_empty_regions.append((int(height / 2), height, int(width / 2), width))

    return non_empty_regions


def find_empty_regions(pixel_matrix):
    height, width = pixel_matrix.shape

    empty_regions = []

    if numpy.sum(pixel_matrix[0: int(height / 2), 0: int(width / 2)]) < 2:
        empty_regions.append((0, int(height / 2), 0, int(width / 2)))

    if numpy.sum(pixel_matrix[int(height / 2):height, 0: int(width / 2)]) < 2:
        empty_regions.append((int(height / 2), height, 0, int(width / 2)))

    if numpy.sum(pixel_matrix[0: int(height / 2), int(width / 2): width]) < 2:
        empty_regions.append((0, int(height / 2), int(width / 2), width))

    if numpy.sum(pixel_matrix[int(height / 2):height, int(width / 2): width]) < 2:
        empty_regions.append((int(height / 2), height, int(width / 2), width))

    return empty_regions


# TODO write a function to computer image size that is best suited for displaying formatted text of at a particular font size



def text_to_image(image_text,
                  image_height, image_width,
                  font_size, font_path):

    """
    Draws the supplied image_text string into a new Pillow Image Object. The Image object is monochrome.

    :param image_text: Th text that will be drawn into the image
    :param image_height: The height of the image that the text will be drawn into
    :param image_width: The width of the image that the text will be drawn into
    :param font_size: The size of the font to draw, in pixels
    :param font_path: Path to the true type font to use
    :return: A Pillow.Image object of the text
    """
    height = image_height
    width = image_width
    font_size = font_size

    # create an image

    text_image = Image.new("1", (width, height), 1)

    if not os.path.exists(font_path):
        raise AttributeError("No such file at font path '{}'".format(font_path))
    if not os.path.isfile(font_path):
        raise AttributeError("font file isn't a file '{}'".format(font_path))
    if not os.access(font_path, os.R_OK):
        raise AttributeError("No read access on font file '{}'".format(font_path))

    try:
        fnt = ImageFont.truetype(font_path, font_size)
    except OSError as oe:
        raise AttributeError("Font file doesn't seem to be a True Type font '{}'".format(font_path))
    # get a drawing context
    d = ImageDraw.Draw(text_image)

    # draw multiline text
    d.multiline_text((10, 10), image_text, font=fnt)

    return text_image


def simulate_conway_generations_from_image(initial_image,
                                           life_generations,
                                           empty_space_detection_depth=6):
    """

    :param initial_image: The image that is the initial state, generation 0, of the simulation
    :param life_generations: Number of generations in the simulation. Each generation will produce one image in the result
    :param empty_space_detection_depth: How may times successive region sub-divisions to go to avoid processing empty space. Defaults to 6
    :return: Two arrays of equal length, first is of Pillow Image objects with the initial_image at index 0, the second the time it took to compute each frame generation
    """
    images = []
    frame_compute_times = []

    frame_image_height = initial_image.height
    frame_image_width = initial_image.width

    images.append(initial_image)
    frame_compute_times.append(0)

    for i in range(1, life_generations):

        fstart = time.time()

        x, y = 0, 0

        next_gen_image = Image.new("1", (frame_image_width, frame_image_height), 1)
        pixel_matrix = numpy.logical_not(numpy.asarray(images[i - 1]))

        non_empty_regions = [(0, frame_image_height, 0, frame_image_width)]

        for _ in range(0, empty_space_detection_depth):
            non_empty_regions = [item for sublist in list(
                map(lambda test_region: find_non_empty_regions_bounded(pixel_matrix, *test_region),
                    non_empty_regions)) for item in sublist]

        for region in non_empty_regions:

            for y in range(region[0], region[1]):
                for x in range(region[2], region[3]):

                    neighborhood_region = pixel_matrix[max(0, y - 1): y + 2,
                                                       max(0, x - 1): x + 2]
                    live_neighbors = numpy.sum(neighborhood_region) - pixel_matrix[y, x]

                    if pixel_matrix[y, x] == 1 and (live_neighbors == 2 or live_neighbors == 3):
                        next_gen_image.putpixel((x, y), 0)
                    elif pixel_matrix[y, x] == 0 and live_neighbors == 3:
                        next_gen_image.putpixel((x, y), 0)

        images.append(next_gen_image.copy())
        frame_compute_times.append(time.time() - fstart)

    return images, frame_compute_times


def images_to_animated_gif(gif_file_full_path_name, frame_images):

    container_gif_image = Image.new("1",
                                    (max(map(lambda image: image.width, frame_images)),
                                     max(map(lambda image: image.height, frame_images))),
                                    1)
    draw = ImageDraw.Draw(container_gif_image)

    if os.path.exists(gif_file_full_path_name):
        raise AttributeError("File already exists at specified gif path. Not going to overwrite. '{}'".format(gif_file_full_path_name))

    container_gif_image.save(gif_file_full_path_name,
                             save_all=True,
                             append_images=map(lambda i: i.convert('P'), frame_images),
                             optimize=False, duration=40, loop=0)


consumer_key = os.environ.get('consumer_key')
consumer_secret = os.environ.get('consumer_secret')
access_token = os.environ.get('access_token')
access_token_secret = os.environ.get('access_token_secret')

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

api = tweepy.API(auth)

bot_screenname = api.me().screen_name

max_tweet_id = -1

while True:
    print("getting mentions {}".format(max_tweet_id))
    # Setting the since_id to 0 returns an error
    if max_tweet_id != -1:
        mentions = api.mentions_timeline(since_id=max_tweet_id)
    else:
        mentions = api.mentions_timeline()
    ids = []
    for tweet in mentions:

        #print(tweet)
        replyers = list(map(lambda reply_tweet:  reply_tweet.user.screen_name, tweepy.Cursor(api.search, q='to:{}'.format(tweet.user.screen_name),
                                since_id=tweet.id, tweet_mode='extended').items()))

        if bot_screenname in replyers:
            ids.append(tweet.id)
            continue

        file_name = "local/{}_{}.gif".format(hashlib.md5(tweet.text.encode()).hexdigest()[0:6], time.time())

        seed_image = text_to_image(tweet.text, 800, 800, 80, "fonts/FreeMono.ttf")
        frames, frame_render_times = simulate_conway_generations_from_image(seed_image, 100)
        images_to_animated_gif(file_name,
                               [frames[0]] * 45 + frames)

        api.update_with_media(file_name, "@{}".format(tweet.user.screen_name), in_reply_to_status_id=tweet.id)

        ids.append(tweet.id)

    max_tweet_id = max(ids, default=max_tweet_id)

    time.sleep(10)

