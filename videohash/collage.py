from math import isqrt
from pathlib import Path
from typing import Collection

from PIL import Image

from .exceptions import CollageOfZeroFramesError


def make_collage(
    image_list: Collection[Image.Image],
    frame_size: int,
) -> Image.Image:
    """
    Creates a fixed size collage from list of images.
    """
    number_of_images = len(image_list)
    if number_of_images == 0:
        raise CollageOfZeroFramesError("Can not make a collage of zero images.")

    collage_frames_per_row = isqrt(number_of_images)
    collage_size = collage_frames_per_row * frame_size

    # create a black base image of collage_size x collage_size
    collage_image = Image.new("RGB", (collage_size, collage_size))

    # iterate and paste frames
    y = -frame_size
    x = 0
    for count, frame in enumerate(image_list):
        # set the x coordinate to zero if we are on the first column and increment row by increasing y
        if not count % collage_frames_per_row:
            x = 0
            y += frame_size

        # paste the frame image onto base image
        collage_image.paste(frame, (x, y))

        frame.close()

        # get the x coordinate of the next frame
        x += frame_size

    # return the base image with all the frame images embedded on it
    return collage_image
