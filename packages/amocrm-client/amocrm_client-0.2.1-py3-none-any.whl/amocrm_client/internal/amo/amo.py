from .internal.auth.amo_auth import AmoAuth
from .internal.entities.account import Account
from .internal.entities.lead import Lead
from .internal.entities.pipeline import Pipeline
from .internal.entities.contact import Contact
from .internal.entities.company import Company
from .internal.entities.catalog import Catalog
from .internal.entities.customer import Customer
import os


class AMO(object):
    instance = None
    client_id = None

    def __init__(self, subdomain, client_id, client_secret, amo_account_id, redirect_uri, config_file, code='', zone='ru'):
        self.subdomain = subdomain
        self.client_id = client_id
        self.client_secret = client_secret
        self.amo_account_id = amo_account_id
        self.redirect_uri = redirect_uri
        self.zone = zone
        self.config_file = config_file
        if code == '':
            token_data = self.refresh_token(subdomain, client_id, client_secret, redirect_uri, config_file, zone)
        else:
            token_data = self.get_token_by_auth_code(subdomain, client_id, client_secret, code, redirect_uri, config_file)
        self.token_type = token_data['token_type']
        self.access_token = token_data['access_token']
        self.fulldomain = f'https://{subdomain}.amocrm.{zone}'

    def __new__(cls, subdomain, client_id, client_secret, amo_account_id, redirect_uri, config_file, zone='ru'):
        if not cls.instance or not cls.client_id or cls.client_id and cls.client_id != client_id:
            cls.client_id = client_id
            cls.instance = object.__new__(cls)
        return cls.instance

    @staticmethod
    def get_token_by_auth_code(subdomain, client_id, client_secret, code, redirect_uri, config_file, zone='ru'):
        old_path = os.getcwd()
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
        token = AmoAuth.get_token(subdomain, client_id, client_secret, 'authorization_code', code, redirect_uri, config_file, zone)
        os.chdir(old_path)
        return token

    @staticmethod
    def refresh_token(subdomain, client_id, client_secret, redirect_uri, config_file, zone='ru'):
        old_path = os.getcwd()
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
        token = AmoAuth.refresh_token(subdomain, client_id, client_secret, redirect_uri, config_file, zone)
        os.chdir(old_path)
        return token

    def __getattr__(self, item):
        token_data = self.refresh_token(self.subdomain, self.client_id, self.client_secret, self.redirect_uri, self.config_file, self.zone)
        self.token_type = token_data['token_type']
        self.access_token = token_data['access_token']
        if item == 'account':
            return Account(self.fulldomain, self.access_token, self.token_type)
        elif item == 'lead':
            return Lead(self.fulldomain, self.access_token, self.token_type)
        elif item == 'pipeline':
            return Pipeline(self.fulldomain, self.access_token, self.token_type)
        elif item == 'contact':
            return Contact(self.fulldomain, self.access_token, self.token_type)
        elif item == 'company':
            return Company(self.fulldomain, self.access_token, self.token_type)
        elif item == 'catalog':
            return Catalog(self.fulldomain, self.access_token, self.token_type)
        elif item == 'customer':
            return Customer(self.fulldomain, self.access_token, self.token_type)
        else:
            return object.__getattribute__(self, item)
