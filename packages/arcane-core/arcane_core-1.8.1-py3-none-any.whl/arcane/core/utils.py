from typing import Union

from .exceptions import BadRequestError
from .types import AttributionModel


def check_all_accounts_available(attribution_model: Union[dict, AttributionModel]):
    """
    Check if an account is not available in pilot
    :raises BadRequestError if an account has not run yet
    """
    for scope in attribution_model.get('scope').values():
        for account in scope:
            if not account.get('first_available_date'):
                raise BadRequestError(
                    f"Account {account.get('account_id')} is not available")


def add_backfill_suffix(backfill: bool=False):
    if backfill:
        return "_backfill"
    else:
        return ""
