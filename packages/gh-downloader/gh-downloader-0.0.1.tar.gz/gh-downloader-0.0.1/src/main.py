#!/usr/bin/env python3

import os
import subprocess
import sys

import inquirer
from inquirer import Path
from inquirer.themes import GreenPassion
from requests import get, Response
from tqdm import tqdm


class Repository:
    selected: bool

    def __init__(self, **response):
        self.__dict__.update(response)


def get_repo_list(oauth_token: str) -> list[Repository]:
    print("Downloading repositories data...")
    header: dict = {
        "Accept": "application/vnd.github+json",
        "Authorization": f'token {oauth_token}'
    }
    page: int = 1
    old_size: int = -1
    new_size: int = 0
    json_content_list: list[dict] = []
    while old_size != new_size:
        response: Response = get(f'https://api.github.com/user/repos?page={page}',
                                 headers=header)
        if response.status_code != 200:
            raise Exception(response.content)
        old_size = len(json_content_list)
        json_content_list.extend(response.json())
        new_size = len(json_content_list)
        page += 1

    return [Repository(**content) for content in json_content_list]


def clone_repository(repository_list: list[Repository], folder: str) -> None:
    os.makedirs(folder, exist_ok=True)
    for repo in tqdm(repository_list, unit="Repository"):
        subprocess.run(["git", "clone", repo.ssh_url],
                       cwd=folder,
                       stdout=subprocess.DEVNULL,
                       stderr=subprocess.DEVNULL)


def main():
    user_infos = inquirer.prompt([
        inquirer.Password(
            'OAUTH',
            message="OAUTH Token",
            validate=lambda _, token: len(token) == 40
        ),
        inquirer.Path('FOLDER',
                      message="Download in which folder?",
                      path_type=Path.DIRECTORY)
    ], theme=GreenPassion())
    repo_list: list[Repository] = get_repo_list(user_infos['OAUTH'])
    to_download: list[Repository] = []
    option = inquirer.prompt([inquirer.List(
        'select_all',
        message="Selection type",
        choices=['All', "Select"],
    )], theme=GreenPassion())
    if option["select_all"] == "All":
        to_download = repo_list
    else:
        answers = inquirer.prompt([inquirer.Checkbox(
            'repositories',
            message="Which repositories",
            choices=list(map(lambda repo: repo.name, repo_list)),
        )], theme=GreenPassion())
        to_download = list(filter(lambda repo: repo.name in answers["repositories"], repo_list))
    print(f'The following repositories will be downloaded:\n{", ".join(map(lambda repo: repo.name, to_download))}')
    validate_downloads = inquirer.prompt([inquirer.Confirm(
        'VALIDATE',
        message="Confirm?",
    )], theme=GreenPassion())
    if not validate_downloads["VALIDATE"]:
        print("Canceled")
        sys.exit(1)
    clone_repository(to_download, user_infos["FOLDER"])


def cli():
    try:
        main()
    except:
        pass


if __name__ == "__main__":
    cli()
