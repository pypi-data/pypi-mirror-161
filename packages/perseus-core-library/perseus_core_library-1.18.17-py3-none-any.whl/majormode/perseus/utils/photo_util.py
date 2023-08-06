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

import io
import math

from majormode.perseus.model import enum
from majormode.perseus.model.geolocation import GeoPoint
from majormode.perseus.utils import cast
import exifread


ErrorType = enum.Enum(
    'HeterogeneousMetaDatumValue',
    'MissingMetaDatum',
    'PrimaryMarkerNotHorizontallyCentered',
    'PrimaryMarkerNotVerticallyCentered',
    'SecondaryMarkerNotHorizontallyCentered',
 )

# Define several useful Exif tags used to check whether the cameras
# mounted on a same rig have the same configuration.
EXIF_TAG_EXPOSURE_TIME = 0x829A
EXIF_TAG_F_NUMBER = 0x829D
EXIF_TAG_FOCAL_LENGTH = 0x920A
EXIF_TAG_ISO_SPEED_RATINGS = 0x8827
EXIF_TAG_ORIENTATION = 0x0112

EXIF_ESSENTIAL_TAGS = [
    EXIF_TAG_EXPOSURE_TIME,
    EXIF_TAG_F_NUMBER,
    EXIF_TAG_FOCAL_LENGTH,
    EXIF_TAG_ISO_SPEED_RATINGS,
    EXIF_TAG_ORIENTATION
]


class BoundingBox(object):
    """
    Represent a rectangular border with the smallest area that fully
    encloses a part of a marker distinguishable by its chroma key.
    """
    def __init__(self, x, y):
        """
        Build an instance ``BoundingBox`` initially composed of one pixel of
        the photo that is quite similar to the chroma key of the marker.

        :param x: horizontal offset, i.e., abscissa, of the pixel.
        :param y: vertical offset, i.e., ordinate, of the pixel
        """
        self.x_left = self.x_right = x
        self.y_top = self.y_bottom = y


def calculate_bearing(from_point, to_point):
    """
    Return the approximate bearing in degrees East of true North when
    traveling along the shortest path between a first point and a second
    point nearby.  The shortest path is defined using a line.  Points that
    far from each other produce meaningless results.


    @note: if you are using a method to calculate the approximate bearing
        between two points using the WGS84 ellipsoid. you should consider
        using the "Inverse Formula" as described in the section 4 of this
        document <http://www.ngs.noaa.gov/PUBS_LIB/inverse.pdf>_.


    :param from_point: a GeoPoint instance corresponding to the origin
        location.

    :param to_point: a GeoPoint corresponding to the destination location.


    :return: the number of degrees in the angle measured in a clockwise
        direction from the north line to the line passing through the
        the origin point in the direction of the destination point.
    """
    angle = abs(
        math.degrees(
            math.atan(
                (to_point.latitude - from_point.latitude)
                / (to_point.longitude - from_point.longitude))))

    if from_point.latitude > to_point.latitude:
        if from_point.longitude <= to_point.longitude:
            # North
            #   :
            #   :
            # O +------
            #   :\ /  |
            #   : \   |
            #   :  \  |
            #   :   \ |
            #   :    \|
            #   :     + P    90 + α
            #
            bearing = 90 + angle

        else:
            #     North
            #       :
            #       :
            # ------+ O
            # |  \ /:
            # |   / :
            # |  /  :
            # | /   :
            # |/    :
            # + P   :    180 + (90 - α)
            #
            bearing = 180 + (90 - angle)
    else:
        if from_point.longitude <= to_point.longitude:
            # North
            #   :
            #   :
            #   :     + P    90 - α
            #   :    /|
            #   :   / |
            #   :  /  |
            #   : /   |
            #   :/\   |
            # O +------
            #
            bearing = 90 - angle

        else:
            #       North
            #         :
            #         :
            # P +     :    270 + α
            #   |\    :
            #   | \   :
            #   |  \  :
            #   |   \ :
            #   |   /\:
            #   ------+ O
            #
            bearing = 270 + angle

    return bearing


