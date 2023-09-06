import time
from bs4 import BeautifulSoup
import requests
import pandas as pd

my_data = {
    "link": [],
    "city": [],
    "district": [],
    "property_type": [],
    "price": [],
    "price_tax_included": [],
    "area": [],
    "floor": [],
    "gas": [],
    "tec": [],
    "building_type": [],
    "year_built": [],
    "features_list": []
}

city_list = {
    'Sofia': '9pprbb',
    'Plovdiv': '9prleg',
    'Varna': '9prls2'
}

start = time.time()

for citi in city_list:
    for page in range(1, 26):
        html_requests = requests.get(f'https://www.imot.bg/pcgi/imot.cgi?act=3&slink={city_list[citi]}&f1={page}')
        html_requests.encoding = 'windows-1251'
        soup = BeautifulSoup(html_requests.text, 'lxml')
        listings = soup.find_all('td', valign='top', width='270', height='40')
        for listing in listings:
            if listing.find('div', class_= 'price').text != 'Цена при запитване ':
                my_data['price'].append(listing.find('div', class_= 'price').text.replace('Цената е без ДДС',''))
                my_data['link'].append('https:'+listing.find('a', class_= 'lnk1')['href'])
                my_data['property_type'].append(listing.find('a', class_= 'lnk1').text.split()[-1].replace('СТАЕН','Стаен'))
                my_data['city'].append(listing.find('a', class_= 'lnk2').text.split(', ')[0].replace('град ',''))
                my_data['district'].append(listing.find('a', class_= 'lnk2').text.split(', ')[1])
                my_data['price_tax_included'].append("Не" if 'Цената е без ДДС' in my_data['price'] else "Да")

                listing_request = requests.get('https:'+listing.find('a', class_= 'lnk1')['href'])
                listing_request.encoding = 'windows-1251'
                listings_soup = BeautifulSoup(listing_request.text, 'lxml')
                print('https:'+listing.find('a', class_= 'lnk1')['href'])
                listing_params = listings_soup.find('div', class_="adParams").find_all('div')

                has_param_floor = False
                has_param_gas = False
                has_param_tec = False
                has_param_building_type = False
                has_param_year_built = False
                has_param_features = False

                for param in listing_params:
                    if 'Площ' in param.text:
                        my_data['area'].append(int(param.text.replace('Площ: ','').replace(' m2','')))
                    if 'Етаж' in param.text:
                        my_data['floor'].append(param.text.replace('Етаж: ',''))
                        has_param_floor = True
                    if 'Газ' in param.text:
                        my_data['gas'].append('Да') if param.text.replace('Газ: ','') == 'ДА' else my_data['gas'].append('Не')
                        has_param_gas = True
                    if 'ТEЦ' in param.text:
                        my_data['tec'].append('Да') if param.text.replace('ТEЦ: ','') == 'ДА' else my_data['tec'].append('Не')
                        has_param_tec = True
                    if 'Строителство' in param.text:
                        my_data['building_type'].append(param.text.replace('Строителство: ','').split(', ')[0])
                        has_param_building_type = True
                    if len(param.text.replace('Строителство: ','').split(', ')) > 1:
                        my_data['year_built'].append(param.text.replace('Строителство: ','').split(', ')[1].replace(' г.',''))
                        has_param_year_built = True

                features = listings_soup.find_all('td', valign='top', width='20%')
                    
                features_txt = ''
                for feature in features:
                    features_txt += feature.text.replace('• ',', ').replace('\n','')
                features_txt = features_txt.lstrip(', ')
                my_data['features_list'].append(features_txt)

                if len(features_txt) > 0:
                    has_param_features = True
                features_txt = ''

                if has_param_floor == False:
                    my_data['floor'].append(None)
                if has_param_gas == False:
                    my_data['gas'].append(None)
                if has_param_tec == False:
                    my_data['tec'].append(None)
                if has_param_building_type == False:
                    my_data['building_type'].append(None)
                if has_param_year_built == False:
                    my_data['year_built'].append(None)
                if has_param_features == False:
                    my_data['features_list'].append(None)

end = time.time()
print(f'Time Elapsed: {end - start}')
df = pd.DataFrame(my_data)

my_csv = df.to_excel('data/imot_bg_dataset.xlsx', index = None)