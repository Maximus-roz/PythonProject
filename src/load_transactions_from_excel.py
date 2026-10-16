from pathlib import Path

import pandas as pd


def load_transactions(path: Path) -> list[dict]:
    df = pd.read_excel(
        path,
        names=[
            "id",
            "state",
            "date",
            "amount",
            "currency_name",
            "currency_code",
            "from",
            "to",
            "description",
        ],
        header=0,
    ).dropna(how="all")
    return df.to_dict(orient="records")


if __name__ == "__main__":
    path = Path(__file__).parent.parent / "data" / "transactions_excel.xlsx"
    print(load_transactions(path))
