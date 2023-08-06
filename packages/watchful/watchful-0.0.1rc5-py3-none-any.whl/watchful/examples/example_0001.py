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


class StatisticsEnricher(Enricher):
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
        `enrich_row` to enrich our data row-wise.
        """

        import numpy as np

        np_mean = np.mean
        np_std = np.std
        def scaler(x, loc, scale):
            return (x - loc) / scale
        def uniform_sampler(*args):
            return np.random.uniform(*args)
        def normal_sampler(*args):
            return np.random.normal(*args)
        n_samples = 3

        self.enrichment_args = (
            np_mean,
            np_std,
            scaler,
            uniform_sampler,
            normal_sampler,
            n_samples
        )

    def enrich_row(
        self,
        row: Iterable[str],
    ) -> List[attributes.TYPE_ENRICHED_CELL]:
        """
        In this function, we use our variables from `self.enrichment_args` to
        enrich every row of your data. The return value is our enriched row.
        Refer to Watchful documentation on creating attribute spans. In the
        example below, the return value is:
        [
            [
                (
                    [(0, 1)],
                    {
                        'mean': ['0.5'],
                        'stddev': ['0.5'],
                        ...
                    },
                    'STATS'
                ),
                (
                    [(0, 1)],
                    {
                        'linear': ['0.0'],
                        'zscore': ['-1.0'],
                        ...
                    },
                    'STD'
                ),
                (
                    [(0, 1), (0, 1), (0, 1)],
                    {
                        'uniform': ['0.5', '0.5', '0.5'],
                        'normal': ['0.4214157484771408',
                                   '-2.2016363649754167',
                                   '-0.3288956896624914'],
                        ...
                    },
                    'SAMP'
                ),
                ...
            ],
            ...
        ]
        """

        np_mean, np_std, scaler, uniform_sampler, normal_sampler, n_samples = \
            self.enrichment_args

        float_row = list(map(int, row))
        min_cell = min(float_row)
        range_cell = max(float_row) - min_cell
        mean = np_mean(float_row)
        std_dev = np_std(float_row)

        enriched_row = list(
            map(
                lambda cell: [
                    (
                        [(0, len(str(cell)))],
                        {"mean": [str(mean)], "stddev": [str(std_dev)]},
                        "STATS",
                    ),
                    (
                        [(0, len(str(cell)))],
                        {
                            "linear": [str(scaler(cell, min_cell, range_cell))],
                            "zscore": [str(scaler(cell, mean, std_dev))],
                        },
                        "STD",
                    ),
                    (
                        [(0, len(str(cell)))] * n_samples,
                        {
                            "uniform": list(
                                map(str, uniform_sampler(
                                    mean, std_dev, n_samples)
                                )
                            ),
                            "normal": list(
                                map(
                                    str,
                                    normal_sampler(
                                        min_cell, range_cell, n_samples
                                    ),
                                )
                            ),
                        },
                        "SAMP",
                    ),
                ],
                float_row,
            )
        )

        # print("Enriched row:")
        # pprint(enriched_row)
        # print("*" * 80)

        return enriched_row


if __name__ == "__main__":

    # Test user-defined enrichers adhering to the `Enricher` interface.
    assert Enricher.is_enricher(StatisticsEnricher)

    # Negative test.
    assert not Enricher.is_enricher(str)

    test_dir_path = os.path.join(os.path.dirname(THIS_FILE_DIR), "data")

    # Test `SentimentEnricher`
    hub = Hub()
    hub.enrich_dataset(
        "",
        StatisticsEnricher,
        os.path.join(test_dir_path, "dataset_1.csv"),
        os.path.join(test_dir_path, "attributes_1.attrs"),
    )

    sys.exit(0)
