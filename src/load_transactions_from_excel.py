from pathlib import Path
import pandas as pd


def load_transactions(path: Path) -> pd.DataFrame:
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
    return df


if __name__ == "__main__":
    path = Path(__file__).parent.parent / "data" / "transactions.xlsx"
    print(load_transactions(path))
