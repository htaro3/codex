# 0円・5分間隔PC監視：cron-job.org → GitHub Actions

この手順は「完全無料」に限定します。Render有料Cron Jobは使いません。

## 現状と限界
- GitHub Actionsの`schedule`自体は設定済みだが、定期起動の成功履歴は未確認。
- GitHub Actionsの`workflow_dispatch`は手動/APIから起動でき、既存のPC監視Pythonを実行する。
- cron-job.orgは無料で、5分ごとのPOST、カスタムHTTPヘッダー、JSONボディを設定できる。
- Yahoo!フリマ側は一部の新着検索結果のみ。メルカリ新着10件はまだ未実装。両サイト完全監視とは呼べない。

## ユーザー操作が必要な箇所
1. https://cron-job.org/en/ の無料アカウントを作る。
2. GitHubのSettings > Developer settings > Personal access tokens > Fine-grained tokensでトークンを作る。**対象は`htaro3/codex`だけ**、権限は`Actions: Read and write`のみに絞り、短い有効期限を設定する。トークンは公開リポジトリ、Issue、チャット、URLクエリに書かない。
3. cron-job.orgに以下のジョブを作る：
   - 名前: mini-pc-watch
   - URL: `https://api.github.com/repos/htaro3/codex/actions/workflows/pc-watch-live.yml/dispatches`
   - メソッド: POST
   - 5分間隔 / timezone: UTC
   - Header: `Authorization: Bearer <YOUR_FINE_GRAINED_PAT>`
   - Header: `Accept: application/vnd.github+json`
   - Header: `X-GitHub-Api-Version: 2022-11-28`
   - Header: `Content-Type: application/json`
   - Body: `{"ref":"main"}`
   - 成功ステータス: HTTP 204
   - 保存するレスポンスログ/通知にAuthorizationヘッダーが表示されないか確認する。
4. GitHub Actionsの`Mini PC deal watcher`で`workflow_dispatch`イベントの成功履歴を確認する。これが継続して出るまでは稼働保証なし。
5. 外部ジョブが継続稼働したらGitHub側`schedule`を無効化し、二重起動を防ぐ。既存Issue重複排除は残す。

## GitHubのアクセスに関する注意
- 外部サービスに渡すトークンは「Actionsの起動」だけに使い、商品検索やIssue作成には渡さない。
- Issue作成はGitHub内部の`secrets.GITHUB_TOKEN`で行う。
- 安全な送信が確認できなければ、外部サービスにトークンを預けず停止する。
- GitHub標準の`schedule`には遅延/欠落があり、5分ちょうどの実行は保証されない。cron-job.orgでもネットワークの遅延はあり得る。
