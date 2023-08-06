import imghdr

import click
import metadata_parser
import requests


@click.command()
@click.argument("url")
def main(url: str) -> None:
    """Download metadata images (e.g., OG images) from web pages."""
    page = metadata_parser.MetadataParser(url=url, search_head_only=True)

    img_url = page.get_metadatas("image", strategy=["og"])[0]

    img_data = requests.get(img_url).content
    img_extension = imghdr.what("", h=img_data)

    img_filename = img_url.split("/")[-1]
    img_full_filename = f"{img_filename}.{img_extension}"

    with open(img_full_filename, "wb") as handler:
        handler.write(img_data)

    click.echo(f"Metadata image: {repr(img_full_filename)}")
    click.echo("\n✨ Done!")
