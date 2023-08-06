import io
import re

import pandas as pd
import requests
from pandas.api.extensions import register_dataframe_accessor

from .config import config


@register_dataframe_accessor("askedith")
class AskEdithAccessor:
    def __init__(self, pandas_obj: pd.DataFrame) -> None:
        self._df = pandas_obj

    def ask(self, question: str) -> pd.DataFrame:
        """
        Use AskEdith to ask a Natural Language Query on a Pandas DataFrame.

        Args:
            question: Natural Language Question (e.g. What was the average sales cycle for each product?)

        Returns:
            DataFrame
        """
        # Write contents to a CSV buffer
        buffer = io.StringIO()
        self._df.to_csv(buffer, index=False)
        buffer.seek(0)

        # Make request
        response = requests.post(
            url=f"{config.API_URL}/api/query/demo",
            data={"question": question},
            files={"DataFrame": buffer},
        )

        body = response.json()

        explanation = body["explanation"]
        explanation = explanation.replace("\n", "")
        for i, part in enumerate(
            filter(lambda part: len(part) > 0, re.split("\s[0-9]+\.\s", explanation))
        ):
            print(f"{i + 1}. {part}")

        return pd.read_csv(io.StringIO(body["csv_file"]))
