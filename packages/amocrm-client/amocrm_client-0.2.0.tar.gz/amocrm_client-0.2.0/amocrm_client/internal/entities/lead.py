from .entity import Entity
from .pipeline import Pipeline
from .custom_field import CustomField
from .product import Product
from .customer import Customer


class Lead(Entity):

	async def query(self, query=None):
		amo = super().amo_init()
		response = await amo.lead.query(query)
		return {'result': True, 'data': response} if response['result'] else response

	async def add(self, lead_name, pipeline_name, status_name=None, custom_fields=None, price=None):
		amo = super().amo_init()
		pipelines = await Pipeline(self.config).get()
		if not pipelines['result']:
			return pipelines
		if pipeline_name not in pipelines['data'].keys():
			return {'result': False, 'data': 'Invalid pipeline name'}

		lead = {
			'name': lead_name,
			'pipeline_id': int(pipelines['data'][pipeline_name]['id'])
		}
		if custom_fields:
			cfs = await CustomField(self.config).prepare(custom_fields, 'lead')
			if not cfs['result']:
				return cfs
			lead['custom_fields_values'] = cfs['data']

		if status_name and status_name not in pipelines['data'][pipeline_name]['statuses']:
			return {'result': False, 'data': 'Invalid status name'}
		elif status_name:
			lead['status_id'] = int(pipelines['data'][pipeline_name]['statuses'][status_name]['id'])
		if price:
			lead['price'] = int(price)
		response = await amo.lead.add([lead])
		return {'result': True, 'data': response['data'][0]} if response['result'] else response

	async def add_unsorted(self, source, source_name, pipeline_name, source_uid, metadata, leadata={}, condata={}, comdata={}):
		amo = super().amo_init()
		pipelines = await Pipeline(self.config).get()
		if not pipelines['result']:
			return pipelines
		if pipeline_name not in pipelines['data'].keys():
			return {'result': False, 'data': 'Invalid pipeline name'}

		lead_data = {
			'source_uid': source_uid,
			'source_name': source_name,
			'pipeline_id': int(pipelines['data'][pipeline_name]['id']),
			'_embedded': {
				'leads': [leadata],
				'contacts': [condata],
				'companies': [comdata]
			},
			'metadata': metadata
		}
		response = await amo.lead.add_unsorted(source, [lead_data])
		return response

	async def edit_price(self, lead_id, new_price):
		amo = super().amo_init()
		new_lead_data = {
			'id': lead_id,
			'price': new_price
		}
		response = await amo.lead.edit([new_lead_data])
		return {'result': True, 'data': response['data'][0]} if response['result'] else response

	async def edit_custom_field(self, lead_id, custom_fields):
		amo = super().amo_init()
		new_lead_data = {'id': lead_id}
		cfs = await CustomField(self.config).prepare(custom_fields, 'lead')
		if not cfs['result']:
			return cfs
		new_lead_data['custom_fields_values'] = cfs['data']
		response = await amo.lead.edit([new_lead_data])
		return {'result': True, 'data': response['data'][0]} if response['result'] else response

	async def add_product(self, lead_id, product_name, product_count=1):
		amo = super().amo_init()
		products = await Product(self.config).get_all()
		if not products['result']:
			return products
		products = products['data']
		if product_name not in products['products']:
			return {'result': False, 'data': 'Invalid product name'}
		else:
			link = {
				'entity_id': int(lead_id),
				'to_entity_id': int(products['products'][product_name]['id']),
				'to_entity_type': 'catalog_elements',
				'metadata': {
					'quantity': product_count,
					'catalog_id': products['id']
				}
			}
			response = await amo.lead.add_links([link])
			return {'result': True, 'data': response['data'][0]} if response['result'] else response

	async def change_status(self, lead_id, status_name):
		amo = super().amo_init()
		lead = await amo.lead.get_by_id(lead_id)
		if not lead['result']:
			return lead
		lead = lead['data']
		pipelines = await Pipeline(self.config).get(True)
		if not pipelines['result']:
			return pipelines
		elif status_name and status_name not in pipelines['data'][lead['pipeline_id']]['statuses']:
			return {'result': False, 'data': 'Invalid status name'}
		update_lead = {
			'id': lead_id,
			'status_id': int(pipelines['data'][lead['pipeline_id']]['statuses'][status_name]['id'])
		}
		response = await amo.lead.edit([update_lead])
		return {'result': True, 'data': response['data'][0]} if response['result'] else response

	async def change_pipeline(self, lead_id, pipeline_name, status_name):
		amo = super().amo_init()
		pipelines = await Pipeline(self.config).get()
		if not pipelines['result']:
			return pipelines
		if pipeline_name not in pipelines['data'].keys():
			return {'result': False, 'data': 'Invalid pipeline name'}

		update_lead = {
			'id': lead_id,
			'pipeline_id': int(pipelines['data'][pipeline_name]['id'])
		}
		if status_name and status_name not in pipelines['data'][pipeline_name]['statuses']:
			return {'result': False, 'data': 'Invalid status name'}
		elif status_name:
			update_lead['status_id'] = int(pipelines['data'][pipeline_name]['statuses'][status_name]['id'])
		response = await amo.lead.edit([update_lead])
		return {'result': True, 'data': response['data'][0]} if response['result'] else response

	async def link_with_contact(self, lead_id, contact_id):
		amo = super().amo_init()
		link = {
			'entity_id': int(lead_id),
			'to_entity_id': int(contact_id),
			'to_entity_type': 'contacts'
		}
		response = await amo.lead.add_links([link])
		return {'result': True, 'data': response['data'][0]} if response['result'] else response

	async def link_with_customer(self, lead_id, customer_id, contact_id):
		link_with_contact = await self.link_with_contact(lead_id, contact_id)
		if not link_with_contact['result']:
			return {'result': False, 'data': f'Cannot link lead [{lead_id}] with contact [{contact_id}]'}
		customer_link = await Customer(self.config).link_with_contact(customer_id, contact_id)
		if not customer_link['result']:
			return {'result': False, 'data': f'Cannot link customer [{customer_id}] with contact [{contact_id}]'}
		return {
			'result': True,
			'data': {
				'lead_id': lead_id,
				'customer_id': customer_id,
				'contact_id': contact_id
			}
		}
