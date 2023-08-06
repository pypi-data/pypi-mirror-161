"""EUMETSAT Data Access Client"""
from __future__ import annotations
from .__version__ import __title__, __documentation__, __version__  # noqa

import argparse
import os
import shlex
import sys
import pathlib
import stat
import re
import fnmatch
import shutil
import itertools
from datetime import datetime
from requests.exceptions import HTTPError
import requests
import yaml
import time

import eumdac

from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from typing import Optional, Any, Union
    from eumdac.product import Product

    if sys.version_info < (3, 9):
        from typing import Sequence, Iterable
    else:
        from collections.abc import Sequence, Iterable


def get_config_dir() -> pathlib.Path:
    return pathlib.Path(os.getenv("EUMDAC_CONFIG_DIR", (pathlib.Path.home() / ".eumdac")))


def get_credentials_path() -> pathlib.Path:
    return get_config_dir() / "credentials"


def load_credentials(parser: argparse.ArgumentParser) -> Iterable[str]:
    credentials_path = get_credentials_path()
    try:
        content = credentials_path.read_text()
    except FileNotFoundError:
        parser.error("No credentials found! Please set credentials!")
    match = re.match(r"(\w+),(\w+)$", content)
    if match is None:
        parser.error(f'Corrupted file "{credentials_path}"! Please reset credentials!')
    return match.groups()


class SetCredentials(argparse.Action):
    def __call__(
        self,
        parser: argparse.ArgumentParser,
        namespace: argparse.Namespace,
        values: Union[str, Sequence[Any], None],
        option_string: Optional[str] = None,
    ) -> None:
        token = eumdac.AccessToken(values)  # type: ignore[arg-type]
        config_dir = get_config_dir()
        config_dir.mkdir(exist_ok=True)
        credentials_path = get_credentials_path()
        credentials_path.touch(mode=(stat.S_IRUSR | stat.S_IWUSR))

        try:
            print(f"Credentials are correct. Token was generated: {token}")
            try:
                with credentials_path.open(mode="w") as file:
                    file.write(",".join(values))  # type: ignore[arg-type]
                namespace.credentials = values
                print(f"Credentials are written to file {credentials_path}")
            except OSError:
                print(
                    "Credentials could not be written to {credentials_path}. Please review your configuration."
                )
        except HTTPError as e:
            if e.response.status_code == 401:
                print(
                    "The provided credentials are not valid. Get your personal credentials at https://api.eumetsat.int/api-key",
                )
            else:
                report_request_error(e.response)

        parser.exit()


class CommandAction(argparse._SubParsersAction):  # type: ignore[type-arg]
    def __call__(
        self,
        parser: argparse.ArgumentParser,
        namespace: argparse.Namespace,
        values: Union[str, Sequence[Any], None],
        option_string: Optional[str] = None,
    ) -> None:
        super().__call__(parser, namespace, values, option_string=option_string)
        requires_credentials = [
            command
            for command, parser in self._name_parser_map.items()
            if any(action.dest == "credentials" for action in parser._actions)
        ]
        if namespace.command in requires_credentials and namespace.credentials is None:
            namespace.credentials = load_credentials(parser)


def describe(args: argparse.Namespace) -> None:
    token = eumdac.AccessToken(args.credentials)
    datastore = eumdac.DataStore(token)
    if args.collection is None and args.product is None:
        for collection in datastore.collections:
            print(f"{collection} - {collection.title}")
    elif args.collection is not None and args.product is None:
        collection = datastore.get_collection(args.collection)
        date = collection.metadata["properties"].get("date", "/")
        match = re.match(r"([^/]*)/([^/]*)", date)
        start_date, end_date = match.groups()  # type: ignore[union-attr]
        start_date = start_date or "-"
        end_date = end_date or "now"
        print(f"{collection} - {collection.title}")
        print(f"Date: {start_date} - {end_date}")
        print(collection.abstract)
        print(f'Licence: {"; ".join(collection.metadata["properties"].get("rights", "-"))}')
    elif args.collection is None and args.product is not None:
        raise ValueError("Product ID requires a Collection ID!")
    else:
        product = datastore.get_product(args.collection, args.product)
        attributes = {
            "Mission": product.satellite,
            "Instrument": product.instrument,
            "Sensing Start": "none"
            if (product.sensing_start is False)
            else f"{product.sensing_start.isoformat(timespec='milliseconds')}Z",
            "Sensing End": "none"
            if (product.sensing_end is False)
            else f"{product.sensing_end.isoformat(timespec='milliseconds')}Z",
            "Size": f"{product.size} KB",
        }
        lines = [f"{product.collection} - {product}"] + [
            f"{key}: {value}" for key, value in attributes.items()
        ]
        print("\n".join(lines))


