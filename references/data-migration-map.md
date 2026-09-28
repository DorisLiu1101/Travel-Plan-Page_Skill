# Data Migration Map — Historical to Standard Generator

狀態：框架維護參考，不是單次Trip生成清單。  
普通現行流程：根目錄 `SKILL.md`；本文僅用於 advanced/canonical 相容。

本文記錄舊手工B-Template欄位如何歸入Config、canonical data、generated assets與runtime state。不得因讀取本文而修改某位使用者的Core。

## 1. Disposition vocabulary

| Disposition | Meaning |
|---|---|
| `CONFIG` | 進入`trip-config.json`，由使用者確認 |
| `CANONICAL` | 進入倉庫外 canonical build input 的唯一事實源；再由 compiler 生成 `travel-data.json` |
| `REFERENCE` | 用stable typed ID關聯 |
| `DERIVE` | 由build/renderer生成，不再人工維護 |
| `PRESENTATION` | 僅保持Golden顯示文案，不參與identity |
| `RUNTIME` | 執行後狀態，預設瀏覽器local |
| `GENERATE` | 由deterministic map/build tool輸出 |
| `PRIVATE INPUT` | 僅留在倉庫外的Source Facts/原始資料 |

## 2. Module and deployment decisions

| Old concern | Current owner | Disposition |
|---|---|---|
| 手工刪除section/nav/init | `trip-config.json > modules` | `CONFIG` |
| 元件自行判斷是否存在內容 | Config + validator | `CONFIG` / `DERIVE` |
| 預設請求shared API | `trip-config.json > persistence` | `CONFIG`; default local |
| Pages/D1繫結資訊 | 使用者Cloudflare專案 | 不進入倉庫 |

## 3. Core trip facts

| Old concern | Current owner | Disposition |
|---|---|---|
| 重複Trip ID | canonical Trip ID | `CANONICAL` / `REFERENCE` |
| 手寫日期範圍/day count | Days/events | `DERIVE` |
| 重複Place/address/query | Place entity | `CANONICAL` |
| schedule文字識別Place/Ticket | Day Item typed refs | `REFERENCE` |
| schedule index識別Transport | Transport/Day Item IDs | `REFERENCE` |
| 固定機場offset或租車offset | zoned endpoint/event | `CANONICAL` |
| display route/duration/summary | canonical facts | `DERIVE` or `PRESENTATION` |
| 原始訂單、PDF、OCR | private workspace | `PRIVATE INPUT` |

## 4. Map

| Old concern | Current owner | Disposition |
|---|---|---|
| 手寫國家輪廓 | authorized boundary GeoJSON + generator | `GENERATE` |
| 人工x/y | Place geo + projection | `GENERATE` |
| 人工route SVG | ordered Place/Transport refs | `GENERATE` |
| 人工label anchor | deterministic default label layout | `GENERATE` |
| Daily複用整國尺度 | Day places + generated bounds | `GENERATE` |
| schedule index pins | Transport/Day Item refs | `REFERENCE` / `GENERATE` |
| 私人Golden map | private fixture | 永不遷入Public Template |

生成結果可以快取於該Trip的assets/data；公共cache只能儲存不含Trip地點、路線、日期、地址或query的純country base。

## 5. Tickets, Todo and Ledger

| Concern | Current owner | Disposition |
|---|---|---|
| Ticket booking/document facts | Ticket entity | `CANONICAL` |
| Ticket displayed in a day | Day Item `ticketIds[]` | `REFERENCE` |
| Ticket completion | Runtime storage | `RUNTIME` |
| User-added Todo | Runtime storage | `RUNTIME` |
| Static preparation guidance | Trip/pre-trip facts | `CANONICAL` |
| Travelers, bills, settings | Runtime storage | `RUNTIME` |

Default runtime storage is localStorage by Trip ID, with in-memory fallback. Only explicit D1 mode and `sharedCollections` may send selected state to the user's D1.

## 6. Framework-maintenance gate

Changing schemas, adapters, Core files, generators or migration logic requires a dedicated framework task that:

1. states the contract being changed;
2. updates code and corresponding reference once;
3. runs Golden behavior/UI/map/Ledger regressions;
4. validates privacy and Demo neutrality;
5. only then regenerates `schemas/core-integrity.json` with `node scripts/validate-generation.mjs freeze`.

A normal user-trip task must stop at validator failure and report the framework gap. It must never run `freeze` to hide drift.
