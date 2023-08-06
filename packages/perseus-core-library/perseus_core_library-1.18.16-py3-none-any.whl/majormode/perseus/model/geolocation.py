# -*- coding: utf-8 -*-
#
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

import math

from majormode.perseus.model.obj import Serializable


class BoundingBox:
    """
    Represent a rectangle in geographical coordinates.
    """
    def __init__(self, southwest, northeast):
        """
        Build an instance `BoundinxBox` from the points at its south-west
        and north-east corners.


        :param southwest: an instance `GeoPoint` corresponding to the south-
            west corner of the bounding box.

        :param northeast: an instance `GeoPoint` corresponding to the north-
            east corner of the bounding box.
        """
        self.__southwest = southwest
        self.__northeast = northeast

    @property
    def northeast(self):
        return self.__northeast

    @property
    def southwest(self):
        return self.__southwest


class GeoPoint:
    """
    Represent the geographic coordinates of a location as reported by a
    location provider, such as Global Positioning System (GPS) or an
    Hybrid Positioning System based on wireless network.

    For more information about a variety of calculations for latitude/
    longitude points, with the formula and code fragments for implementing
    them, we recommend the following link:

    * Calculate distance, bearing and more between Latitude/Longitude
      points; Movable Type Scripts;
      http://www.movable-type.co.uk/scripts/latlong.html
    """

    # Code names of the supported location providers.
    LOCATION_PROVIDER_NAMES = ['gps', 'network', 'fused']

    # Radius of the Earth expressed in meters.
    EARTH_RADIUS_METERS = 6371009

    def __eq__(self, other):
        """
        Indicate whether this location corresponds to the specified other
        location.


        :param other: an other instance `GeoPoint`.


        :return: `True` if these two instance represents the same geographic
            location, at least the same longitude and latitude, and the same
            altitude if defined in both instances.
        """
        if self.__longitude != other.__longitude or self.__latitude != other.__latitude:
            return False

        return self.__altitude is None or other.__altitude is None or \
            self.__altitude == other.__altitude

    def __hash__(self):
        return hash(str(self))

    def __init__(
            self,
            latitude,
            longitude,
            altitude=None,
            accuracy=None,
            bearing=None,
            fix_time=None,
            provider=None,
            speed=None):
        """
        Build a `GeoPoint` instance.


        :param latitude: Latitude-angular distance, expressed in decimal
            degrees (WGS84 datum), measured from the center of the Earth, of a
            point north or south of the Equator.

        :param longitude: Longitude-angular distance, expressed in decimal
            degrees (WGS84 datum), measured from the center of the Earth, of a
            point east or west of the Prime Meridian.

        :param altitude: Altitude in meters of the location.

        :param accuracy: Accuracy in meters of the position.

        :param bearing: Bearing in degrees.  Bearing is the horizontal
            direction of travel of the device, and is not related to the
            device orientation.  It is guaranteed to be in the range
            `[0.0, 360.0]`, or `null` if this device does not have a
            bearing.

        :param fix_time: Time when the fix of the location has been
            calculated.

        :param provider: Code name of the location provider that reported the
            geographical location:

            * `gps`: Indicate that the location has been provided by a
              Global Positioning System (GPS).

            * `network`: Indicate that the location has been provided by an
              hybrid positioning system, which uses different positioning
              technologies, such as Global Positioning System (GPS), Wi-Fi
              hotspots, cell tower signals.

        :param speed: Speed in meters/second over the ground, or `null` if
            this location does not have a speed.


        @raise ValueError: If some arguments are missing or of a wrong format
            or value.
        """
        if latitude is None or longitude is None:
            raise ValueError("Undefined latitude or longitude")

        if provider is not None:
            provider = provider.strip().lower()
            if provider not in GeoPoint.LOCATION_PROVIDER_NAMES:
                raise ValueError(f'Unsupported location provider "{provider}"')

        self.__latitude = float(latitude)
        self.__longitude = float(longitude)
        self.__altitude = altitude and float(altitude)
        self.__accuracy = accuracy and float(accuracy)
        self.__bearing = bearing and float(bearing)
        self.__speed = speed and float(speed)
        self.__fix_time = fix_time
        self.__provider = provider

    def __repr__(self):
        optional_arguments = (
            ('altitude', self.__altitude),
            ('accuracy', self.__accuracy),
            ('bearing', self.__bearing),
            ('fix_time', self.__fix_time and f"'{str(self.__fix_time)}'"),
            ('provider', self.__provider and f"'{self.__provider}'"),
            ('speed', self.__speed)
        )

        optional_arguments_str = ', '.join([
            f'{name}={value}'
            for name, value in optional_arguments
            if value is not None
        ])

        return f'{self.__class__.__name__}({self.__latitude}, {self.__longitude}' \
            f', {optional_arguments_str}' if optional_arguments_str else '' \
            ')'

    def __str__(self):
        return f'({self.__latitude}, {self.__longitude})' if not self.__altitude \
            else f'({self.__latitude}, {self.__longitude}, {self.__altitude})'

    @staticmethod
    def objectify_attributes(o):
        """
        Replace in place the geolocation attributes of an object to an
        attribute `GeoPoint` of this object grouping all these attributes.


        :param o: An object.  This object MUST at least contains the
            attributes `latitude` and `longitude`.
        """
        if o.longitude is None or o.latitude is None:
            return

        o.location = GeoPoint(
            o.latitude,
            o.longitude,
            altitude=getattr(o, 'altitude', None),
            accuracy=getattr(o, 'accuracy', None),
            bearing=getattr(o, 'bearing', None),
            fix_time=getattr(o, 'fix_time', None),
            provider=getattr(o, 'provider', None),
            speed=getattr(o, 'speed', None))

        del o.latitude
        del o.longitude
        if hasattr(o, 'altitude'):
            del o.altitude
        if hasattr(o, 'accuracy'):
            del o.accuracy
        if hasattr(o, 'bearing'):
            del o.bearing
        if hasattr(o, 'fix_time'):
            del o.fix_time
        if hasattr(o, 'provider'):
            del o.provider
        if hasattr(o, 'speed'):
            del o.speed

    def equirectangular_distance(self, other):
        """
        Return the approximate equirectangular when the location is close to
        the center of the cluster.

        For small distances, Pythagoras’ theorem can be used on an
        equirectangular projection.

        Equirectangular formula::

            x = Δλ ⋅ cos φm
            y = Δφ
            d = R ⋅ √(x² + y)²

        It will always over-estimate compared to the real Haversine distance.
        For example it will add no more than 0.05382 % to the real distance if
        the delta latitude or longitude between your two points does not
        exceed 4 decimal degrees.

        The standard formula (Haversine) is the exact one (that is, it works
        for any couple of longitude/latitude on earth) but is much slower as
        it needs 7 trigonometric and 2 square roots.  If your couple of points
        are not too far apart, and absolute precision is not paramount, you
        can use this approximate version (Equirectangular), which is much
        faster as it uses only one trigonometric and one square root:

        ```python
        Python 2.7.6rc1 (v2.7.6rc1:4913d0e9be30+, Oct 27 2013, 20:52:11)
        [GCC 4.2.1 (Apple Inc. build 5666) (dot 3)] on darwin
        Type "help", "copyright", "credits" or "license" for more information.
        >>> from majormode.perseus.model.geolocation import GeoPoint
        >>> import time
        >>>
        >>> source = GeoPoint(106.739036, 10.797977)
        >>> destination = GeoPoint(106.743325, 10.800195)
        >>>
        >>> start_time = time.time()
        >>> for i in xrange(1000000):
        ...     d = source.great_circle_distance(destination)
        ...
        >>> print time.time() - start_time
        5.62202811241
        >>> print d
        529.424701041
        >>>
        >>> start_time = time.time()
        >>> for i in xrange(1000000):
        ...     d = source.equirectangular_distance(destination)
        ...
        >>> print time.time() - start_time
        2.78262710571
        >>> print d
        529.424701073
            >>>
        ```


        :param other: a `GeoPoint` instance.


        :return: the great-circle distance, in meters, between this geographic
            coordinates to the specified other point.
        """
        x = math.radians(other.__longitude - self.__longitude) \
            * math.cos(math.radians(other.__latitude + self.__latitude) / 2)
        y = math.radians(other.__latitude - self.__latitude)

        return math.sqrt(x * x + y * y) * GeoPoint.EARTH_RADIUS_METERS

    def great_circle_distance(self, other):
        """
        Return the great-circle distance, in meters, from this geographic
        coordinates to the specified other point, i.e., the shortest distance
        over the earth’s surface, ‘as-the-crow-flies’ distance between the
        points, ignoring any natural elevations of the ground.

        Haversine formula::

          R = earth’s radius (mean radius = 6,371km)
          Δlat = lat2 − lat1
          Δlong = long2 − long1
          a = sin²(Δlat / 2) + cos(lat1).cos(lat2).sin²(Δlong/2)
          c = 2.atan2(√a, √(1−a))
          d = R.c


        :param other: a `GeoPoint` instance.


        :return: the great-circle distance, in meters, between this geographic
            coordinates to the specified other point.
        """
        distance_latitude = math.radians(abs(self.__latitude - other.__latitude))
        distance_longitude = math.radians(abs(self.__longitude - other.__longitude))

        a = math.sin(distance_latitude / 2) * math.sin(distance_latitude / 2) + \
            math.cos(math.radians(self.__latitude)) \
            * math.cos(math.radians(other.__latitude)) \
            * math.sin(distance_longitude / 2) \
            * math.sin(distance_longitude / 2)

        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

        return GeoPoint.EARTH_RADIUS_METERS * c

    @staticmethod
    def from_json(payload):
        """
        Build a `GeoPoint` instance from the specified JSON object.


        :param payload: JSON representation of a geographic location::

                {
                  "accuracy": decimal,
                  "altitude": decimal,
                  "bearing": decimal,
                  "longitude": decimal,
                  "latitude": decimal,
                  "provider": string,
                  "speed": decimal
                }

            where:

            * `accuracy`: accuracy of the position in meters.

            * `altitude`: altitude in meters of the location.

            * `bearing`: bearing in degrees.  Bearing is the horizontal direction
              of travel of the device, and is not related to the device orientation.
              It is guaranteed to be in the range `[0.0, 360.0]`, or `null` if
              this device does not have a bearing.

            * `latitude`: latitude-angular distance, expressed in decimal degrees
              (WGS84 datum), measured from the center of the Earth, of a point north
              or south of the Equator.

            * `longitude`: longitude-angular distance, expressed in decimal
              degrees (WGS84 datum), measured from the center of the Earth, of a
              point east or west of the Prime Meridian.

            * `provider`: code name of the location provider that reported the
              geographical location:

              * `gps`: indicate that the location has been provided by a Global
                Positioning System (GPS).

              * `network`: indicate that the location has been provided by an hybrid
                positioning system, which uses different positioning technologies,
                such as Global Positioning System (GPS), Wi-Fi hotspots, cell tower
                signals.

            * `speed`: speed in meters/second over the ground, or `None` if this
              location does not have a speed.


        :return: a `GeoPoint` instance or `None` if the JSON payload is nil.
        """
        return payload and GeoPoint(
            payload['latitude'],
            payload['longitude'],
            accuracy=payload.get('accuracy'),
            altitude=payload.get('altitude'),
            bearing=payload.get('bearing'),
            fix_time=payload.get('fix_time'),
            provider=payload.get('provider'),
            speed=payload.get('speed'))

    @staticmethod
    def convert_dd_to_dms_string(dd):
        """
        Convert decimal degrees (DD), which expresses latitude and longitude
        geographic coordinates as decimal fraction, to a degrees, minutes, and
        seconds (DMS) string representation, such as 38° 53' 23" N.


        :param dd: decimal degrees of the geographic coordinates of a location
            on the Earth.


        :return: degrees, minutes, and seconds (DMS) string representation of
            this location.
        """
        degrees = int(dd)
        minutes = (dd - degrees) * 60
        seconds = int((minutes - int(minutes)) * 60)
        return f"{degrees}° {int(minutes)}' {int(seconds)}\""

    @staticmethod
    def convert_dms_to_dd(
            degree_num, degree_den,
            minute_num, minute_den,
            second_num, second_den):
        """
        Convert the degree/minute/Second formatted GPS data to decimal
        degrees.


        :param degree_num: the numerator of the degree object.

        :param degree_den: the denominator of the degree object.

        :param minute_num: the numerator of the minute object.

        :param minute_den: the denominator of the minute object.

        :param second_num: the numerator of the second object.

        :param second_den: the denominator of the second object.


        :return: a decimal degree.
        """
        degree = float(degree_num) / float(degree_den)
        minute = float(minute_num) / float(minute_den) / 60
        second = float(second_num) / float(second_den) / 3600
        return degree + minute + second

    @staticmethod
    def convert_dms_string_to_dd(dms):
        """
        Convert a degrees, minutes, and seconds (DMS) string representation,
        such as 38° 53' 23" N, to a decimal degrees (DD), which expresses
        latitude and longitude geographic coordinates as decimal fraction.


        :param dms: degrees, minutes, and seconds (DMS) string representation
            of a location on the Earth.


        :return: decimal degrees of the geographic coordinates of a location.
        """
        degree_mark_offset = dms.find(u'°')
        degrees = float(dms[:degree_mark_offset].strip())
        minute_mark_offset = dms.find(u"'")
        minutes = float(dms[degree_mark_offset + 1:minute_mark_offset].strip())
        second_mark_offset = dms.find(u'"')
        seconds = float(dms[minute_mark_offset + 1:second_mark_offset].strip())
        return degrees + (minutes / 60) + (seconds / 3600)

    @staticmethod
    def convert_meter_to_dd(distance, latitude):
        """
        Convert distances expressed in meters to degrees.  A degree of
        longitude at the equator is 111.2 kilometers.  A minute is 1853
        meters.  A second is 30.9 meters.  For other latitudes multiply by
        cos(lat).  Distances for degrees, minutes and seconds in latitude
        are very similar and differ very slightly with latitude.


        :param distance: distance expressed in meters.

        :param latitude: latitude, expressed in degrees, of a point at the
            surface of the Earth.


        :return: approximation of the conversion of this distance in
            degrees for the specified latitude.
        """
        return distance * math.cos(math.radians(latitude)) / 111200

    @property
    def accuracy(self):
        return self.__accuracy

    @property
    def altitude(self):
        return self.__altitude

    @property
    def bearing(self):
        return self.__bearing

    @property
    def fix_time(self):
        return self.__fix_time

    @property
    def latitude(self):
        return self.__latitude

    @property
    def longitude(self):
        return self.__longitude

    @property
    def provider(self):
        return self.__provider

    @property
    def speed(self):
        return self.__speed