def search(args: argparse.Namespace) -> None:
    token = eumdac.AccessToken(args.credentials)
    datastore = eumdac.DataStore(token)
    for collection in args.collection:
        collection = datastore.get_collection(collection)
        _query = {
            "dtstart": args.dtstart,
            "dtend": args.dtend,
            "bbox": args.bbox,
            "geo": args.geo,
            "sat": args.sat,
            "sort": args.sort,
            "cycle": args.cycle,
            "orbit": args.orbit,
            "relorbit": args.relorbit,
            "title": args.filename,
            "timeliness": args.timeliness,
        }
        query = {key: value for key, value in _query.items() if value is not None}
        limit = args.limit
        bbox = query.pop("bbox", None)
        if bbox is not None:
            query["bbox"] = ",".join(map(str, bbox))
        products_query = collection.search(**query)
        products = itertools.islice(products_query, limit)
        products_count = len(products_query)

        if products_count > limit and limit == 10:
            # show a warning through stderr only when more than 10
            # products would be shown and limit keyword is not used.
            print(
                f"By default, only 10 of {products_count} products are displayed.",
                file=sys.stderr,
            )
            print(
                "Please use --limit to increase the number of products if necessary.",
                file=sys.stderr,
            )

        if products_count > 10000:
            print(
                "Notice: EUMETSATs DataStore APIs allow a maximum of 10.000 items in a single request. If more than 10.000 items are needed, please split your requests.",
                file=sys.stderr,
            )

        for product in products:
            CRLF = "\r\n"
            print(str(product).replace(CRLF, "-"))


def download(args: argparse.Namespace) -> None:
    try:
        token = eumdac.AccessToken(args.credentials)
    except requests.exceptions.HTTPError as exception:
        if exception.response.status_code >= 400 and exception.response.status_code < 500:
            print("Token couldn't be generated. See below:")
            print(exception)
        elif exception.response.status_code >= 500:
            try:
                time.sleep(2000)
                token = eumdac.AccessToken(args.credentials)
            except requests.exceptions.HTTPError:
                time.sleep(2000)
                token = eumdac.AccessToken(args.credentials)
    try:
        datastore = eumdac.DataStore(token)
    except requests.exceptions.HTTPError as exception:
        if exception.response.status_code >= 400 and exception.response.status_code < 500:
            print("Failed authorization with Data Store API. See below:")
            print(exception)
        elif exception.response.status_code >= 500:
            try:
                time.sleep(2000)
                datastore = eumdac.DataStore(token)
            except requests.exceptions.HTTPError:
                time.sleep(2000)
                datastore = eumdac.DataStore(token)
    datastore = eumdac.DataStore(token)
    collection_id = args.collection

    def download_product(product: Product, args: argparse.Namespace) -> None:
        with product.open(entry=entry) as fsrc:
            if args.entry is None:
                output = args.output_dir / fsrc.name
                if output.is_file():
                    print(f"Skip {fsrc.name} it already exists")
                else:
                    print(f"Downloading {fsrc.name}")
                    tmp = args.output_dir / (fsrc.name + ".tmp")
                    with tmp.open(mode="wb") as fdst:
                        # note: currently, there is no content-length header
                        # in the data store http response, so it is not simple to
                        # build a progress bar. In case it is added in future,
                        # just check fsrc.getheader("Content-Length")
                        shutil.copyfileobj(fsrc, fdst)
                    tmp.rename(output)
            else:
                # If --entry is used, a directory for each product will
                # be generated, in which the desired files will be downloaded.
                path = pathlib.Path(args.output_dir, str(product_id))
                if not os.path.exists(path):
                    os.mkdir(path)
                output = path / fsrc.name
                if output.is_file():
                    print(f"Skip {str(product_id)}/{fsrc.name} it already exists")
                else:
                    print(f"Downloading {str(product_id)}/{fsrc.name}")
                    tmp = path / (fsrc.name + ".tmp")
                    with tmp.open(mode="wb") as fdst:
                        # note: currently, there is no content-length header
                        # in the data store http response, so it is not simple to
                        # build a progress bar. In case it is added in future,
                        # just check fsrc.getheader("Content-Length")
                        shutil.copyfileobj(fsrc, fdst)
                    tmp.rename(output)

    if not args.product:
        if not args.time_range:
            raise ValueError("Please provide either products or a time-range!")
        start, end = args.time_range
        collection = datastore.get_collection(collection_id)
        args.product = [str(product) for product in collection.search(dtstart=start, dtend=end)]

    # Create specified output directory and report
    os.makedirs(args.output_dir, exist_ok=True)
    print(f"Output directory: {os.path.abspath(args.output_dir)}")

    for product_id in args.product:
        try:
            product = datastore.get_product(collection_id, product_id)
        except requests.exceptions.HTTPError as exception:
            if exception.response.status_code >= 400 and exception.response.status_code < 500:
                print("Product ID doesn't exist. See below:")
                print(exception)
            elif exception.response.status_code >= 500:
                try:
                    time.sleep(2000)
                    product = datastore.get_product(collection_id, product_id)
                except requests.exceptions.HTTPError:
                    time.sleep(2000)
                    product = datastore.get_product(collection_id, product_id)
        if args.entry is None:
            entries = [None]
        else:
            matches = (fnmatch.filter(product.entries, pattern) for pattern in args.entry)
            entries = sum(matches, [])
        for entry in entries:
            try:
                download_product(product, args)
            except requests.exceptions.HTTPError as exception:
                if exception.response.status_code >= 400 and exception.response.status_code < 500:
                    print("Product ID doesn't exist. See below:")
                    print(exception)
                elif exception.response.status_code >= 500:
                    try:
                        time.sleep(2000)
                        download_product(product, args)
                    except requests.exceptions.HTTPError:
                        time.sleep(2000)
                        download_product(product, args)


