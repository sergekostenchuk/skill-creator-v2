# Skill Creator V2

Skill Creator V2 は、AI skill と skill group を production 品質で作るための meta-skill です。

完成しているように見える prompt ではなく、文書化され、テスト可能で、依存関係と失敗モードを明示し、証拠を残す skill が必要なときに役立ちます。

使い方: npm package をインストールし、対象 runtime に skill をコピーして、agent に skill の作成または改善を依頼します。この skill は依頼を分類し、必要な reference だけを読み、tool/dependency を検証し、必要に応じて lint/evals を実行し、readiness report を作成します。

期待される成果物: `SKILL.md`, references, scripts, evals, tests, evidence-backed review を含む構造化された package です。

例: UI Intelligence group は、浅い reference 収集から、live-site evidence、scroll-state screenshots、public code/font/effect metadata、originality checks、そして実行結果を skill 改善へ戻す feedback loop へ発展しました。
