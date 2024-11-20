JIT コンパイルのオーバーヘッド
==============================

HftBacktest は Numba の機能を活用しており、Numba JIT によってクラスがコンパイルされます。そのため、HftBacktest をインポートする際には JIT コンパイルが必要で、数秒かかることがあります。さらに、戦略関数もパフォーマンスの高いバックテストのために JIT コンパイルされる必要があり、これもコンパイルに時間がかかります。複数日のバックテストを行う場合にはそれほど重要ではないかもしれませんが、それでも煩わしいことがあります。このオーバーヘッドを最小限に抑えるために、Numba の ``cache`` 機能を使用することを検討してください。以下の例を参照してください。

.. code-block:: python

    from numba import njit
    # May take a few seconds
    from hftbacktest import BacktestAsset, HashMapMarketDepthBacktest

    # Enables caching feature
    @njit(cache=True)
    def algo(arguments, hbt):
        # your algo implementation.

    asset = (
        BacktestAsset()
            .linear_asset(1.0)
            .data([
                'data/ethusdt_20221003.npz',
                'data/ethusdt_20221004.npz',
                'data/ethusdt_20221005.npz',
                'data/ethusdt_20221006.npz',
                'data/ethusdt_20221007.npz'
            ])
            .initial_snapshot('data/ethusdt_20221002_eod.npz')
            .no_partial_fill_exchange()
            .intp_order_latency([
                'data/latency_20221003.npz',
                'data/latency_20221004.npz',
                'data/latency_20221005.npz',
                'data/latency_20221006.npz',
                'data/latency_20221007.npz'
            ])
            .power_prob_queue_model3(3.0)
            .tick_size(0.01)
            .lot_size(0.001)
            .trading_value_fee_model(0.0002, 0.0007)
    )

    hbt = HashMapMarketDepthBacktest([asset])
    algo(arguments, hbt)

