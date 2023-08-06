import logging

import grequests
from json import dumps, loads
import os.path
from os import mkdir
import time


logger = logging.getLogger(__name__)


class AmoAuth:
    instance = None

    @staticmethod
    def get_token(subdomain, client_id, client_secret, grant_type, code, redirect_uri, config_file, zone='ru'):
        file_path_split = config_file.split('/')
        AmoAuth.config_filename = file_path_split[-1]
        file_path_split[-1] = ''
        AmoAuth.config_path = '/'.join(file_path_split)
        url = f'https://{subdomain}.amocrm.{zone}/oauth2/access_token'
        data = {
            'client_id': client_id,
            'client_secret': client_secret,
            'grant_type': grant_type,
            'redirect_uri': redirect_uri
        }
        if grant_type == 'authorization_code':
            data['code'] = code
        if grant_type == 'refresh_token':
            data['refresh_token'] = code
        req = grequests.map((grequests.post(u, data=data) for u in [url]))[0]

        if req.status_code == 200:
            response = req.json()
            config_file = os.path.join(AmoAuth.config_path, AmoAuth.config_filename)
            token_data = {}
            if not os.path.isdir(AmoAuth.config_path):
                mkdir(AmoAuth.config_path)
            token_data[client_id] = {
                'client_id': client_id,
                'client_secret': client_secret,
                'redirect_uri': redirect_uri,
                'token_type': response['token_type'],
                'access_token': response['access_token'],
                'refresh_token': response['refresh_token'],
                'last_update_time': int(time.time()),
                'expires_in': response['expires_in']
            }
            with open(config_file, 'w') as file:
                file.write(dumps(token_data, indent=4))
            return {'access_token': response['access_token'], 'token_type': response['token_type']}
        else:
            logger.error(req.text)
            return False

    @staticmethod
    def get_token_by_auth_code(subdomain, client_id, client_secret, code, redirect_uri, zone='ru'):
        return AmoAuth.get_token(subdomain, client_id, client_secret, 'authorization_code', code, redirect_uri, zone)

    @staticmethod
    def refresh_token(subdomain, client_id, client_secret, redirect_uri, config_file, zone='ru'):
        file_path_split = config_file.split('/')
        AmoAuth.config_filename = file_path_split[-1]
        file_path_split[-1] = ''
        AmoAuth.config_path = '/'.join(file_path_split)
        config_file = os.path.join(AmoAuth.config_path, AmoAuth.config_filename)
        tokens_file = open(config_file, 'r')
        tokens_file_content = tokens_file.read()
        if tokens_file_content == '':
            raise ValueError('!!!! Файл конфигурации пуст !!!!\n\nЗаполните auth_code метода config \nПосле чего выполните любой запрос и очистите параметр\nОн является флагом, для выпуска ключей конфигурации\nПомните, что 20 минутный ключ одноразовый')
        config = loads(tokens_file_content)[client_id]
        tokens_file.close()
        if int(time.time()) - config['last_update_time'] < config['expires_in']:
            return {'access_token': config['access_token'], 'token_type': config['token_type']}
        return AmoAuth.get_token(subdomain, client_id, client_secret, 'refresh_token', config['refresh_token'], redirect_uri, config_file, zone)