def subscribe_list_subscriptions(args: argparse.Namespace) -> None:
    token = eumdac.AccessToken(args.credentials)
    datastore = eumdac.DataStore(token)
    subscriptions = datastore.subscriptions
    if not subscriptions:
        print("No subscriptions registered")
    else:
        print(
            "{:<40} {:<8} {:<25} {:<20} {:<20}".format(
                "Subscription ID", "Status", "Collection", "Area of interest", "Listener URL"
            )
        )
        print(
            "{:<40} {:<8} {:<25} {:<20} {:<20}".format(
                "----------------------------------------",
                "--------",
                "-------------------------",
                "--------------------",
                "--------------------",
            )
        )
        for subscription in datastore.subscriptions:
            lines = [
                str(subscription),
                str(subscription.status),
                str(subscription.collection),
                str(subscription.area_of_interest),
                str(subscription.url),
            ]
            print(
                "{:<40} {:<8} {:<25} {:<20} {:<20}".format(
                    lines[0], lines[1], lines[2], lines[3], lines[4]
                )
            )


def subscribe_create_subscriptions(args: argparse.Namespace) -> None:
    token = eumdac.AccessToken(args.credentials)
    datastore = eumdac.DataStore(token)
    collection = datastore.get_collection(args.collection)
    try:
        subscription = datastore.new_subscription(
            collection, args.url, area_of_interest=args.area_of_interest
        )
        print(
            "{:<40} {:<8} {:<25} {:<20} {:<20}".format(
                "Subscription ID", "Status", "Collection", "Area of interest", "Listener URL"
            )
        )
        print(
            "{:<40} {:<8} {:<25} {:<20} {:<20}".format(
                "----------------------------------------",
                "--------",
                "-------------------------",
                "--------------------",
                "--------------------",
            )
        )
        lines = [
            str(subscription),
            str(subscription.status),
            str(subscription.collection),
            str(subscription.area_of_interest),
            str(subscription.url),
        ]
        print(
            "{:<40} {:<8} {:<25} {:<20} {:<20}".format(
                lines[0], lines[1], lines[2], lines[3], lines[4]
            )
        )
    except requests.exceptions.HTTPError as exception:
        if exception.response.status_code >= 400 and exception.response.status_code < 500:
            report_request_error(
                exception.response, "Please provide a correct collection and URL. See below:"
            )
        elif exception.response.status_code >= 500:
            report_request_error(
                exception.response, "There was an issue on server side. See below:"
            )


