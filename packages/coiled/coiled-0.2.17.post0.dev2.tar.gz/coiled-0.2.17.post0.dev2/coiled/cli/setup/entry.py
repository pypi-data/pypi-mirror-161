import click
import coiled
from rich import print
from rich.prompt import Prompt

from ..utils import CONTEXT_SETTINGS


@click.command(context_settings=CONTEXT_SETTINGS)
def setup_wizard() -> bool:
    return do_setup_wizard()


def do_setup_wizard() -> bool:
    coiled.add_interaction(
        action="cli-setup-wizard:start",
        success=True,
    )

    print(
        "Coiled creates and manages Dask clusters in your own cloud provider account.\n\n"
        "  1. AWS\n"
        "  2. Google Cloud\n"
        "  3. Azure\n"
        "  4. I don't have an AWS, GCP, or Azure account, help me choose!\n"
        "  [red]x[/red]. Exit the setup wizard\n"
    )

    try:
        choice = Prompt.ask(
            "Please choose your cloud provider so we can guide you in setting up Coiled",
            choices=["1", "2", "3", "4", "x"],
            show_choices=False,
        )
    except KeyboardInterrupt:
        coiled.add_interaction(
            action="cli-setup-wizard:KeyboardInterrupt", success=False
        )
        return False

    coiled.add_interaction(
        action="cli-setup-wizard:prompt", success=True, choice=choice
    )

    if choice == "1":  # AWS
        print("\nRunning [green]coiled setup aws[/green]\n")
        from .aws import do_setup

        return do_setup(slug="coiled")
    elif choice == "2":  # GCP
        print(
            "\nWe don't currently have a CLI wizard for Google Cloud setup, but our documentation will guide you "
            "through using the [green]gcloud[/green] CLI from Google to set up the permissions Coiled needs to use "
            "your Google Cloud account. Please follow the instructions in our documentation about configuring GCP:\n"
            "[link]https://docs.coiled.io/user_guide/gcp_configure.html[/link]"
        )
    elif choice == "3":  # Azure
        print(
            "\nWe don't currently offer managed infrastructure for Dask on Azure. If you're running Dask on Azure, "
            "Coiled can provide you with a platform for advanced analytics of our Dask usage. "
            "Please see our documentation about deploying Dask on Azure:\n"
            "[link]https://docs.coiled.io/user_guide/azure_reference.html[/link]"
        )
    elif choice == "4":  # Other
        print(
            "\nCoiled currently supports AWS and Google Cloud. It's easy to make an account with either and get "
            "started using Coiled. Please see our documentation about choosing a cloud provider:\n"
            "[link]https://docs.coiled.io/user_guide/backends.html#need-a-cloud-provider-account[/link]"
        )

    return False