# def check_photos_settings(file_path_names, exif_tags):
#     """
#     Check that the specified photos were taken with the same settings, as
#     referenced in their Exif metadata, such as exposure time, f-number,
#     the focal length, the ISO speed ratings, etc.
#
#     If some discrepancies are found, the function determines what the most
#     common value for a each particular Exif metadatum among all the
#     photos, and it determines which photo(s) have deviant values.
#
#     The function also checks that the specified photos have all the
#     required metadata defined.
#
#
#     :param file_path_names: A list of the path and file names of the
#         photos to check settings.
#
#     :param exif_tags: A list of Exif tags to be verified.
#
#
#     :return: A list of errors that were detected, if any.  The detected
#         errors are identified as follows::
#
#             (ErrorType.MissingMetadatum, tag, [ file_path_name, ... ])
#
#             (ErrorType.HeterogeneousMetadatumValue, tag, most_used_value,
#                 [ (file_path_name, incorrect_value), ... ])
#
#
#     :raise ValueError: If the given list contains zero or one file path
#         name only.
#     """
#     if len(file_path_names) < 2:
#         raise ValueError('The list MUST contain more than 1 photo')
#
#     # Build a dictionary of dictionaries that group photos per value for
#     # each Exif tag:
#     #   Exif tag -> Exif value -> [list of photo file path names]
#     tag_value_photos = dict()
#
#     for file_path_name in file_path_names:
#         with open(file_path_name, 'rb') as handle:
#             file_exif_tags = dict([
#                 (exif_tag.tag, exif_tag)
#                 for exif_tag in exifread.process_file(handle).itervalues()
#                 if hasattr(exif_tag, 'tag')
#             ])
#
#         for (key, tag) in file_exif_tags.items():
#             if key in exif_tags:
#                 value_photos = tag_value_photos.get(key)  # Is this tag already stored?
#                 if value_photos is None:
#                     tag_value_photos[key] = value_photos = collections.defaultdict(list)
#                 value_photos[str(tag)].append(file_path_name)
#
#     # Determine value inconsistencies for each tag accross all the
#     # specified photos.
#     errors = []
#
#     for (tag, value_photos) in tag_value_photos.items():
#         # Check that all the photos have the same value for this Exif tag, and
#         # that all the photos contain this tag.
#         if len(value_photos.keys()) == 1: # Perfect!
#             if len(value_photos.values()[0]) < len(file_path_names):
#                 errors.append((ErrorType.MissingMetaDatum, tag, set(file_path_names) - set(value_photos.values()[0])))
#
#         # All the photos are not defined with the same value for this Exif
#         # tag.  Determine the most frequently defined value of this tag
#         # across all the photos where this tag is defined.
#         else:
#             sorted_values = list(sorted(value_photos.keys(), key=lambda value: len(value_photos[value]), reverse=True))
#             most_used_value = sorted_values[0]
#             less_used_values = sorted_values[1:]
#             errors.append((ErrorType.HeterogeneousMetadatumValue, tag, most_used_value,
#                 [ (file_path_name, value)
#                   for value in less_used_values
#                       for file_path_name in value_photos[value] ]))
#
#     return errors


