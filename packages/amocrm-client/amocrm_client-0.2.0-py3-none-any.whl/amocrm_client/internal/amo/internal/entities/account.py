from .entity import Entity


class Account(Entity):
    ''' Класс для получения параметров аккаунта (раздел AMO API: Параметры аккаунта) '''
    async def get(self):
        ''' Получение параметров аккаунта '''
        return super().get(f'{self.fulldomain}/api/v4/account')
