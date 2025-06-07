\
import json
import csv

def _create_point_geometry(lon, lat):
    """Creates a GeoJSON Point geometry."""
    return {"type": "Point", "coordinates": [lon, lat]}

def _create_linestring_geometry(coordinates):
    """Creates a GeoJSON LineString geometry.
    Coordinates should be a list of [lon, lat] pairs.
    """
    return {"type": "LineString", "coordinates": coordinates}

def _create_polygon_geometry(coordinates):
    """Creates a GeoJSON Polygon geometry.
    Coordinates should be a list of lists of [lon, lat] pairs (e.g., [[[lon, lat], ...]] for a simple polygon).
    """
    return {"type": "Polygon", "coordinates": coordinates}

def to_geojson_feature(item, geometry_type, lon_field=None, lat_field=None, coordinates_field=None, properties_fields=None):
    """
    Converts a single data item to a GeoJSON Feature.

    Args:
        item (dict): The data item (dictionary).
        geometry_type (str): Type of geometry ('Point', 'LineString', 'Polygon').
        lon_field (str, optional): Key for longitude (for Point geometry).
        lat_field (str, optional): Key for latitude (for Point geometry).
        coordinates_field (str, optional): Key for coordinates list (for LineString/Polygon).
        properties_fields (list, optional): List of keys from item to include as properties.
                                            If None, all keys not used for geometry are included.

    Returns:
        dict: A GeoJSON Feature dictionary, or None if conversion fails.
    """
    geometry = None
    item_properties = {}

    if not isinstance(item, dict):
        print(f"Warning: Item is not a dictionary: {item}")
        return None

    if geometry_type == 'Point':
        if lon_field and lat_field and lon_field in item and lat_field in item:
            try:
                lon = float(item[lon_field])
                lat = float(item[lat_field])
                geometry = _create_point_geometry(lon, lat)
            except (ValueError, TypeError):
                print(f"Warning: Could not parse coordinates for Point from item: {item}. Ensure '{lon_field}' and '{lat_field}' are valid numbers.")
                return None
        else:
            print(f"Warning: Missing longitude ('{lon_field}') or latitude ('{lat_field}') fields for Point in item: {item}")
            return None
    elif geometry_type in ['LineString', 'Polygon']:
        if coordinates_field and coordinates_field in item:
            coords = item[coordinates_field]
            # Basic validation for coordinate structure could be added here
            # For example, check if coords is a list, and elements are pairs/lists of pairs of numbers
            if geometry_type == 'LineString':
                geometry = _create_linestring_geometry(coords)
            else: # Polygon
                geometry = _create_polygon_geometry(coords)
        else:
            print(f"Warning: Missing coordinates field ('{coordinates_field}') for {geometry_type} in item: {item}")
            return None
    else:
        print(f"Warning: Unsupported geometry type: {geometry_type}")
        return None

    if properties_fields:
        item_properties = {key: item[key] for key in properties_fields if key in item}
    else:
        # Default: include all keys not used for geometry
        exclude_keys = {lon_field, lat_field, coordinates_field}
        item_properties = {key: value for key, value in item.items() if key not in exclude_keys}

    return {
        "type": "Feature",
        "geometry": geometry,
        "properties": item_properties
    }

def to_geojson_feature_collection(data_list, geometry_type, lon_field=None, lat_field=None, coordinates_field=None, properties_fields=None):
    """
    Converts a list of data items to a GeoJSON FeatureCollection.

    Args:
        data_list (list): A list of dictionaries, where each dictionary represents an item.
        geometry_type (str): The type of geometry for all features ('Point', 'LineString', 'Polygon').
                             Assumes all items in data_list conform to this geometry type.
        lon_field (str, optional): The key in each dictionary for longitude (for 'Point' geometry).
        lat_field (str, optional): The key in each dictionary for latitude (for 'Point' geometry).
        coordinates_field (str, optional): The key in each dictionary for the coordinates
                                           (for 'LineString' or 'Polygon' geometry).
                                           For LineString: list of [lon, lat] pairs.
                                           For Polygon: list of lists of [lon, lat] pairs (e.g., [[[lon, lat], ...]]).
        properties_fields (list, optional): A list of keys from the dictionaries to include in the
                                            'properties' of each feature. If None, all keys not
                                            used for geometry are included.

    Returns:
        str: A JSON string representing the GeoJSON FeatureCollection.
             Returns None if data_list is empty or if errors occur during feature conversion.
    """
    if not isinstance(data_list, list) or not data_list:
        print("Warning: Input data_list is not a list or is empty.")
        return None

    features = []
    for item in data_list:
        feature = to_geojson_feature(item, geometry_type, lon_field, lat_field, coordinates_field, properties_fields)
        if feature:
            features.append(feature)

    if not features:
        print("Warning: No valid features could be created from the data_list.")
        return None

    feature_collection = {
        "type": "FeatureCollection",
        "features": features
    }
    return json.dumps(feature_collection, indent=2)

