import base64
import io
import pandas as pd


def decode_upload(contents: str) -> bytes:
    if not contents or ',' not in contents:
        raise ValueError("Invalid upload payload")

    _, content_string = contents.split(',', 1)
    return base64.b64decode(content_string)


def parse_csv(contents: bytes) -> pd.DataFrame:
    return pd.read_csv(io.StringIO(contents.decode("utf-8")))


def parse_tsf(contents: bytes) -> list[str]:
    return contents.decode("utf-8").splitlines()