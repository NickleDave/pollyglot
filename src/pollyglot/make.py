"""script that generates the Pollyglot data repository"""
import argparse
from pathlib import Path
import shutil
import tarfile
import zipfile

import rarfile
import yaml

from .urlcopy import urlcopy


HERE = Path(__file__).parent
REPO_YAML = HERE.joinpath('../../data/repo.yaml')
with REPO_YAML.open() as f:
    repo_dict = yaml.safe_load(f)

repo_keys = [k for k in repo_dict.keys()]

# target paths
DOWNLOADS_DIR = HERE.joinpath('../../results/downloads')
TARGZBALLS_DIR = HERE.joinpath('../../results/targzballs')


def clean():
    downloads_dir_dirs = [d for d in DOWNLOADS_DIR.iterdir() if d.is_dir()]
    if downloads_dir_dirs:
        for downloads_dir in downloads_dir_dirs:
            shutil.rmtree(downloads_dir)

    targzballs_dir_dirs = [d for d in TARGZBALLS_DIR.iterdir() if d.is_dir()]
    if targzballs_dir_dirs:
        for targzballs_dir in targzballs_dir_dirs:
            shutil.rmtree(targzballs_dir)


def makedirs_downloads():
    for repo_key in repo_keys:
        download_dir = DOWNLOADS_DIR / f"{repo_key}"
        download_dir.mkdir()


def download():
    for repo_key, repo_url_dict in repo_dict.items():
        print(
            f'downloading data for {repo_key}'
        )
        local_repo_path = DOWNLOADS_DIR.joinpath(repo_key)
        prefixes = []

        if 'data_url' in repo_url_dict:
            prefixes.append('data')
        elif 'audio_url' in repo_url_dict and 'annot_url' in repo_url_dict:
            prefixes.append('audio')
            prefixes.append('annot')

        for prefix in prefixes:
            url = repo_url_dict[f'{prefix}_url']
            filename = repo_url_dict[f'{prefix}_filename']
            dst = local_repo_path.joinpath(filename)
            urlcopy(url, dst=str(dst))

            print(
                f'extracting data for {repo_key}'
            )

            if dst.suffixes[-2:] == ['.tar', '.gz']:
                tar = tarfile.open(str(dst))
                tar.extractall(str(local_repo_path))
            elif dst.suffixes[-1:] == ['.zip']:
                with zipfile.ZipFile(str(dst), 'r') as zip_ref:
                    zip_ref.extractall(local_repo_path)
            elif dst.suffixes[-1:] == ['.rar']:
                with rarfile.RarFile(str(dst), 'r') as rar_ref:
                    rar_ref.extractall(local_repo_path)


def targzball():
    for repo_key in repo_keys:
        results_tar_gz = TARGZBALLS_DIR / f'{repo_key}.tar.gz'


def all():
    makedirs_downloads()
    download()
    targzball()


def make(command):
    """a function that acts kind of like Unix make
    except that you don't have to do backflips to get it
    to work on a whole directory
    """
    if command == 'clean':
        clean()
    elif command == 'all':
        all()
    elif command == 'makedirs_downloads':
        makedirs_downloads()
    elif command == 'download':
        download()
    elif command == 'targzball':
        targzball()
    else:
        raise ValueError(
            f'unknown command: {command}'
        )


def get_argparser():
    DESCRIPTION = 'command-line interface for script that generates Pollyglot dataset'
    CHOICES = [
        'clean',
        'all',
        'makedirs_downloads',
        'download',
        'targzball',
    ]

    parser = argparse.ArgumentParser(description=DESCRIPTION)
    parser.add_argument('command', type=str, metavar='command',
                        choices=CHOICES,
                        help="Command to run, valid options are:\n"
                             f"{CHOICES}\n")
    return parser


def main():
    parser = get_argparser()
    args = parser.parse_args()
    make(args.command)


if __name__ == '__main__':
    main()
