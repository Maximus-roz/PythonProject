from pathlib import Path

import pandas as pd


def load_transactions_csv(path: Path) -> list[dict]:
    try:
        df = pd.read_csv(
            path,
            sep=";",
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
            encoding="utf-8",
        ).dropna(how="all")
        return df.to_dict(orient="records")
    except Exception:
        return []


if __name__ == "__main__":
    path = Path(__file__).parent.parent / "data" / "transactions.csv"
    result_csv = load_transactions_csv(path)
    print(result_csv)
