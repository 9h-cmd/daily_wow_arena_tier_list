# daily_wow_arena_tier_list
World of Warcraft(와우) PvP 데이터를 매일 자동으로 수집하고, 각 점수대별(2000~2500+) 특성(Spec)의 상위 백분위 및 순위 변동을 분석하는 프로젝트입니다.

🚀 주요 기능 (Features)
자동 데이터 수집 (Daily Scraping): 매일 오전 9시(KST)에 Drustvar API를 통해 3v3 및 Solo Shuffle의 실시간 데이터를 수집합니다.

상위 백분위 분석 (Tier Analysis): 각 점수대별 누적 백분위를 계산하여, 해당 점수대 이상의 상위 유저 비율을 산출합니다.

순위 변동 추적 (Rank Tracking): 매일 변동하는 특성별 순위를 rank_history에 누적 기록합니다.

트렌드 시각화 (Visualization): 최근 14일간의 상위 10개 특성 순위 변화를 Bump Chart(순위 변동 그래프)로 생성하여 한눈에 메타 변화를 파악할 수 있게 합니다.

📂 리포지토리 구조 (Directory Structure)
Plaintext
.

├── 3v3_percentile/        # 3v3 투기장 날짜별 원본 백분위 데이터 (CSV)
├── shuffle_percentile/    # 솔로 셔플 날짜별 원본 백분위 데이터 (CSV)
├── 3v3_tier_list/         # 3v3 점수대별 상위 % 통합 랭킹 리스트
├── shuffle_tier_list/     # 솔로 셔플 점수대별 상위 % 통합 랭킹 리스트
├── rank_history/          # 시계열 분석을 위한 점수대별 순위 누적 데이터
├── plots/                 # [최신] 메타 트렌드 시각화 그래프 (PNG)
├── main.py                # 데이터 수집 및 분석 핵심 엔진
└── .github/workflows/     # GitHub Actions 자동화 설정 (매일 09:00 실행)
📈 메타 트렌드 미리보기 (Visual Preview)
plots/ 폴더에서 각 점수대별 최신 트렌드 그래프를 확인할 수 있습니다. 그래프의 Y축은 순위(Rank)를 나타내며, 위로 갈수록 해당 점수대에서 가장 강력한 성능(또는 인구수)을 보여주는 1티어 특성입니다.

Tip: 그래프는 매일 업데이트되며, 선이 우상향하고 있다면 현재 메타에서 급부상 중인 '사기 특성'일 확률이 높습니다.

🛠️ 기술 스택 (Tech Stack)
Language: Python 3.10+

Libraries: Pandas, Requests, Matplotlib

Automation: GitHub Actions

⚠️ 주의 사항
본 프로젝트는 교육 및 개인 분석용으로 제작되었습니다.

데이터의 출처는 Drustvar이며, 게임 내 실시간 상황과 약간의 오차가 있을 수 있습니다.
