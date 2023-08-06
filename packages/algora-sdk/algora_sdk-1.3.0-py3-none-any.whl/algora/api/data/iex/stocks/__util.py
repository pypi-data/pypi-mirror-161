def _symbols_request_info() -> dict:
    return {
        "extension": f"ref-data/symbols"
    }


def _historical_prices_request_info(*symbol: str, **kwargs) -> dict:
    request_info = {
        'range': '1m',
        'sort': 'asc'
    }
    request_info.update(kwargs)

    if len(symbol) > 1:
        request_info.update({
            'extension': "stock/market/batch",
            'symbols': ','.join(symbol),
            'types': 'chart'
        })
    else:
        request_info.update({'extension': f"time-series/HISTORICAL_PRICES/{symbol[0]}"})

    return request_info


def _news_request_info(symbol: str, kwargs):
    request_info = {
        "extension": f"time-series/news/{symbol}"
    }
    request_info.update(kwargs)
    return request_info


def _peer_group_request_info(symbol: str) -> dict:
    return {
        "extension": f"stock/{symbol}/peers"
    }
