from logdatasets import api

import argparse


def status_dataset_func(args: argparse.Namespace) -> None:
    api.status_dataset(args.dataset)


def status_datasets_func(args: argparse.Namespace) -> None:
    api.status_all_datasets()


def get_names_datasets(args: argparse.Namespace) -> None:
    api.get_dataset_names()


def get_names_datasets_sub(args: argparse.Namespace) -> None:
    api.get_sub_dataset_names(args.dataset)


def load_datset_func(args: argparse.Namespace) -> None:
    api.load_dataset(args.dataset, args.sub_dataset, do_cache=args.force_download)

def main():
    parser = argparse.ArgumentParser()
    commands = parser.add_subparsers(
        dest="exec",
        required=True,
        help="Command to execute in the API"
    )

    status_dataset = commands.add_parser(
        "status_dataset",
        help="Check the status of a dataset",
    )
    status_dataset.add_argument(
        "dataset",
        help="Dataset to inspect"
    )
    status_dataset.set_defaults(func=status_dataset_func)

    status_datasets = commands.add_parser(
        "status_all_dataset",
        help="Check the status of all the dataset",
    )
    status_datasets.set_defaults(func=status_datasets_func)

    get_names = commands.add_parser(
        "dataset_names",
        help="Get the names of the datasets",
    )
    get_names.set_defaults(func=get_names_datasets)

    get_sub_names = commands.add_parser(
        "sub_dataset_names",
        help="Get the names of the subdataset",
    )
    get_sub_names.add_argument(
        "dataset",
        help="Dataset to inspect"
    )
    get_sub_names.set_defaults(func=get_names_datasets_sub)

    load_dataset = commands.add_parser(
        "load_dataset",
        help="Load a dataset",
    )
    load_dataset.add_argument(
        "dataset",
        help="Dataset to load"
    )
    load_dataset.add_argument(
        "sub_dataset",
        nargs="?",
        help="sub dataset to load",
        default=""
    )
    load_dataset.add_argument(
        "--force_download",
        action="store_false",
        help="Ignore cache, always download"
    )
    load_dataset.set_defaults(func=load_datset_func)

    args = parser.parse_args()
    args.func(args)

