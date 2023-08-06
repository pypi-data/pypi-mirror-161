def get_query_string(*, file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()


def make_query(*, context, query: str = None, variables: dict = None, file_path: str = None):
    if query is None and file_path is None:
        raise Exception('Either `query` or `file_path` are required. Please provide 1.')
    elif query is not None and file_path is not None:
        raise Exception('Ambiguous: provide only 1 of `query` or `file_path`.')
    else:
        query = query if query else get_query_string(file_path=file_path)

    variables = variables if variables else {}
    gql = context.env_data['gql_url']
    data = {'query': query, 'variables': variables}

    # selenium
    if hasattr(context, 'session'):
        return context.request.post(
            url=gql,
            data=data
        )
    # playwright
    else:
        return context.session.post(
            url=gql,
            json=data
        )
