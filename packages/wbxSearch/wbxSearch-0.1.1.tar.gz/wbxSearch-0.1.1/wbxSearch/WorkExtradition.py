from wbxSearch import WorkCSV, Extradition


class WorkExtradition:
    def __init__(self, path_read_file: str, path_write_file: str = ""):
        self.csv = WorkCSV(path_file=path_read_file)
        self._data_csv = self.csv.read_csv()
        self.path_write_file = path_write_file
        self._list_ex = [Extradition(x) for x in self._data_csv]

        """в этот лист записываются результаты поиска выдач, потом из этого листа
        # формируем этот файл, либо удалям эти выдачи из листа list_ex"""
        self._new_list_ex = []

        if self.path_write_file:
            self._new_csv = WorkCSV(path_file=path_write_file)

    def _param_search(self, param: str,
                      value_param: str,
                      complete_match: bool = True,
                      contains: bool = False) -> list:
        """
        ищем записи по параметру в выдачах
        :param param: наименование параметра по которому ищем(всего их 10, список в шапке класса Extradition)
        :param value_param: значение параметра по которому ищем
        :param complete_match: полное совпадение
        :param contains: наоборот ищем выдачи где нет value_param(True - ищем где нет value_param, по умолчанию False)
        :return: list с подходящими выдачами
        """
        # поиск по полному совпадению
        if complete_match and contains is False:
            result_list = [x for x in self._list_ex if value_param == x.get_param(param)]
        # поиск по частичному совпадению
        elif complete_match is False and contains is False:
            result_list = [x for x in self._list_ex if value_param in x.get_param(param)]
        # попадают в результат все выдачи где нет полного совпадения
        elif complete_match and contains:
            result_list = [x for x in self._list_ex if value_param != x.get_param(param)]
        # попадают в результат все выдачи где нет частичного совпадения
        elif complete_match is False and contains:
            result_list = [x for x in self._list_ex if value_param not in x.get_param(param)]
        else:
            raise "Не правильно выставлены условия"

        self._new_list_ex += result_list
        return result_list

    def search_query_search(self, search_query: str, complete_match: bool = True, contains: bool = False) -> list:
        """
        ищем записи по 1 столбцу в выдачах
        :param search_query: наименование search_query по которому ищем
        :param complete_match: полное совпадение
        :param contains: наоборот ищем выдачи где нет search_query(True - ищем где нет value_param, по умолчанию False)
        :return: list с подходящими выдачами
        """
        return self._param_search("search_query", search_query, complete_match, contains)

    def search_preset_id(self, preset_id: str, complete_match: bool = True, contains: bool = False) -> list:
        """
        ищем записи по 2 столбцу в выдачах
        :param preset_id: наименование preset_id по которому ищем
        :param complete_match: полное совпадение
        :param contains: наоборот ищем выдачи где нет preset_id(True - ищем где нет value_param, по умолчанию False)
        :return: list с подходящими выдачами
        """
        return self._param_search("preset_id", preset_id, complete_match, contains)

    def active_search(self, active: bool = True) -> list:
        """ищем записи по 3 столбцу в выдачах, это поле актив, оно бывает двух видов yes и no,
        по умолчанию ищем yes"""
        result_list = [x for x in self._list_ex if x.get_active() is active]
        self._new_list_ex += result_list
        return result_list

    def kind_search(self, kind: str, complete_match: bool = True, contains: bool = False) -> list:
        """
        ищем записи по 4 столбцу в выдачах
        :param kind: наименование kind по которому ищем
        :param complete_match: полное совпадение
        :param contains: наоборот ищем выдачи где нет kind(True - ищем где нет kind, по умолчанию False)
        :return: list с подходящими выдачами
        """
        return self._param_search("kind", kind, complete_match, contains)

    def parent_search(self, parent: str, complete_match: bool = True, contains: bool = False) -> list:
        """
        ищем записи по 5 столбцу в выдачах
        :param parent: наименование parent по которому ищем
        :param complete_match: полное совпадение
        :param contains: наоборот ищем выдачи где нет parent(True - ищем где нет parent, по умолчанию False)
        :return: list с подходящими выдачами
        """
        return self._param_search("parent", parent, complete_match, contains)

    def miner_search(self, miner: str, complete_match: bool = True, contains: bool = False) -> list:
        """
        ищем записи по 6 столбцу в выдачах
        :param miner: наименование parent по которому ищем
        :param complete_match: полное совпадение
        :param contains: наоборот ищем выдачи где нет miner(True - ищем где нет miner, по умолчанию False)
        :return: list с подходящими выдачами
        """
        return self._param_search("miner", miner, complete_match, contains)

    def miners_args_search(self, miners_args: str, complete_match: bool = True, contains: bool = False) -> list:
        """
        ищем записи по 7 столбцу в выдачах
        :param miners_args: наименование parent по которому ищем
        :param complete_match: полное совпадение
        :param contains: наоборот ищем выдачи где нет miners_args(True - ищем где нет miners_args, по умолчанию False)
        :return: list с подходящими выдачами
        """
        # TODO miners_args это самостоятельный объект с разными параметрами, данная функция осуществляет работу с
        #  miners_args как с строкой, нужна дополнительная функция по поиску по объекту miners_args
        return self._param_search("miners_args", miners_args, complete_match, contains)

    def shard_kind_search(self, shard_kind: str, complete_match: bool = True, contains: bool = False) -> list:
        """
        ищем записи по 8 столбцу в выдачах
        :param shard_kind: наименование parent по которому ищем
        :param complete_match: полное совпадение
        :param contains: наоборот ищем выдачи где нет shard_kind(True - ищем где нет shard_kind, по умолчанию False)
        :return: list с подходящими выдачами
        """
        return self._param_search("shard_kind", shard_kind, complete_match, contains)

    def query_search(self, query: str, complete_match: bool = True, contains: bool = False) -> list:
        """
        ищем записи по 9 столбцу в выдачах
        :param query: наименование parent по которому ищем
        :param complete_match: полное совпадение
        :param contains: наоборот ищем выдачи где нет query(True - ищем где нет query, по умолчанию False)
        :return: list с подходящими выдачами
        """
        return self._param_search("query", query, complete_match, contains)

    def category_search(self, category: str, complete_match: bool = True, contains: bool = False) -> list:
        """
        ищем записи по 10 столбцу в выдачах
        :param category: наименование parent по которому ищем
        :param complete_match: полное совпадение
        :param contains: наоборот ищем выдачи где нет query
        :return: list с подходящими выдачами
        """
        return self._param_search("category", category, complete_match, contains)

    def get_new_list_ex(self):
        return self._new_list_ex

    def write_file(self) -> bool:
        """записываем результат в файл у которого путь path_write_file"""
        if self.path_write_file == "":
            raise "Не указан path_write_file"
        if not self._new_list_ex:
            self._new_csv.write_csv([])
            return True

        new_data_csv = [x.record_for_write_file() for x in self._new_list_ex]
        self._new_csv.write_csv(new_data_csv)
        return True