def subscribe_delete_subscriptions(args: argparse.Namespace) -> None:
    token = eumdac.AccessToken(args.credentials)
    datastore = eumdac.DataStore(token)
    for subscription_id in args.sub_ids:
        try:
            subscription = datastore.get_subscription(subscription_id)
            subscription.delete()
            print(f"Deleted subscription {subscription_id}")
        except requests.exceptions.HTTPError as exception:
            if exception.response.status_code >= 400 and exception.response.status_code < 500:
                report_request_error(
                    exception.response, "Subscription ID does not seem to be a valid. See below:"
                )
            elif exception.response.status_code >= 500:
                report_request_error(
                    exception.response, "There was an issue on server side. See below:"
                )


def tailor_post_job(args: argparse.Namespace) -> None:
    from eumdac.tailor_models import Chain

    token = eumdac.AccessToken(args.credentials)
    datastore = eumdac.DataStore(token)
    datatailor = eumdac.DataTailor(token)
    collection_id = args.collection
    product_ids = args.product
    chain_file = args.chain

    if not args.collection or not args.product or not args.chain:
        raise ValueError("Please provide collection ID, product ID and a chain file!")
    with open(chain_file, "r") as file:
        chain = yaml.safe_load(file)
    chain = Chain(**chain)
    products = [datastore.get_product(collection_id, product_id) for product_id in product_ids]
    try:
        customisation = datatailor.new_customisations(products, chain=chain)
        jobidsToStr = "\n".join([str(jobid) for jobid in customisation])
        print("Customisation(s) has been started.")
        print(jobidsToStr)
    except requests.exceptions.HTTPError as exception:
        if exception.response.status_code >= 400 and exception.response.status_code < 500:
            report_request_error(
                exception.response,
                "Collection ID and/or Product ID does not seem to be a valid. See below:",
            )
        elif exception.response.status_code >= 500:
            report_request_error(
                exception.response, "There was an issue on server side. See below:"
            )


def tailor_list_customisations(args: argparse.Namespace) -> None:
    token = eumdac.AccessToken(args.credentials)
    datatailor = eumdac.DataTailor(token)
    try:
        customisations = datatailor.customisations
        if not customisations:
            print("No customisations available", file=sys.stderr)
        else:
            print(
                "{:<10} {:<8} {:<10} {:<20}".format("Job ID", "Status", "Product", "Creation Time")
            )
            print(
                "{:<10} {:<8} {:<10} {:<20}".format(
                    "----------", "--------", "----------", "--------------------"
                )
            )
            for customisation in datatailor.customisations:
                lines = [
                    str(customisation),
                    customisation.status,
                    customisation.product_type,
                    str(customisation.creation_time),
                ]
                print("{:<10} {:<8} {:<10} {:<20}".format(lines[0], lines[1], lines[2], lines[3]))
    except requests.exceptions.HTTPError as exception:
        report_request_error(exception.response)


def tailor_show_status(args: argparse.Namespace) -> None:
    token = eumdac.AccessToken(args.credentials)
    datatailor = eumdac.DataTailor(token)
    if args.verbose:
        print("{:<10} {:<8} {:<10} {:<20}".format("Job ID", "Status", "Product", "Creation Time"))
        print(
            "{:<10} {:<8} {:<10} {:<20}".format(
                "----------", "--------", "----------", "--------------------"
            )
        )
        for customisation_id in args.job_ids:
            try:
                customisation = datatailor.get_customisation(customisation_id)
                lines = [
                    str(customisation),
                    customisation.status,
                    customisation.product_type,
                    str(customisation.creation_time),
                ]
                print("{:<10} {:<8} {:<10} {:<20}".format(lines[0], lines[1], lines[2], lines[3]))
            except requests.exceptions.HTTPError as exception:
                if exception.response.status_code >= 400 and exception.response.status_code < 500:
                    report_request_error(
                        exception.response,
                        f"{customisation_id} does not seem to be a valid job id. See below:",
                    )
                elif exception.response.status_code >= 500:
                    report_request_error(
                        exception.response, "There was an issue on server side. See below:"
                    )
    else:
        for customisation_id in args.job_ids:
            try:
                customisation = datatailor.get_customisation(customisation_id)
                print(customisation.status)
            except requests.exceptions.HTTPError as exception:
                if exception.response.status_code >= 400 and exception.response.status_code < 500:
                    report_request_error(
                        exception.response,
                        f"{customisation_id} does not seem to be a valid job id. See below:",
                    )
                elif exception.response.status_code >= 500:
                    report_request_error(
                        exception.response, "There was an issue on server side. See below:"
                    )


