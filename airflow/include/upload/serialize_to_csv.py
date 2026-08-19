import io

def records_to_csv_bytes(records: list[dict]) -> bytes:
    df = pd.DataFrame.from_records(records)
    buffer = io.StringIO()
    df.to_csv(buffer, index=False)
    return buffer.getvalue().encode("utf-8")