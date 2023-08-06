""" Build an 410E 2022 Midyear PDF document from a supplied markdown file and source dir

"""
__author__ = "K van Wyk"
__version__ = "0.0.1"
import os.path

import click
import docker
from rich import print

IMAGE = "registry.gitlab.com/lions-410e-midyear-2022/pdf-creator:main"

CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])


def build_pdf(source_dir, source_file, pull=False, debug=False):
    """Read SOURCE_FILE from SOURCE_DIR and write an equivalently named PDF file to SOURCE_DIR"""
    client = docker.from_env()
    volumes = {source_dir: {"bind": "/io", "mode": "rw"}}
    if pull:
        if debug:
            print(f"[yellow]Pulling {IMAGE}[/]")
        client.images.pull(IMAGE)
        if debug:
            print(f"[green]Done pulling {IMAGE}[/]")

    res = client.containers.run(
        IMAGE,
        name="lions_410e_midyear_2022_pdf_creator",
        command=source_file,
        volumes=volumes,
        auto_remove=True,
        stdout=True,
        stderr=True,
        tty=False,
    ).decode("utf-8")
    fn = f"{os.path.splitext(source_file)[0]}.pdf"
    if debug:
        print(f'Built PDF of "{fn}"')
    return fn


@click.command(context_settings=CONTEXT_SETTINGS)
@click.argument(
    "source_dir",
)
@click.argument(
    "source_file",
)
@click.option("--pull", is_flag=True, help="Whether to also pull a fresh image")
@click.option("--debug/--no-debug", default=True, help="Whether to output debug")
def main(source_dir, source_file, pull, debug):
    build_pdf(source_dir, source_file, pull, debug)


if __name__ == "__main__":
    main()
