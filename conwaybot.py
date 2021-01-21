from PIL import Image, ImageDraw, ImageFont

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

for i in range(1, 50):

    x, y = 0, 0

    next_gen_image = Image.new("1", (width, height), 1)

    while y < height:
        x = 0
        while x < width:
            cell = int(not cimage.getpixel((x, y)))

            live_neighbors = 0
            if x > 0:
                live_neighbors += int(not cimage.getpixel((x-1, y))) # Left
                if y > 0:
                    live_neighbors += int(not cimage.getpixel((x - 1, y - 1))) # upper left
                    live_neighbors += int(not cimage.getpixel((x, y - 1))) # upper center
                if y < (height - 1):
                    live_neighbors += int(not cimage.getpixel((x - 1, y + 1))) # lower left
                    live_neighbors += int(not cimage.getpixel((x, y + 1))) # lower center

            if x < (width - 1):
                live_neighbors += int(not cimage.getpixel((x+1, y))) # right
                if y > 0:
                    live_neighbors += int(not cimage.getpixel((x+1, y - 1))) # upper right
                if y < (height - 1):
                    live_neighbors += int(not cimage.getpixel((x+1, y + 1))) # lower right

            if cell == 1 and (live_neighbors == 2 or live_neighbors == 3):
                next_gen_image.putpixel((x,y), 0)
            elif cell == 0 and live_neighbors == 3:
                next_gen_image.putpixel((x, y), 0)

            x += 1
        y += 1

    images.append(next_gen_image.copy())
    cimage = next_gen_image
    print("FRAME {}".format(i))

agif = Image.new("1", (width, height), 1)
draw = ImageDraw.Draw(agif)
agif.save('pillow_imagedraw.gif',
          save_all=True,
          append_images=map(lambda i: i.convert('P'), images),
          optimize=False, duration=40, loop=0)