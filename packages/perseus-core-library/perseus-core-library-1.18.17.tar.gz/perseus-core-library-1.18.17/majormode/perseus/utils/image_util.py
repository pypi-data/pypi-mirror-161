# Copyright (C) 2019 Majormode.  All rights reserved.
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import collections

from PIL import Image
import exifread

from majormode.perseus.model.enum import Enum


# Exif tag which value corresponds to the exposure time, which is the
# effective length of time a camera’s shutter is open.  The total
# exposure is proportional to this exposure time, or duration of light
# reaching the film or image sensor.
EXIF_TAG_EXPOSURE_TIME = 0x829A

# Exif tag which value corresponds to the f-number, which is the
# ratio of the lens’s focal length to the diameter of the entrance
# pupil.  It is a dimensionless number that is a quantitative measure
# of lens speed.
EXIF_TAG_F_NUMBER = 0x829D

# Exif tag which value corresponds to the focal length, which is the
# actual focal length of the lens of the camera, which is a measure of
# how strongly the system converges or diverges light. For an optical
# system in air, it is the distance over which initially collimated
# rays are brought to a focus.  A system with a shorter focal length
# has greater optical power than one with a long focal length; that
# is, it bends the rays more strongly, bringing them to a focus in a
# shorter distance.
EXIF_TAG_FOCAL_LENGTH = 0x920A

# Exif tag which value corresponds to the ISO speed ratings, which is
# the measure of a digital imaging systems.  ISO speed ratings of a
# digital camera are based on the properties of the sensor and the
# image processing done in the camera, and are expressed in terms of
# the luminous exposure H (in lux seconds) arriving at the sensor.
EXIF_TAG_ISO_SPEED_RATINGS = 0x8827

# Exif tag which value corresponds to the orientation, which indicates
# the orientation of the camera relative to the captured scene.
#EXIF_TAG_ORIENTATION = 0x0112
EXIF_TAG_ORIENTATION = 'Image Orientation'


ColorComponentFilter = Enum(
    'Red',
    'Green',
    'Blue',
    'Grey'
)

CropAlignment = Enum(
    'left_or_top',
    'right_or_bottom',
    'center'
)

CropForm = Enum(
    'rectangle',
    'circle'
)

Filter = Enum(
    'NearestNeighbor', # nearest neighbor
    'Bilinear',        # linear interpolation in a 2x2 environment
    'Bicubic',         # cubic spline interpolation in a 4x4 environment
    'AntiAlias'        # high-quality downsampling filter
)

PIL_FILTER_MAP = {
    Filter.NearestNeighbor: Image.NEAREST,
    Filter.Bilinear: Image.BILINEAR,
    Filter.Bicubic: Image.BICUBIC,
    Filter.AntiAlias: Image.ANTIALIAS
}

PictureExposure = Enum(
    'OverExposed',
    'UnderExposed',
    'NormallyExposed'
)


def convert_image_to_rgb_mode(image, fill_color=(255, 255, 255)):
    """
    Convert the specified image instance to RGB mode.


    @param image: a Python Library Image (PIL) instance to convert its
        pixel format to RGB, discarding the alpha channel.

    @param fill_color: color to be used to fill transparent pixels when
        discarding the alpha channel.  By default, the white color.


    @return: a Python Library Image instance with pixel format of RGB.
    """
    if image.mode not in ('RGBA', 'LA'):
        return image

    # In most cases simply discarding the alpha channel will give
    # undesirable result, because transparent pixels also have some
    # unpredictable colors. It is much better to fill transparent pixels
    # with a specified color.
    background_image = Image.new(image.mode[:-1], image.size, fill_color)
    background_image.paste(image, image.split()[-1])
    return background_image


def generate_multiple_pixel_resolutions(
        image,
        pixel_resolutions,
        filter=Filter.NearestNeighbor,
        does_crop=False,
        crop_alignment=CropAlignment.center,
        match_orientation=False):
    """
    Generate multiple resolution images of the given image.


    @param image: a Python Library Image (PIL) instance to generate
       multiple pixel resolutions from.

    @param pixel_resolutions: a list of tuples  ``(logical_size, width, height)``
        where:

        * ``logical_size``: string representation of the image size, such
          as, for instance, "thumbnail", "small", "medium", "large".

        * ``width``: positive integer corresponding to the number of pixel
          columns of the image.

        * ``height``: positive integer corresponding to the number of
          pixel rows.

    @param filter: indicate the filter to use when resizing the image.

    @param does_crop: indicate whether to crop each generated images.

    @param crop_alignment: if the image needs to be cropped, select which
        alignment to use when cropping.

    @param match_orientation: indicate whether the given canvas size
        should be inverted to match the orientation of the image.


    @return: an iterator, known as a generator, that returns a Python
             Library Image (PIL) instance each the generator is called.
    """
    for (logical_size, width, height) in \
            sorted(pixel_resolutions, key=lambda pixel_resolution: pixel_resolution[1], reverse=True):
        yield logical_size, resize_image(
            image,
            (width, height),
            filter=filter,
            does_crop=does_crop,
            crop_alignment=crop_alignment,
            match_orientation=match_orientation)


