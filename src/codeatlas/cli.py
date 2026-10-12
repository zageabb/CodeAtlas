"""CodeAtlas CLI."""
import argparse
import json

from .analyzer import analyze
from .source import snapshot


def main() -> None:
    parser = argparse.ArgumentParser(description="Analyse code relationships")
    parser.add_argument("source", help="Local directory or public GitHub HTTPS URL")
    parser.add_argument("--output", "-o", help="JSON report path")
    args = parser.parse_args()
    with snapshot(args.source) as root:
        report = analyze(root)
    payload = json.dumps(report, indent=2)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as stream:
            stream.write(payload + "\n")
    else:
        print(payload)


if __name__ == "__main__":
    main()
