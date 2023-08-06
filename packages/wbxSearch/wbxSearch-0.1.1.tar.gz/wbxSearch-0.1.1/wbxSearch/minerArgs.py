from wbxSearch.filterArgs import FilterArgs


class MinerArgs:
    def __init__(self, str_args, miner):
        self.miner = miner
        self.str_args = str_args

        """elasticsearch"""
        self.context_subject = None
        self.query = None
        self.irrelevant_score_percent = None
        self.filter = None
        self.max_product = None
        self.boost_query = None
        self.boost_query_percent = None
        self.sorting_group_number = None
        self.search_model = None
        self.adult_filter_show_threshold = None
        self.enrich_response = None
        self.sort_version = None
        self.keep_adult = None

        self.limit = None
        self.arr_urls = []
        self.limit = None
        self.country = None
        self.timeout_between_requests = None
        self.one_by_one_join = None
        # @sort
        self.apply_self_ranker_sales = None
        self.apply_self_ranker_views = None
        self.self_ranker_views_weight = None
        self.self_ranker_sales_weight = None

        self.arr_str_args = self.str_args.split("--")

        self._flag_boost_query = "boost-query"
        self._flag_adult_filter_show_threshold = "adult-filter-show-threshold"
        self._flag_max_product = "max-product"
        self._flag_boost_query_percent = "boost-query-percent"
        self._flag_sorting_group_number = "sorting-group-number"
        self._flag_search_model = "search-model"
        self._flag_enrich_response = "enrich-response"
        self._flag_sort_version = "sort-version"
        self._flag_keep_adult = "keep-adult"

        self._flag_one_by_one_join = "--one-by-one-join"
        self._flag_limit = "limit"
        self._flag_country = "country"
        # @sort
        self._flag_apply_self_ranker_sales = "apply-self-ranker-sales"
        self._flag_apply_self_ranker_views = "apply-self-ranker-views"
        self._flag_self_ranker_views_weight = "self-ranker-views-weight"
        self._flag_self_ranker_sales_weight = "self-ranker-sales-weight"

        self._flag_context_subject = "context-subject"
        self._flag_query = "query"
        self._flag_irrelevant_score_percent = "irrelevant-score-percent"
        self._flag_filter = "filter"
        self._flag_timeout_between_requests = "timeoutBetweenRequests"

        self.parse_args()
        self.filter_object = FilterArgs(self.filter)

    def parse_args(self):
        if self._check_str_args():
            self.search_url()
            self.apply_self_ranker_sales = self._check_and_set_arg(self._flag_apply_self_ranker_sales)
            self.apply_self_ranker_views = self._check_and_set_arg(self._flag_apply_self_ranker_views)
            self.self_ranker_views_weight = self._check_and_set_arg(self._flag_self_ranker_views_weight)
            self.self_ranker_sales_weight = self._check_and_set_arg(self._flag_self_ranker_sales_weight)
            self.one_by_one_join = self._check_and_set_arg(self._flag_one_by_one_join)
            self.query = self._check_and_set_arg(self._flag_query)
            self.limit = self._check_and_set_arg(self._flag_limit)
            self.context_subject = self._check_and_set_arg(self._flag_context_subject)
            self.filter = self._check_and_set_arg(self._flag_filter)
            self.irrelevant_score_percent = self._check_and_set_arg(self._flag_irrelevant_score_percent)
            self.country = self._check_and_set_arg(self._flag_country, separator=" ")
            self.timeout_between_requests = self._check_and_set_arg(self._flag_timeout_between_requests,
                                                                    separator=" ")
            self.max_product = self._check_and_set_arg(self._flag_max_product)
            self.boost_query = self._check_and_set_arg(self._flag_boost_query)
            self.boost_query_percent = self._check_and_set_arg(self._flag_boost_query_percent)
            self.sorting_group_number = self._check_and_set_arg(self._flag_sorting_group_number)
            self.search_model = self._check_and_set_arg(self._flag_search_model)
            self.adult_filter_show_threshold = self._check_and_set_arg(self._flag_adult_filter_show_threshold)
            self.enrich_response = self._check_and_set_arg(self._flag_enrich_response)
            self.sort_version = self._check_and_set_arg(self._flag_sort_version)
            self.keep_adult = self._check_and_set_arg(self._flag_keep_adult)

    def _check_str_args(self) -> bool:
        return True if self.str_args else False

    def _get_arg(self, key, separator="=") -> str:
        """в этой функции достаем аргумент по флагу"""
        result = ""
        for arg in self.arr_str_args:
            if arg.startswith(key):
                arr_key = arg.split(separator)
                result = arr_key[1].replace('"', "")
                break
        return result

    # новое-------------------------------

    def _check_and_set_arg(self, flag_arg: str, separator: str = "="):
        if self._check_flag(flag_arg):
            try:
                return self._set_arg(flag_arg, separator)
            except IndexError:
                return self._set_arg(flag_arg, separator=" ")
        return None

    def _check_flag(self, flag_arg: str):
        return flag_arg in self.str_args

    def _set_arg(self, flag_arg: str, separator: str = "="):
        return self.del_space(self._get_arg(flag_arg, separator))

    # новое-------------------------------



    def search_url(self):
        list_str_args = self.str_args.split(" ")
        for x in list_str_args:
            if x.startswith('"http'):
                self.arr_urls.append(x)

    def construct_url_record(self):
        str_urls = " ".join(self.arr_urls)
        sort = f"{str_urls} @sort: --{self._flag_apply_self_ranker_sales}={self.apply_self_ranker_sales} --{self._flag_apply_self_ranker_views}={self.apply_self_ranker_views}"
        return sort

    def construct_url_record_for_elasticsearch(self):
        list_result = []
        if self.apply_self_ranker_sales:
            list_result.append(f'--{self._flag_apply_self_ranker_sales}={self.apply_self_ranker_sales}')
        if self.apply_self_ranker_views:
            list_result.append(f'--{self._flag_apply_self_ranker_views}={self.apply_self_ranker_views}')
        if self.self_ranker_views_weight:
            list_result.append(
                f'--{self._flag_self_ranker_views_weight}={self.self_ranker_views_weight}')
        if self.self_ranker_sales_weight:
            list_result.append(
                f'--{self._flag_self_ranker_sales_weight}={self.self_ranker_sales_weight}')
        sort = f"@sort: {' '.join(list_result)}"
        return sort

    def create_result_elasticsearch(self):
        """Собираем результат для выдачи, новый str_args, функция для майнера elasticsearch"""
        list_result = []

        if self.context_subject:
            list_result.append(f'--{self._flag_context_subject}="{self.context_subject}"')
        if self.max_product:
            list_result.append(f'--{self._flag_max_product}={self.max_product}')
        if self.query:
            list_result.append(f'--{self._flag_query}="{self.del_sort(self.query)}"')
        if self.keep_adult:
            list_result.append(f'--{self._flag_keep_adult}={self.keep_adult}')
        if self.boost_query:
            list_result.append(f'--{self._flag_boost_query}="{self.boost_query}"')
        if self.boost_query_percent:
            list_result.append(f'--{self._flag_boost_query_percent}={self.boost_query_percent}')
        if self.sorting_group_number:
            list_result.append(f'--{self._flag_sorting_group_number}={self.sorting_group_number}')
        if self.search_model:
            list_result.append(f'--{self._flag_search_model}={self.search_model}')
        if self.sort_version:
            list_result.append(f'--{self._flag_sort_version}={self.sort_version}')
        if self.enrich_response:
            list_result.append(f'--{self._flag_enrich_response}={self.enrich_response}')
        if self.adult_filter_show_threshold:
            list_result.append(f'--{self._flag_adult_filter_show_threshold}'
                               f'={self.adult_filter_show_threshold}')
        if self.irrelevant_score_percent:
            list_result.append(
                f"--{self._flag_irrelevant_score_percent}={self.irrelevant_score_percent}")
        if self.filter:
            list_result.append(f'--{self._flag_filter}="{self.filter_object.get_result_for_write()}"')
        if self.apply_self_ranker_views or self.apply_self_ranker_sales or self.self_ranker_sales_weight or \
                self.self_ranker_views_weight:
            list_result.append(self.construct_url_record_for_elasticsearch())
        return " ".join(list_result)

    def get_result_for_write(self):
        if self.miner == "elasticsearch":
            result = self.create_result_elasticsearch()
            return result
        result = self.str_args
        return result

    def del_space(self, arg):
        if arg[-1:] == " ":
            return arg[:-1]
        return arg

    def del_sort(self, arg):
        if arg[-7:] == " @sort:":
            return arg[:-7]
        return arg

    def __str__(self):
        return self.str_args
