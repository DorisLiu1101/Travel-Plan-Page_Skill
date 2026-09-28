# Known Issues

原則：記錄，不修復；Confirmed/Potential/Unverified均不得自動寫入 Frozen正確行為。

## Summary

預設執行模式現為瀏覽器本地儲存。以下D1問題隻影響使用者明確啟用的shared mode，不影響普通本地預覽或靜態部署。

| 分類 | 數量 | ID |
|---|---:|---|
| Confirmed Issue | 3 | CI-01 ～ CI-03 |
| Potential Bug | 1 | PB-04 |
| Unverified Behavior | 8 | UV-01 ～ UV-08 |

## [CONFIRMED ISSUE]

### CI-01 — Ledger settings未進入D1共享鏈路

**受影響欄位**

- `baseCurrency`
- `commonCurrencies`
- `lastCurrency`

**已確認事實**

- D1只儲存`bills`、`travelers`；API snapshot不提供共享settings。
- 可選D1 migration無settings table/column。
- runtime D1 adapter使用獨立local adapter儲存settings，並把當前瀏覽器settings合併到遠端snapshot。

**當前影響**

- D1模式下Settings不能跨裝置共享。
- 預設local模式不受影響；Settings會隨該Trip儲存在當前瀏覽器。
- D1模式中的Settings仍按當前瀏覽器本地狀態處理，不能將其描述為雲端同步。

**分類決定**

這是可選D1 shared mode的當前限制，不是 `[FROZEN BEHAVIOR]` 或 `[FROZEN ALGORITHM]`。

### CI-02 — D1模式下Ticket mutation失敗不回滾且無使用者可見錯誤

**已確認事實**

- Checkbox change先修改`purchasedTickets` Set並更新所有ticket UI/day summary。
- 之後非同步POST upsert/delete。
- Promise rejection僅 `.catch(console.error)`。

**當前影響**

- 儲存失敗後當前頁面仍顯示使用者操作已成功。
- Reload後可能恢復服務端舊狀態。
- 使用者無法從頁面知道失敗或主動重試。

**分類決定**

Pending/Purchased互動意圖被凍結；失敗不rollback的結果不凍結為正確行為。本輪未修復。

### CI-03 — D1模式下Todo mutation失敗不回滾且無使用者可見錯誤

**已確認事實**

- 新增、完成/取消、刪除均先修改本地陣列並重繪。
- 之後非同步POST。
- Promise rejection僅 `.catch(console.error)`。

**當前影響**

- 失敗後UI與D1可能不一致。
- Reload後新增項可能消失、完成態可能反轉、刪除項可能重新出現。
- 頁面沒有失敗notice或retry狀態。

**分類決定**

Todo CRUD的使用者意圖被凍結；無rollback錯誤路徑不凍結。本輪未修復。

## [POTENTIAL BUG]

### PB-04 — D1 shared state讀取失敗可能被呈現為空狀態

- Travel shared API load失敗時，todos和purchasedTickets被清空並繼續渲染。
- 頁面只寫console，不顯示共享狀態讀取失敗。
- 使用者可能把“讀取失敗”誤判為“沒有資料”；真實D1恢復後的合併體驗未驗證。

## [CURRENT IMPLEMENTATION] — 不凍結的脆弱路徑

以下不是單獨bug計數，但不得升級為未來產品合同：

- 舊Demo/相容資料仍可能包含Ticket `scheduleMatchTerms`或Navigation文字匹配；新canonical Trip必須使用typed IDs，validator不得允許這些相容路徑成為新資料的identity。
- Todo ID使用timestamp + random suffix；穩定唯一語義保留，具體格式不凍結。
- Ledger settings defaults仍固定CNY/EUR/CHF/HKD；未來可由Config給初始值。
- Ledger多裝置同record寫入當前推導為last-write-wins。
- `local-preview-server.mjs`現在只提供靜態GET/HEAD預覽，不模擬`/api/trip`。可選D1的錯誤語義必須在使用者明確啟用後，透過Cloudflare本地開發環境或真實測試專案驗證。

## [UNVERIFIED]

### UV-01 — Travel details鍵盤行為

原生`details/summary`在不同瀏覽器的Escape、方向鍵與`role=menu`組合尚未驗證。

### UV-02 — 同view瀏覽器歷史與scroll

`#ledger/#ledger-stats`或多個Travel anchors之間Back/Forward的精確scroll恢復尚未做瀏覽器矩陣測試。

### UV-03 — Countdown時間邊界

精確等於target的毫秒、後臺tab interval節流、系統時間跳變與裝置休眠喚醒尚未驗證。

### UV-04 — Google Maps網路/瀏覽器限制

iframe被阻止、Google不可達、popup policy、外鏈開啟失敗時的完整使用者體驗尚未驗證。

### UV-05 — Fullscreen map dialog focus

Fullscreen的初始focus、Tab containment、Escape後的focus return和fallback-open路徑尚未完整驗證。

### UV-06 — Ledger dialog focus return

Native/fallback Ledger dialog關閉後的focus return目標與跨瀏覽器Tab containment尚未驗證。

### UV-07 — D1真實失敗注入

Ledger load/save failure、note failure、恢復網路後的重試和最終一致性尚未在真實Cloudflare D1環境完成。

### UV-08 — 兩裝置併發

不同record推導為record-level merge，同record推導為last-write-wins；尚未完成真實雙裝置D1測試。

## Resolved direction

- D1不再是預設依賴；有效Config的預設生成值為local mode。缺失/非法Config在頁面端顯示載入錯誤，不猜測模組選擇，也不連線D1。
- Local mode按Trip ID儲存Todo、Ticket、Ledger travelers/bills/settings，不請求`/api/trip`。
- D1只能由使用者顯式啟用，並使用使用者自己的Cloudflare database。
- module visibility由Config控制，單次Trip不修改Core。

## Deferred framework work

- D1模式下是否共享Ledger settings及採用何種server shape。
- 是否為D1模式的Todo/Ticket增加rollback、retry或衝突UI。
- 是否引入D1 revision/conflict control與認證。