def tailor_get_log(args: argparse.Namespace) -> None:
    token = eumdac.AccessToken(args.credentials)
    datatailor = eumdac.DataTailor(token)
    try:
        customisation = datatailor.get_customisation(args.job_id)
        print(customisation.logfile)
    except requests.exceptions.HTTPError as exception:
        if exception.response.status_code >= 400 and exception.response.status_code < 500:
            report_request_error(
                exception.response, f"{args.job_id} does not seem to be a valid job id. See below:"
            )
        elif exception.response.status_code >= 500:
            report_request_error(
                exception.response, "There was an issue on server side. See below:"
            )


def tailor_delete_jobs(args: argparse.Namespace) -> None:
    token = eumdac.AccessToken(args.credentials)
    datatailor = eumdac.DataTailor(token)
    for customisation_id in args.job_ids:
        customisation = datatailor.get_customisation(customisation_id)
        try:
            customisation.delete()
            print(f"Customisation {customisation_id} has been deleted.")
        except requests.exceptions.HTTPError as exception:
            if exception.response.status_code >= 400:
                report_request_error(
                    exception.response,
                    f"{customisation_id} does not seem to be a valid job id or there was an issue on server side. See below:",
                )


def tailor_cancel_jobs(args: argparse.Namespace) -> None:
    token = eumdac.AccessToken(args.credentials)
    datatailor = eumdac.DataTailor(token)

    for customisation_id in args.job_ids:
        customisation = datatailor.get_customisation(customisation_id)
        try:
            customisation.kill()
            print(f"Customisation {customisation_id} has been cancelled.")
        except requests.exceptions.HTTPError as exception:
            if exception.response.status_code >= 400 and exception.response.status_code < 500:
                report_request_error(
                    exception.response,
                    f"{customisation_id} is already cancelled or job id is invalid. See below:",
                )
            elif exception.response.status_code >= 500:
                report_request_error(
                    exception.response, "There was an issue on server side. See below:"
                )


def tailor_clear_jobs(args: argparse.Namespace) -> None:
    token = eumdac.AccessToken(args.credentials)
    datatailor = eumdac.DataTailor(token)

    jobs_to_clean = args.job_ids

    if args.all and len(args.job_ids) > 0:
        print("All flag provided. Ignoring the provided customization IDs and clearing all jobs")

    if args.all:
        # Fetch all job ids
        jobs_to_clean = datatailor.customisations

    for customisation in jobs_to_clean:
        # If we are provided a job id, get the customisation
        if isinstance(customisation, str):
            customisation_id = customisation
            customisation = datatailor.get_customisation(customisation)
        else:
            customisation_id = customisation._id

        try:
            if (
                customisation.status == "QUEUED"
                or customisation.status == "RUNNING"
                or customisation.status == "INACTIVE"
            ):
                customisation.kill()
                print(f"Customisation {customisation_id} has been cancelled.")
        except requests.exceptions.HTTPError as exception:
            if exception.response.status_code >= 400 and exception.response.status_code < 500:
                report_request_error(
                    exception.response,
                    f"{customisation_id} is already cancelled or job id is invalid. See below:",
                )
            elif exception.response.status_code >= 500:
                report_request_error(
                    exception.response, "There was an issue on server side. See below:"
                )
        try:
            customisation.delete()
            print(f"Customisation {customisation_id} has been deleted.")
        except requests.exceptions.HTTPError as exception:
            report_request_error(
                exception.response,
                f"{customisation_id} does not seem to be a valid job id or there was an issue on server side. See below:",
            )


