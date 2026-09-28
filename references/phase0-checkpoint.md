# Phase 0 Checkpoint — Historical Record

狀態：歷史審計記錄；舊B-Template執行方向已被`standard-generation-workflow.md`取代。

## Retained findings

Phase 0確認並保留了這些長期有效的成果：

- Golden UI、Behavior、Ledger Algorithm與Map Style擁有獨立合同；
- HTML/CSS/JavaScript、Ledger、Pages Function與D1 migration職責已審計；
- 舊版存在Trip ID重複、文字/陣列位置關聯、固定時區、D1無認證和Ledger settings共享缺失等風險；
- 私人Golden fixture、真實Trip ID、路線、日期、座標和assets不得進入Public Template；
- 公開Demo必須完全虛構或取得明確授權。

## Superseded Phase 0 decisions

以下曾是早期B-Template的臨時方向，現已廢止，不能再指導單次生成：

- 允許為每個Trip區域性修改HTML/CSS/JavaScript；
- 缺少Config時手工刪除模組；
- 人工放置地圖座標、手畫route和daily layouts；
- 不實現projection、validator或標準Map Generator；
- 預設圍繞Cloudflare D1 shared adapter執行。

現行方向是：

- 兩輪確認；
- Config-driven modules；
- canonical data與stable references；
- 自動boundary projection、route和Daily bounds；
- Core integrity驗證；
- local-first persistence；
- deployment與D1均為使用者明確選擇的後續任務。

## Privacy note

早期Phase 0審計曾包含私人倉庫與Custom Map Fixture資訊。那些值已從本公開目錄移除；不得透過Git history、線上頁面、截圖或私人目錄還原到Public Template。

## Current entry points

- `../SKILL.md`：Agent入口與強制邊界；
- `standard-generation-workflow.md`：當前單次生成權威流程；
- `deployment-guide.md`：本地預覽之後的可選釋出與D1流程；
- `golden-contract.md`：Core、隱私、行為和演算法總合同；
- `golden-map-spec.md`：當前標準地圖生成與視覺合同。
