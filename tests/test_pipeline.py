from hdx.utilities.compare import assert_files_same
from hdx.utilities.dateparse import parse_date
from hdx.utilities.downloader import Download
from hdx.utilities.path import temp_dir
from hdx.utilities.retriever import Retrieve

from hdx.scraper.wikimpact.pipeline import Pipeline


class TestWikimpact:
    global_dataset = {
        "data_update_frequency": "-2",
        "dataset_date": "[2020-01-10T00:00:00 TO 2020-01-26T23:59:59]",
        "groups": [{"name": "world"}],
        "maintainer": "196196be-6037-4488-8b71-d786adf4c081",
        "name": "wikimpact-impact-database",
        "owner_org": "ebcfe377-bad0-46d0-b68f-cca8e6b54e33",
        "subnational": "0",
        "tags": [
            {
                "name": "hazards and risk",
                "vocabulary_id": "b891512e-9516-4bf5-962a-7a289772a2a1",
            },
            {
                "name": "natural disasters",
                "vocabulary_id": "b891512e-9516-4bf5-962a-7a289772a2a1",
            },
        ],
        "title": "WIKIMPACT Impact Database",
    }
    global_resource = {
        "description": "WIKIMPACT global disaster impact events",
        "format": "csv",
        "name": "wikimpact_impact_events.csv",
    }

    def test_generate_dataset(self, configuration, fixtures_dir, input_dir):
        with temp_dir(
            "TestWikimpact", delete_on_success=True, delete_on_failure=False
        ) as tempdir:
            with Download(user_agent="test") as downloader:
                retriever = Retrieve(
                    downloader=downloader,
                    fallback_dir=tempdir,
                    saved_dir=input_dir,
                    temp_dir=tempdir,
                    save=False,
                    use_saved=True,
                )
                today = parse_date("2026-06-15")
                pipeline = Pipeline(configuration, retriever, today, tempdir)
                dataset = pipeline.generate_dataset()
                assert dataset == self.global_dataset
                resources = dataset.get_resources()
                assert resources[0] == self.global_resource

                filename = "wikimpact_impact_events.csv"
                assert_files_same(fixtures_dir / filename, tempdir / filename)
