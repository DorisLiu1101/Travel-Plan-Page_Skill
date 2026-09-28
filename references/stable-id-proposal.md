# Stable ID Convention

狀態：Standard Generator關係約束；具體可執行要求以當前Schema與validator為準。  
用途：避免文字匹配和陣列索引關聯。本文示例均為虛構值。

## 1. Current Generator Rule

- canonical Trip ID是唯一Trip ID；
- 已存在的flight、journey、stay、ticket、place、day/item與transport ID不得因顯示文案、日期或排序變化而改名；
- 新ID清晰、唯一、穩定且不包含私人敏感資訊；
- Day Item透過typed IDs引用Place、Ticket與Transport；
- Map直接引用Day、Place、Transport與Map Segment IDs；
- validator拒絕schedule/day array index、substring、match terms或display name充當Core-facing identity。

## 2. Naming convention

- lowercase ASCII kebab-case；
- 帶type prefix；
- 首次mint後不因name、language、date或sorting改變；
- readable slug是初始提示，不是每次重算公式；
- object map key可作為canonical ID，value不再重複漂移的`id`。

示例：

```text
entities.places["place-demo-airport"]
days[].items[].placeId = "place-demo-airport"
map.layouts.places["place-demo-airport"]
```

## 3. ID class catalog

| # | Class | Suggested prefix | Fictional example |
|---:|---|---|---|
| 1 | Trip | `trip-*` | `trip-demo-aster-isles` |
| 2 | Day | `day-*` | `day-demo-arrival` |
| 3 | Day Item | `item-*` | `item-demo-airport-arrival` |
| 4 | Place | `place-*` | `place-demo-airport` |
| 5 | Stay | `stay-*` | `stay-demo-bay-001` |
| 6 | Flight | `flight-*` | `flight-demo-gl101` |
| 7 | Flight Group | `journey-*` / `flight-group-*` | `journey-demo-outbound` |
| 8 | Carrier | `carrier-*` | `carrier-demo-glimmer` |
| 9 | Ticket | `ticket-*` | `ticket-demo-museum` |
| 10 | Transport | `transport-*` | `transport-demo-ferry-out` |
| 11 | Rental | `rental-*` | `rental-demo-001` |
| 12 | Restaurant | `restaurant-*` | `restaurant-demo-bistro` |
| 13 | Pre-trip Item | `prep-*` / `pack-*` | `pack-demo-documents` |
| 14 | Map Region | `map-region-*` | `map-region-demo-country` |
| 15 | Map Route | `map-route-*` | `map-route-demo-day2` |
| 16 | Map Segment | `map-segment-*` | `map-segment-demo-bay-harbor` |
| 17 | Map Feature | `map-feature-*` | `map-feature-demo-ferry-pin` |
| 18 | Issue | `issue-*` | `issue-demo-time-unconfirmed` |

Runtime Todo IDs不屬於靜態Trip Package；多裝置併發ID策略應在專門的Runtime State工作中決定。

## 4. Typed references

Day Item按需要顯式引用：

| Field | Target |
|---|---|
| `placeId` / `placeIds` | Place |
| `stayId` | Stay |
| `flightId` | Flight |
| `ticketIds` | Tickets |
| `transportId` | Transport |
| `rentalId` | Rental |
| `restaurantId` | Restaurant |
| `issueIds` | Issues |

Flight Group可擁有ordered `flightIds[]`；Flight不再同時儲存group membership和sequence。Map可直接引用Day、Place、Transport與Map Segment IDs。

## 5. Relations an Upgrade Should Remove

- `schedule[index]`或`days[index]`作為跨模組identity；
- numeric day number作為唯一關係鍵；
- `scheduleMatchTerms`、`matchTerms`和substring entity lookup；
- 從display name動態生成restaurant/entity ID；
- SVG child order決定route branch；
- destination/day-specific name conditions。

Arrays仍可表達顯示順序，strings仍可用於標題、說明和provider query；禁止的是用它們隱式發現identity。

## 6. Validation

validator至少檢查：

- ID格式和collection內唯一性；
- typed reference存在且型別正確；
- Day Item ID在Trip內唯一；
- ordered reference array無重複；
- map/day/place/transport/segment引用全部可解析；
- display text修改不會改變entity selection。

## 7. Implementation boundary

Schema可以分階段支援上述ID classes，但單次Trip生成不得透過修改Renderer或放寬validator來容納例外。需要新增entity type或關係時，記錄為獨立框架維護任務，幷包含data adapter、behavior regression、map regression與rollback。
