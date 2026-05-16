# ⚔️ WoW Arena Meta Analytics Dashboard

이 리포지토리는 세계 최대 PvP 데이터 사이트인 [Drustvar](https://www.google.com/search?q=https://drustvar.com)의 데이터를 기반으로, 매일 오전 9시(KST) 투기장 및 솔로 셔플의 **실시간 메타 변동을 추적하고 시각화**합니다.

## 📊 실시간 메타 트렌드 (Live Dashboard)

가장 최신의 60일간 순위 변동 그래프입니다. Y축 상단(1위)에 위치할수록 현재 해당 점수대에서 가장 강력한 영향력을 가진 특성(Spec)입니다.

### [3v3 Arena] 2400+ Meta Trend

### [Solo Shuffle] 2400+ Meta Trend

---

## 🛠️ 핵심 분석 지표 (Key Analysis)

| 기능 | 세부 사양 |
| --- | --- |
| **순위 추적 (Bump Chart)** | 최근 60일간의 전체 특성 순위 궤적을 유지하며 메타 흐름 파악 |
| **Top 20 집중 분석** | 오늘 기준 상위 20개 특성을 굵은 선으로 강조하고 범례에 순위별 정렬 표시 |
| **직업 가독성 (Class Colors)** | 전사(갈색), 법사(하늘색) 등 와우 공식 직업 색상을 적용하여 직관성 확보 |
| **전 특성 모니터링** | 악마사냥꾼(파멸 포함) 등 모든 세부 특성의 누적 백분위 데이터 수집 |
| **데이터 보존** | `rank_history` 내 CSV 파일을 통해 시즌 전체의 시계열 데이터 누적 관리 |

## 📂 데이터 저장 구조 (Data Map)

* **`/plots`**: 최신 트렌드 그래프 이미지 (PNG)
* **`/rank_history`**: 점수대별 순위 누적 데이터 (CSV)
* **`/*_tier_list`**: 날짜별 상위 유저 백분위 통합 랭킹 (CSV)
* **`/*_percentile`**: 전체 특성별 로우(Raw) 데이터 (CSV)

---

## ⚙️ 시스템 아키텍처 (Technical Specs)

* **Data Engine**: Python 3.10 / Pandas / Matplotlib
* **Automation**: GitHub Actions (Cron: `00:00 UTC`)
* **Visualization Logic**:
* 10위권 내 특성: **Solid & Bold Lines** (High Visibility)
* 10위권 외 특성: **Faded & Thin Lines** (Historical Continuity)
* Y-Axis: Inverted Rank (1-10 Focus Viewport)