class WeightedGeoPointCluster:
    """
    Cluster of geographical points weighted with their accuracy.
    """
    def __calculate_center(self):
        """
        Determine the center of the cluster depending on the current list of
        geographical points and their respective accuracy .

        The more accurate a geographical point is, the more the center of the
        cluster moves toward this point.


        :return: An object `GeoPoint` to be used as the center of this cluster.
        """
        points = [
            (point.latitude, point.longitude, point.accuracy)
            for point in self.__points
        ]

        latitudes, longitudes, accuracies = list(zip(*points))
        coefficients = [1 / accuracy for accuracy in accuracies]

        coefficients_sum = sum(coefficients)

        center_latitude = sum([latitudes[i] * coefficients[i] for i in range(len(latitudes))]) / coefficients_sum
        center_longitude = sum([longitudes[i] * coefficients[i] for i in range(len(longitudes))]) / coefficients_sum
        center_accuracy = len(coefficients) / coefficients_sum

        return GeoPoint(center_latitude, center_longitude, accuracy=center_accuracy)

    def __init__(
            self,
            points=None):
        """
        Build a cluster of geographical points.


        :param points: A list of objects `GeoPoints`.
        """
        self.__points = points or []
        self.__is_dirty = bool(points)  # points is None or len(points) == 0
        self.__center = None

    def add(self, point):
        """
        Add a geographical point to the cluster.


        :param point: An object `GeoPoint`.


        :return: This object `WeightedGeoPointCluster`.
        """
        if not isinstance(point, GeoPoint):
            raise ValueError("The argument `point` must be an object `GeoPoint`")

        self.__points.append(point)
        self.__is_dirty = True
        return self

    @property
    def center(self):
        """
        Return the center of this cluster.


        :return: An object `GeoPoint` corresponding to the center of this
            cluster.
        """
        if self.__is_dirty:
            self.__center = self.__calculate_center()
            self.__is_dirty = False

        return self.__center