# def detect_markers(
#         file_path_name,
#         marker_color,
#         central_strip_width_percent,
#         max_marker_count=None,
#         expected_marker_count=None,
#         debug=False):
#     """
#     Detect the possible presence of a primary and secondary markers in the
#     specified photo.
#
#     The primary marker is expected to be in the center of the photo, while
#     the subsequent markers are expected to be below and vertically aligned
#     with this primary marker.
#
#
# :param photo: an instance containing the following members:
#        * ``photo_id``: identification of the photo.
# :param marker_color: tuple ``(R, G, B)`` describing the color of
#        the marker chroma key.
# :param central_strip_width_percent: width of the central strip of the
#        photo to analyze, expressed as a percentage relative to the
#        total width of the photo.
# :param expected_marker_count: indicate the number of markers that are
#        expected to be detected in the photo.
# :param debug: indicate whether to write on the file system, in the
#        same folder, an image file with rectangles bounding every
#        detected marker.
#
#     :return: a list composed of a first tuple ``(shift_x, shift_y)`` and
#              possible additional tuples ``(center_x, center_y, shift_angle, d_number)``
#              where:
#              * ``(shift_x, shift_y)`` represent the horizontal and
#                vertical shifts of the primary marker relative to the
#                center of the photo.
#              * ``(center_x, center_y, shift_angle, d_number)`` represent
#                the abscissa and ordinate of the subsequent marker, its
#                displacement angle in degrees relative to the primary
#                marker, and its distance in pixels to the primary marker.
#
#
# :raise ValueError: if the specified RGB components of
#            the marker color are not in the range ``[0, 255]``, or if the
#            specified width percentage of the central strip is not in the
#            range ``]0.0, 1.0]``.
#     """
#     (r, g, b) = marker_color
#     if not (0 <= r <= 255 and 0 <= g <= 255 and 0 <= b <= 255):
#         raise ValueError('The specified RGB components of the marker color are not in the range [0, 255]')
#
#     if not 0.0 < central_strip_width_percent <= 1.0:
#         raise ValueError('The specified width percentage of the central strip is not in the range ]0.0, 1.0]')
#
#     # Load and rotate the photo, if its orientation is not top left side.
#     picture = Image.open(file_path_name)
#
#     exif_tags = dict([ (exif_tag.tag, exif_tag)
#         for exif_tag in exifread.process_file(open(file_path_name, 'rb')).itervalues()
#              if hasattr(exif_tag, 'tag') ])
#
#     exif_tag_orientation = exif_tags.get(EXIF_TAG_ORIENTATION)
#     if exif_tag_orientation:
#         rotation_angle = {
#             3: 180,
#             6: 270,
#             8: 90 }.get(exif_tag_orientation.values[0])
#
#         if rotation_angle:
#             picture = picture.rotate(rotation_angle)
#
#     # Detect the central marker around the center of this photo.
#     (width, height) = picture.size
#     pixels = picture.load()
#
#     marker_area_width = int(width * central_strip_width_percent)
#     marker_area_height = int(height * central_strip_width_percent)
#
#     marker_area_x_left = (width - marker_area_width) / 2
#     marker_area_x_right = (width + marker_area_width) / 2
#     marker_area_y_top = 0 # [PATCH] Since we are using the 3-dots marker system # (height - marker_area_height) / 2
#     marker_area_y_bottom = height - 1 #(height + marker_area_height) / 2
#
#     marker_area_width = (marker_area_x_right - marker_area_x_left) + 1
#     marker_area_height = (marker_area_y_bottom - marker_area_y_top) + 1
#
#     print (marker_area_x_left, marker_area_y_top), (marker_area_x_right, marker_area_y_bottom)
#
#     marker_color_map = [ is_similar_color(pixels[x, y], marker_color)
#         for y in range(marker_area_y_top, marker_area_y_bottom + 1)
#             for x in range(marker_area_x_left, marker_area_x_right + 1) ]
#
#     # Find all the bounding boxes that encompass zone of marker color.
#     bounding_boxes = [ bounding_box for bounding_box in find_bounding_boxes(marker_color_map, marker_area_width, marker_area_height)
#         if (bounding_box.x_right - bounding_box.x_left + 1) * (bounding_box.y_bottom - bounding_box.y_top + 1) > 16 ]
#
#     if len(bounding_boxes) == 0:
#         raise Exception('No marker has been detected')
#
#     if len(bounding_boxes) > 1:
#         # Remove noises that are 1/3 smaller than the biggest marker zone
#         # detected.
#         bounding_box_surfaces = [
#             (bounding_box, (bounding_box.x_right - bounding_box.x_left + 1) * (bounding_box.y_bottom - bounding_box.y_top + 1))
#                 for bounding_box in bounding_boxes ]
#         biggest_bounding_box_surface = sorted(bounding_box_surfaces, key=lambda (bounding_box, surface): surface, reverse=True)[0][1]
#         bounding_boxes = [ bounding_box for (bounding_box, surface) in bounding_box_surfaces
#             if float(surface) / biggest_bounding_box_surface > 0.33 ]
#
#     if expected_marker_count and len(bounding_boxes) != expected_marker_count:
#         raise Exception('The number of markers that has been detected (%d) does not correspond to the number detected' % \
#             (len(bounding_boxes), expected_marker_count))
#
#     # Make sure that the bounding boxes are ordered from top to bottom.
#     bounding_boxes.sort(key=lambda bounding_box: bounding_box.y_top)
#
#     if max_marker_count and len(bounding_boxes) > max_marker_count:
#         print '[INFO] Found +%d marker(s) more than expected' % (len(bounding_boxes) - max_marker_count)
#         bounding_boxes = bounding_boxes[:max_marker_count]
#
#     # Check that all the markers are strictly inside the central strip
#     # that has been analyzed, i.e., not partially detected, except for
#     # other than the central marker and the second marker, as for zoom-in
#     # shot any other markers below might be partially in the photo.
#     for (i, bounding_box) in enumerate(bounding_boxes):
#         if bounding_box.x_left == 0 or \
#            bounding_box.x_right == marker_area_width - 1 or \
#            bounding_box.y_top == 0 or \
#            (i < 1 and  bounding_box.y_bottom == marker_area_height - 1):
#             raise Exception('A detected marker is truncated; the specified width of the central strip might be too small')
#
#     # Determine the coordinates of the central marker, and the abscissa
#     # and distance in pixels of the other markers relative to the central
#     # marker.
#     markers = []
#
#     bounding_box = bounding_boxes[0]
#     central_marker_center_x = bounding_box.x_left + (bounding_box.x_right - bounding_box.x_left + 1) / 2 + marker_area_x_left
#     central_marker_center_y = bounding_box.y_top + (bounding_box.y_bottom - bounding_box.y_top + 1) / 2 + marker_area_y_top
#     central_marker_delta_x = central_marker_center_x - width / 2
#     central_marker_delta_y = central_marker_center_y - height / 2
#
#     markers.append((central_marker_delta_x, central_marker_delta_y))
#
#     if debug:
#         print '\t- Central marker coordinates: [(%d, %d), (%d, %d)]' % (bounding_box.x_left, bounding_box.y_bottom, bounding_box.x_right, bounding_box.y_top)
#         print '\t- Central marker center: (%d, %d)' % (central_marker_center_x, central_marker_center_y)
#         print '\t- Central marker area coordinates: (%d, %d)' % (marker_area_x_left, marker_area_y_top)
#
#     for bounding_box in bounding_boxes[1:]:
#         marker_center_x = bounding_box.x_left + (bounding_box.x_right - bounding_box.x_left + 1) / 2 + marker_area_x_left
#         marker_center_y = bounding_box.y_top + (bounding_box.y_bottom - bounding_box.y_top + 1) / 2 + marker_area_y_top
#         shift_angle = math.degrees(math.atan(
#             float(marker_center_x - central_marker_center_x)
#                 / float(marker_center_y - central_marker_center_y)))
#
#         d_number = math.sqrt((marker_center_x - central_marker_center_x) ** 2
#             + (marker_center_y - central_marker_center_y) ** 2)
#
#         markers.append((marker_center_x, marker_center_y, shift_angle, d_number))
#
#         if debug:
#             print '\t- Subsequent marker coordinates: [(%d, %d), (%d, %d)]' % (bounding_box.x_left, bounding_box.y_bottom, bounding_box.x_right, bounding_box.y_top)
#             print '\t- Subsequent marker center: (%d, %d)' % (marker_center_x, marker_center_y)
#             print '\t- Subsequent marker shift angle: %f' % shift_angle
#
#     if debug:
#         draw = ImageDraw.Draw(picture)
#
#         for bounding_box in bounding_boxes:
#             for x in range(bounding_box.x_left, bounding_box.x_right + 1):
#                 pixels[x + marker_area_x_left, bounding_box.y_top + marker_area_y_top] = (255, 0, 0)
#                 pixels[x + marker_area_x_left, bounding_box.y_bottom + marker_area_y_top] = (255, 0, 0)
#             for y in range(bounding_box.y_top, bounding_box.y_bottom + 1):
#                 pixels[bounding_box.x_left + marker_area_x_left, y + marker_area_y_top] = (255, 0, 0)
#                 pixels[bounding_box.x_right + marker_area_x_left, y + marker_area_y_top] = (255, 0, 0)
#
#             marker_center_x = bounding_box.x_left + (bounding_box.x_right - bounding_box.x_left + 1) / 2 + marker_area_x_left
#             marker_center_y = bounding_box.y_top + (bounding_box.y_bottom - bounding_box.y_top + 1) / 2 + marker_area_y_top
#             for x in range(marker_center_x - 100, marker_center_x + 100 + 1):
#                 pixels[x, marker_center_y] = (255, 0, 0)
#             for y in range(marker_center_y - 100, marker_center_y + 100 + 1):
#                 pixels[marker_center_x, y] = (255, 0, 0)
#
#             draw.line((central_marker_center_x, central_marker_center_y,
#                     marker_center_x, marker_center_y), fill=(0, 0, 255))
#
#         picture.save('%s_marker.jpg' % os.path.splitext(file_path_name)[0])
#         print 'Saving debug version in %s_marker.jpg' % os.path.splitext(file_path_name)[0]
#
#     return markers
#
#
# def detect_markers_v2(file_path_name, marker_color, central_strip_width_percent,
#         max_marker_count=None,
#         expected_marker_count=None,
#         debug=False):
#     """
#     Detect the possible presence of a primary and secondary markers in the
#     specified photo.
#
#     The primary marker is expected to be in the center of the photo, while
#     the subsequent markers are expected to be below and vertically aligned
#     with this primary marker.
#
#     :param photo: an instance containing the following members:
#            * ``photo_id``: identification of the photo.
#     :param marker_color: tuple ``(R, G, B)`` describing the color of
#            the marker chroma key.
#     :param central_strip_width_percent: width of the central strip of the
#            photo to analyze, expressed as a percentage relative to the
#            total width of the photo.
#     :param expected_marker_count: indicate the number of markers that are
#            expected to be detected in the photo.
#     :param debug: indicate whether to write on the file system, in the
#            same folder, an image file with rectangles bounding every
#            detected marker.
#
#     :return: a list composed of a first tuple ``(shift_x, shift_y)`` and
#              possible additional tuples ``(center_x, center_y, shift_angle, d_number)``
#              where:
#              * ``(shift_x, shift_y)`` represent the horizontal and
#                vertical shifts of the primary marker relative to the
#                center of the photo.
#              * ``(center_x, center_y, shift_angle, d_number)`` represent
#                the abscissa and ordinate of the subsequent marker, its
#                displacement angle in degrees relative to the primary
#                marker, and its distance in pixels to the primary marker.
#
#     :raise InvalidArgumentException: if the specified RGB components of
#            the marker color are not in the range ``[0, 255]``, or if the
#            specified width percentage of the central strip is not in the
#            range ``]0.0, 1.0]``.
#     """
#     (r, g, b) = marker_color
#     if not ((r >= 0 and r <= 255) and
#             (g >= 0 and g <= 255) and
#             (b >= 0 and b <= 255)):
#         raise InvalidArgumentException('The specified RGB components of the marker color are not in the range [0, 255]')
#
#     if not (central_strip_width_percent > 0.0 and central_strip_width_percent <= 1.0):
#         raise InvalidArgumentException('The specified width percentage of the central strip is not in the range ]0.0, 1.0]')
#
#     # Load and rotate the photo, if its orientation is not top left side.
#     picture = Image.open(file_path_name)
#
#     exif_tags = dict([ (exif_tag.tag, exif_tag)
#         for exif_tag in exifread.process_file(open(file_path_name, 'rb')).itervalues()
#              if hasattr(exif_tag, 'tag') ])
#
#     exif_tag_orientation = exif_tags.get(EXIF_TAG_ORIENTATION)
#     if exif_tag_orientation:
#         rotation_angle = {
#             3L: 180,
#             6L: 270,
#             8L: 90 }.get(exif_tag_orientation.values[0])
#
#         if rotation_angle:
#             picture = picture.rotate(rotation_angle)
#
#     # Detect the central marker around the center of this photo.
#     (width, height) = picture.size
#     pixels = picture.load()
#
#     marker_area_width = int(width * central_strip_width_percent)
#     marker_area_height = int(height * central_strip_width_percent)
#
#     marker_area_x_left = (width - marker_area_width) / 2
#     marker_area_x_right = (width + marker_area_width) / 2
#     marker_area_y_top = 0 # [PATCH] Since we are using the 3-dots marker system # (height - marker_area_height) / 2
#     marker_area_y_bottom = height - 1 #(height + marker_area_height) / 2
#
#     marker_area_width = (marker_area_x_right - marker_area_x_left) + 1
#     marker_area_height = (marker_area_y_bottom - marker_area_y_top) + 1
#
#     marker_color_map = [ is_similar_color(pixels[x, y], marker_color)
#         for y in range(marker_area_y_top, marker_area_y_bottom + 1)
#             for x in range(marker_area_x_left, marker_area_x_right + 1) ]
#
#     # Find all the bounding boxes that encompass zone of marker color.
#     bounding_boxes = [ bounding_box for bounding_box in find_bounding_boxes(marker_color_map, marker_area_width, marker_area_height)
#         if (bounding_box.x_right - bounding_box.x_left + 1) * (bounding_box.y_bottom - bounding_box.y_top + 1) > 16 ]
#
#     if len(bounding_boxes) == 0:
#         raise Exception('No marker has been detected')
#
#     if len(bounding_boxes) > 1:
#         # Remove noises that are 1/3 smaller than the biggest marker zone
#         # detected.
#         bounding_box_surfaces = [
#             (bounding_box, (bounding_box.x_right - bounding_box.x_left + 1) * (bounding_box.y_bottom - bounding_box.y_top + 1))
#                 for bounding_box in bounding_boxes ]
#         biggest_bounding_box_surface = sorted(bounding_box_surfaces, key=lambda (bounding_box, surface): surface, reverse=True)[0][1]
#         bounding_boxes = [ bounding_box for (bounding_box, surface) in bounding_box_surfaces
#             if float(surface) / biggest_bounding_box_surface > 0.33 ]
#
#     if expected_marker_count and len(bounding_boxes) != expected_marker_count:
#         raise Exception('The number of markers that has been detected (%d) does not correspond to the number detected' % \
#             (len(bounding_boxes), expected_marker_count))
#
#     # Make sure that the bounding boxes are ordered from top to bottom.
#     bounding_boxes.sort(key=lambda bounding_box: bounding_box.y_top)
#
#     if max_marker_count and len(bounding_boxes) > max_marker_count:
#         print '[INFO] Found +%d marker(s) more than expected' % (len(bounding_boxes) - max_marker_count)
#         bounding_boxes = bounding_boxes[:max_marker_count]
#
#     # Check that all the markers are strictly inside the central strip
#     # that has been analyzed, i.e., not partially detected, except for
#     # other than the central marker and the second marker, as for zoom-in
#     # shot any other markers below might be partially in the photo.
#     for (i, bounding_box) in enumerate(bounding_boxes):
#         if bounding_box.x_left == 0 or \
#            bounding_box.x_right == marker_area_width - 1 or \
#            bounding_box.y_top == 0 or \
#            (i < 1 and  bounding_box.y_bottom == marker_area_height - 1):
#             raise Exception('A detected marker is truncated; the specified width of the central strip might be too small')
#
#     # Determine the coordinates of the central marker, and the abscissa
#     # and distance in pixels of the other markers relative to the central
#     # marker.
#     markers = []
#
#     bounding_box = bounding_boxes[1] # The central dot marker is the 2nd dot.
#     central_marker_center_x = bounding_box.x_left + (bounding_box.x_right - bounding_box.x_left + 1) / 2 + marker_area_x_left
#     central_marker_center_y = bounding_box.y_top + (bounding_box.y_bottom - bounding_box.y_top + 1) / 2 + marker_area_y_top
#     shift_x = central_marker_center_x - width / 2
#     shift_y = central_marker_center_y - height / 2
#
#     if debug:
#         print '\t- Central marker coordinates: [(%d, %d), (%d, %d)]' % (bounding_box.x_left, bounding_box.y_bottom, bounding_box.x_right, bounding_box.y_top)
#         print '\t- Central marker center: (%d, %d)' % (central_marker_center_x, central_marker_center_y)
#         print '\t- Central marker area coordinates: (%d, %d)' % (marker_area_x_left, marker_area_y_top)
#
#     bounding_box = bounding_boxes[0] # top marker
#     top_marker_center_x = bounding_box.x_left + (bounding_box.x_right - bounding_box.x_left + 1) / 2 + marker_area_x_left
#     top_marker_center_y = bounding_box.y_top + (bounding_box.y_bottom - bounding_box.y_top + 1) / 2 + marker_area_y_top
#
#     bounding_box = bounding_boxes[2] # bottom marker
#     bottom_marker_center_x = bounding_box.x_left + (bounding_box.x_right - bounding_box.x_left + 1) / 2 + marker_area_x_left
#     bottom_marker_center_y = bounding_box.y_top + (bounding_box.y_bottom - bounding_box.y_top + 1) / 2 + marker_area_y_top
#
#     shift_angle = math.degrees(math.atan(
#         float(bottom_marker_center_x - top_marker_center_x)
#             / float(bottom_marker_center_y - top_marker_center_y)))
#
#     d_number = math.sqrt((bottom_marker_center_x - top_marker_center_x) ** 2
#         + (bottom_marker_center_y - top_marker_center_y) ** 2)
#
#     return (shift_x, shift_y, shift_angle, d_number)
#
#
# def display_markers(marker_color_map, width, bounding_boxes):
#     """
#     Display a collection of bounding boxes.
#
#     @note: the bounding boxes MUST be ordered by offset.
#
#     :param marker_color_map: a bitmap that indicates for each pixel the
#            presence or not of a marker.
#     :param width: width of the bitmap.
#     :param boxing_boxes: a list of ``BoundingBox`` instances.
#     """
#     def get_bounding_box_index(x, y):
#         for bounding_box in bounding_boxes:
#             if x >= bounding_box.x_left and x <= bounding_box.x_right and \
#                y >= bounding_box.y_top and y <= bounding_box.y_bottom:
#                 return bounding_boxes.index(bounding_box)
#         return '.'
#
#     x_left = sorted(bounding_boxes, key=lambda bounding_box: bounding_box.x_left)[0].x_left
#     x_right = sorted(bounding_boxes, key=lambda bounding_box: bounding_box.x_right, reverse=True)[0].x_right
#     y_top = sorted(bounding_boxes, key=lambda bounding_box: bounding_box.y_top)[0].y_top
#     y_bottom = sorted(bounding_boxes, key=lambda bounding_box: bounding_box.y_bottom, reverse=True)[0].y_bottom
#
#     for y in range(y_top, y_bottom + 1):
#         print ''.join([ str(get_bounding_box_index(x, y))
#                 if marker_color_map[x + y * width] else '.'
#             for x in range(x_left, x_right + 1) ])
#
#
# def find_bounding_boxes(marker_color_map, width, height):
#     """
#     Determine bounding boxes that encloses the different elements of the
#     given map that are set to ``1``.
#
#     :param marker_color_map:  a bitmap that indicates for each pixel the
#            presence or not of a marker.
#     :param width: number of elements per row.
#     :param height: number of rows.
#
#     :return: a dictionary where the key corresponds to an offset
#              ``x + y * width`` of an element in the map and the value
#              corresponds to an instance ``BoundingBox`` representing the
#              bounding box that encloses this particular element.
#     """
#     bounding_boxes = dict()
#
#     def __replace_bounding_boxes(from_bounding_box, with_bounding_box):
#         """
#         Replace a bounding box into another, which consists in merging the
#         first bounding box into the second.
#
#         @note: this function updates the local variable ``bounding_boxes``.  It
#                uses the local variables ``width`` and ``height``.
#
#         :param from_bounding_box: the first bounding box to be replaced by the
#                second specified.
#         :param with_bounding_box: the bounding box to replace the first
#                specified.
#
#         :return: ``True`` if the function did merge the first bounding box into
#                  the second; ``False`` if no merge was actually necessary as
#                  the two specified bounding boxes are the same.
#         """
#         if from_bounding_box == with_bounding_box:
#             return False
#
#         bounding_boxes.update(dict(
#             [ (offset, with_bounding_box)
#                   for offset in range(from_bounding_box.x_left + from_bounding_box.y_top * width,
#                                       from_bounding_box.x_right + from_bounding_box.y_bottom * width + 1)
#                   if bounding_boxes.get(offset) == from_bounding_box ]))
#
#         with_bounding_box.x_left = min(from_bounding_box.x_left, with_bounding_box.x_left)
#         with_bounding_box.x_right = max(from_bounding_box.x_right, with_bounding_box.x_right)
#         with_bounding_box.y_top = min(from_bounding_box.y_top, with_bounding_box.y_top)
#         with_bounding_box.y_bottom = max(from_bounding_box.y_bottom, with_bounding_box.y_bottom)
#
#         return True
#
#     for y in range(height):
#         for x in range(width):
#             if marker_color_map[x + y * width]:
#                 # Determine whether this point belong to an existing bounding zone or
#                 # a new bounding box, based on the nearby previous analyzed points,
#                 # such as:
#                 #
#                 #     ???.
#                 #     ?#..
#                 bounding_box = None
#                 for (delta_x, delta_y) in [(-1, -1), (0, -1), (1, -1), (-1, 0)]:
#                     if x + delta_x >= 0 and y + delta_y >= 0 and x + delta_x < width and y + delta_y < height \
#                        and bounding_boxes.get((x + delta_x) + (y + delta_y) * width):
#                         bounding_box = bounding_boxes[(x + delta_x) + (y + delta_y) * width]
#                         bounding_box.x_left = min(bounding_box.x_left, x)
#                         bounding_box.x_right = max(bounding_box.x_right, x)
#                         bounding_box.y_top = min(bounding_box.y_top, y)
#                         bounding_box.y_bottom = max(bounding_box.y_bottom, y)
#                         break
#
#                 bounding_boxes[x + y * width] = bounding_box or BoundingBox(x, y)
#
#                 # Determine if this point unified two disconnected existing bounding
#                 # boxes, such as the following configuration:
#                 #
#                 #     ?.?.
#                 #     ?X..
#                 if x > 0 and y > 0  and x + 1 < width \
#                    and (bounding_boxes.get(x - 1 + y * width) or bounding_boxes.get(x - 1 + (y - 1) * width)) \
#                    and bounding_boxes.get(x + 1 + (y - 1) * width):
#                     __replace_bounding_boxes(
#                         bounding_boxes.get(x - 1 + y * width) or bounding_boxes[x - 1 + (y - 1) * width], \
#                         bounding_boxes[x + 1 + (y - 1) * width])
#
#     return list(set(bounding_boxes.values()))


