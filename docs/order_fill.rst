==========
注文の埋め合わせ
==========

取引所モデル
===============

HftBacktest は、市場データのリプレイに基づくバックテストツールであり、注文がシミュレートされた市場に変更を加えることはできません。市場への影響は考慮されません。したがって、最も重要な仮定の1つは、注文が市場に影響を与えないほど小さいことです。最終的には、実際の市場参加者とともにライブ市場でテストし、バックテスト結果とライブ結果の相違に基づいてバックテストを調整する必要があります。

Hftbacktest は、2 種類の取引所シミュレーションを提供します。:ref:`order_fill_no_partial_fill_exchange` は、部分的な埋め合わせが発生しないデフォルトの取引所シミュレーションです。:ref:`order_fill_partial_fill_exchange` は、特定のケースで部分的な埋め合わせを考慮する拡張取引所シミュレーションです。市場データのリプレイに基づくバックテストでは市場を変更できないため、一部の部分的な埋め合わせケースは依然として非現実的である可能性があります。たとえば、市場の流動性を取る場合です。これは、注文が市場の流動性を取る場合でも、リプレイされた市場データの市場深度と取引は変更できないためです。各バックテストシミュレーションの基礎となる仮定を理解することが重要です。

.. _order_fill_no_partial_fill_exchange:

NoPartialFillExchange
---------------------

完全実行の条件
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

注文書の買い注文

* 注文価格 >= 最良売り価格
* 注文価格 > 売り取引価格
* 注文がキューの先頭にあり、注文価格 == 売り取引価格

注文書の売り注文

* 注文価格 <= 最良買い価格
* 注文価格 < 買い取引価格
* 注文がキューの先頭にあり、注文価格 == 買い取引価格

流動性を取る注文
~~~~~~~~~~~~~~~~~~~~~~

    最良の数量に関係なく、流動性を取る注文は最良で完全に実行されます。大量の数量を実行しようとすると、非現実的な埋め合わせシミュレーションが発生する可能性があることに注意してください。

詳細は以下をご覧ください。

* `NoPartialFillExchange <https://docs.rs/hftbacktest/latest/hftbacktest/backtest/proc/struct.NoPartialFillExchange.html>`_
  および :meth:`no_partial_fill_exchange <hftbacktest.BacktestAsset.no_partial_fill_exchange>`

.. _order_fill_partial_fill_exchange:

PartialFillExchange
-------------------

完全実行の条件
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

注文書の買い注文

* 注文価格 >= 最良売り価格
* 注文価格 > 売り取引価格

注文書の売り注文

* 注文価格 <= 最良買い価格
* 注文価格 < 買い取引価格

部分実行の条件
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

注文書の買い注文

* 残りの売り取引数量によって埋め合わせ: 注文がキューの先頭にあり、注文価格 == 売り取引価格

注文書の売り注文

* 残りの買い取引数量によって埋め合わせ: 注文がキューの先頭にあり、注文価格 == 買い取引価格

流動性を取る注文
~~~~~~~~~~~~~~~~~~~~~~

    流動性を取る注文は、注文書の数量に基づいて実行されます。最良価格と数量は実行によって変更されませんが、大量の数量を実行しようとすると、非現実的な埋め合わせシミュレーションが発生する可能性があることに注意してください。

詳細は以下をご覧ください。

* `PartialFillExchange <https://docs.rs/hftbacktest/latest/hftbacktest/backtest/proc/struct.PartialFillExchange.html>`_
  および :meth:`partial_fill_exchange <hftbacktest.BacktestAsset.partial_fill_exchange>`

キューモデル
============

注文のキュー位置を知ることは、注文書の流動性と取引活動に応じて、バックテストで正確な注文埋め合わせシミュレーションを実現するために重要です。
取引所が Market-By-Order を提供しない場合、モデル化によって推測する必要があります。
HftBacktest は現在、ほとんどの暗号取引所が提供する Market-By-Price のみをサポートしており、注文埋め合わせシミュレーションのための以下のキュー位置モデルを提供しています。

詳細は `Models <https://docs.rs/hftbacktest/latest/hftbacktest/backtest/models/index.html>`_ を参照してください。

.. image:: images/liquidity-and-trade-activities.png

RiskAverseQueueModel
--------------------