def csv_to_list_of_dicts(csv_file_path, encoding='utf-8'):
    """
    Reads a CSV file and converts it into a list of dictionaries.
    Each dictionary represents a row, with column headers as keys.

    Args:
        csv_file_path (str): The path to the CSV file.
        encoding (str): The encoding of the CSV file.

    Returns:
        list: A list of dictionaries, or an empty list if an error occurs or file is empty.
    """
    data = []
    try:
        with open(csv_file_path, mode='r', newline='', encoding=encoding) as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                data.append(dict(row))
    except FileNotFoundError:
        print(f"Error: CSV file not found at {csv_file_path}")
        return []
    except Exception as e:
        print(f"Error reading CSV file {csv_file_path}: {e}")
        return []
    return data

# Example Usage:
if __name__ == '__main__':
    # --- Point Data Example ---
    point_data = [
        {'id': 1, 'name': 'Place A', 'lon': 127.0, 'lat': 37.5, 'value': 100},
        {'id': 2, 'name': 'Place B', 'lon': 127.1, 'lat': 37.55, 'value': 200}
    ]
    geojson_points = to_geojson_feature_collection(point_data, 'Point', lon_field='lon', lat_field='lat')
    if geojson_points:
        print("GeoJSON Points:")
        print(geojson_points)
        # To save to a file:
        # with open('points.geojson', 'w') as f:
        #     f.write(geojson_points)

    # --- LineString Data Example ---
    linestring_data = [
        {
            'id': 'route1',
            'name': 'Main Road',
            'road_type': 'highway',
            'coords': [[127.0, 37.5], [127.05, 37.52], [127.1, 37.5]] # [[lon, lat], [lon, lat], ...]
        }
    ]
    geojson_linestrings = to_geojson_feature_collection(
        linestring_data,
        'LineString',
        coordinates_field='coords',
        properties_fields=['id', 'name', 'road_type'] # Explicitly list properties
    )
    if geojson_linestrings:
        print("\\nGeoJSON LineStrings:")
        print(geojson_linestrings)

    # --- Polygon Data Example ---
    polygon_data = [
        {
            'id': 'area1',
            'name': 'Park Area',
            'status': 'open',
            'boundary': [ # A single polygon with one exterior ring
                [[127.0, 37.5], [127.1, 37.5], [127.1, 37.6], [127.0, 37.6], [127.0, 37.5]]
            ]
        },
        {
            'id': 'area2',
            'name': 'Lake Area',
            'status': 'restricted',
            'boundary': [ # A polygon with an exterior ring and one interior ring (hole)
                [[128.0, 38.0], [128.1, 38.0], [128.1, 38.1], [128.0, 38.1], [128.0, 38.0]], # Exterior
                [[128.02, 38.02], [128.08, 38.02], [128.08, 38.08], [128.02, 38.08], [128.02, 38.02]] # Interior (hole)
            ]
        }
    ]
    geojson_polygons = to_geojson_feature_collection(polygon_data, 'Polygon', coordinates_field='boundary')
    if geojson_polygons:
        print("\\nGeoJSON Polygons:")
        print(geojson_polygons)

    # --- CSV Data Example ---
    # First, create a dummy CSV file for testing
    dummy_csv_path = 'dummy_locations.csv'
    with open(dummy_csv_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['city_id', 'city_name', 'longitude', 'latitude', 'population'])
        writer.writerow(['S01', 'Seoul', '126.9780', '37.5665', '9776000'])
        writer.writerow(['B01', 'Busan', '129.0756', '35.1796', '3441000'])

    csv_data = csv_to_list_of_dicts(dummy_csv_path)
    if csv_data:
        print(f"\\nData from CSV ({dummy_csv_path}):")
        # print(csv_data) # uncomment to see raw list of dicts
        
        # Convert numeric fields from string after reading CSV
        for row in csv_data:
            row['longitude'] = float(row['longitude'])
            row['latitude'] = float(row['latitude'])
            row['population'] = int(row['population'])

        geojson_from_csv = to_geojson_feature_collection(
            csv_data,
            'Point',
            lon_field='longitude',
            lat_field='latitude',
            properties_fields=['city_id', 'city_name', 'population'] # Specify properties to include
        )
        if geojson_from_csv:
            print("\\nGeoJSON from CSV:")
            print(geojson_from_csv)
            # Clean up dummy CSV
            import os
            os.remove(dummy_csv_path)
    else:
        print(f"\\nCould not load data from {dummy_csv_path}")

    # Example of handling data where not all items might be convertible
    mixed_point_data = [
        {'id': 1, 'name': 'Valid Point', 'lon': 127.0, 'lat': 37.5},
        {'id': 2, 'name': 'Missing Lon', 'lat': 37.55},
        {'id': 3, 'name': 'Invalid Coords', 'lon': 'not-a-number', 'lat': 37.6},
        {'id': 4, 'name': 'Another Valid', 'lon': 127.1, 'lat': 37.58}
    ]
    geojson_mixed_points = to_geojson_feature_collection(mixed_point_data, 'Point', lon_field='lon', lat_field='lat')
    if geojson_mixed_points:
        print("\\nGeoJSON from mixed quality point data (valid points only):")
        print(geojson_mixed_points)
    else:
        print("\\nNo valid GeoJSON created from mixed quality point data.")
