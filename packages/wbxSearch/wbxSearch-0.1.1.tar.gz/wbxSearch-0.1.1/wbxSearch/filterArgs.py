class FilterArgs:
    _list_args = ("subjectId", "parentSubjectId", "parentSubject", "brandId")

    def __init__(self, str_args):
        self.str_args = str_args
        self.subject_id = ""
        self.parent_subject_id = ""
        self.parent_subject = ""
        self.brand_id = ""

        self._flag_subject_id = "subjectId"
        self._flag_parent_subject_id = "parentSubjectId"
        self._flag_parent_subject = "parentSubject"
        self._flag_brand_id = "brandId"

        self.parse_args()

    def parse_args(self):
        if self.str_args:
            if self._check_subject_id():
                self._set_subject_id()
            if self._check_parent_subject_id():
                self._set_parent_subject_id()
            if self._check_parent_subject():
                self._set_parent_subject()
            if self._check_brand_id():
                self._set_brand_id()

    def _get_arg(self, key) -> str:
        """в этой функции достаем аргумент по флагу"""
        result = ""

        if self.str_args.startswith(key):
            result = self.str_args.split(":")[1]

        return result

    def _check_subject_id(self) -> bool:
        return self._flag_subject_id in self.str_args

    def _set_subject_id(self):
        self.subject_id = self._get_arg(self._flag_subject_id)

    def _check_parent_subject_id(self) -> bool:
        return self._flag_parent_subject_id in self.str_args

    def _set_parent_subject_id(self):
        self.parent_subject_id = self._get_arg(self._flag_parent_subject_id)

    def _check_parent_subject(self) -> bool:
        return self._flag_parent_subject in self.str_args

    def _set_parent_subject(self):
        self.parent_subject = self._get_arg(self._flag_parent_subject).replace("\\", '\\"')

    def _check_brand_id(self) -> bool:
        return self._flag_brand_id in self.str_args

    def _set_brand_id(self):
        self.brand_id = self._get_arg(self._flag_brand_id)

    def __str__(self):
        return self.del_space(self.str_args)

    def get_result_for_write(self):
        # TODO: супер костыли, удаляем пробел и @sort с конца строки, нужно передалть
        return self.del_sort(self.del_space(self.str_args)).replace("\\", '\\"')
        """пока проблемы с этой функцией, нужно подумать как обрабатывать когда несколько аргументов в фильтре
        кейс не частый, но такие есть"""
        if self.str_args is None:
            return ""

        list_result = []
        if self.parent_subject_id:
            list_result.append(f"{self._flag_parent_subject_id}:{self.del_space(self.parent_subject_id)}")
        if self.parent_subject:
            if self.parent_subject_id:
                pass
            else:
                list_result.append(f"{self._flag_parent_subject}:{self.del_space(self.parent_subject)}")
        if self.subject_id:
            list_result.append(f"{self._flag_subject_id}:{self.del_space(self.subject_id)}")
        if self.brand_id:
            list_result.append(f"{self._flag_brand_id}:{self.del_space(self.brand_id)}")
        return " OR ".join(list_result)

    def del_space(self, arg):
        if arg[-1:] == " ":
            return arg[:-1]
        return arg

    def del_sort(self, arg):
        if arg[-7:] == " @sort:":
            return arg[:-7]
        return arg

    def check_filter_args(self):
        """функция возвращает tuple с аргументами фильтра
        пример: ("brandId",) или ("brandId","subjectId",)"""
        pass