def tailor_download(args: argparse.Namespace) -> None:
    token = eumdac.AccessToken(args.credentials)
    # for customisation_id in customisation_ids:  # type: ignore[union-attr]
    customisation_id = args.job_id
    url = "https://api.eumetsat.int/epcs/customisations/" + customisation_id
    response = requests.get(
        url,
        headers={
            "Authorization": "Bearer {}".format(token),
            "referer": __documentation__,
            "User-Agent": str(__title__ + "/" + __version__),
        },
    )
    if response.status_code == 200:
        results = response.json()[customisation_id]["output_products"]

        # Create output path if it does not exist
        print(f"Output directory: {os.path.abspath(args.output_dir)}")
        if not os.path.exists(args.output_dir):
            print(f"Output directory {args.output_dir} does not exist. It will be created.")
            os.makedirs(args.output_dir)

        # Download all the output files into the output path
        print(f"Downloading {len(results)} output products")
        for result in results:
            print("Downloading " + os.path.basename(result))
            url = "https://api.eumetsat.int/epcs/download?path=" + result
            response = requests.get(
                url,
                headers={
                    "Authorization": "Bearer {}".format(token),
                    "referer": __documentation__,
                    "User-Agent": str(__title__ + "/" + __version__),
                },
            )
            output = args.output_dir
            if response.status_code == 200:
                product_path = os.path.join(output, os.path.basename(result))
                open(product_path, "wb").write(response.content)
                print(f"{os.path.basename(result)} has been downloaded.")
            else:
                report_request_error(
                    response, f"{os.path.basename(result)} couldn't be downloaded:"
                )
    elif response.status_code >= 400 and response.status_code < 500:
        report_request_error(
            response, f"{customisation_id} does not seem to be a valid job id. See below:"
        )
    elif response.status_code >= 500:
        report_request_error(response)


def report_request_error(response: requests.Response, message: Optional[str] = None) -> None:
    if response is None:
        if not message:
            print("An unexpected error has occurred.")
        else:
            print(message)
        return

    if message is None:
        if response.status_code >= 400 and response.status_code < 500:
            message = "The provided inputs were not accepted by the server. See below:"
        elif response.status_code >= 500:
            message = "There was an issue on server side. See below:"
        else:
            message = "An error occurred. See below:"
    print(message)
    print(f"{response.status_code} - {response.text}")


class PrintHelpAction(argparse.Action):
    def __call__(self, parser: argparse.ArgumentParser, *args: Any, **kwargs: Any) -> None:
        # Print the help if the command has 2 args,
        # meaning it's just $ eumdac tailor
        if len(sys.argv) == 2:
            parser.print_help()
            parser.exit()


