from urllib.parse import quote_plus

import click
import pyperclip
from giturlparse import parse

from .constants import BINDER_BASE_BADGE, COLAB_BASE_BADGE, DEEPNOTE_BASE_BADGE


# https://click.palletsprojects.com/en/8.1.x/setuptools/
@click.command()
# https://click.palletsprojects.com/en/8.1.x/quickstart/#adding-parameters
# https://click.palletsprojects.com/en/8.1.x/arguments/
@click.argument("url")
def main(url: str) -> None:
    """Generate Jupyter notebook badges for different services."""

    # https://github.com/nephila/giturlparse#exposed-attributes
    p = parse(url)
    ref, notebook = p.path.split("/", maxsplit=1)

    binder_badge = BINDER_BASE_BADGE.format(
        owner=p.owner, repo=p.repo, ref=ref, notebook=notebook
    )
    colab_badge = COLAB_BASE_BADGE.format(
        owner=p.owner, repo=p.repo, ref=ref, notebook=notebook
    )
    deepnote_badge = DEEPNOTE_BASE_BADGE.format(url=quote_plus(url))

    all_badges = " ".join([binder_badge, colab_badge, deepnote_badge])

    click.secho("Badges:", bold=True)
    click.echo(all_badges)
    pyperclip.copy(all_badges)

    click.echo("\n📋 Copied!")
