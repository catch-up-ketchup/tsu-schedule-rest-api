import shelve


class ShelveStorage:
    """
    Данный класс представляет собой удобный интерфейс для работы с shelve хранилищем
    """
    def __init__(self, path: str):
        self.__path = path

    def update_schedule(self, group: str, new_schedule: dict):
        with shelve.open(self.__path) as storage:
            storage[group] = new_schedule

    def get_schedule(self, group: str) -> dict:
        with shelve.open(self.__path) as storage:
            schedule = storage.get(group)
            if schedule:
                return schedule
            raise Exception('no such group in storage')


shelve_storage = ShelveStorage('./shelve_storage/storage/storage')
