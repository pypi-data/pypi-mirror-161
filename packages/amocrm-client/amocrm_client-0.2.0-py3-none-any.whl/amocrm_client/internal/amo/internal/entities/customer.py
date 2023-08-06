import time
from .entity import Entity


class Customer(Entity):

    async def add(self, customers_data):  # USE !!!!
        ''' Метод для добавление нового покупателя '''
        response = await super().post(f'{self.fulldomain}/api/v4/customers', customers_data)
        if response['result']:
            response['data'] = response['data']['_embedded']['customers']
        return response

    async def edit(self, edit_data, customer_id=None):  # USE !!!!
        ''' Метод для изменения данных покупателя '''
        url = f'{self.fulldomain}/api/v4/customers'
        if customer_id:
            url += f'/{customer_id}'
        response = await super().patch(url, edit_data)
        if response['result'] and not customer_id:
            response['data'] = response['data']['_embedded']['customers']
        return response

    async def add_links(self, post_data):  # USE !!!!
        response = await super().post(f'{self.fulldomain}/api/v4/customers/link', post_data)
        if response['result']:
            response['data'] = response['data']['_embedded']['links']
        return response

    async def get_all_custom_fields(self):  # USE !!!!
        limit = 50
        page = 1
        cfs = await self.get_custom_fields({'limit': limit, 'page': page})
        if not cfs['result']:
            return cfs
        result = cfs['data']
        while cfs['result'] and len(cfs['data']) >= limit:
            page += 1
            cfs = await self.get_custom_fields({'limit': limit, 'page': page})
            if cfs['result']:
                result += cfs['data']
            if page % 7 == 0:
                time.sleep(1)
        return {'result': True, 'data': result} if cfs['result'] else cfs

    async def get_custom_fields(self, params={}):  # USE !!!!
        response = await super().get(f'{self.fulldomain}/api/v4/customers/custom_fields', params)
        if response['result']:
            response['data'] = response['data']['_embedded']['custom_fields']
        return response
