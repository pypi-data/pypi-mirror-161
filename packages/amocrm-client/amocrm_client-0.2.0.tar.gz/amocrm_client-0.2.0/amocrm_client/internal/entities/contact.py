from .entity import Entity
from .custom_field import CustomField


class Contact(Entity):

	async def add(self, name, first_name=None, last_name=None, custom_fields=None):
		amo = super().amo_init()
		contact = {'name': name}
		if first_name:
			contact['first_name'] = first_name
		if last_name:
			contact['last_name'] = last_name
		if custom_fields:
			cfs = await CustomField(self.config).prepare(custom_fields, 'contact')
			if not cfs['result']:
				return cfs
			contact['custom_fields_values'] = cfs['data']
		response = await amo.contact.add([contact])
		return {'result': True, 'data': response['data'][0]} if response['result'] else response

	async def edit(self, contact_id, name=None, first_name=None, last_name=None):
		amo = super().amo_init()
		new_contact_data = {'id': contact_id}
		if name is not None:
			new_contact_data['name'] = name
		if first_name is not None:
			new_contact_data['first_name'] = first_name
		if last_name is not None:
			new_contact_data['last_name'] = last_name
		response = await amo.contact.edit([new_contact_data])
		return {'result': True, 'data': response['data'][0]} if response['result'] else response

	async def edit_custom_field(self, contact_id, custom_fields):
		amo = super().amo_init()
		new_contact_data = {'id': contact_id}
		cfs = await CustomField(self.config).prepare(custom_fields, 'contact')
		if not cfs['result']:
			return cfs
		new_contact_data['custom_fields_values'] = cfs['data']
		response = await amo.contact.edit([new_contact_data])
		return {'result': True, 'data': response['data'][0]} if response['result'] else response

	async def link_with_lead(self, contact_id, lead_id):
		amo = super().amo_init()
		link = {
			'entity_id': int(contact_id),
			'to_entity_id': int(lead_id),
			'to_entity_type': 'leads'
		}
		response = await amo.contact.add_links([link])
		return {'result': True, 'data': response['data'][0]} if response['result'] else response

	async def link_with_customer(self, contact_id, customer_id):
		amo = super().amo_init()
		link = {
			'entity_id': int(contact_id),
			'to_entity_id': int(customer_id),
			'to_entity_type': 'customers'
		}
		response = await amo.contact.add_links([link])
		return {'result': True, 'data': response['data'][0]} if response['result'] else response
