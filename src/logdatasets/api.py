from logdatasets._datasets.list_datasets import overall_datasets
from logdatasets._datasets.dataset import MainDataset

import tabulate


def load_dataset(
    dataset: str, sub_name: str = "", do_cache: bool = True
) -> MainDataset:
    
    print(db := MainDataset(dataset, sub_name=sub_name, use_cache=do_cache))
    return db


def status_dataset(dataset: str) -> None:
    def get_values(sub_name: str) -> tuple[list[str], list[str]]:
        db = MainDataset(dataset, sub_name=sub_name, do_download=False)
        dict_ = db.get_dict()
        downloaded = "✅"
        if len(db) == 0:
            downloaded = "❌"

        values = [sub_name, downloaded] + dict_["Values"]
        fields = ["Name", "Downloaded"] + dict_["Field"]

        return fields, values

    if "List" in overall_datasets[dataset]:
        values = []
        for name in overall_datasets[dataset]["List"]:
            fields, values_row = get_values(name["Name"]) 
            values.append(values_row)

    else:
        fields, values = get_values("")
        values = [values]

    print(dataset)
    print(tabulate.tabulate(values, headers=fields, tablefmt="grid"))


def status_all_datasets() -> None:
    for dataset in overall_datasets:
        status_dataset(dataset)


def get_dataset_names() -> list[str]:
    print("Datasets:")
    for name in overall_datasets:
        print("  ->", name)

    return overall_datasets


def get_sub_dataset_names(dataset: str) -> list[str]:
    print("From dataset", dataset)
    sel_dataset = overall_datasets[dataset]

    sub_datsets = []
    if "List" in sel_dataset:
        for name in sel_dataset["List"]:
            print("   ->", name["Name"])
            sub_datsets.append(name["Name"])
    else:
        print("<None>")
        sub_datsets.append("")

    return sub_datsets
