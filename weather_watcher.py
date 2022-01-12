from bs4 import BeautifulSoup
import requests
from credentials import SLACK_WEBHOOK
import os
import sys

print(os.getcwd(), __file__, sys.argv[0])
LAST_UPDATE_FILE_PATH = os.path.dirname(os.path.realpath(__file__)) + '/last_update.txt'

NEW_FORECAST = 'There is a new forecast! https://booneweather.com/Forecast/Boone'

def get_rays_weather_content():
    resp = requests.get('https://booneweather.com/Forecast/Boone')
    if resp.ok:
        return resp
    else:
        raise Exception('Unable to load content')
        
def get_last_update_str(soup):
    forecast_texts = soup.find_all('p', {'class': 'forecast_text'})
    forecast_items = next(iter([f for f in forecast_texts if 'last updated' in f.text.lower()]), None)
    return forecast_items.text

def read_file_path(file_path):
    with open(file_path, 'r+') as last_update_file:
        return last_update_file.read()
    
def overwrite_file_path(file_path, contents):
    with open(file_path, 'w+') as last_update_file:
        last_update_file.write(contents)

def send_message(msg):
	return requests.post(SLACK_WEBHOOK, json={'text':msg})

def main():
	rays_weather_content = get_rays_weather_content()
	rays_weather_soup = BeautifulSoup(rays_weather_content.text, 'lxml')
	last_update_str = get_last_update_str(rays_weather_soup)

	cached_update_str = read_file_path(LAST_UPDATE_FILE_PATH)
	if last_update_str == cached_update_str:
		print('Forecast has been seen')
	else:
		print('New forecast!')
		resp = send_message(NEW_FORECAST)
		if not resp.ok:
			raise Exception(resp.text)
		else:
			overwrite_file_path(LAST_UPDATE_FILE_PATH, last_update_str)

if __name__ == '__main__':
	main()