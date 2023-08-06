from .entity import Entity
from .custom_field import CustomField
from .contact import Contact


class Customer(Entity):

	async def add(self, name, custom_fields=None):
		amo = super().amo_init()
		customer = {'name': name}
		if custom_fields:
			cfs = await CustomField(self.config).prepare(custom_fields, 'customer')
			if not cfs['result']:
				return cfs
			customer['custom_fields_values'] = cfs['data']
		return await amo.customer.add([customer])

	async def edit_custom_field(self, customer_id, custom_fields):
		amo = super().amo_init()
		new_contact_data = {'id': customer_id}
		cfs = await CustomField(self.config).prepare(custom_fields, 'customer')
		if not cfs['result']:
			return cfs
		new_contact_data['custom_fields_values'] = cfs['data']
		response = await amo.customer.edit([new_contact_data])
		return {'result': True, 'data': response['data'][0]} if response['result'] else response

	async def link_with_contact(self, customer_id, contact_id):
		amo = super().amo_init()
		link = {
			'entity_id': int(customer_id),
			'to_entity_id': int(contact_id),
			'to_entity_type': 'contacts'
		}
		response = await amo.customer.add_links([link])
		return {'result': True, 'data': response['data'][0]} if response['result'] else response

	async def link_with_lead(self, customer_id, lead_id, contact_id):
		link_with_contact = await self.link_with_contact(customer_id, contact_id)
		if not link_with_contact['result']:
			return {'result': False, 'data': f'Cannot link customer [{customer_id}] with contact [{contact_id}]'}
		lead_link = await Contact(self.config).link_with_lead(contact_id, lead_id)
		if not lead_link['result']:
			return {'result': False, 'data': f'Cannot link lead [{lead_id}] with contact [{contact_id}]'}
		return {
			'result': True,
			'data': {
				'customer_id': customer_id,
				'lead_id': lead_id,
				'contact_id': contact_id
			}
		}
