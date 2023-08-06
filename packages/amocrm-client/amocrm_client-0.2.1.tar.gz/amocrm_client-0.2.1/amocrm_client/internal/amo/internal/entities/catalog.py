from .entity import Entity


class Catalog(Entity):
    ''' Singleton-класс для работы с каталогами '''
    async def get(self, params={}):  # USE !!!!
        ''' Метод для получения доступных списков в аккаунте. '''
        response = await super().get(f'{self.fulldomain}/api/v4/catalogs', params)
        if response['result']:
            response['data'] = response['data']['_embedded']['catalogs']
        return response

    async def get_elements(self, catalog_id, params={}):  # USE !!!!
        ''' Метод для получения доступных элементов в аккаунте '''
        response = await super().get(f'{self.fulldomain}/api/v4/catalogs/{catalog_id}/elements', params)
        if response['result']:
            response['data'] = response['data']['_embedded']['elements']
        return response
