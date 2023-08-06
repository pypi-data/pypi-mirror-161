from .entity import Entity


class Product(Entity):

	async def get_all(self):
		amo = super().amo_init()
		catalogs = await amo.catalog.get()
		if not catalogs['result']:
			return {'result': False, 'data': 'Error: cannot get catalogs'}
		filter_catalogs = list(filter(lambda catalog: catalog['name'] == 'Товары', catalogs['data']))
		if len(filter_catalogs) == 0:
			return {'result': False, 'data': 'Products catalog does not exist'}

		result = {'id': filter_catalogs[0]['id'], 'name': filter_catalogs[0]['name']}
		products = await amo.catalog.get_elements(filter_catalogs[0]['id'])
		if not products['result']:
			return {'result': False, 'data': 'Error: cannot get catalogs elements'}
		result['products'] = {product['name']: product for product in products['data']}
		return {'result': True, 'data': result}
