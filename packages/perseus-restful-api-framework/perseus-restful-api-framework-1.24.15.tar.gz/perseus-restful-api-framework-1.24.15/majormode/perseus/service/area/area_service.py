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

import re
import unidecode

from majormode.perseus.constant.area import AREA_LEVEL_COUNTRY
from majormode.perseus.constant.area import AREA_LEVEL_WARD
from majormode.perseus.model.label import Label
from majormode.perseus.model.geolocation import BoundingBox
from majormode.perseus.model.geolocation import GeoPoint
from majormode.perseus.model.locale import DEFAULT_LOCALE
from majormode.perseus.model.locale import Locale
from majormode.perseus.service.base_rdbms_service import BaseRdbmsService
from majormode.perseus.utils import cast


class AreaService(BaseRdbmsService):
    DEFAULT_DEPTH = 1
    MAXIMUM_DEPTH = 3

    # Define the regular expression that matches a word.
    REGEX_PATTERN_WORD = re.compile('[\W_]+')


    @staticmethod
    def _cleanse_keywords(keywords, keyword_minimal_length=2):
        """
        Remove any punctuation character from the specified list of keywords,
        remove any double or more space character and represent Unicode
        characters in ASCII.


        :param keywords: a list of keywords strip out any punctuation characters.


        :return: the set of keywords cleansed from any special Unicode
            accentuated character, punctuation character, and double space
            character.
        """
        # Normalize the given keywords and split them into sub-keywords if
        # needed.  For instance:
        #
        #   [ u'Saint-Élie-de-Caxton', u'Québec' ]
        #
        # becomes:
        #
        #   [ [ u'saint', u'elie', u'de', u'caxton' ], [ u'Québec' ]]
        sub_keywords_list = [
            re.sub(  # 3. Remove any double space character
                r'\s{2,}', ' ',
                re.sub(  # 2. Remove any punctuation character
                    r"""[.,\\/#!$%\^&*;:{}=\-_`~()<>"']""",
                    ' ',
                    unidecode.unidecode(keyword).lower()))  # 1. Convert to ASCII lowercased characters
            .split(' ')  # 4. Split sub-keywords
            for keyword in keywords]

        # Merge all the sub-keywords in a single list, filtering out
        # sub-keywords of less than 2 characters.
        return set([
            sub_keyword
            for sub_keywords in sub_keywords_list
            for sub_keyword in sub_keywords
            if len(sub_keyword) >= keyword_minimal_length])

    def find_areas_with_ip_address(
            self,
            ip_address,
            connection=None,
            lowest_area_level=5,
            highest_area_level=0,
            locale=DEFAULT_LOCALE):
        """
        Return information of a list of areas that encompass the IP address.


        :param ip_address: a dotted-decimal notation of an IPv4 address,
            consisting of four decimal numbers, each ranging from ``0`` to
            ``255``, separated by dots.

        :param connection: A `RdbmsConnection` instance to be used supporting
            the Python clause `with ...:`.

        :param lowest_area_level: the level of the smallest administrative
            area to start with.

            As a reminder, for clarity and convenience the standard neutral
            reference for the largest administrative subdivision of a country
            is called the "first-level administrative division" or "first
            administrative level". Next smaller is called "second-level
            administrative division" or "second administrative level", etc.

            Note: the smallest the area, the fastest the function returns
            result.

        :param highest_area_level: the level of the largest administrative
            area to finish with.

        :param locale: an instance ``Locale`` representing the locale to
            return the text information of each administrative areas found.


        :return: a list of instances containing the following members:

            * ``area_id`` (required): identification of an administrative
              subdivision.

            * ``parent_area_id`` (optional): identification of the parent
              administrative subdivision, if any.

            * ``area_type`` (required): name of the type of the administrative
              subdivision.  This name can have been localized.  There is no naming
              convention as each country might have its own administrative
              subdivision classification.

            * ``area_level`` (required): administrative level of this area.  For
              clarity and convenience the standard neutral reference for the largest
              administrative subdivision of a country is called the "first-level
              administrative division" or "first administrative level".  Next
              smaller is called "second-level administrative division" or "second
              administrative level".

            * ``label`` (required): an instance ``Label`` of the name of the
              administrative subdivision written in a locale closest to the one
              specified.
        """
        with self.acquire_rdbms_connection(auto_commit=False, connection=connection) as connection:
            cursor = connection.execute(
                """
                SELECT 
                    area_id,
                    parent_area_id,
                    ST_X(centroid) AS longitude,
                    ST_Y(centroid) AS latitude,
                    ST_XMin(bounding_box) AS x_min,
                    ST_YMin(bounding_box) AS y_min,
                    ST_XMax(bounding_box) AS x_max,
                    ST_YMax(bounding_box) AS y_max,
                    area_type,
                    area_level,
                    content,
                    get_area_path(area_id, p_locale:=%(locale)s) AS path,
                    locale
                  FROM 
                    find_areas_with_ip_address(
                      %(ip_address)s,
                      p_lowest_area_level:=%(lowest_area_level)s,
                      p_highest_area_level:=%(highest_area_level)s,
                      p_locale:=%(locale)s)
                """,
                {
                    'highest_area_level': highest_area_level,
                    'ip_address': '.'.join([str(byte) for byte in ip_address]),
                    'locale': locale,
                    'lowest_area_level': lowest_area_level
                })

            areas = [
                row.get_object({
                    'area_id': cast.string_to_uuid,
                    'locale': Locale,
                    'parent_area_id': cast.string_to_uuid
                })
                for row in cursor.fetch_all()
            ]

            for area in areas:
                area.label = Label(area.content, area.locale)
                area.path = Label(area.path, area.locale)

                del area.content, area.path, area.locale

                area.centroid = GeoPoint(area.latitude, area.longitude)
                del area.longitude, area.latitude

                area.bounding_box = BoundingBox(
                    GeoPoint(area.y_min, area.x_min),
                    GeoPoint(area.y_max, area.x_max))
                del area.x_min, area.y_min, area.x_max, area.y_max

            return areas

    def find_areas_with_location(
            self,
            location,
            connection=None,
            lowest_area_level=AREA_LEVEL_WARD,
            highest_area_level=AREA_LEVEL_COUNTRY,
            locale=None):
        with self.acquire_rdbms_connection(auto_commit=False, connection=connection) as connection:
            cursor = connection.execute(
                """
                SELECT 
                    area_id,
                    parent_area_id,
                    ST_X(centroid) AS longitude,
                    ST_Y(centroid) AS latitude,
                    ST_XMin(bounding_box) AS x_min,
                    ST_YMin(bounding_box) AS y_min,
                    ST_XMax(bounding_box) AS x_max,
                    ST_YMax(bounding_box) AS y_max,
                    area_type,
                    area_level,
                    content,
                    get_area_path(area_id, p_locale:=%(locale)s) AS path,
                    locale
                  FROM 
                    find_areas_with_location(
                      ST_SetSRID(ST_MakePoint(%(longitude)s, %(latitude)s), 4326),
                      p_lowest_area_level:=%(lowest_area_level)s,
                      p_highest_area_level:=%(highest_area_level)s,
                      p_locale:=%(locale)s)
                """,
                {
                    'highest_area_level': highest_area_level,
                    'latitude': location.latitude,
                    'locale': locale,
                    'longitude': location.longitude,
                    'lowest_area_level': lowest_area_level
                })

            areas = [
                row.get_object({
                    'area_id': cast.string_to_uuid,
                    'locale': Locale,
                    'parent_area_id': cast.string_to_uuid
                })
                for row in cursor.fetch_all()
            ]

            for area in areas:
                area.label = Label(area.content, area.locale)
                area.path = Label(area.path, area.locale)

                del area.content, area.path, area.locale

                area.centroid = GeoPoint(area.latitude, area.longitude)
                del area.longitude, area.latitude

                area.bounding_box = BoundingBox(
                    GeoPoint(area.y_min, area.x_min),
                    GeoPoint(area.y_max, area.x_max))
                del area.x_min, area.y_min, area.x_max, area.y_max

            return areas

    def find_location_with_ip_address(
            self,
            ip_address,
            connection=None):
        """
        Return the location based on the specified IP address.


        :param ip_address: A dotted-decimal notation of an IPv4 address,
            consisting of four decimal numbers, each ranging from ``0`` to
            ``255``, separated by dots.

        :param connection: A `RdbmsConnection` instance to be used supporting
            the Python clause `with ...:`.


        :return: An instance ``GeoPoint`` corresponding to the location
            associated to the specified IP address.
        """
        with self.acquire_rdbms_connection(auto_commit=False, connection=connection) as connection:
            cursor = connection.execute(
                """
                SELECT
                    ST_X(location) AS longitude,
                    ST_Y(location) AS latitude,
                    ST_Z(location) AS altitude,
                    accuracy
                  FROM
                    geoip_block
                  WHERE
                    network >> %(ip_address)s
                """,
                {
                    'ip_address': '.'.join([str(byte) for byte in ip_address])
                })

            row = cursor.fetch_one()
            location = row and row.get_object()

            return location and GeoPoint(
                location.latitude,
                location.longitude,
                altitude=location.altitude,
                accuracy=location.accuracy)

    def get_area_boundaries(
            self,
            area_id,
            connection=None,
            sync_time=None):
        """
        Return the boundaries of the specified geographic area.


        :param area_id: Identification of the geographic area to return its
            boundaries.

        :param connection: A `RdbmsConnection` instance to be used supporting
            the Python clause `with ...:`.

        :param sync_time: Time of the latest version of the coordinates of the
            boundaries of this geographic area cached by the caller.  If this
            time corresponds to the most recent coordinates of this geographic
            area's boundaries, the request returns `None`, otherwise it
            returns the last version of these coordinates.  If this parameter
            is not provided, the function always returns the most recent
            version of the coordinates of this geographic area's boundaries.


        :return: a list of the coordinates of the boundaries of this
            geographic area:

            * ``[ (lng, lat), ... ]`` for a polygon

            * ``[ [ (lng, lat), ... ], ... ]`` for a multipolygon

            The function returns ``None`` if no geographic area corresponds to
            the specified identification, or if the caller passed the argument
            ``sync_time`` that indicates the caller already cached the most
            recent version of the coordinates of this geographic area's
            boundaries.
        """
        with self.acquire_rdbms_connection(auto_commit=False, connection=connection) as connection:
            cursor = connection.execute(
                """
                SELECT
                    ST_AsText(_boundaries) AS boundaries
                  FROM
                    area
                  WHERE
                    area_id = %(area_id)s
                    AND (%(sync_time)s IS NULL OR %(sync_time)s < update_time)
                """,
                {
                    'area_id': area_id,
                    'sync_time': sync_time
                })
            row = cursor.fetch_one()
            if row is None:
                return None

            boundaries = row.get_value('boundaries')
            if boundaries == 'POLYGON EMPTY' or boundaries == 'MULTIPOLYGON EMPTY':
                return

            # MULTIPOLYGON(((lng lat, ...)), ((lng lat, ...)), ...)
            if boundaries.startswith('MULTIPOLYGON'):
                return [
                    [
                        (float(x), float(y)) for (x, y) in [
                            coordinates.split(' ')
                            for coordinates in polygon.split(',')
                        ]
                    ]
                    for polygon in boundaries[len('MULTIPOLYGON((('):-3].split(')),((')
                ]

            # POLYGON((lng lat, ...))
            elif boundaries.startswith('POLYGON'):
                return [
                    (float(x), float(y)) for (x, y) in [
                        coordinates.split(' ')
                        for coordinates in boundaries[len('POLYGON(('):-2].split(',')
                    ]
                ]

            else:
                raise ValueError(
                    "the boundaries of this area are stored in a wrong format",
                    payload={'area_id': area_id})

    def get_area_extended_id(self, area_id, connection=None):
        """

        :param area_id:

        :param connection: A `RdbmsConnection` instance to be used supporting
            the Python clause `with ...:`.


        :return:
        """
        with self.acquire_rdbms_connection(auto_commit=False, connection=connection) as connection:
            cursor = connection.execute(
                """
                SELECT 
                    get_area_extended_id(%(area_id)s) AS area_extended_id
                """,
                {
                    'area_id': area_id
                })
            row = cursor.fetch_one()
            return row and row.get_value('area_extended_id')

    def get_areas(
            self,
            area_ids,
            connection=None,
            locale=DEFAULT_LOCALE):
        """
        Return the specified geographic areas worth of extended information.

        If a requested geographic area is unknown, then that area will not be
        returned in the results list.


        :param area_ids: a list of identifications of geographic areas.

        :param connection: A `RdbmsConnection` instance to be used supporting
            the Python clause `with ...:`.

        :param locale: a ``Locale`` instance that specifies the locale of the
            area labels to be returned.


        :return: a list of instances containing the following members:

            * ``area_id`` (required): identification of the geographic area.

            * ``area_type`` (required): symbolic name of the type of the geographic
              area.

            * ``label`` (required): an instance ``Label`` corresponding to the name
              of this geographic area written in the closest locale to the one
              specified.

            * ``area_level`` (required): administrative level of this geographic
              area.  For clarity and convenience the standard neutral reference for
              the largest administrative subdivision of a country is called the
              "first-level administrative division" or "first administrative level".
              Next smaller is called "second-level administrative division" or
              "second administrative level".

            * ``parent_area_id`` (optional): identification of the parent geographic
              area.
        """
        area_ids = [area_ids] if not isinstance(area_ids, (list, set, tuple)) else list(set(area_ids))

        with self.acquire_rdbms_connection(auto_commit=False, connection=connection) as connection:
            cursor = connection.execute(
                """
                SELECT 
                    area_id,
                    area_type,
                    area_level,
                    (get_area_label(area_id, %(locale)s)).*,
                    get_area_path(area_id, p_locale:=%(locale)s) AS path,
                    ST_X(centroid) AS longitude,
                    ST_Y(centroid) AS latitude,
                    ST_XMin(bounding_box) AS x_min,
                    ST_YMin(bounding_box) AS y_min,
                    ST_XMax(bounding_box) AS x_max,
                    ST_YMax(bounding_box) AS y_max,
                    parent_area_id
                  FROM
                    area
                  WHERE
                    area_id IN (%(area_ids)s)
                """,
                {
                    'area_ids': area_ids[:self.MAXIMUM_LIMIT],
                    'locale': locale
                })

            areas = [
                row.get_object({
                    'area_id': cast.string_to_uuid,
                    'parent_area_id': cast.string_to_uuid })
                for row in cursor.fetch_all()
            ]

            for area in areas:
                area.label = Label(area.content, area.locale)
                area.path = Label(area.path, area.locale)
                del area.content, area.locale

                area.centroid = GeoPoint(area.latitude, area.longitude)
                del area.longitude, area.latitude

                area.bounding_box = BoundingBox(
                    GeoPoint(area.y_min, area.x_min),
                    GeoPoint(area.y_max, area.x_max))

                del area.x_min, area.y_min, area.x_max, area.y_max

            return areas

    def get_areas_in_bounding_box(
            self,
            bounding_box,
            connection=None,
            locale=DEFAULT_LOCALE):
        """
        Return the geographic areas that intersect the specified bounding box.


        :param bounding_box: a tuple of two instances ``GeoPoint`` that
            represent the north-east corner and the south-west corners of the
            rectangle area to search places in.

        :param connection: A `RdbmsConnection` instance to be used supporting
            the Python clause `with ...:`.

        :param locale: a ``Locale`` instance that specifies the locale of the
             area labels to be returned.


        :return: a list of instances containing the following attributes:

            * ``area_id``: identification of the geographic area.

            * ``area_type``: symbolic name of the type of the geographic area.

            * ``area_label``: label in the specified locale, or the closest locale
              if no label is defined for this particular locale, which is, at
              least, English by default.

            * ``parent_area_id``: identification of the parent geographic area or
              ``None`` if none defined.
        """
        (southwest_location, northeast_location) = bounding_box

        with self.acquire_rdbms_connection(auto_commit=False, connection=connection) as connection:
            cursor = connection.execute(
                """
                SELECT 
                    area_id,
                    parent_area_id,
                    ST_X(centroid) AS longitude,
                    ST_Y(centroid) AS latitude,
                    ST_XMin(bounding_box) AS x_min,
                    ST_YMin(bounding_box) AS y_min,
                    ST_XMax(bounding_box) AS x_max,
                    ST_YMax(bounding_box) AS y_max,
                    area_type,
                    area_level,
                    content,
                    get_area_path(area_id, p_locale:=%(locale)s) AS path,
                    locale
                  FROM
                    find_areas_in_bounding_box(
                        ST_MakePolygon(ST_GeomFromText(%(bounding_box)s, 4326)),
                        p_locale:=%(locale)s)
                """,
                {
                    'bounding_box': 'LINESTRING({} {},{} {},{} {},{} {},{} {})'.format(
                        southwest_location.longitude, northeast_location.latitude,
                        northeast_location.longitude, northeast_location.latitude,
                        northeast_location.longitude, southwest_location.latitude,
                        southwest_location.longitude, southwest_location.latitude,
                        southwest_location.longitude, northeast_location.latitude),
                    'locale': locale
                })

            areas = [
                row.get_object({
                    'area_id': cast.string_to_uuid,
                    'parent_area_id': cast.string_to_uuid })
                for row in cursor.fetch_all()
            ]

            for area in areas:
                area.label = Label(area.content, area.locale)
                area.path = Label(area.path, area.locale)
                del area.content, area.locale

                area.centroid = GeoPoint(area.latitude, area.longitude)
                del area.longitude, area.latitude

                area.bounding_box = BoundingBox(
                    GeoPoint(area.y_min, area.x_min),
                    GeoPoint(area.y_max, area.x_max))

                del area.x_min, area.y_min, area.x_max, area.y_max

            return areas

    def get_areas_by_ip_address(
            self,
            ip_address,
            connection=None,
            lowest_area_level=AREA_LEVEL_WARD,
            highest_area_level=AREA_LEVEL_COUNTRY,
            minimal_area_surface=None,
            locale=DEFAULT_LOCALE):
        """
        Return the geographic areas that encompass the location determined
        from the specified IP address.


        :param ip_address: a dotted-decimal notation of an IPv4 address,
            consisting of four decimal numbers, each ranging from ``0`` to
            ``255``, separated by dots.

        :param connection: A `RdbmsConnection` instance to be used supporting
            the Python clause `with ...:`.

        :param lowest_area_level: the level of the smallest administrative
            area to start with.

            As a reminder, for clarity and convenience the standard neutral
            reference for the largest administrative subdivision of a country
            is called the "first-level administrative division" or "first
            administrative level". Next smaller is called "second-level
            administrative division" or "second administrative level", etc.

            Note: the smallest the area, the fastest the function returns
            result.

        :param highest_area_level: the level of the largest administrative
            area to finish with.

        :param locale: a ``Locale`` instance that specifies the locale of the
            area labels to be returned.

        :param minimal_area_surface: minimal surface in square meter of the
            geographical area that are returned.


        :return: a list of instances containing the following members:

            * ``area_id`` (required): identification of the geographic area.

            * ``area_label`` (required): an instance ``Label`` corresponding to the
              name of this area in the specified locale, or the closest locale if
              no name is defined for this particular locale, which is, at least,
              English by default.

            * ``area_level`` (required): administrative level of this geogaphic area.
              For clarity and convenience the standard neutral reference for the
              largest administrative subdivision of a country is called the "first-
              level administrative division" or "first administrative level".  Next
              smaller is called "second-level  administrative division" or "second
              administrative level".

            * ``area_type`` (optional): symbolic name of the type of this geographic
              area.

            * ``bounding_box`` (required): an instance ``BoundingBox`` representing
              the maximum extents of the geographical area.

            * ``centroid`` (required): an instance ``GeoPoint`` representing the
              centroid of this area.

            * ``parent_area_id`` (optional): identification of the parent geographic
              area or ``None`` if none defined.
        """
        location = self.find_location_with_ip_address(ip_address, connection=connection)

        return [] if location is None else self.get_areas_by_location(
            location,
            connection=connection,
            lowest_area_level=lowest_area_level,
            highest_area_level=highest_area_level,
            minimal_area_surface=minimal_area_surface,
            locale=locale)

    def get_areas_by_keywords(
            self,
            keywords,
            connection=None,
            highest_area_level=None,
            locale=DEFAULT_LOCALE,
            lowest_area_level=None,
            limit=BaseRdbmsService.DEFAULT_LIMIT,
            minimal_area_surface=None,
            offset=0):
        """
        Return the geographic areas that match the specified keywords.


        :param keywords: a list of one or more keywords.

        :param connection: A `RdbmsConnection` instance to be used supporting
            the Python clause `with ...:`.

        :param lowest_area_level: the level of the smallest administrative
            area to start with.

            As a reminder, for clarity and convenience the standard neutral
            reference for the largest administrative subdivision of a country
            is called the "first-level administrative division" or "first
            administrative level". Next smaller is called "second-level
            administrative division" or "second administrative level", etc.

            Note: the smallest the area, the fastest the function returns
            result.

        :param highest_area_level: The level of the largest administrative
            area to finish with.

        :param limit: Constrain the number of areas that are returned to the
            specified number.

        :param locale: An object ``Locale`` that specifies the locale of the
             area labels to be returned.

        :param minimal_area_surface: Minimal surface of the areas to return.

        :param offset: require to skip that many areas before beginning to
            return them.  If both ``limit`` and ``offset`` are specified, then
            ``offset`` areas are skipped before starting to count the
            `limit`` areas that are returned.  The default value is ``0``.


        :return: an instance containing the following members:

            * ``area_id``: identification of the geographic area.

            * ``area_type``: symbolic name of the type of the geographic area.

            * ``area_label``: label in the specified locale, or the closest locale
              if no label is defined for this particular locale, which is, at
              least, English by default.

            * ``parent_area_id``: identification of the parent geographic area or
              ``None`` if none defined.
        """
        keywords = self._cleanse_keywords(keywords)
        if len(keywords) == 0:
            return []

        with self.acquire_rdbms_connection(auto_commit=False, connection=connection) as connection:
            cursor = connection.execute(
                """
                SELECT
                    area_id,
                    parent_area_id,
                    score,
                    ST_X(centroid) AS longitude,
                    ST_Y(centroid) AS latitude,
                    ST_XMin(bounding_box) AS x_min,
                    ST_YMin(bounding_box) AS y_min,
                    ST_XMax(bounding_box) AS x_max,
                    ST_YMax(bounding_box) AS y_max,
                    area_type,
                    area_level,
                    (get_area_label(area_id, %(locale)s)).*,
                    get_area_path(area_id, p_locale:=%(locale)s) AS path
                  FROM (
                    SELECT
                        area_id,
                        COUNT(*) AS score
                      FROM area_index
                      INNER JOIN area
                        USING (area_id)
                      WHERE keyword IN (%[keywords]s)
                        AND (%(highest_area_level)s IS NULL OR area_level >= %(highest_area_level)s)
                        AND (%(lowest_area_level)s IS NULL OR area_level <= %(lowest_area_level)s)
                        AND (%(minimal_area_surface)s IS NULL OR surface >= %(minimal_area_surface)s)
                      GROUP BY area_id
                      ORDER BY
                          score DESC,
                          area_id DESC -- @hack: to preserve order of photos with same score from an offset to another
                      LIMIT %(limit)s
                      OFFSET %(offset)s) AS foo
                  INNER JOIN area
                    USING (area_id)
                """,
                {
                    'keywords': keywords,
                    'highest_area_level': highest_area_level,
                    'limit': min(limit, self.DEFAULT_LIMIT),
                    'locale': locale,
                    'lowest_area_level': lowest_area_level,
                    'minimal_area_surface': minimal_area_surface,
                    'offset': offset
                })

            areas = [
                row.get_object({
                    'area_id': cast.string_to_uuid,
                    'parent_area_id': cast.string_to_uuid,
                    'locale': cast.string_to_locale
                })
                for row in cursor.fetch_all()
            ]

            for area in areas:
                area.label = Label(area.content, area.locale)
                area.path = Label(area.path, area.locale)
                del area.content, area.locale

                area.centroid = GeoPoint(area.latitude, area.longitude)
                del area.longitude, area.latitude

                area.bounding_box = BoundingBox(
                        GeoPoint(area.y_min, area.x_min),
                        GeoPoint(area.y_max, area.x_max))
                del area.x_min, area.y_min, area.x_max, area.y_max

            return areas

    def get_areas_by_location(
            self,
            location,
            connection=None,
            lowest_area_level=AREA_LEVEL_WARD,
            highest_area_level=AREA_LEVEL_COUNTRY,
            locale=None,
            minimal_area_surface=None):
        """
        Return the geographic areas that encompass the specified location.


        :param location: a ``GeoPoint`` instance that specifies a location.

        :param connection: A `RdbmsConnection` instance to be used supporting
            the Python clause `with ...:`.

        :param lowest_area_level: the level of the smallest administrative
            area to start with.

            As a reminder, for clarity and convenience the standard neutral
            reference for the largest administrative subdivision of a country
            is called the "first-level administrative division" or "first
            administrative level". Next smaller is called "second-level
            administrative division" or "second administrative level", etc.

            Note: the smallest the area, the fastest the function returns
            result.

        :param highest_area_level: the level of the largest administrative
            area to finish with.

        :param locale: a ``Locale`` instance that specifies the locale of the
            area labels to be returned.

        :param minimal_area_surface: minimal surface in square meter of the
            geographical area that are returned.


        :return: a list of instances containing the following members:

            * ``area_id`` (required): identification of the geographic area.

            * ``area_label`` (required): an instance ``Label`` corresponding to the
              name of this area in the specified locale, or the closest locale if
              no name is defined for this particular locale, which is, at least,
              English by default.

            * ``area_level`` (required): administrative level of this geogaphic area.
              For clarity and convenience the standard neutral reference for the
              largest administrative subdivision of a country is called the "first-
              level administrative division" or "first administrative level".  Next
              smaller is called "second-level  administrative division" or "second
              administrative level".

            * ``area_type`` (optional): symbolic name of the type of this geographic
              area.

            * ``bounding_box`` (required): an instance ``BoundingBox`` representing
              the maximum extents of the geographical area.

            * ``centroid`` (required): an instance ``GeoPoint`` representing the
              centroid of this area.

            * ``parent_area_id`` (optional): identification of the parent geographic
              area or ``None`` if none defined.
        """
        with self.acquire_rdbms_connection(auto_commit=False, connection=connection) as connection:
            cursor = connection.execute(
                """
                SELECT
                    area_id,
                    parent_area_id,
                    area_level,
                    content,
                    get_area_path(area_id, p_locale:=%(locale)s) AS path,
                    locale,
                    ST_X(centroid) AS longitude,
                    ST_Y(centroid) AS latitude,
                    ST_XMin(bounding_box) AS x_min,
                    ST_YMin(bounding_box) AS y_min,
                    ST_XMax(bounding_box) AS x_max,
                    ST_YMax(bounding_box) AS y_max
                  FROM
                    find_areas_with_location(
                        ST_SetSRID(ST_MakePoint(%(longitude)s, %(latitude)s), 4326),
                        p_lowest_area_level:=%(lowest_area_level)s,
                        p_highest_area_level:=%(highest_area_level)s,
                        p_minimal_area_surface:=%(minimal_area_surface)s,
                        p_locale:=%(locale)s)
                """,
                {
                    'highest_area_level': highest_area_level,
                    'latitude': location.latitude,
                    'locale': locale or DEFAULT_LOCALE,
                    'lowest_area_level': lowest_area_level,
                    'longitude': location.longitude,
                    'minimal_area_surface': minimal_area_surface or 0
                })

            areas = [
                row.get_object({
                    'area_id': cast.string_to_uuid,
                    'locale': Locale,
                    'parent_area_id': cast.string_to_uuid
                })
                for row in cursor.fetch_all()
            ]

            for area in areas:
                area.label = Label(area.content, area.locale)
                area.path = Label(area.path, area.locale)
                del area.content, area.locale

                area.centroid = GeoPoint(area.latitude, area.longitude)
                del area.longitude, area.latitude

                area.bounding_box = BoundingBox(
                    GeoPoint(area.y_min, area.x_min),
                    GeoPoint(area.y_max, area.x_max))

                del area.x_min, area.y_min, area.x_max, area.y_max

            return areas
