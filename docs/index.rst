.. meta::
   :google-site-verification: IJcyhIoS28HF0lp6fGjBEOC65kVecelW6ZsFhbDaD-A

===========
HftBacktest
===========

|codeql| |python| |pypi| |downloads| |rustc| |crates| |license| |docs| |roadmap| |github|

高頻度取引バックテストツール
==============================

このフレームワークは、高頻度取引およびマーケットメイキング戦略の開発を目的としています。フィードおよび注文のレイテンシー、ならびに注文埋め合わせシミュレーションのための注文キュー位置を考慮することに重点を置いています。このフレームワークは、完全な注文書および取引ティックフィードデータに基づくより正確な市場リプレイベースのバックテストを提供することを目的としています。

主な機能
========

実験的な機能は現在開発の初期段階にあり、Rust で完全に書き直されて以下の機能をサポートしています。

* `Numba <https://numba.pydata.org/>`_ JIT 関数 (Python) で動作します。
* カスタマイズ可能な時間間隔またはフィードおよび注文の受信に基づく完全なティックバイティックシミュレーション。
* L2 Market-By-Price および L3 Market-By-Order フィードに基づく完全な注文書の再構築。
* 提供されたモデルまたは独自のカスタムモデルを使用して、フィードおよび注文のレイテンシーを考慮したバックテスト。
* 提供されたモデルまたは独自のカスタムモデルを使用して、注文キュー位置を考慮した注文埋め合わせシミュレーション。
* 複数資産および複数取引所モデルのバックテスト。
* 同じアルゴリズムコードを使用してライブトレーディングボットを展開: 現在は Binance Futures および Bybit に対応。(Rust の��)

ドキュメント
=============

`こちら <https://hftbacktest.readthedocs.io/>`_ で完全なドキュメントを参照してください。

始め方
=======

インストール
------------

hftbacktest は Python 3.10+ をサポートしています。``pip`` を使用して hftbacktest をインストールできます。

.. code-block:: console

 pip install hftbacktest

または、Git リポジトリから最新の開発バージョンをクローンすることもできます。

.. code-block:: console

 git clone https://github.com/nkaz001/hftbacktest

データソースとフォーマット
--------------------

`Data <https://hftbacktest.readthedocs.io/en/latest/data.html>`_ または `Data Preparation <https://hftbacktest.readthedocs.io/en/latest/tutorials/Data%20Preparation.html>`_ を参照してください。

サポーターがホストしている `こちら <https://reach.stratosphere.capital/data/usdm/>`_ でもデータを見つけることができます。

クイック例
----------

hftbacktest を使用したバックテストの様子を以下のコードスニペットでご覧ください。

.. code-block:: python

    @njit
    def market_making_algo(hbt):
        asset_no = 0
        tick_size = hbt.depth(asset_no).tick_size
        lot_size = hbt.depth(asset_no).lot_size

        # in nanoseconds
        while hbt.elapse(10_000_000) == 0:
            hbt.clear_inactive_orders(asset_no)

            a = 1
            b = 1
            c = 1
            hs = 1

            # Alpha, it can be a combination of several indicators.
            forecast = 0
            # In HFT, it can be various measurements of short-term market movements,
            # such as the high-low range in the last X minutes.
            volatility = 0
            # Delta risk, it can be a combination of several risks.
            position = hbt.position(asset_no)
            risk = (c + volatility) * position
            half_spread = (c + volatility) * hs

            max_notional_position = 1000
            notional_qty = 100

            depth = hbt.depth(asset_no)

            mid_price = (depth.best_bid + depth.best_ask) / 2.0

            # fair value pricing = mid_price + a * forecast
            #                      or underlying(correlated asset) + adjustment(basis + cost + etc) + a * forecast
            # risk skewing = -b * risk
            reservation_price = mid_price + a * forecast - b * risk
            new_bid = reservation_price - half_spread
            new_ask = reservation_price + half_spread

            new_bid_tick = min(np.round(new_bid / tick_size), depth.best_bid_tick)
            new_ask_tick = max(np.round(new_ask / tick_size), depth.best_ask_tick)

            order_qty = np.round(notional_qty / mid_price / lot_size) * lot_size

            # Elapses a process time.
            if not hbt.elapse(1_000_000) != 0:
                return False

            last_order_id = -1
            update_bid = True
            update_ask = True
            buy_limit_exceeded = position * mid_price > max_notional_position
            sell_limit_exceeded = position * mid価格 < -max_notional_position
            orders = hbt.orders(asset_no)
            order_values = orders.values()
            while order_values.has_next():
                order = order_values.get()
                if order.side == BUY:
                    if order.price_tick == new_bid_tick or buy_limit_exceeded:
                        update_bid = False
                    if order.cancellable and (update_bid or buy_limit_exceeded):
                        hbt.cancel(asset_no, order.order_id, False)
                        last_order_id = order.order_id
                elif order.side == SELL:
                    if order.price_tick == new_ask_tick or sell_limit_exceeded:
                        update_ask = False
                    if order.cancellable and (update_ask or sell_limit_exceeded):
                        hbt.cancel(asset_no, order.order_id, False)
                        last_order_id = order.order_id

            # It can be combined with a grid trading strategy by submitting multiple orders to capture better spreads and
            # have queue position.
            # This approach requires more sophisticated logic to efficiently manage resting orders in the order book.
            if update_bid:
                # There is only one order at a given price, with new_bid_tick used as the order ID.
                order_id = new_bid_tick
                hbt.submit_buy_order(asset_no, order_id, new_bid_tick * tick_size, order_qty, GTX, LIMIT, False)
                last_order_id = order_id
            if update_ask:
                # There is only one order at a given price, with new_ask_tick used as the order ID.
                order_id = new_ask_tick
                hbt.submit_sell_order(asset_no, order_id, new_ask_tick * tick_size, order_qty, GTX, LIMIT, False)
                last_order_id = order_id

            # All order requests are considered to be requested at the same time.
            # Waits until one of the order responses is received.
            if last_order_id >= 0:
                # Waits for the order response for a maximum of 5 seconds.
                timeout = 5_000_000_000
                if not hbt.wait_order_response(asset_no, last_order_id, timeout):
                    return False

        return True


