import logging
from argparse import ArgumentParser

from castor_extractor.visualization import qlik  # type: ignore

logging.basicConfig(level=logging.INFO, format="%(levelname)s - %(message)s")


def main():
    parser = ArgumentParser()

    parser.add_argument("-b", "--base-url", help="Qlik base url")
    parser.add_argument("-a", "--api-key", help="Generated API key")
    parser.add_argument("-o", "--output", help="Directory to write to")
    parser.add_argument(
        "-e",
        "--except-http-error-statuses",
        type=int,
        nargs="+",
        help="List of HTTP statuses for which to catch errors from and log "
        "as warning instead. Helpful to continue script execution when "
        "missing rights on some assets.",
    )

    args = parser.parse_args()
    qlik.extract_all(
        base_url=args.base_url,
        api_key=args.api_key,
        output_directory=args.output,
        except_http_error_statuses=args.except_http_error_statuses,
    )
