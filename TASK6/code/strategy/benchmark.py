# -*- coding: utf-8 -*-
"""基准收益：市场平均（截面等权）"""


def calc_benchmark(test_df):
    """
    计算市场平均基准：每个季度所有股票等权平均收益。

    Returns:
        bench_df: DataFrame[quarter_str, benchmark_return]
    """
    bench = test_df.groupby('quarter_str')['next_return'].mean().reset_index()
    bench.columns = ['quarter_str', 'benchmark_return']
    return bench
