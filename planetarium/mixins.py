class QueryParamsTransform:
    @staticmethod
    def query_params_to_int(query_param):
        return [int(str_id) for str_id in query_param.split(",")]