チュートリアル
=============
* `Data Preparation <https://hftbacktest.readthedocs.io/en/latest/tutorials/Data%20Preparation.html>`_
* `Getting Started <https://hftbacktest.readthedocs.io/en/latest/tutorials/Getting%20Started.html>`_
* `Working with Market Depth and Trades <https://hftbacktest.readthedocs.io/en/latest/tutorials/Working%20with%20Market%20Depth%20and%20Trades.html>`_
* `Integrating Custom Data <https://hftbacktest.readthedocs.io/en/latest/tutorials/Integrating%20Custom%20Data.html>`_
* `Making Multiple Markets - Introduction <https://hftbacktest.readthedocs.io/en/latest/tutorials/Making%20Multiple%20Markets%20-%20Introduction.html>`_
* `High-Frequency Grid Trading <https://hftbacktest.readthedocs.io/en/latest/tutorials/High-Frequency%20Grid%20Trading.html>`_
* `Impact of Order Latency <https://hftbacktest.readthedocs.io/en/latest/tutorials/Impact%20of%20Order%20Latency.html>`_
* `Order Latency Data <https://hftbacktest.readthedocs.io/en/latest/tutorials/Order%20Latency%20Data.html>`_
* `Guéant–Lehalle–Fernandez-Tapia Market Making Model and Grid Trading <https://hftbacktest.readthedocs.io/en/latest/tutorials/GLFT%20Market%20Making%20Model%20and%20Grid%20Trading.html>`_
* `Making Multiple Markets <https://hftbacktest.readthedocs.io/en/latest/tutorials/Making%20Multiple%20Markets.html>`_
* `Risk Mitigation through Price Protection in Extreme Market Conditions <https://hftbacktest.readthedocs.io/en/latest/tutorials/Risk%20Mitigation%20through%20Price%20Protection%20in%20Extreme%20Market%20Conditions.html>`_
* `Level-3 Backtesting <https://hftbacktest.readthedocs.io/en/latest/tutorials/Level-3%20Backtesting.html>`_
* `Market Making with Alpha - Order Book Imbalance <https://hftbacktest.readthedocs.io/en/latest/tutorials/Market%20Making%20with%20Alpha%20-%20Order%20Book%20Imbalance.html>`_
* `Queue-Based Market Making in Large Tick Size Assets <https://hftbacktest.readthedocs.io/en/latest/tutorials/Queue-Based%20Market%20Making%20in%20Large%20Tick%20Size%20Assets.html>`_

例
==

`examples <https://github.com/nkaz001/hftbacktest/tree/master/examples>`_ ディレクトリおよび `Rust examples <https://github.com/nkaz001/hftbacktest/blob/master/hftbacktest/examples/>`_ でさらに多くの例を見つけることができます。

Binance Futures のバックテストの完全なプロセス
----------------------------------------------
`high-frequency gridtrading <https://github.com/nkaz001/hftbacktest/blob/master/hftbacktest/examples/gridtrading.ipynb>`_: Rust で実装された高頻度グリッドトレーディング戦略を使用した Binance Futures のバックテストの完全なプロセス。

