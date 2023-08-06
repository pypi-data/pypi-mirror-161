from .internal.amo.amo import AMO
from .internal.entities.lead import Lead
from .internal.entities.pipeline import Pipeline
from .internal.entities.custom_field import CustomField
from .internal.entities.customer import Customer
from .internal.entities.product import Product
from .internal.entities.contact import Contact


class AmoCRMMeta(type):
	_config = None

	def config(cls, domain, id_integration, secret_key, amo_user_id, config_file, auth_url, auth_code=''):
		cls._config = (domain, id_integration, secret_key, amo_user_id, auth_url, auth_code, config_file)
		return cls

	def __getattr__(cls, key):
		if cls._config is None:
			raise ValueError('AmoCRM config is not initialized')
		if key == 'lead':
			return Lead(cls._config)
		elif key == 'pipeline':
			return Pipeline(cls._config)
		elif key == 'custom_field':
			return CustomField(cls._config)
		elif key == 'customer':
			return Customer(cls._config)
		elif key == 'product':
			return Product(cls._config)
		elif key == 'contact':
			return Contact(cls._config)
		elif key == 'amo':
			return AMO(
				cls._config[0],
				cls._config[1],
				cls._config[2],
				cls._config[3],
				cls._config[4],
				cls._config[5],
				cls._config[6]
			)
		raise AttributeError(key)


class AmoCRM(metaclass=AmoCRMMeta):
	pass
