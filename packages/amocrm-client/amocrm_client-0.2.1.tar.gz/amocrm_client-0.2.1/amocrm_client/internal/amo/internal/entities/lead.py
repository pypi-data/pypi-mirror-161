from .entity import Entity
import time


class Lead(Entity):
    ''' Singleton-класс для работы со сделками '''

    async def query(self, query):  # USE !!!!
        ''' Метод для добавление новой сделки '''
        response = await super().get(f'{self.fulldomain}/api/v4/leads?' + query)
        if response['result']:
            response['data'] = response['data']['_embedded']['leads']
        return response

    async def add(self, lead_data):  # USE !!!!
        ''' Метод для добавление новой сделки '''
        response = await super().post(f'{self.fulldomain}/api/v4/leads', lead_data)
        if response['result']:
            response['data'] = response['data']['_embedded']['leads']
        return response

    async def add_unsorted(self, source, lead_data):
        ''' Метод для добавление новой неразобранной сделки '''
        response = await super().post(f'{self.fulldomain}/api/v4/leads/unsorted/' + source, lead_data)
        if response['result']:
            response['data'] = response['data']['_embedded']['unsorted']
        return response

    async def add_links(self, post_data):  # USE !!!!
        response = await super().post(f'{self.fulldomain}/api/v4/leads/link', post_data)
        if response['result']:
            response['data'] = response['data']['_embedded']['links']
        return response

    async def edit(self, edit_data, lead_id=None):  # USE !!!!
        ''' Метод для изменения данных сделки '''
        url = f'{self.fulldomain}/api/v4/leads'
        if lead_id:
            url += f'/{lead_id}'
        response = await super().patch(url, edit_data)
        if response['result'] and not lead_id:
            response['data'] = response['data']['_embedded']['leads']
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
        response = await super().get(f'{self.fulldomain}/api/v4/leads/custom_fields', params)
        if response['result']:
            response['data'] = response['data']['_embedded']['custom_fields']
        return response

    async def get_by_id(self, lead_id, params={}):  # USE !!!!
        ''' Метод для получения информации о сделке по ID '''
        return await super().get(f'{self.fulldomain}/api/v4/leads/{lead_id}', params)
