# Data Duplication Matrix

狀態：Advanced/legacy One Fact 檢查參考；普通生成以根目錄 `SKILL.md` 與 `validate-lite` 為準。

## 1. Authoritative ownership

| Fact | Authoritative source | Derived / presentation consumers | Forbidden second authority |
|---|---|---|---|
| Module enablement | `trip-data.json > config.modules` | section/navigation/init visibility | 刪除HTML、JS條件特判 |
| Persistence mode | `trip-data.json > config.persistence` | runtime storage adapter | Ledger/Todo/Ticket各自猜測後端 |
| Trip identity | canonical Trip ID | runtime storage namespace、API path | HTML第二個Trip ID |
| Trip dates/day count | Days/events | Hero與summary | 人工維護衝突摘要 |
| Flight facts | Flight entity | cards、timeline references | schedule文字中的獨立事實 |
| Stay facts | Stay + Place | daily display/navigation | HTML品牌/地址常量 |
| Place name/address/geo/query | Place entity | itinerary、map、overlay | map/navigation平行Place目錄 |
| Ticket identity/document | Ticket entity | Day Item、Ticket renderer | substring匹配、重複票據記錄 |
| Ticket completion | Runtime state by Ticket ID | Ticket UI/day summary | 靜態Trip Data boolean |
| Transport leg | Transport entity | Day Item、map route/pin/popup | schedule index或複製文字 |
| Rental facts | Rental + Place | driving card/countdown | HTML provider或固定時區 |
| Day item order | `days[].items[]` sequence | Timeline | array position充當跨模組ID |
| Map country | canonical destination countries | generated country packages/tabs | 從display text猜國家 |
| Map place | canonical Place geo | projected x/y、labels、hit targets | 第二套手工地點identity |
| Map route | Day/Transport/Place order | generated SVG paths | 手工path充當路線事實 |
| Daily map range | selected Day place set | generated bounds/layout | 複用整國畫布造成城市點聚集 |
| Todo items/completion | Runtime state | Todo UI | 靜態規劃內容混入runtime list |
| Ledger travelers/bills/settings | Runtime state | Ledger views/stats | 靜態Trip fixture |
| Missing/ambiguous facts | private Source Facts issues | preview待補充狀態/report | Agent猜測值 |

## 2. Current authoring rules

1. 先從倉庫外`source-facts.json`生成canonical data。
2. 所有entity和cross-module relation使用stable typed IDs。
3. Presentation text可以重複顯示，但不能控制選擇、匹配或identity。
4. Map Package由generator派生，不人工同步座標、route或schedule indexes。
5. Runtime Todo、Ticket completion與Ledger不寫入靜態Demo或Trip Data。
6. Config/Data和所有引用必須透過validator。

## 3. Validation gate

以下情況必須失敗，而不是要求Agent手工“記得同步”：

- 同一事實出現兩個可編輯來源；
- 任一typed reference懸空、型別錯誤或重複；
- display text變化導致entity、Ticket、Place或Transport選擇改變；
- schedule/day/SVG child位置被用作跨模組identity；
- Map Package與canonical Place/Day/Transport不一致；
- Runtime state進入公開Trip fixture；
- 私人Source Facts、原始檔案路徑或Cloudflare identity進入釋出目錄。

需要改變上述所有權時，作為獨立框架維護任務處理；單次旅行生成不得修改Core來繞過檢查。
