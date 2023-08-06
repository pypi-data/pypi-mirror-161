def __build_params(**kwargs) -> dict:
    # default query params
    params = {
        'range': '1m',
        'sort': 'asc'
    }

    params.update(kwargs)
    return params
