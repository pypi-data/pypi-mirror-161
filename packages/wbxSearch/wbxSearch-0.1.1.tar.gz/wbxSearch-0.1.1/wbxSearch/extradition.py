# 0 (задний фонарь на велосипед) 'Search Query'
# 1 10776176                     'PresetID'
# 2 yes                          'Active'
# 3 common                       'Kind'
# 4 empty                        'Parent'
# 5 elasticsearch (miner)        'Miner'
# 6 miner's parametr 'Miner'     "Miner's args"
# 7 presets/bucket_120           'Shard Kind'
# 8 preset=10776176              'Query'
# 9 ()                           'Category\n'
from wbxSearch.minerArgs import MinerArgs


class Extradition:
    """класс для работы с записями выгрузки"""

    def __init__(self, extradition_arr, len_extradition: tuple[int] = (10,)):
        if isinstance(extradition_arr, str):
            self.extradition_arr = extradition_arr.split("|")
        else:
            self.extradition_arr = extradition_arr

        self.len_extradition = len_extradition

        if self.check_len_extradition() is False:
            print(extradition_arr)
            raise f"Не верный формат выдачи"

        if len(self.extradition_arr) == 10:
            # стандартная длина выдачи
            self.search_query = self.extradition_arr[0]
            self.preset_id = self.extradition_arr[1]
            self.active = self.extradition_arr[2]
            self.kind = self.extradition_arr[3]
            self.parent = self.extradition_arr[4]
            self.miner = self.extradition_arr[5]
            self.miners_args = self.extradition_arr[6]
            self.miners_args_object = MinerArgs(self.miners_args, self.miner)
            self.shard_kind = self.extradition_arr[7]
            self.query = self.extradition_arr[8]
            self.category = self.extradition_arr[9]

    def check_len_extradition(self) -> bool:

        len_extradition_arr = len(self.extradition_arr)

        for value_len in self.len_extradition:
            if len_extradition_arr == value_len:
                return True
        return False

    def get_active(self):
        return True if self.active.lower() == "yes" else False

    def get_param(self, param: str) -> str:
        match param:
            case "search_query":
                return self.search_query
            case "preset_id":
                return self.preset_id
            case "active":
                return self.active
            case "kind":
                return self.kind
            case "parent":
                return self.parent
            case "miner":
                return self.miner
            case "miners_args":
                return self.miners_args
            case "shard_kind":
                return self.shard_kind
            case "query":
                return self.query
            case "category":
                return self.category
            case _:
                raise "Не правильно задан параметр"

    def record_for_write_file(self):
        return f"{self.search_query}|{self.preset_id}|{self.active}|{self.kind}|{self.parent}|{self.miner}|" \
               f"{self.miners_args_object.get_result_for_write()}|" \
               f"{self.shard_kind}|{self.query}|{self.category}".split("|")

    def __str__(self):
        return f"{self.search_query}|{self.preset_id}|{self.active}|{self.kind}|{self.parent}|{self.miner}|{self.miners_args_object.get_result_for_write()}|{self.shard_kind}|{self.query}|{self.category}"
