import requests
from urllib.parse import urlparse
from dotenv import load_dotenv
import os
import pandas as pd


def create_header(token):
    header = {
        'Authorization': 'Bearer ' + token,
        'Content-Type': 'application/json'
    }
    return header


def is_bitlink(link, token):
    bitly_api_url = 'https://api-ssl.bitly.com/v4/'
    parse = urlparse(link)
    header = create_header(token)
    link_to_check = f'{bitly_api_url}bitlinks/{parse.netloc + parse.path}'
    response = requests.get(link_to_check, headers=header)
    return response.ok


def shorten_link(url, token):
    bitlink_url = 'https://api-ssl.bitly.com/v4/bitlinks'
    header = create_header(token)
    request_body = {
        'long_url': url,
        'domain': 'bit.ly',
    }

    response = requests.post(
        bitlink_url,
        json=request_body,
        headers=header
    )

    response.raise_for_status()
    response = response.json()

    return response["id"]


def count_clicks(link, token):
    header = create_header(token)
    bitly_api_url = 'https://api-ssl.bitly.com/v4/'
    parse = urlparse(link)
    clicks_url = f'{bitly_api_url}bitlinks/{parse.netloc + parse.path}/clicks/'
    params = {
        'unit': 'day',
        'units': -1,
    }

    response = requests.get(clicks_url, params=params, headers=header)
    response.raise_for_status()
    response = response.json()
    clicks_data = pd.DataFrame(response['link_clicks'])
    clicks_data['date'] = pd.to_datetime(clicks_data['date']).\
        dt.strftime('%Y-%m-%d')
    return clicks_data['clicks'].sum(), clicks_data


def run_bitly(link, token):
    if not is_bitlink(link, token):
        try:
            short_url = shorten_link(link, token)
            print(f'Отлично! Вы получили короткую ссылку: {short_url}')
        except requests.exceptions.HTTPError:
            print('Невозможно обработать вашу ссылку,'
                  ' возможно вы забыли указать http:// в начале')
    else:
        try:
            total_clicks = count_clicks(link, token)
            print(f'Общее количество кликов по ссылке: {total_clicks[0]}')
            download_data_flag = input('Выгрузить статистику по кликам в файл?'
                                       ' (Введите Y для получения): ')
            if download_data_flag == 'Y':
                total_clicks[1].to_excel('bitly_stats.xlsx', index=False)
        except requests.exceptions.HTTPError:
            print('Что-то пошло не так')


if __name__ == "__main__":
    load_dotenv()
    token = os.getenv('BITLY_TOKEN')
    link = input('Введите ссылку: ')
    run_bitly(link, token)
