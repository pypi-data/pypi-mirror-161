from .entity import Entity


class Pipeline(Entity):
    ''' Singleton-класс для работы с воронками и статусами '''

    async def get(self):  # USE !!!!
        ''' Метод для получения воронок '''
        response = await super().get(f'{self.fulldomain}/api/v4/leads/pipelines')
        if response['result']:
            response['data'] = response['data']['_embedded']['pipelines']
        return response