def __search_exif_tag_value(exif_tags, tag_subname, optional=False, default_value=None):
    for tag_name, tag_value in exif_tags.items():
        offset = tag_name.find(tag_subname)
        if offset == -1 or \
           (offset > 0 and tag_name[offset - 1] != ' ') or \
           (offset + len(tag_subname) < len(tag_name) and tag_name[offset + len(tag_subname)] != ' '):
            continue

        return tag_value

    if not optional:
        raise KeyError('Undefined key with subname "%s"' % tag_subname)

    return default_value


def get_photo_capture_time(file, strict=True):
    """
    Return the capture time of a photo.


    :param file: An file-like object (in-memory bytes buffer) of the
        photo's image file.

    :param strict: Indicate whether the photo MUST have an Exif tag that
        indicates when the photo has been captured.

    :return: An object `ISO8601DateTime` representing the time when the
        photo has been captured.


    :raise ValueError: If the photo's image file doesn't contain an Exif
        tag that indicates when the photo has been captured.
    """
    # Retrieve tags from the Exchangeable image file format (Exif) included
    # in the photo.
    file.seek(0)
    exif_tags = exifread.process_file(file)

    # Retrieve the date and time when the original image data were
    # generated, which, for a digital still camera, is the date and time the
    # picture was taken or recorded. The format is "YYYY:MM:DD HH:MM:SS"
    # with time shown in 24-hour format, and the date and time separated by
    # one blank character (hex 20).
    #
    # When the date and time are unknown, all the character spaces except
    # colons (":") may be filled with blank characters, or else the
    # interoperability field may be filled with blank characters.
    exif_tag_value = exif_tags.get('EXIF DateTimeOriginal')
    if not exif_tag_value and strict:
        raise ValueError("the photo does not have information that indicates when the photo has been taken")

    captured_date_value, captured_time_value = exif_tag_value.printable.split(' ')
    capture_time = cast.string_to_timestamp(
        '{} {}+00'.format(
            captured_date_value.replace(':', '-'),
            captured_time_value))

    return capture_time


