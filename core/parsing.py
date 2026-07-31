import base64
import io
import pandas as pd


def parse_time_column(values) -> pd.Series:
    series = pd.Series(values)
    cleaned = series.astype(str).str.strip()
    cleaned = cleaned.replace({"": pd.NA, "nan": pd.NA, "None": pd.NA, "none": pd.NA})

    if cleaned.isna().all():
        return pd.Series(pd.NaT, dtype="datetime64[ns]")

    numeric = pd.to_numeric(cleaned, errors="coerce")
    non_empty = cleaned.notna()

    if non_empty.sum() and numeric.notna().sum() == non_empty.sum():
        return numeric.astype(float)

    parsed = pd.to_datetime(cleaned, dayfirst=True, errors="coerce")
    if parsed.notna().sum() > 0:
        return parsed

    return cleaned


def decode_upload(contents: str) -> bytes:
    if not contents or ',' not in contents:
        raise ValueError("Invalid upload")

    _, content_string = contents.split(',', 1)
    return base64.b64decode(content_string)


def parse_csv(contents: bytes) -> pd.DataFrame:
    return pd.read_csv(io.StringIO(contents.decode("utf-8")))


def parse_tsf(contents: bytes) -> list[str]:
    return contents.decode("utf-8").splitlines()