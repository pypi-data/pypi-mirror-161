from .entity import Entity


class CustomField(Entity):

	async def get(self, entity_type):
		amo = super().amo_init()
		if entity_type == 'lead':
			all_cfs = await amo.lead.get_all_custom_fields()
		elif entity_type == 'company':
			all_cfs = await amo.company.get_all_custom_fields()
		elif entity_type == 'contact':
			all_cfs = await amo.contact.get_all_custom_fields()
		elif entity_type == 'customer':
			all_cfs = await amo.customer.get_all_custom_fields()
		else:
			return {'result': False, 'data': 'No such entity type.'}
		if not all_cfs['result']:
			return all_cfs
		return {'result': True, 'data': {cf['name']: cf for cf in all_cfs['data']}}

	async def prepare(self, custom_fields, entity_type):
		cfs = await self.get(entity_type)
		if not cfs['result']:
			return {'result': False, 'data': 'Getting custom fields error'}
		result = []
		for cf_name in custom_fields.keys():
			if cf_name not in cfs['data']:
				continue
			cf = {'field_id': cfs['data'][cf_name]['id']}
			if isinstance(custom_fields[cf_name], list):
				cf['values'] = [{'value': val} for val in custom_fields[cf_name]]
			else:
				cf['values'] = [{'value': custom_fields[cf_name]}]
			result.append(cf)
		return {'result': True, 'data': result}
