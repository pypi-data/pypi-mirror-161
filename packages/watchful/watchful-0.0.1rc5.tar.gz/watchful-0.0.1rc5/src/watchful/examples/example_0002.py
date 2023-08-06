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


class SentimentEnricher(Enricher):
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

        import os
        import tensorflow as tf
        import transformers as tr
        from transformers import TFBertForSequenceClassification, BertTokenizer

        tr.logging.set_verbosity_error()
        os.environ["TF_CPP_MIN_LOG_LEVEL"] = "1"

        model = TFBertForSequenceClassification.from_pretrained(
            "bert-base-uncased"
        )
        tokenizer = BertTokenizer.from_pretrained("bert-base-uncased")

        pred = tf.math.argmax(
            tf.math.softmax(
                model(tokenizer("This is a sentence.", return_tensors="tf"))[0],
                -1,
            ),
            -1,
        ).numpy()
        assert pred == [0] or pred == [1]

        def predict(review: str) -> List[int]:
            return tf.math.argmax(
                tf.math.softmax(
                    model(
                        tokenizer(
                            review,
                            max_length=512,
                            truncation=True,
                            return_tensors="tf",
                        ),
                        training=False,
                    )[0],
                    -1,
                ),
                -1,
            ).numpy()

        pred2sent = {0: "neg", 1: "pos"}

        self.enrichment_args = (
            predict,
            pred2sent
        )

    def enrich_row(
        self,
        row: Iterable[str],
    ) -> List[attributes.TYPE_ENRICHED_CELL]:
        """
        In this function, we use our variables from `self.enrichment_args` to
        enrich every row of your data. The return value is our enriched row.
        """

        predict, pred2sent = self.enrichment_args

        enriched_row = []

        for raw_cell in row:
            pred = predict(raw_cell)

            enriched_cell = [
                (
                    [(0, len(raw_cell))], 
                    {
                        "sentiment": [pred2sent[pred[0]]], 
                        "score": [str(int(round(pred[0], 2) * 100))]
                    },
                    "INFRNC"
                )
            ]

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
    assert Enricher.is_enricher(SentimentEnricher)

    # Negative test.
    assert not Enricher.is_enricher(str)

    test_dir_path = os.path.join(os.path.dirname(THIS_FILE_DIR), "data")

    # Test `SentimentEnricher`
    hub = Hub()
    hub.enrich_dataset(
        "",
        SentimentEnricher,
        os.path.join(test_dir_path, "dataset_2.csv"),
        os.path.join(test_dir_path, "attributes_2.attrs"),
    )

    sys.exit(0)
