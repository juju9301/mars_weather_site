import json, requests

API_URL = 'http://cab.inta-csic.es/rems/wp-content/plugins/marsweather-widget/api.php'
SOURCE = 'inta-csic'

def request_data():
    resp = requests.get(API_URL)
    data = resp.json()
    return data

result = []

data = request_data()
soles = data['soles']
i = 1
for sol in soles:
    obj = {"model": "weather.Weather", "pk": i, "fields": {}}
    obj['fields']['orig_id'] = sol['id']
    obj['fields']['terrestrial_date'] = sol['terrestrial_date']
    obj['fields']['sol'] = sol['sol']
    obj['fields']['ls'] = sol['ls']
    obj['fields']['season'] = sol['season']
    obj['fields']['min_temp'] = sol['min_temp']
    obj['fields']['max_temp'] = sol['max_temp']
    obj['fields']['pressure'] = sol['pressure']
    obj['fields']['pressure_string'] = sol['pressure_string']
    obj['fields']['abs_humidity'] = sol['abs_humidity']
    obj['fields']['wind_speed'] = sol['wind_speed']
    obj['fields']['wind_direction'] = sol['wind_direction']
    obj['fields']['atmo_opacity'] = sol['atmo_opacity']
    obj['fields']['sunrise'] = sol['sunrise']
    obj['fields']['sunset'] = sol['sunset']
    obj['fields']['local_uv_irradiance_index'] = sol['local_uv_irradiance_index']
    obj['fields']['min_gts_temp'] = sol['min_gts_temp']
    obj['fields']['max_gts_temp'] = sol['max_gts_temp']
    for key in obj['fields'].keys():
        if obj['fields'][key] == '--':
            obj['fields'][key] = None
    result.append(obj)
    i += 1

with open(r'mars_weather_app\weather\fixtures\weather_fixture.json', 'w') as result_file:
    json.dump(result, result_file)