def get_exposure(image, filters=None):
    """
    Determine the exposure of a photo, which can be under-exposed,
    normally exposed or over-exposed.


    @param image: a Python Library Image (PIL) object to determine the
        exposure.

    @param filters: a list of ``ColorComponentFilter`` filter or ``None``
        to use all the filters.


    @return: an ``ExposureStatus`` instance that represents the exposure
             of the given PIL object.
    """
    def _get_exposure(histogram):
        total = sum(histogram)
        range_offset = len(histogram) / 4
        dark = float(sum(histogram[0:range_offset])) / total
        #normal = float(sum(histogram[range_offset:-range_offset])) / total
        light = float(sum(histogram[-range_offset:])) / total
        return PictureExposure.UnderExposed if dark > 0.5 and light < 0.5 \
            else PictureExposure.OverExposed if dark < 0.5 and light > 0.5 \
            else PictureExposure.NormallyExposed

    FILTER_SETTINGS = {
        ColorComponentFilter.Red: ('RGB', 0, 256),
        ColorComponentFilter.Green: ('RGB', 256, 512),
        ColorComponentFilter.Blue: ('RGB', 512, 768),
        ColorComponentFilter.Grey: ('L', 0, 256)
    }

    exposures = collections.defaultdict(int)
    for exposure in [ _get_exposure(image.convert(mode).histogram()[start_index:end_index])
        for (mode, start_index, end_index) in [ FILTER_SETTINGS[filtr]
            for filtr in filters or [
                ColorComponentFilter.Red,
                ColorComponentFilter.Green,
                ColorComponentFilter.Blue,
                ColorComponentFilter.Grey
            ] ] ]:
        exposures[exposure] += 1

    return sorted(exposures.iterkeys(), key=lambda k: exposures[k], reverse=True)[0]


def is_image_file_valid(file_path_name):
    """
    Indicate whether the specified image file is valid or not.


    @param file_path_name: absolute path and file name of an image.


    @return: ``True`` if the image file is valid, ``False`` if the file is
        truncated or does not correspond to a supported image.
    """
    # Image.verify is only implemented for PNG images, and it only verifies
    # the CRC checksum in the image.  The only way to check from within
    # Pillow is to load the image in a try/except and check the error.  If
    # as much info as possible is from the image is needed,
    # ``ImageFile.LOAD_TRUNCATED_IMAGES=True`` needs to bet set and it
    # will attempt to parse as much as possible.
    try:
        with Image.open(file_path_name) as image:
            image.load()
    except IOError:
        return False

    return True


def open_and_reorient_image(handle):
    """
    Load the image from the specified file and orient the image accordingly
    to the Exif tag that the file might embed, which would indicate the
    orientation of the camera relative to the captured scene.


    @param handle: a Python file object.


    @return: an instance returned by the Python Library Image library.
    """
    # Retrieve tags from the Exchangeable image file format (Exif)
    # included in the picture.  If the orientation of the picture is not
    # top left side, rotate it accordingly.

    # @deprecated
    # exif_tags = dict([ (exif_tag.tag, exif_tag)
    #     for exif_tag in exif.process_file(handle).itervalues()
    #         if hasattr(exif_tag, 'tag') ])

    exif_tags = exifread.process_file(handle)
    exif_tag_orientation = exif_tags.get(EXIF_TAG_ORIENTATION)

    rotation_angle = exif_tag_orientation and {
            3: 180,
            6: 270,
            8: 90
        }.get(exif_tag_orientation.values[0])

    handle.seek(0)  # exif.process_file has updated the file's current position.
    image = Image.open(handle)

    return image if rotation_angle is None else image.rotate(rotation_angle)
    # if rotation_angle:
    #     (width, height) = image.size
    #
    #     image = image.rotate(rotation_angle)
    #
    #     # @patch: PIL doesn't adjust the size of a rotated image!
    #     if rotation_angle in (90, 270) and width != height and image.size == (width, height):
    #         image.size = (height, width)
    #
    # return image


