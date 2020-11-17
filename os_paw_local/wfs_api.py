from itertools import count

import requests
from geojson import Feature, FeatureCollection, LineString

import os_paw_local.project_paths as paths
from os_paw_local.api_utils import (convert_features_to_geojson,
                              get_feature_geometry_type, validate_api_key,
                              validate_bbox, validate_output_format,
                              validate_request_params, validate_srs,
                              validate_type_name, create_polygon_filter)
from os_paw_local.products import wfs_products


class WFS_API:
    """Wrapper for the Ordnance Survey Web Feature Survey API. 
    To generate your own key, please create an account at
        https://osdatahub.os.uk/
    To see some examples of what can be done with Ordnance Survey data, refer to
        https://labs.os.uk/public/os-data-hub-tutorials/
    """

    _SERVICE = 'wfs'
    _WFS_ENDPOINT = r'https://api.os.uk/features/v1/wfs'
    _VERSION = '2.0.0'
    _MAX_FEATURES_PER_REQUEST = 100
    _PREMIUM_PRODUCTS = wfs_products['Premium']
    _OPEN_PRODUCTS = wfs_products['Open']
    _ALL_PRODUCTS = _PREMIUM_PRODUCTS | _OPEN_PRODUCTS

    def __init__(self, api_key):
        print('Dev mode!')
        self.__api_key = api_key

    @property
    def api_key(self):
        return self.__api_key

    @api_key.setter
    def api_key(self, new_api_key):
        validate_api_key(new_api_key)
        self.__api_key = new_api_key


    def get_all_features_within_bbox(self, type_name, bbox,
                                     allow_premium=False,
                                     srs='EPSG:4326', 
                                     output_format='geojson',
                                     max_feature_count=1000):
        request_params = self._create_request_params(type_name=type_name, 
                                                bbox=bbox,
                                                polygon_string=False,
                                                allow_premium=allow_premium,
                                                output_format=output_format,
                                                srs=srs,
                                                start_index=0)
        index_count = count(1, self._MAX_FEATURES_PER_REQUEST)

        all_features = []
        features = True

        # This could be adapted to fetch all features if max_feature_count == False 
        while features and request_params['startIndex'] < max_feature_count:
            response = requests.get(self._WFS_ENDPOINT, params=request_params)
            payload = response.json()
            features = payload['features']
            all_features.extend(features)
            request_params['startIndex'] = next(index_count)

        if all_features:
            # Assumes all features in collection will be of the same type
            geometry_type = get_feature_geometry_type(all_features[0]).lower()
            if geometry_type == 'linestring':
                all_features = convert_features_to_geojson(all_features)
            elif geometry_type not in {'point', 'polygon'}:
                raise Exception(f'Currently unable to handle {geometry_type}s.')

        return FeatureCollection(all_features, crs=srs)


    def get_features_within_polygon(self,  type_name, polygon,
                                     allow_premium=False,
                                     srs='EPSG:4326', 
                                     output_format='geojson',
                                     max_feature_count=1000):

        # Set up polygon for request
        # check to make sure that the polygon is GeoJSON
        geom_type = get_feature_geometry_type(polygon).lower()
        if geom_type != "polygon":
            raise Exception("Geometry to fetch intersecting features is not a valid GeoJSON Polygon Feature")
        

        polygon_coord_strings = [','.join([str(z) for z in coord[::-1]]) for coord in polygon['geometry']['coordinates'][0]]
        # Flip coords to [y, x] and convert to space-delimited string of comma-separated coords
        polygon_string = ' '.join(polygon_coord_strings)
        
        request_params = self._create_request_params(type_name=type_name, 
                                                bbox=False,
                                                polygon_string=polygon_string,
                                                allow_premium=allow_premium,
                                                output_format=output_format,
                                                srs=srs,
                                                start_index=0)
        index_count = count(1, self._MAX_FEATURES_PER_REQUEST)

        all_features = []
        features = True
        while features and request_params['startIndex'] <= max_feature_count:
            response = requests.get(self._WFS_ENDPOINT, params=request_params)
            payload = response.json()
            print(payload)
            features = payload['features']
            all_features.extend(features)
            request_params['startIndex'] = next(index_count)

        if all_features:
            # Assumes all features in collection will be of the same type
            geometry_type = get_feature_geometry_type(all_features[0]).lower()
            if geometry_type == 'linestring':
                all_features = convert_features_to_geojson(all_features)
            elif geometry_type not in {'point', 'polygon'}:
                raise Exception(f'Currently unable to handle {geometry_type}s.')

        return FeatureCollection(all_features, crs=srs)

    def _create_request_params(self, allow_premium, type_name, bbox, polygon_string,
                               output_format, srs='EPSG:4326', start_index=0):

        validate_request_params(api_service=self._SERVICE,
                                type_name=type_name,
                                bbox=bbox,
                                polygon_string=polygon_string,
                                allow_premium=allow_premium,
                                srs=srs,
                                output_format=output_format)        
        request_params = {
            'key': self.api_key,
            'service': self._SERVICE,
            'version': self._VERSION,
            'startIndex': start_index,
            'request': 'GetFeature',
            'typeNames': type_name,
            'outputFormat': output_format,
            'srsName': srs,
            'count': self._MAX_FEATURES_PER_REQUEST
        }

        if bbox:
            request_params['bbox'] = bbox 
        if polygon_string:
            request_params['filter'] = create_polygon_filter(polygon_string, srs)

        return request_params



if __name__ == '__main__':
    import configparser

    config = configparser.ConfigParser()
    config.read(paths.config_path)
    keys = config['KEYS']
    API_KEY = keys['API_KEY']

    WGS84_SRS = 'EPSG:4326'
    BNG_SRS = 'EPSG:27700'

    wfs_api = WFS_API(api_key=API_KEY)
    wgs_bbox = '51.0162, 0.9160, 51.1388, 0.9877'
    # LINESTRINGS
    wgs_payload = wfs_api.get_all_features_within_bbox(type_name='Zoomstack_RoadsRegional',
                                                       bbox=wgs_bbox, 
                                                       srs=WGS84_SRS)
    # # POLYGONS
    # wgs_payload = wfs_api.get_all_features_within_bbox(type_name='Zoomstack_Greenspace', 
    #                                                    bbox=wgs_bbox)
    # POINTS
    # wgs_payload = wfs_api.get_all_features_within_bbox(type_name='Zoomstack_Names', 
    #                                                    bbox=wgs_bbox)

    # # PREMIUM
    # wgs_payload = wfs_api.get_all_features_within_bbox(type_name='Highways_RoadLink',
    #                                                    bbox=wgs_bbox, 
    #                                                    allow_premium=True,
    #                                                    srs=WGS84_SRS)

    print(len(wgs_payload['features']))

    # bng_bbox = '605621, 139199, 607621, 141199'
    # bng_bbox = '605621, 139199, 605622, 139200'
    # bng_payload = wfs_api.get_all_features_within_bbox(type_name='Zoomstack_RoadsRegional',
    #                                                    bbox=bng_bbox, 
    #                                                    srs=BNG_SRS)
    # print(len(bng_payload['features']))
