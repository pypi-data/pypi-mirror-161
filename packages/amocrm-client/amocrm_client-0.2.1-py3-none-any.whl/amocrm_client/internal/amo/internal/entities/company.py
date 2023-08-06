from .entity import Entity
import time


class Company(Entity):
    ''' Singleton-класс для работы с компаниями '''

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
        response = await super().get(f'{self.fulldomain}/api/v4/companies/custom_fields', params)
        if response['result']:
            response['data'] = response['data']['_embedded']['custom_fields']
        return response
