#!/usr/bin/python
"""
Top level script. Calls other functions that generate datasets that this
script then creates in HDX.

"""

import logging
from os.path import expanduser, join

from hdx.api.configuration import Configuration
from hdx.data.user import User
from hdx.facades.infer_arguments import facade
from hdx.utilities.dateparse import now_utc
from hdx.utilities.downloader import Download
from hdx.utilities.path import script_dir_plus_file, wheretostart_tempdir_batch
from hdx.utilities.retriever import Retrieve

from hdx.scraper.wikimpact._version import __version__
from hdx.scraper.wikimpact.pipeline import Pipeline

logger = logging.getLogger(__name__)

_LOOKUP = "hdx-scraper-wikimpact"
_SAVED_DATA_DIR = "saved_data"
_UPDATED_BY_SCRIPT = "HDX Scraper: WIKIMPACT"


def main(
    save: bool = False,
    use_saved: bool = False,
) -> None:
    """Generate dataset and create it in HDX

    Args:
        save: Save downloaded data. Defaults to False.
        use_saved: Use saved data. Defaults to False.

    Returns:
        None
    """
    logger.info(f"##### {_LOOKUP} version {__version__} ####")
    if not User.check_current_user_organization_access(
        "8d1a8248-a48f-440a-9ff3-e659e9a917d8", "create_dataset"
    ):
        raise PermissionError(
            "API Token does not give access to Wikimpacts organisation!"
        )
    configuration = Configuration.read()

    with wheretostart_tempdir_batch(folder=_LOOKUP) as info:
        tempdir = info["folder"]
        with Download() as downloader:
            retriever = Retrieve(
                downloader=downloader,
                fallback_dir=tempdir,
                saved_dir=_SAVED_DATA_DIR,
                temp_dir=tempdir,
                save=save,
                use_saved=use_saved,
            )
            today = now_utc()
            pipeline = Pipeline(configuration, retriever, today, tempdir)
            dataset = pipeline.generate_dataset()
            if dataset:
                dataset.update_from_yaml(
                    script_dir_plus_file(
                        join("config", "hdx_dataset_static.yaml"), main
                    )
                )
                logger.info(f"Updating {dataset['name']}")
                dataset.create_in_hdx(
                    remove_additional_resources=True,
                    match_resource_order=False,
                    updated_by_script=_UPDATED_BY_SCRIPT,
                    batch=info["batch"],
                )


if __name__ == "__main__":
    facade(
        main,
        user_agent_config_yaml=join(expanduser("~"), ".useragents.yaml"),
        user_agent_lookup=_LOOKUP,
        project_config_yaml=script_dir_plus_file(
            join("config", "project_configuration.yaml"), main
        ),
    )
