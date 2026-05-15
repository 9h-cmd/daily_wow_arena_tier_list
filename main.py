import requests
import pandas as pd
import time
import os
from datetime import datetime
import matplotlib.pyplot as plt

# 서버 환경 설정 및 폰트 설정
plt.switch_backend('Agg')
plt.rcParams['font.sans-serif'] = ['DejaVu Sans']

today = datetime.now().strftime("%Y-%m-%d")
print(f"📅 [분석 시작] {today} - 구조 최적화 및 시각화 작업을 시작합니다.")

# 1. 고정 폴더 생성
base_folders = [
    "3v3_percentile", "shuffle_percentile", 
    "3v3_tier_list", "shuffle_tier_list",
    "rank_history", "plots"
]
for folder in base_folders:
    os.makedirs(folder, exist_ok=True)

wow_classes = {
    "death-knight": ["blood", "frost", "unholy"], "demon-hunter": ["havoc", "vengeance"],
    "druid": ["balance", "feral", "guardian", "restoration"], "evoker": ["augmentation", "devastation", "preservation"],
    "hunter": ["beast-mastery", "marksmanship", "survival"], "mage": ["arcane", "fire", "frost"],
    "monk": ["brewmaster", "mistweaver", "windwalker"], "paladin": ["holy", "protection", "retribution"],
    "priest": ["discipline", "holy", "shadow"], "rogue": ["assassination", "outlaw", "subtlety"],
    "shaman": ["elemental", "enhancement", "restoration"], "warlock": ["affliction", "demonology", "destruction"],
    "warrior": ["arms", "fury", "protection"]
}

target_ratings = [2000, 2100, 2200, 2300, 2400, 2500]
ratings_idx = list(range(1000, 2700, 100))
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

# 2. 데이터 수집 및 처리
for mode in ["3v3", "shuffle"]:
    url_part = "leaderboard-distrubution" if mode == "3v3" else "shuffle-distrubution"
    print(f"\n--- {mode.upper()} 데이터 수집 중 ---")
    current_df = pd.DataFrame(index=ratings_idx)
    
    for cls, specs in wow_classes.items():
        for spec in specs:
            col = f"{cls.replace('-', ' ').title()} - {spec.replace('-', ' ').title()}"
            url = f"https://drustvar.com/api/v1/leaderboard/{url_part}?search[region]=all&search[bracket]={mode}&search[role]=spec&search[cc]={cls}&search[cs]={spec}"
            try:
                res = requests.get(url, headers=headers, timeout=10)
                if res.status_code == 200:
                    for item in res.json().get("stats", []):
                        if item["rating"] in current_df.index:
                            current_df.loc[item["rating"], col] = item["percentile"]
            except: pass
            time.sleep(0.4)

    current_df = current_df.ffill().fillna(0)
    current_df.to_csv(f"{mode}_percentile/raw_{today}.csv", encoding="utf-8-sig")

    # 3. 점수대별 랭킹 및 시각화
    for target in target_ratings:
        calc_r = target - 100
        if calc_r not in current_df.index: continue

        # 상위 % 계산 및 순위
        top_pct = 100 - current_df.loc[calc_r]
        ranks = top_pct.rank(ascending=False, method='min')
        
        # 히스토리 업데이트 (rank_history 폴더로 집중)
        hist_file = f"rank_history/{mode}_{target}_history.csv"
        df_rank_today = pd.DataFrame(ranks).T
        df_rank_today.index = [today]
        
        if os.path.exists(hist_file):
            df_hist = pd.read_csv(hist_file, index_col=0)
            df_hist.loc[today] = df_rank_today.loc[today]
        else:
            df_hist = df_rank_today
        df_hist.to_csv(hist_file, encoding="utf-8-sig")

        # 4. 그래프 생성 (plots 폴더로 집중, 최신 1개만 유지)
        current_top10 = ranks.sort_values().head(10).index
        
        # 범례 공간 확보를 위해 가로 길이를 늘림
        plt.figure(figsize=(14, 8))
        for spec in current_top10:
            plot_data = df_hist[spec].tail(14)
            plt.plot(plot_data.index, plot_data.values, marker='o', linewidth=3, label=spec)
            
        plt.title(f"{target}+ {mode.upper()} Top 10 Spec Rank Trend", fontsize=16, pad=20)
        plt.ylabel("Rank (Top 1 is Higher)", fontsize=12)
        plt.xlabel("Date", fontsize=12)
        plt.gca().invert_yaxis()
        plt.yticks(range(1, 16)) # 1~15위까지만 표시하여 집중도 향상
        plt.grid(True, axis='y', linestyle='--', alpha=0.5)
        
        # 범례(Legend)를 그래프 오른쪽에 배치하여 겹치지 않게 함
        plt.legend(title="Specs", bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=10)
        
        plt.tight_layout()
        plt.savefig(f"plots/{mode}_{target}_trend.png", dpi=150)
        plt.close()

    # 통합 티어 리스트 저장 (tier_list 폴더)
    # 2200+ 상위 % 기준 정렬
    if 2100 in current_df.index:
        df_tier = (100 - current_df.loc[[r-100 for r in target_ratings if r-100 in current_df.index]]).T
        df_tier.columns = [f"{int(r)}+ 상위 (%)" for r in target_ratings if r-100 in current_df.index]
        df_tier.sort_values(by=df_tier.columns[2] if len(df_tier.columns)>2 else df_tier.columns[0], ascending=False).to_csv(f"{mode}_tier_list/ranking_{today}.csv", encoding="utf-8-sig")

print("\n🎉 구조 최적화 및 최신 트렌드 시각화 완료!")
