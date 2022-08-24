import argparse

import requests


def main():
    parser = argparse.ArgumentParser("Make an HTTP request.")
    parser.add_argument(
        "-p", "--proxies", nargs="*", help="Proxies to use. E.g., http://10.10.10.1:80"
    )
    parser.add_argument("url")
    args = parser.parse_args()

    if args.proxies:
        proxies = {v[: v.find("://")]: v for v in args.proxies}

    response = requests.get(args.url, proxies=proxies)
    print(response.text)


if __name__ == "__main__":
    main()
