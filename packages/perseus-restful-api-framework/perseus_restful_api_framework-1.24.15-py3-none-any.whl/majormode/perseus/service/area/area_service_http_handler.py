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

from majormode.perseus.constant.http import HttpMethod
from majormode.perseus.model.geolocation import GeoPoint
from majormode.perseus.model.locale import DEFAULT_LOCALE
from majormode.perseus.service.base_http_handler import HttpRequest
from majormode.perseus.service.base_http_handler import HttpRequestHandler
from majormode.perseus.service.base_http_handler import http_request
from majormode.perseus.service.area.area_service import AreaService


class AreaServiceHttpRequestHandler(HttpRequestHandler):
    pass
    # @http_request(r'^/area$',
    #               http_method=HttpMethod.GET,
    #               authentication_required=False)
    # def get_areas(self, request):
    #     locale = request.get_argument('locale',
    #             data_type=HttpRequest.ArgumentDataType.locale,
    #             default_value=DEFAULT_LOCALE)
    #
    #     # Return areas specified by their identification.
    #     area_id_list = request.get_argument('ids',
    #             data_type=HttpRequest.ArgumentDataType.list,
    #             item_data_type=HttpRequest.ArgumentDataType.uuid,
    #             is_required=False)
    #
    #     if area_id_list:
    #         return AreaService().get_areas(request.app_id, area_id_list, locale=locale)
    #
    #     highest_area_level = request.get_argument('highest_area_level',
    #             data_type=HttpRequest.ArgumentDataType.integer,
    #             is_required=False)
    #
    #     lowest_area_level = request.get_argument('lowest_area_level',
    #             data_type=HttpRequest.ArgumentDataType.integer,
    #             is_required=False)
    #
    #     minimal_area_surface = request.get_argument(
    #         'minimal_area_surface',
    #         data_type=HttpRequest.ArgumentDataType.decimal,
    #         is_required=False)
    #
    #     # Return the areas that encompass the specified location.
    #     location_url_value = request.get_argument(
    #         'll',
    #         data_type=HttpRequest.ArgumentDataType.string,
    #         is_required=False)
    #
    #     if location_url_value:
    #         location_coordinates = location_url_value.split(',')
    #         if len(location_coordinates) != 2:
    #             raise AreaService.InvalidArgumentException('The location MUST have the form "lon,lat"')
    #
    #         location = GeoPoint(float(location_coordinates[0]), float(location_coordinates[1]))
    #
    #         return AreaService().get_areas_by_location(
    #             request.app_id, location,
    #             highest_area_level=highest_area_level,
    #             locale=locale,
    #             lowest_area_level=lowest_area_level,
    #             minimal_area_surface=minimal_area_surface)
    #
    #     # Return the areas that encompass the approximate location corresponding
    #     # to the specified IPv4 address.
    #     ip_address = request.get_argument(
    #         'ip_address',
    #         data_type=HttpRequest.ArgumentDataType.ipv4,
    #         is_required=False)
    #
    #     if ip_address:
    #         return AreaService().get_areas_by_ip_address(
    #             request.app_id,
    #             ip_address,
    #             highest_area_level=highest_area_level,
    #             locale=locale,
    #             lowest_area_level=lowest_area_level,
    #             minimal_area_surface=minimal_area_surface)
    #
    #     # Return the areas that are including in the specified boundaries.
    #     bounds_url_value = request.get_argument(
    #         'bounds',
    #         data_type=HttpRequest.ArgumentDataType.string,
    #         is_required=False)
    #
    #     if bounds_url_value:
    #         bounds_coordinates = bounds_url_value.split(',')
    #         if len(bounds_coordinates) != 4:
    #             raise AreaService.InvalidArgumentException('The bounds MUST have the form "NE-lon,NE-lat,SW-lon,SW-lat"')
    #
    #         bounds = (GeoPoint(float(bounds_coordinates[0]), float(bounds_coordinates[1])),
    #                   GeoPoint(float(bounds_coordinates[2]), float(bounds_coordinates[3])))
    #
    #         return AreaService().get_areas_in_bounding_box(request.app_id, bounds, locale=locale)
    #
    #     # Return areas that match the specified keywords.
    #     keywords = request.get_argument(
    #         'keywords',
    #         data_type=HttpRequest.ArgumentDataType.list,
    #         is_required=True)
    #
    #     offset = request.get_argument(
    #         'offset',
    #         data_type=HttpRequest.ArgumentDataType.integer,
    #         is_required=False,
    #         default_value=0)
    #
    #     limit = request.get_argument(
    #         'limit',
    #         data_type=HttpRequest.ArgumentDataType.integer,
    #         is_required=False,
    #         default_value=AreaService.MAXIMUM_LIMIT)
    #
    #     return AreaService().get_areas_by_keywords(
    #         request.app_id,
    #         keywords,
    #         highest_area_level=highest_area_level,
    #         limit=limit,
    #         locale=locale,
    #         lowest_area_level=lowest_area_level,
    #         minimal_area_surface=minimal_area_surface,
    #         offset=offset)
    #
    # @http_request(r'^/area/(area_id:uuid)/boundaries$',
    #               http_method=HttpMethod.GET,
    #               authentication_required=False)
    # def get_area_boundaries(self, request, area_id):
    #     return AreaService().get_area_boundaries(request.app_id, area_id)