def cli(command_line: Optional[Sequence[str]] = None) -> None:
    # append piped args
    if not sys.stdin.isatty():
        sys.argv.extend(shlex.split(sys.stdin.read()))

    # main parser
    parser = argparse.ArgumentParser(description=__doc__, fromfile_prefix_chars="@")
    parser.add_argument("--version", action="version", version=f"%(prog)s {eumdac.__version__}")
    parser.add_argument(
        "--set-credentials",
        nargs=2,
        action=SetCredentials,
        help=(
            "permanently set consumer key and secret and exit, "
            "see https://api.eumetsat.int/api-key"
        ),
        metavar=("ConsumerKey", "ConsumerSecret"),
        dest="credentials",
    )
    parser.add_argument("--debug", help="show backtrace for errors", action="store_true")

    subparsers = parser.add_subparsers(dest="command", action=CommandAction)

    # describe parser
    parser_describe = subparsers.add_parser(
        "describe",
        help="describe a collection or product",
        epilog="example: %(prog)s -c EO:EUM:DAT:MSG:HRSEVIRI",
    )
    parser_describe.add_argument(
        "-c", "--collection", help="collection to describe", metavar="CollectionId"
    )
    parser_describe.add_argument("-p", "--product", help="product to describe", metavar="ProductId")
    parser_describe.add_argument(
        "--credentials",
        nargs=2,
        default=argparse.SUPPRESS,
        help="consumer key and secret, see https://api.eumetsat.int/api-key",
        metavar=("ConsumerKey", "ConsumerSecret"),
    )
    parser_describe.set_defaults(func=describe)

    # search parser
    parser_search = subparsers.add_parser(
        "search",
        help="search for products at the collection level",
        epilog="example: %(prog)s -s 2020-03-01 -e 2020-03-15T12:15 -c EO:EUM:DAT:MSG:CLM",
    )
    parser_search.add_argument(
        "-c", "--collection", nargs="+", help="collection ID(s)", required=True
    )
    parser_search.add_argument(
        "-s",
        "--start",
        type=datetime.fromisoformat,
        help="UTC start date e.g. 2002-12-21T12:30:15",
        metavar="YYYY-MM-DD[THH[:MM[:SS]]]",
        dest="dtstart",
    )
    parser_search.add_argument(
        "-e",
        "--end",
        type=datetime.fromisoformat,
        help="UTC end date e.g. 2002-12-21T12:30:15",
        metavar="YYYY-MM-DD[THH[:MM[:SS]]]",
        dest="dtend",
    )
    parser_search.add_argument(
        "--bbox",
        nargs=4,
        type=float,
        metavar=("W", "S", "E", "N"),
        help="filter by bounding box, the box is defined in EPSG:4326 decimal degrees",
    )
    parser_search.add_argument(
        "--geometry",
        help="filter by geometry, a custom geomtery in a EPSG:4326 decimal degrees.",
        dest="geo",
    )
    parser_search.add_argument(
        "--cycle",
        help="filter by cycle number, must be a positive integer.",
        dest="cycle",
        type=int,
    )
    parser_search.add_argument(
        "--orbit",
        help="filter by orbit number, must be a positive integer.",
        dest="orbit",
        type=int,
    )
    parser_search.add_argument(
        "--relorbit",
        help="filter by relative orbit number, must be a positive integer.",
        dest="relorbit",
        type=int,
    )
    parser_search.add_argument(
        "--filename",
        help="Can be used to define a wildcard search on the product title (product identifier), use set notation as OR and space as AND operator between multiple search terms.",
        dest="filename",
        type=str,
    )
    parser_search.add_argument(
        "--timeliness", help="filter by timeliness", dest="timeliness", choices=["NT", "NR", "ST"]
    )
    parser_search.add_argument("--satellite", help="filter by satellite", dest="sat")
    parser_search.add_argument("--sort", help="sort results")
    parser_search.add_argument(
        "--limit", type=int, help="Max Items to return, default = %(default)s", default=10
    )
    parser_search.add_argument(
        "--credentials",
        nargs=2,
        default=argparse.SUPPRESS,
        help="consumer key and secret, see https://api.eumetsat.int/api-key",
        metavar=("ConsumerKey", "ConsumerSecret"),
    )
    parser_search.set_defaults(func=search)

    parser_download = subparsers.add_parser(
        "download", help="download product(s) from a collection"
    )
    parser_download.add_argument("-c", "--collection", help="collection ID", required=True)
    parser_download.add_argument("-p", "--product", nargs="*", help="product ID(s)")
    parser_download.add_argument(
        "-o",
        "--output-dir",
        type=pathlib.Path,
        help="path to output directory, default CWD",
        metavar="DIR",
        default=pathlib.Path.cwd(),
    )
    parser_download.add_argument(
        "--entry", nargs="+", help="shell-style wildcard pattern(s) to filter product files"
    )
    parser_download.add_argument(
        "--time-range",
        nargs=2,
        type=datetime.fromisoformat,
        help="convenience search on UTC time range",
        metavar="YYYY-MM-DD[THH[:MM[:SS]]]",
    )
    parser_download.add_argument(
        "--credentials",
        nargs=2,
        default=argparse.SUPPRESS,
        help="consumer key and secret, see https://api.eumetsat.int/api-key",
        metavar=("ConsumerKey", "ConsumerSecret"),
    )
    parser_download.set_defaults(func=download)

    # subscribe parser
    parser_subscribe = subparsers.add_parser(
        "subscribe", help="subscribe a server for a collection"
    )
    parser_subscribe.add_argument(
        dest="print_help", nargs=0, action=PrintHelpAction, help=argparse.SUPPRESS
    )

    subscribe_subparsers = parser_subscribe.add_subparsers(dest="subscribe-command")

    subscribe_list_parser = subscribe_subparsers.add_parser(
        "list",
        description="List subscriptions from Data Store",
        help="List subscriptions from Data Store",
    )
    subscribe_list_parser.set_defaults(func=subscribe_list_subscriptions)

    subscribe_create_parser = subscribe_subparsers.add_parser(
        "create",
        description="Create a new subscription for Data Store",
        help="Create a new subscription for Data Store",
    )
    subscribe_create_parser.add_argument("-c", "--collection", help="collection ID", required=True)
    subscribe_create_parser.add_argument(
        "-u", "--url", help="public URL of the listener server", required=True
    )
    subscribe_create_parser.add_argument(
        "--area-of-interest",
        help="area of interest, a custom geomtery in a EPSG:4326 decimal degrees.",
    )
    subscribe_create_parser.set_defaults(func=subscribe_create_subscriptions)

    subscribe_delete_parser = subscribe_subparsers.add_parser(
        "delete",
        description="Delete subscriptions from Data Store",
        help="Delete subscriptions from Data Store",
    )
    subscribe_delete_parser.add_argument("sub_ids", help="Subscription ID", type=str, nargs="+")
    subscribe_delete_parser.set_defaults(func=subscribe_delete_subscriptions)

    parser_subscribe.add_argument(
        "--credentials",
        nargs=2,
        default=argparse.SUPPRESS,
        help="consumer key and secret, see https://api.eumetsat.int/api-key",
        metavar=("ConsumerKey", "ConsumerSecret"),
    )

    # tailor parser
    parser_tailor = subparsers.add_parser(
        "tailor",
        description="Manage Data Tailor customisations",
        help="tailoring product(s) from collection",
    )
    parser_tailor.add_argument(
        dest="print_help", nargs=0, action=PrintHelpAction, help=argparse.SUPPRESS
    )
    tailor_subparsers = parser_tailor.add_subparsers(dest="tailor-command")

    tailor_post_parser = tailor_subparsers.add_parser(
        "post",
        description="Posts a new customisation job into Data Tailor",
        help="Posts a new customisation job into Data Tailor",
    )
    tailor_post_parser.add_argument("-c", "--collection", help="collection ID")
    tailor_post_parser.add_argument("-p", "--product", nargs="+", help="product ID(s)")
    tailor_post_parser.add_argument(
        "--chain",
        help="define a chain for customisation",
        metavar="chain",
    )
    tailor_post_parser.set_defaults(func=tailor_post_job)

    tailor_list_parser = tailor_subparsers.add_parser("list", help="list customisations")
    tailor_list_parser.set_defaults(func=tailor_list_customisations)

    tailor_status_parser = tailor_subparsers.add_parser(
        "status",
        description="(DESC) Gets the status of one (or more) customisations",
        help="Get status of customisation",
    )
    tailor_status_parser.add_argument("job_ids", metavar="Customisation ID", type=str, nargs="+")
    tailor_status_parser.add_argument(
        "-v", "--verbose", help="Show all details of customisation", action="store_true"
    )
    tailor_status_parser.set_defaults(func=tailor_show_status)

    tailor_log_parser = tailor_subparsers.add_parser("log", help="Get the log of a customisation")
    tailor_log_parser.add_argument(
        "job_id", metavar="Customisation ID", type=str, help="Customisation ID"
    )
    tailor_log_parser.set_defaults(func=tailor_get_log)

    tailor_delete_parser = tailor_subparsers.add_parser(
        "delete",
        description="Delete finished customisations",
        help="Delete finished customisations",
    )
    tailor_delete_parser.add_argument("job_ids", metavar="Customisation ID", type=str, nargs="+")
    tailor_delete_parser.set_defaults(func=tailor_delete_jobs)

    tailor_cancel_parser = tailor_subparsers.add_parser(
        "cancel",
        description="Cancel QUEUED, RUNNING or INACTIVE customisations",
        help="Cancel QUEUED, RUNNING or INACTIVE customisations",
    )
    tailor_cancel_parser.add_argument("job_ids", metavar="Customisation ID", type=str, nargs="+")
    tailor_cancel_parser.set_defaults(func=tailor_cancel_jobs)

    tailor_clean_parser = tailor_subparsers.add_parser(
        "clean",
        description="Remove customisations in any state",
        help="Remove customisations in any state",
    )
    tailor_clean_parser.add_argument("job_ids", metavar="Customisation ID", type=str, nargs="*")
    tailor_clean_parser.add_argument("--all", help="Clean all customisations", action="store_true")
    tailor_clean_parser.set_defaults(func=tailor_clear_jobs)

    tailor_download_parser = tailor_subparsers.add_parser(
        "download", help="Download the output of a customisation"
    )
    tailor_download_parser.add_argument(
        "job_id", metavar="Customisation ID", type=str, help="Customisation ID"
    )
    tailor_download_parser.add_argument(
        "-o",
        "--output-dir",
        type=pathlib.Path,
        help="path to output directory, default CWD",
        metavar="DIR",
        default=pathlib.Path.cwd(),
    )
    tailor_download_parser.set_defaults(func=tailor_download)

    parser_tailor.add_argument(
        "--credentials",
        nargs=2,
        default=argparse.SUPPRESS,
        help="consumer key and secret, see https://api.eumetsat.int/api-key",
        metavar=("ConsumerKey", "ConsumerSecret"),
    )

    args = parser.parse_args(command_line)
    if args.command:
        try:
            args.func(args)
        except KeyboardInterrupt:
            # Ignoring KeyboardInterrupts to allow for clean CTRL+C-ing
            pass
        except Exception as error:
            if args.debug:
                raise
            parser.error(str(error))
    else:
        parser.print_help()