def realign_image(image, shift_x, shift_y, max_shift_x, max_shift_y,
        shift_angle=0.0, filter=Filter.NearestNeighbor,
        stretch_factor=None,
        cropping_box=None):
    """
    Realign the given image providing the specific horizontal and vertical
    shifts, and crop the image providing the maximum horizontal and
    vertical shifts of images of a same set so that they all have the same
    size.


    @param image: an instance of Python Image Library (PIL) image.

    @param shift_x: horizontal shift in pixels of the image.

    @param shift_y: vertical shift in pixels of the image.

    @param max_shift_x: maximum absolute value of the horizontal shift in
        pixels of the images in the capture.

    @param max_shift_y: maximum absolute value of the vertical shift in
        pixels of the images in the capture.

    @param shift_angle: horizontal displacement angle in degrees of
           the image.

    @param filter: indicate the filter to use when rotating the image.

    @param stretch_factor: coefficient of multiplication to stretch or
           to shrink the image in both horizontal and vertical
           directions.

    @param cropping_box: a 4-tuple defining the left, upper, right, and
           lower pixel coordinate of the rectangular region from the
           specified image.


    @return: a new instance of Python Image Library (PIL) image.
    """
    (width, height) = image.size

    # Determine the new size of the image based on the maximal horizontal
    # and vertical shifts of all the other images in this series.
    new_width = width - max_shift_x * 2
    new_height = height - max_shift_y * 2

    # Determine the coordinates of the zone to crop to center the image
    # based on the horizontal and vertical shifts.
    bounding_box_x = (0 if shift_x < 0 else shift_x * 2)
    bounding_box_y = (0 if shift_y < 0 else shift_y * 2)

    if max_shift_x > shift_x:
        bounding_box_width = width - abs(shift_x) * 2
        bounding_box_x += (bounding_box_width - new_width) / 2
        #bounding_box_x = max_shift_x - abs(shift_x)

    if max_shift_y > shift_y:
        bounding_box_height = height - abs(shift_y) * 2
        bounding_box_y += (bounding_box_height - new_height) / 2
        #bounding_box_y = max_shift_y - abs(shift_y)

    # Crop the image and rotate it based on the horizontal displacement
    # angle of this image.
    image = image.crop((bounding_box_x, bounding_box_y,
                        bounding_box_x + new_width, bounding_box_y + new_height)) \
        .rotate(-shift_angle, PIL_FILTER_MAP[filter])

    # Stretch or shrink this image based on its coefficient, keeping the
    # calculated new size of this image.
    if stretch_factor and stretch_factor > 0:
        image = image.resize((int(round(width * stretch_factor)), int(round(height * stretch_factor))),
                             PIL_FILTER_MAP[filter])
        (width, height) = image.size

        if stretch_factor >= 1:
            image = image.crop(((width - new_width) / 2, (height - new_height) / 2,
                                (width - new_width) / 2 + new_width - 1, (height - new_height) / 2 + new_height - 1))
        else:
            _image = Image.new(image.mode, (new_width, new_height))
            _image.paste(image, ((new_width - width) / 2, (new_height - height) / 2))
            image = _image

    # Crop the image to the specified rectangle, if any defined.
    if cropping_box:
        (crop_x1, crop_y1, crop_x2, crop_y2) = cropping_box
        (width, height) = image.size

        image = image.crop(
            (int(round(crop_x1 * width)), int(round(crop_y1 * height)),
             int(round(crop_x2 * width)), int(round(crop_y2 * height))))

    return image


def resize_image(image, canvas_size,
        filter=Filter.NearestNeighbor,
        does_crop=False,
        crop_alignment=CropAlignment.center,
        crop_form=CropForm.rectangle,
        match_orientation=False):
    """
    Resize the specified image to the required dimension.


    @param image: a Python Image Library (PIL) image instance.

    @param canvas_size: requested size in pixels, as a 2-tuple
        ``(width, height)``.

    @param filter: indicate the filter to use when resizing the image.

    @param does_crop: indicate whether the image needs to be cropped.

    @param crop_alignment: if the image needs to be cropped, select which
       alignment to use when cropping.

    @param match_orientation: indicate whether the given canvas size
        should be inverted to match the orientation of the image.


    @return: a PIL image instance corresponding to the image that has been
        resized, and possibly cropped.
    """
    (source_width, source_height) = image.size
    source_aspect = source_width / float(source_height)

    (canvas_width, canvas_height) = canvas_size
    canvas_aspect = canvas_width / float(canvas_height)

    if match_orientation:
        if (source_aspect > 1.0 > canvas_aspect) or (source_aspect < 1.0 < canvas_aspect):
            (canvas_width, canvas_height) = (canvas_height, canvas_width)
            canvas_aspect = canvas_width / float(canvas_height)

    if does_crop:
        if source_aspect > canvas_aspect:
            destination_width = int(source_height * canvas_aspect)
            offset = 0 if crop_alignment == CropAlignment.left_or_top \
                else source_width - destination_width if crop_alignment == CropAlignment.right_or_bottom \
                else (source_width - destination_width) / 2
            box = (offset, 0, offset + destination_width, source_height)
        else:
            destination_height = int(source_width / canvas_aspect)
            offset = 0 if crop_alignment == CropAlignment.left_or_top \
                else source_height - destination_height if crop_alignment == CropAlignment.right_or_bottom \
                else (source_height - destination_height) / 2
            box = (0, offset, source_width, destination_height + offset)

    else:
        if canvas_aspect > source_aspect:
            # The canvas aspect is greater than the image aspect when the canvas's
            # width is greater than the image's width, in which case we need to
            # crop the left and right edges of the image.
            destination_width = int(canvas_aspect * source_height)
            offset = (source_width - destination_width) / 2
            box = (offset, 0, source_width - offset, source_height)
        else:
            # The image aspect is greater than the canvas aspect when the image's
            # width is greater than the canvas's width, in which case we need to
            # crop the top and bottom edges of the image.
            destination_height = int(source_width / canvas_aspect)
            offset = (source_height - destination_height) / 2
            box = (0, offset, source_width, source_height - offset)

    return image.crop(box).resize((canvas_width, canvas_height), PIL_FILTER_MAP[filter])