def get_photo_location(file):
    """
    Parse out the GPS coordinates from the Exif tags of a photo file.


    :param file: Path and file name of a photo's image, or an object
        `BytesIO` (in-memory bytes buffer) of the photo's image file, to
        retrieve the GPS coordinates of the location where the photo has
        been captured.


    :return: An object `GeoPoint` representing the geographical location
        where the photo has been captured, or `None` if the photo's image
        file doesn't contain an Exif tag that indicates where the photo
        has been captured.
    """
    # Retrieve the Exif tags from the photo's image file.
    if isinstance(file, str):
        with open(file, 'rb') as handle:
            exif_tags = exifread.process_file(handle)
    elif isinstance(file, io.BytesIO):
        file.seek(0)
        exif_tags = exifread.process_file(file)
    else:
        raise ValueError("the argument 'file' MUST be either a file path name or an object BytesIO")

    try:
        lat_dms = __search_exif_tag_value(exif_tags, 'GPSLatitude').values  # GPS GPSLatitude
        latitude = GeoPoint.convert_dms_to_dd(
            lat_dms[0].num, lat_dms[0].den,
            lat_dms[1].num, lat_dms[1].den,
            lat_dms[2].num, lat_dms[2].den)
        if __search_exif_tag_value(exif_tags, 'GPSLatitudeRef').printable == 'S':
            latitude *= -1

        long_dms = __search_exif_tag_value(exif_tags, 'GPSLongitude').values  # GPS GPSLongitude
        longitude = GeoPoint.convert_dms_to_dd(
                long_dms[0].num, long_dms[0].den,
                long_dms[1].num, long_dms[1].den,
                long_dms[2].num, long_dms[2].den)
        if __search_exif_tag_value(exif_tags, 'GPSLongitudeRef').printable == 'W':
            longitude *= -1
    except KeyError:
        return None

    try:
        acc = __search_exif_tag_value(exif_tags, 'GPSHPositioningError').values[0]
        accuracy = float(acc.num) / acc.den
    except KeyError:
        accuracy = None

    # Retrieve the altitude of the location where this photo has been
    # taken, if defined.
    try:
        alt = __search_exif_tag_value(exif_tags, 'GPSAltitude').values[0]
        altitude = float(alt.num) / alt.den
        if __search_exif_tag_value(exif_tags, 'GPS GPSAltitudeRef') == 1:
            altitude *= -1
    except KeyError:
        altitude = None

    # Retrieve the angle of the direction that the camera points to,
    # either from the EXIF GPS tag ``GPSDestBearing``, or the tag
    # ``GPSImgDirection``, in this preference order, when available.
    try:
        _bearing_tag = __search_exif_tag_value(exif_tags, 'GPSDestBearing', optional=True)
        if _bearing_tag:
            _bearing_ = _bearing_tag.values[0]
            bearing = float(_bearing_.num) / _bearing_.den
        else:
            _bearing_ = __search_exif_tag_value(exif_tags, 'GPSImgDirection').values[0]
            bearing = float(_bearing_.num) / _bearing_.den
            if __search_exif_tag_value(exif_tags, 'GPSImgDirectionRef').printable == 'T':
                bearing += 180
    except KeyError:
        bearing = None

    # Retrieve the date and the time of the location fix.
    try:
        _date_ = __search_exif_tag_value(exif_tags, 'GPSDate').values.replace(':', '-')
        _time_ = __search_exif_tag_value(exif_tags, 'GPSTimeStamp').values

        _date_time_ = '%sT%02d:%02d:%02d+00' % \
                (_date_, _time_[0].num, _time_[1].num, float(_time_[2].num) / _time_[2].den)

        fix_time = cast.string_to_timestamp(_date_time_)
    except KeyError:
        fix_time = None

    # Build a geo-point with the information collected.
    return GeoPoint(
        latitude,
        longitude,
        accuracy=accuracy,
        altitude=altitude,
        bearing=bearing,
        fix_time=fix_time)


# def is_similar_color(pixel_color, reference_color, color_distance_tolerance=20.0):
#     """"
#     Indicate whether the given pixel color matches the given color.
#
#     :param pixel_color: a tuple ``(R, G, B)`` representing the color of a
#            given pixel.
#     :param reference_color: a tuple ``(R, G, B)`` representing the
#            reference color.
#     :param color_distance_tolerance: maximum acceptable difference,
#            expressed in percentage, from a pixel  of the photo with the
#            reference color to consider this pixel color similar to the
#            latter.
#
#     :return: ``True`` if the given pixel color matches the given reference
#              color; ``False`` otherwise.
#     """
#     (R1, G1, B1) = pixel_color
#     (R2, G2, B2) = (15, 15, 15) #reference_color
#     diff = (abs(R1 - R2) + abs(G1 - G2) + abs(B1 - B2)) / 3.0
#     return diff <= color_distance_tolerance

#     pixel_color = convert_color(AdobeRGBColor(R, G, B), LabColor)
#     (R, G, B) = reference_color
#     reference_color = convert_color(AdobeRGBColor(R, G, B), LabColor)
#     return abs(delta_e_cie1976(pixel_color, reference_color)) < color_distance_tolerance
