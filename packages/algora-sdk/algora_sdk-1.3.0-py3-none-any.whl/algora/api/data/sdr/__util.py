from typing import Optional, Union, Any, Dict, List

from algora.api.data.sdr.enum import Repository, AssetClass
from algora.api.data.sdr.model import APIFieldFilter, FieldFilter, LogicalDisplayName, DataFilter


def __transform_filter(filter: Union[FieldFilter, APIFieldFilter]) -> APIFieldFilter:
    if isinstance(filter, APIFieldFilter):
        return filter

    return APIFieldFilter(
        logical_display=LogicalDisplayName(
            logical_name=filter.field,
            display_name=filter.field
        ),
        operator=filter.operator,
        selected_values=filter.selected_values
    )


def transform_data_filter(data_filter: Optional[DataFilter]) -> Optional[Dict[str, Any]]:
    """
    Transforms a data filter to dict.

    Args:
        data_filter (Optional[DataFilter]): Data filter to convert to a dict

    Returns:
        Optional[Dict[str, Any]]: A dict representation of a data filter
    """
    if data_filter is not None:
        transformed_filter = DataFilter(
            date_range=data_filter.date_range,
            filters=[__transform_filter(f) for f in data_filter.filters]
        )

        return transformed_filter.dict()

    return None


def _get_by_date_request_info(asset_class: AssetClass, date: str, repos: Optional[List[Repository]] = None) -> dict:
    if repos is None:
        repos = [Repository.CME, Repository.DTCC, Repository.ICE]

    repos_param = ",".join([repo.name for repo in repos])
    return {
        'endpoint': f"data/sdr/{asset_class.value}/{date}?repository={repos_param}"
    }


def _get_distinct_in_field_request_info(asset_class: AssetClass, field: str) -> dict:
    return {
        'endpoint': f"data/sdr/{asset_class.value}/{field}/distinct"
    }


def _commodity_request_info(filter: Optional[DataFilter] = None) -> dict:
    return {
        'id': "2880e242-8db4-49e2-aad3-e0339931582e",
        'json': transform_data_filter(filter)
    }


def _credit_request_info(filter: Optional[DataFilter] = None) -> dict:
    return {
        'id': "04863ce6-b179-420c-bef4-eb71f5391141",
        'json': transform_data_filter(filter)
    }


def _equity_request_info(filter: Optional[DataFilter] = None) -> dict:
    return {
        'id': "0f839686-a878-473b-a8a9-d2de2dcdd42c",
        'json': transform_data_filter(filter)
    }


def _forex_request_info(filter: Optional[DataFilter] = None) -> dict:
    return {
        'id': "f1137a7c-13db-451b-9603-f17dfa8bb147",
        'json': transform_data_filter(filter)
    }


def _rates_request_info(filter: Optional[DataFilter] = None) -> dict:
    return {
        'id': "a812f19c-354c-48e9-b86e-af055c631fcc",
        'json': transform_data_filter(filter)
    }
