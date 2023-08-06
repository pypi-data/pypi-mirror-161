"""
This script tests data enrichment using `enricher`s directly.
"""
################################################################################


import os
import sys

THIS_FILE_DIR = os.path.dirname(os.path.abspath(__file__))

try:
    from watchful import attributes
    from watchful.hub import Hub
    from watchful.examples.example_0001 import StatisticsEnricher
    from watchful.examples.example_0002 import SentimentEnricher
    from watchful.examples.example_0003 import NEREnricher
except (ImportError, ModuleNotFoundError):
    sys.path.insert(1, os.path.dirname(THIS_FILE_DIR))
    import attributes
    from hub import Hub
    from examples.example_0001 import StatisticsEnricher
    from examples.example_0002 import SentimentEnricher
    from examples.example_0003 import NEREnricher


if __name__ == "__main__":

    """
    This test tests data enrichment using user variables for the statistics
    enrichment.
    """
    test_dir_path = os.path.join(os.path.dirname(THIS_FILE_DIR), "data")
    statistics_enricher = StatisticsEnricher()
    attributes.enrich(
        os.path.join(test_dir_path, "dataset_1.csv"),
        os.path.join(test_dir_path, "attributes_1.attrs"),
        statistics_enricher.enrich_row,
        statistics_enricher.enrichment_args
    )

    """
    This test tests data enrichment using user variables for the sentiment
    enrichment.
    """
    test_dir_path = os.path.join(os.path.dirname(THIS_FILE_DIR), "data")
    sentiment_enricher = SentimentEnricher()
    attributes.enrich(
        os.path.join(test_dir_path, "dataset_2.csv"),
        os.path.join(test_dir_path, "attributes_2.attrs"),
        sentiment_enricher.enrich_row,
        sentiment_enricher.enrichment_args
    )

    """
    This test tests data enrichment using user variables for the NER
    enrichment.
    """
    test_dir_path = os.path.join(os.path.dirname(THIS_FILE_DIR), "data")
    ner_enricher = NEREnricher()
    attributes.enrich(
        os.path.join(test_dir_path, "dataset_3.csv"),
        os.path.join(test_dir_path, "attributes_3.attrs"),
        ner_enricher.enrich_row,
        ner_enricher.enrichment_args
    )

    sys.exit(0)
