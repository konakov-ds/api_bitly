import os

from dotenv import load_dotenv
import requests
from urllib.parse import urlparse


def create_header(token):
    header = {
        'Authorization': f'Bearer {token}',
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
    clicks_url = f'{bitly_api_url}bitlinks/' \
                 f'{parse.netloc + parse.path}/clicks/summary'
    params = {
        'unit': 'day',
        'units': -1,
    }

    response = requests.get(clicks_url, params=params, headers=header)
    response.raise_for_status()
    response = response.json()
    return response['total_clicks']


def main():
    load_dotenv()
    token = os.getenv('BITLY_TOKEN')
    link = input('Введите ссылку: ')
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
            print(f'Общее количество кликов по ссылке: {total_clicks}')

        except requests.exceptions.HTTPError:
            print('Что-то пошло не так')


if __name__ == "__main__":
    main()
