# Conwaybot
Twitter bot written in Python that runs Conway's Game of Life seeded with text from a tweet. Running under [@conwaybot1](https://twitter.com/conwaybot1) on Twitter.

A toy project for myself. Inspired by [Thread Reader App](https://threadreaderapp.com/), Yahtzee Croshaw's [Bunker Bustin](https://yzcroshaw.itch.io/bunker-bustin) game that encoded level layout in a format that is Tweet-able, and John Conway's [Game Of Life](https://en.wikipedia.org/wiki/Conway%27s_Game_of_Life). No real goal other than to play around with the Twitter API and try to do some mental recovery from doom scrolling through the 2020 election. 

The bot uses Tweepy to find any Tweet mentions of the screenname of the bot. The text of the Tweet mentioning the bot is then used as the initial "seed" for generation 0 of a Game Of Life Simulation. The simulation lasts 100 generations. Each generation being added to an animated GIF. The animated GIF is then attached a reply to the original mention Tweet.

See [GitHub Issues page](https://github.com/rdpickard/conwaybot/issues) for things that need to be done and general ideas I might implement in the future.

![Example Animated Gif from Tweet](media/hello_lovely.gif)

### 3rd Party Modules

[Pillow](https://pillow.readthedocs.io/en/stable/) - Image creation and manipulation

[Tweepy](https://www.tweepy.org/) - Python API for Twitter access

[NumPy](https://numpy.org/) - Array and matrix math Python library

### Fonts 

Fonts are GNU free mono. Available [here](https://github.com/opensourcedesign/fonts)

### Miscellaneous notes

To convert an animate gif to a mp4 movie. Apps like Instagram want an mp4. 

```
ffmpeg -i animated.gif -movflags faststart -pix_fmt yuv420p -vf "scale=trunc(iw/2)*2:trunc(ih/2)*2" video.mp4
```