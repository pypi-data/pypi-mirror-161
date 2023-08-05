import dddm
import numpy as np
import pandas as pd


def test_print_versions():
    dddm.print_versions()


def test_to_str_tuple():
    tests = [
        'a',
        ['a', 'b'],
        ('a', 'b'),
        np.array(['a', 'b']),
        pd.Series(['a', 'b'])
    ]
    for t in tests:
        res = dddm.to_str_tuple(t)
        assert isinstance(res, tuple)
        assert isinstance(res[0], str)


def test_get_hash():
    dddm.utils.deterministic_hash({'bla': np.zeros(19),
                                   'foo': pd.DataFrame()})
    dddm.utils.deterministic_hash(list(np.arange(19, dtype=np.int64)))
    dddm.utils.deterministic_hash(
        list(np.arange(3, dtype=np.int64)) + 
        [{str(a): a for a in np.arange(3, dtype=np.float64)}] +
        [np.array([np.arange(2), np.arange(2)])]
    )
