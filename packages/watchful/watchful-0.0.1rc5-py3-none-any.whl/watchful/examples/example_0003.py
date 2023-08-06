"""
This script tests data enrichment using `hub` taking in a customized `Enricher`.
"""
################################################################################


import os
import sys
from typing import Iterable, List

THIS_FILE_DIR = os.path.dirname(os.path.abspath(__file__))

try:
    from watchful import attributes
    from watchful.hub import Hub
    from watchful.enricher import Enricher
except (ImportError, ModuleNotFoundError):
    sys.path.insert(1, os.path.dirname(THIS_FILE_DIR))
    import attributes
    from hub import Hub
    from enricher import Enricher


class NEREnricher(Enricher):
    """
    This is an example of a customized enricher class that inherits from the
    `Enricher` interface, with subsequent implementation of the abstract 
    methods.
    """

    def __init__(
        self,
    ) -> None:
        """
        In this function, we create variables that we will later use in
        `enrich_row` to enrich our data row-wise. Refer to Watchful
        documentation on creating attribute spans.
        """

        global Sentence
        from flair.data import Sentence
        from flair.models import SequenceTagger
        import logging
        import warnings

        logging.getLogger("flair").setLevel(logging.ERROR)
        warnings.filterwarnings("ignore", module="huggingface_hub")

        tagger = SequenceTagger.load("ner")

        def predict(sent: Sentence) -> None:
            tagger.predict(sent)

        self.enrichment_args = (predict,)

    def enrich_row(
        self,
        row: Iterable[str],
    ) -> List[attributes.TYPE_ENRICHED_CELL]:
        """
        In this function, we use our variables from `self.enrichment_args` to
        enrich every row of your data. The return value is our enriched row.
        """

        predict, = self.enrichment_args

        enriched_row = []

        for raw_cell in row:
            sent = Sentence(raw_cell)
            predict(sent)

            enriched_cell = []

            ent_spans = []
            ent_values = []
            ent_scores = []
            for ent in sent.get_spans("ner"):
                ent_spans.append((ent.start_position, ent.end_position))
                ent_values.append(ent.get_label("ner").value)
                ent_scores.append(
                    str(int(round(ent.get_label("ner").score, 2) * 100))
                )
            enriched_cell.append(
                (ent_spans, {"entity": ent_values, "score": ent_scores}, "ENTS")
            )

            attributes.adjust_span_offsets_from_char_to_byte(
                raw_cell,
                enriched_cell
            )

            enriched_row.append(enriched_cell)

        # print("Enriched row:")
        # pprint(enriched_row)
        # print("*" * 80)

        return enriched_row


if __name__ == "__main__":

    # Test user-defined enrichers adhering to the `Enricher` interface.
    assert Enricher.is_enricher(NEREnricher)

    # Negative test.
    assert not Enricher.is_enricher(str)

    test_dir_path = os.path.join(os.path.dirname(THIS_FILE_DIR), "data")

    # Test `NEREnricher`
    hub = Hub()
    hub.enrich_dataset(
        "",
        NEREnricher,
        os.path.join(test_dir_path, "dataset_3.csv"),
        os.path.join(test_dir_path, "attributes_3.attrs"),
    )

    sys.exit(0)