このモデルは、キュー内の埋め合わせの機会に関して最も保守的なモデルです。
注文書の数量の減少は、キューの末尾でのみ発生するため、注文のキュー位置は変わりません。
注文のキュー位置は、価格で取引が発生した場合にのみ進行します。

詳細は以下をご覧ください。

* `RiskAdverseQueueModel <https://docs.rs/hftbacktest/latest/hftbacktest/backtest/models/struct.RiskAdverseQueueModel.html>`_
  および :meth:`risk_adverse_queue_model <hftbacktest.BacktestAsset.risk_adverse_queue_model>`

.. _order_fill_prob_queue_model:

ProbQueueModel
--------------
現在のキュー位置に応じた確率モデルに基づいて、数量の減少はキュー位置の前後の両方で発生します。
したがって、キュー位置も確率に応じて進行します。
このモデルは、以下に記載されているように実装されています。

* https://quant.stackexchange.com/questions/3782/how-do-we-estimate-position-of-our-order-in-order-book
* https://rigtorp.se/2013/06/08/estimating-order-queue-position.html

詳細は以下をご覧ください。

* `ProbQueueModel <https://docs.rs/hftbacktest/latest/hftbacktest/backtest/models/struct.ProbQueueModel.html>`_

* `PowerProbQueueFunc <https://docs.rs/hftbacktest/latest/hftbacktest/backtest/models/struct.PowerProbQueueFunc.html>`_
  および :meth:`power_prob_queue_model <hftbacktest.BacktestAsset.power_prob_queue_model>`

* `PowerProbQueueFunc2 <https://docs.rs/hftbacktest/latest/hftbacktest/backtest/models/struct.PowerProbQueueFunc2.html>`_
  および :meth:`power_prob_queue_model2 <hftbacktest.BacktestAsset.power_prob_queue_model2>`

* `PowerProbQueueFunc3 <https://docs.rs/hftbacktest/latest/hftbacktest/backtest/models/struct.PowerProbQueueFunc3.html>`_
  および :meth:`power_prob_queue_model3 <hftbacktest.BacktestAsset.power_prob_queue_model3>`

* `LogProbQueueFunc <https://docs.rs/hftbacktest/latest/hftbacktest/backtest/models/struct.LogProbQueueFunc.html>`_
  および :meth:`log_prob_queue_model <hftbacktest.BacktestAsset.log_prob_queue_model>`

* `LogProbQueueFunc2 <https://docs.rs/hftbacktest/latest/hftbacktest/backtest/models/struct.LogProbQueueFunc2.html>`_
  および :meth:`log_prob_queue_model2 <hftbacktest.BacktestAsset.log_prob_queue_model2>`

デフォルトでは、3 つのバリエーションが提供されています。これらの 3 つのモデルは、異なる確率プロファイルを持っています。

.. image:: images/probqueuemodel.png

関数 f = log(1 + x) は、価格レベルでの総数量に応じて異なる確率プロファイルを示します。これは、べき関数とは異なります。

.. image:: images/probqueuemodel_log.png

.. image:: images/probqueuemodel2.png
.. image:: images/probqueuemodel3.png

関数 f を設定する場合、次のようにする必要があります。

* 0 の確率は 0 である必要があります。キューの先頭に注文がある場合、すべての減少は注文の後に発生するためです。
* 1 の確率は 1 である必要があります。キューの末尾に注文がある場合、すべての減少は注文の前に発生するためです。

モデルの比較は :doc:`here <tutorials/Probability Queue Models>` で確認できます。

カスタムキューモデルの実装
------------------------------
使用要件に基づいて、次のトレイトを Rust で実装する必要があります。

* `QueueModel <https://docs.rs/hftbacktest/latest/hftbacktest/backtest/models/trait.QueueModel.html>`_
* `L3QueueModel <https://docs.rs/hftbacktest/latest/hftbacktest/backtest/models/trait.L3QueueModel.html>`_

キューモデルの実装については、`the queue model implementation <https://github.com/nkaz001/hftbacktest/blob/master/hftbacktest/src/backtest/models/queue.rs>`_ を参照してください。

参考文献
==========
これは、以下の記事に記載されているように最初に実装されました。

* http://www.math.ualberta.ca/~cfrei/PIMS/Almgren5.pdf
* https://quant.stackexchange.com/questions/3782/how-do-we-estimate-position-of-our-order-in-order-book