バージョン2への移行
===================
`migration guide <https://hftbacktest.readthedocs.io/en/latest/migration2.html>`_ を参照してください。

ロードマップ
=========

現在、新機能は Numba の制限のために Rust で実装されています。高頻度データのサイズを考慮すると、パフォーマンスが重要です。
差し迫ったタスクは、Rust 実装をバックエンドとして使用して、Python の hftbacktest と Rust の hftbacktest を統合することです。
一方で、現在異なるデータフォーマットを統一する必要があります。
純粋な Python 側では、パフォーマンスレポートツールを改善して、より多くのパフォーマンスメトリクスを提供し、速度を向上させる必要があります。

`roadmap <https://github.com/nkaz001/hftbacktest/blob/master/ROADMAP.md>`_ を参照してください。

貢献
====

hftbacktest への貢献を検討していただきありがとうございます。プロジェクトの改善に向けたあらゆる支援を歓迎します。改善のアイデアやバグ修正がある場合は、GitHub で問題やディスカッションを開いて話し合ってください。

このプロジェクトに対して行うことができる貢献の例は次のとおりです。

`roadmap <https://github.com/nkaz001/hftbacktest/blob/master/ROADMAP.md>`_ を参照してください。

.. |python| image:: https://shields.io/badge/python-3.10-blue
    :alt: Python Version
    :target: https://www.python.org/

.. |codeql| image:: https://github.com/nkaz001/hftbacktest/actions/workflows/codeql.yml/badge.svg?branch=master&event=push
    :alt: CodeQL
    :target: https://github.com/nkaz001/hftbacktest/actions/workflows/codeql.yml

.. |pypi| image:: https://badge.fury.io/py/hftbacktest.svg
    :alt: Package Version
    :target: https://pypi.org/project/hftbacktest

.. |downloads| image:: https://static.pepy.tech/badge/hftbacktest
    :alt: Downloads
    :target: https://pepy.tech/project/hftbacktest

.. |crates| image:: https://img.shields.io/crates/v/hftbacktest.svg
    :alt: Rust crates.io version
    :target: https://crates.io/crates/hftbacktest

.. |license| image:: https://img.shields.io/badge/License-MIT-green.svg
    :alt: License
    :target: https://github.com/nkaz001/hftbacktest/blob/master/LICENSE

.. |docs| image:: https://readthedocs.org/projects/hftbacktest/badge/?version=latest
    :target: https://hftbacktest.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status

.. |roadmap| image:: https://img.shields.io/badge/Roadmap-gray
    :target: https://github.com/nkaz001/hftbacktest/blob/master/ROADMAP.md
    :alt: Roadmap

.. |github| image:: https://img.shields.io/github/stars/nkaz001/hftbacktest?style=social
    :target: https://github.com/nkaz001/hftbacktest
    :alt: Github

.. |rustc| image:: https://shields.io/badge/rustc-1.80.1-blue
    :alt: Rust Version
    :target: https://www.rust-lang.org/

.. toctree::
   :maxdepth: 1
   :caption: Tutorials
   :hidden:

   tutorials/Data Preparation
   tutorials/Getting Started
   tutorials/Working with Market Depth and Trades
   tutorials/Integrating Custom Data
   tutorials/Making Multiple Markets - Introduction
   tutorials/High-Frequency Grid Trading
   tutorials/Impact of Order Latency
   tutorials/Order Latency Data
   tutorials/GLFT Market Making Model and Grid Trading
   tutorials/Making Multiple Markets
   tutorials/Probability Queue Models
   tutorials/Risk Mitigation through Price Protection in Extreme Market Conditions
   tutorials/Level-3 Backtesting
   tutorials/Market Making with Alpha - Order Book Imbalance
   tutorials/Queue-Based Market Making in Large Tick Size Assets
   tutorials/examples

.. toctree::
   :maxdepth: 2
   :caption: User Guide
   :hidden:

   Migration To v2 <migration2>
   Data <data>
   Latency Models <latency_models>
   Order Fill <order_fill>
   JIT Compilation Overhead <jit_compilation_overhead>
   Debugging Backtesting and Live Discrepancies <debugging_backtesting_and_live_discrepancies>

.. toctree::
   :maxdepth: 2
   :caption: API Reference
   :hidden:

   Initialization <reference/initialization>
   Backtester <reference/backtester>
   Constants <reference/constants>
   Statistics <reference/stats>
   Data Validation <reference/data_validation>
   Data Utilities <reference/data_utilities>
   Index <genindex>
