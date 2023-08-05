# All functions computing a name used across components
from typing_extensions import Literal

def get_account_extract_table_name(
    account_id: str,
    client_id: str,
    account_type: str,
    level: Literal['daily', 'hourly'] = 'daily'
    ) -> str:
    return f'{client_id}.{account_type}_extract_{account_id}_campaign_{level}'


def get_input_file_change_notification_name(
    alert_id: int,
    client_id: str
) -> str:
    return f"{alert_id}_{client_id}_file_change_notification"
