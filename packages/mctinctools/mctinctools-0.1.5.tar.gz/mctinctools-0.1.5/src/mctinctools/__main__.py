"""Main tools."""

# import json
import pandas as pd

# from rich import print as richprint
from dotenv import load_dotenv

# from requests import request
from requests.exceptions import ConnectionError as req_ConnectionError
from requests.exceptions import Timeout, TooManyRedirects

# import click

load_dotenv()


def get_weworked_with_requests_users_with_groupby(
    file_name_input: str,
    file_name_output: str,
    file_name_feather: str,
    data_source: str,
) -> pd.DataFrame:
    """Weworked processing using json file as input."""
    try:
        data_frame = pd.read_json(file_name_input)
        active = data_frame["Active"]
        disabled = data_frame["Disabled"]
        pending = data_frame["Pending"]

        data_frame_active = pd.DataFrame(active[0])
        data_frame_disabled = pd.DataFrame(disabled[0])
        data_frame_pending = pd.DataFrame(pending)

        data_frame_active["source"] = "Active"
        data_frame_disabled["source"] = "Disabled"
        data_frame_pending["source"] = "Pending"

        data_frame_active.to_feather(file_name_feather)

        # feather_data = pd.read_feather(file_name_feather)
        # richprint(feather_data)

        # the if is to catch where data is missing such as in weworked

        if not data_frame_pending.shape.count(1) <= 1:
            frames = [data_frame_active, data_frame_disabled, data_frame_pending]

        else:
            frames = [data_frame_active, data_frame_disabled]

        data_frame_all = pd.concat(frames)
        data_frame_all.rename(
            columns={
                "lastName": "last_name",
                "firstName": "first_name",
                "userId": "user_id",
            },
            inplace=True,
        )

        data_frame_all.set_index("user_id", inplace=True)
        data_frame_all.insert(0, "data_source", data_source, True)

        # richprint(data_frame_all.head())

        data_frame_all.to_excel(file_name_output)
        return data_frame_all

    except (req_ConnectionError, Timeout, TooManyRedirects) as _error:
        raise ValueError("Investigate error with API") from _error
