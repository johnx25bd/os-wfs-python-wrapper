from os_paw_local.wfs_api import WFS_API
import json

API_KEY = "JydUr1HO7ejqBhw0YP19W3b1GonFwmzr"
SRS = "EPSG:4326"
TYPE_NAME = 'Highways_RoadLink'
wfs_api = WFS_API(api_key=API_KEY)

feature =  {
      "type": "Feature",
      "properties": {},
      "geometry": {
        "type": "Polygon",
        "coordinates": [
          [
            [
              -0.196380615234375,
              50.83846776477957
            ],
            [
              -0.19054412841796875,
              50.79855742002198
            ],
            [
              -0.10540008544921875,
              50.806585609679104
            ],
            [
              -0.111236572265625,
              50.8510411296595
            ],
            [
              -0.17200469970703125,
              50.852124881781094
            ],
            [
              -0.182647705078125,
              50.83629960076613
            ],
            [
              -0.19260406494140625,
              50.844538088124544
            ],
            [
              -0.196380615234375,
              50.83846776477957
            ]
          ]
        ]
      }
    }

tinyzone = {
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "properties": {},
      "geometry": {
        "type": "Polygon",
        "coordinates": [
          [
            [
              -0.12943267822265625,
              50.821167077117
            ],
            [
              -0.12943267822265625,
              50.820455395686615
            ],
            [
              -0.12784481048583984,
              50.820455395686615
            ],
            [
              -0.1278555393218994,
              50.82144496882614
            ],
            [
              -0.12943267822265625,
              50.821167077117
            ]
          ]
        ]
      }
    }
  ]
}

payload = wfs_api.get_features_within_polygon(type_name=TYPE_NAME, polygon=feature, srs=SRS, allow_premium=True, max_feature_count=400)

with open('./features3.json', 'w') as file:
    json.dump(payload, file)