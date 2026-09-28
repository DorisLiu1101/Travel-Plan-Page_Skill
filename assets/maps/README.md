# Fixed Map Templates

普通旅行生成只使用 `templates/manifest.json` 中登記的十張固定底圖。Manifest 的執行時路徑全部指向 WebP；底圖負責紙張、地形、水體、山林和整體構圖，路線、節點、地點標籤、目的地標題及日期圖例始終由固定 Renderer 疊加。

1. `inland-alpine`：均衡或東西向路線。
2. `island-archipelago`：分離地點簇或存在明顯長距離跳轉。
3. `coastal-region`：以南北方向為主的路線。
4. `urban-radial`：單城市、緊湊或高密度點位。
5. `river-highland`：均衡路線或分離地點簇。
6. `upland-basin`：緊湊或均衡路線。
7. `compact-basin`：緊湊或高密度點位。
8. `wide-valley`：東西向路線。
9. `radial-watershed`：南北向或放射型路線。
10. `broad-riverland`：大跨度或多站路線。

Builder 先根據地點經緯度、路線跨度、方向、密度和連通關係形成候選池，再使用由區域、地點與路線組成的旅行簽名穩定雜湊，從候選池中確定性選擇一張。Manifest 中的 `selectionRole` 只是維護說明，Builder 不會直接解析這些字串作為選擇規則。Agent 不得自行選擇視覺風格、生成新底圖、重畫國家輪廓或修改模板安全區域。

十張圖片均作為本專案的固定靜態模板資產；普通生成不得覆蓋這些檔案。

`aster-isles-base.png`、`mist-coast-base.png`、`generic-diagram-template.svg` 與 `generated-japan.svg` 僅作為舊實現參考保留，不再進入預設 Builder 鏈路。
