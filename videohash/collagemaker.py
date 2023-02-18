from math import sqrt
from pathlib import Path
from typing import Collection

from PIL import Image

from .exceptions import CollageOfZeroFramesError


class MakeCollage:

    """
    Class that creates the collage from list of images.

    Collage that should be as close to the shape of a square.

    The images are arranged by timestamp of the frames, their
    index in the image_list is based on thier timestamp on the
    video. The image with the index 2 is a frame from the 3rd
    second and an index 39 is from at the 40th second. The index
    is one less due to zero-based indexing.


    Let's say we have a list with 9 images.

    As the images should be arranged in a way to resemble a
    square, we take the square root of 9 and that is 3. Now
    we need to make a 3x3 frames collage.

    Arrangement should be:
    Img1 Img2 Img3
    Img4 Img5 Img6
    Img7 Img8 Img9

    If the number of images is not a perfect square, calculate the
    square root and round it to the nearest integer.

    If number of images is 13, which is not a perfect square.

    sqrt(13) = 3.605551275463989
    round(3.605551275463989) = 4

    Thus the image should be 4x4 frames of collage.

    Arrangement should be:
    -----------------------------
    |  Img1  Img2  Img3   Img4  |
    |  Img5  Img6  Img7   Img8  |
    |  Img9  Img10 Img11  Img12 |
    |  Img13  X     X      X    |
    -----------------------------

    X denotes the empty space due to lack of images.
    But the empty spaces will not affect the robustness
    as downsized/transcoded version of the video will also
    produce these vacant spaces.
    """

    def __init__(
        self,
        image_list: Collection[Path],
        output_path: Path,
        frame_size: int,
    ) -> None:
        """
        Checks if the list passed is not an empty list.
        Also makes sure that the output_path directory exists.

        And calls the make method, the make method creates the collage.

        :param image_list: A python list containing the list of absolute
                           path of images that are to be added in the collage.
                           The order of images is kept intact and is very important.

        :param output_path: Absolute path of the collage including
                            the image name. (This is where the collage is saved.)
                            Example: '/home/username/projects/collage.jpeg'.

        :param collage_image_width: An integer specifying the image width of the
                                    output collage. Default value is 1024 pixels.

        :return: None

        :rtype: NoneType
        """
        self.image_list = image_list
        self.number_of_images = len(self.image_list)
        if self.number_of_images == 0:
            raise CollageOfZeroFramesError("Can not make a collage of zero images.")

        self.frame_size = frame_size
        self.collage_frames_per_row = round(sqrt(self.number_of_images))
        self.collage_size = self.collage_frames_per_row * self.frame_size

        self.output_path = output_path

        self.make()

    def make(self):
        """
        Creates a fixed size collage from list of images.
        """
        # create a black base image of collage_size x collage_size
        collage_image = Image.new("RGB", (self.collage_size, self.collage_size))

        # iterate and paste frames
        y = -self.frame_size
        x = 0
        for count, frame_path in enumerate(self.image_list):
            # set the x coordinate to zero if we are on the first column and increment row by increasing y
            if not count % self.collage_frames_per_row:
                x = 0
                y += self.frame_size

            # open the frame image
            frame = Image.open(frame_path)

            # paste the frame image onto base image
            collage_image.paste(frame, (x, y))
            frame.close()

            # get the x coordinate of the next frame
            x += self.frame_size

        # save the base image with all the frame images embedded on it
        collage_image.save(self.output_path)
        collage_image.close()
