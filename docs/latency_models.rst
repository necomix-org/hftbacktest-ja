レイテンシーモデル
==================

概要
----

レイテンシーは、HFT 戦略をバックテストする際に考慮する必要がある重要な要素です。
HftBacktest には、3 種類のレイテンシーがあります。

.. image:: images/latencies.png

* フィードレイテンシー

これは、取引所が注文書の変更や取引などのフィードイベントを送信する時間と、ローカルで受信される時間の間のレイテンシーです。
このレイテンシーは、ローカルタイムスタンプと取引所タイムスタンプの 2 つの異なるタイムスタンプを通じて処理されます。

* 注文エントリレイテンシー

これは、注文リクエストを送信する時間と、取引所のマッチングエンジンによって処理される時間の間のレイテンシーです。

* 注文応答レイテンシー

これは、取引所のマッチングエンジンが注文リクエストを処理する時間と、注文応答がローカルで受信される時間の間のレイテンシーです。注文のフィルに対する応答もこのタイプのレイテンシーの影響を受けます。

.. image:: images/latency-comparison.png

注文レイテンシーモデル
----------------------

HftBacktest は、次の注文レイテンシーモデルを提供しており、独自のレイテンシーモデルを実装することもできます。

ConstantLatency
~~~~~~~~~~~~~~~
これは、一定のレイテンシーを使用する最も基本的なモデルです。レイテンシーを設定するだけです。

詳細は以下をご覧ください。

* `ConstantLatency <https://docs.rs/hftbacktest/latest/hftbacktest/backtest/models/struct.ConstantLatency.html>`_
  および :meth:`constant_latency <hftbacktest.BacktestAsset.constant_latency>`

IntpOrderLatency
~~~~~~~~~~~~~~~~
このモデルは、実際の注文レイテンシーデータに基づいて注文レイテンシーを補間します。
細かい時間間隔でデータを持っている場合、提供されているモデルの中で最も正確です。
実行不可能な注文を定期的に送信することで、レイテンシーデータを収集できます。

詳細は以下をご覧ください。

* `IntpOrderLatency <https://docs.rs/hftbacktest/latest/hftbacktest/backtest/models/struct.IntpOrderLatency.html>`_
  および :meth:`intp_order_latency <hftbacktest.BacktestAsset.intp_order_latency>`

**データ例**

.. code-block::

    req_ts (ローカルでのリクエストタイムスタンプ), exch_ts (取引所タイムスタンプ), resp_ts (ローカルでの受信タイムスタンプ), _padding
    1670026844751525000, 1670026844759000000, 1670026844762122000, 0
    1670026845754020000, 1670026845762000000, 1670026845770003000, 0

FeedLatency
~~~~~~~~~~~
ライブ注文レイテンシーデータが利用できない場合は、フィードレイテンシーを使用して人工的な注文レイテンシーを生成できます。
ガイダンスについては、:doc:`このチュートリアル <tutorials/Order Latency Data>` を参照してください。

独自の注文レイテンシーモデルを実装する
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
次のトレイトを実装する必要があります。

* `LatencyModel <https://docs.rs/hftbacktest/latest/hftbacktest/backtest/models/trait.LatencyModel.html>`_

レイテンシーモデルの実装については、`こちら <https://github.com/nkaz001/hftbacktest/blob/master/hftbacktest/src/backtest/models/latency.rs>`_ を参照してください。
