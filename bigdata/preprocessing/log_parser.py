import re
import sys
from pathlib import Path
from datetime import datetime

import pyarrow as pa
import pyarrow.parquet as pq

from schema import AccessLogRecord


LOG_PATTERN = re.compile(
    r'^(?P<ip>\S+) '
    r'\S+ \S+ '
    r'\[(?P<timestamp>[^\]]+)\] '
    r'"(?P<method>\S+) (?P<url>.*?) (?P<protocol>HTTP/\d\.\d)" '
    r'(?P<status_code>\d{3}) '
    r'(?P<response_size>\d+) '
    r'"(?P<referer>.*?)" '
    r'"(?P<user_agent>.*?)" '
    r'"(?P<extra>.*?)"$'
)


DATETIME_FORMAT = "%d/%b/%Y:%H:%M:%S %z"

BATCH_SIZE = 10_000


PARQUET_SCHEMA = pa.schema([
    ("ip", pa.string()),
    ("timestamp", pa.timestamp("us")),
    ("method", pa.string()),
    ("url", pa.string()),
    ("protocol", pa.string()),
    ("status_code", pa.int64()),
    ("response_size", pa.int64()),
    ("referer", pa.string()),
    ("user_agent", pa.string()),
])


def parse_line(line: str) -> AccessLogRecord:

    line = line.rstrip("\n")

    match = LOG_PATTERN.match(line)

    if not match:
        raise ValueError(
            "Log line does not match expected Nginx format"
        )

    data = match.groupdict()

    timestamp = datetime.strptime(
        data["timestamp"],
        DATETIME_FORMAT
    )

    return AccessLogRecord(
        ip=data["ip"],
        timestamp=timestamp,
        method=data["method"],
        url=data["url"],
        protocol=data["protocol"],
        status_code=int(data["status_code"]),
        response_size=int(data["response_size"]),
        referer=data["referer"],
        user_agent=data["user_agent"],
    )


def write_batch(writer, records):

    if not records:
        return

    table = pa.Table.from_pylist(
        records,
        schema=PARQUET_SCHEMA
    )

    writer.write_table(table)

    records.clear()


def process_file(
    input_file: Path,
    output_file: Path,
    error_file: Path,
):

    output_file.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    error_file.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    total_lines = 0
    valid_lines = 0
    invalid_lines = 0

    records = []

    writer = None

    try:

        with input_file.open(
            "r",
            encoding="utf-8",
            errors="replace"
        ) as source, error_file.open(
            "w",
            encoding="utf-8"
        ) as errors:

            for line_number, line in enumerate(
                source,
                start=1
            ):

                total_lines += 1

                try:

                    record = parse_line(line)

                    records.append({
                        "ip": record.ip,
                        "timestamp": record.timestamp,
                        "method": record.method,
                        "url": record.url,
                        "protocol": record.protocol,
                        "status_code": record.status_code,
                        "response_size": record.response_size,
                        "referer": record.referer,
                        "user_agent": record.user_agent,
                    })

                    valid_lines += 1

                    if len(records) >= BATCH_SIZE:

                        if writer is None:

                            writer = pq.ParquetWriter(
                                output_file,
                                PARQUET_SCHEMA,
                                compression="snappy"
                            )

                        write_batch(
                            writer,
                            records
                        )

                except Exception as exc:

                    invalid_lines += 1

                    errors.write(
                        f"Line {line_number}: {exc}\n"
                    )

                    errors.write(line)

        # Write remaining records
        if records:

            if writer is None:

                writer = pq.ParquetWriter(
                    output_file,
                    PARQUET_SCHEMA,
                    compression="snappy"
                )

            write_batch(
                writer,
                records
            )

    finally:

        if writer is not None:
            writer.close()

    print()
    print("Processing completed")
    print("--------------------")
    print(f"Total lines   : {total_lines}")
    print(f"Valid lines   : {valid_lines}")
    print(f"Invalid lines : {invalid_lines}")

    if total_lines > 0:

        success_rate = (
            valid_lines / total_lines
        ) * 100

        print(
            f"Success rate  : {success_rate:.2f}%"
        )

    print()
    print("Integrity check")
    print("----------------")

    if total_lines == valid_lines + invalid_lines:

        print(
            "PASS: Total = Valid + Invalid"
        )

    else:

        print(
            "FAIL: Record count mismatch"
        )

        sys.exit(1)


def main():

    project_root = (
        Path(__file__).resolve().parents[2]
    )

    input_file = (
        project_root
        / "data"
        / "raw"
        / "access.log"
    )

    output_file = (
        project_root
        / "data"
        / "processed"
        / "access_logs"
        / "access_logs.parquet"
    )

    error_file = (
        project_root
        / "data"
        / "processed"
        / "parser_errors"
        / "parser_errors.log"
    )

    if not input_file.exists():

        print(
            f"Input file not found: {input_file}"
        )

        sys.exit(1)

    print(
        f"Input : {input_file}"
    )

    print(
        f"Output: {output_file}"
    )

    print(
        f"Batch size: {BATCH_SIZE}"
    )

    process_file(
        input_file,
        output_file,
        error_file
    )


if __name__ == "__main__":
    main()