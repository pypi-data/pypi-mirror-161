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
except (ImportError, ModuleNotFoundError):
    sys.path.insert(1, os.path.dirname(THIS_FILE_DIR))
    import attributes
    from hub import Hub
    from examples.example_0001 import StatisticsEnricher
    from examples.example_0002 import SentimentEnricher


if __name__ == "__main__":

    """
    This test tests data enrichment using user variables for the statistics
    enrichment.
    """
    test_dir_path = os.path.join(os.path.dirname(THIS_FILE_DIR), "data")
    statistics_enricher = StatisticsEnricher()
    attributes.enrich(
        os.path.join(test_dir_path, "dataset_1.csv"),
        os.path.join(test_dir_path, "attributes_1.attr"),
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
        os.path.join(test_dir_path, "attributes_2.attr"),
        sentiment_enricher.enrich_row,
        sentiment_enricher.enrichment_args
    )

    sys.exit(0)
