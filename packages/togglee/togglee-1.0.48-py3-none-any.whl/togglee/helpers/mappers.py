def map_json_to_toggles(json_toggles):
    mapped_toggles = {}
    for toggle in json_toggles:
        mapped_toggles[toggle['name']] = toggle
        mapped_toggles[toggle['name']].pop('name')
    return mapped_toggles
