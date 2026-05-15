import requests
import pandas as pd
import time
import os
from datetime import datetime
import matplotlib.pyplot as plt

# 서버 환경 설정
plt.switch_backend('Agg')
plt.rcParams['font.sans-serif'] = ['DejaVu Sans']

# --- [설정 변수] ---
CHART_DAYS = 60  # 요청하신 대로 60일(약 2달)로 연장
VIEW_RANK_LIMIT = 10  # 그래프에 실제로 보여줄 순위 상한선
# ------------------

today = datetime.now().strftime("%Y-%m-%d")
print(f"📅 [분석 시작] {today} - 전체 특성 추적 및 1~{VIEW_RANK_LIMIT}위 집중 분석을 시작합니다.")

# 폴더 생성
base_folders = ["3v3_percentile", "shuffle_percentile", "3v3_tier_list", "shuffle_tier_list", "rank_history", "plots"]
for folder in base_folders:
    os.makedirs(folder, exist_ok=True)

# 악마사냥꾼 'devour' 특성 추가 반영
wow_classes = {
    "death-knight": ["blood", "frost", "unholy"],
    "demon-hunter": ["havoc", "vengeance", "devour"], # Devour 추가
    "druid": ["balance", "feral", "guardian", "restoration"],
    "evoker": ["augmentation", "devastation", "preservation"],
    "hunter": ["beast-mastery", "marksmanship", "survival"],
    "mage": ["arcane", "fire", "frost"],
    "monk": ["brewmaster", "mistweaver", "windwalker"],
    "paladin": ["holy", "protection", "retribution"],
    "priest": ["discipline", "holy", "shadow"],
    "rogue": ["assassination", "outlaw", "subtlety"],
    "shaman": ["elemental", "enhancement", "restoration"],
    "warlock": ["affliction", "demonology", "destruction"],
    "warrior": ["arms", "fury", "protection"]
}

target_ratings = [2000, 2100, 2200, 2300, 2400, 2500]
ratings_idx = list(range(1000, 2700, 100))
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

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

    for target in target_ratings:
        calc_r = target - 100
        if calc_r not in current_df.index: continue

        top_pct = 100 - current_df.loc[calc_r]
        ranks = top_pct.rank(ascending=False, method='min')
        
        hist_file = f"rank_history/{mode}_{target}_history.csv"
        df_rank_today = pd.DataFrame(ranks).T
        df_rank_today.index = [today]
        
        if os.path.exists(hist_file):
            df_hist = pd.read_csv(hist_file, index_col=0)
            if today in df_hist.index:
                df_hist.loc[today] = df_rank_today.loc[today]
            else:
                df_hist = pd.concat([df_hist, df_rank_today])
        else:
            df_hist = df_rank_today
        df_hist.to_csv(hist_file, encoding="utf-8-sig")

        # --- 그래프 생성 (모든 특성 플로팅 + 1~10위 뷰포트) ---
        plt.figure(figsize=(16, 10))
        
        # 1. 범례 정렬: 최신 날짜(오늘)의 순위 기준 (1등부터 꼴등까지)
        latest_ranks = df_hist.iloc[-1].sort_values()
        sorted_specs = latest_ranks.index

        for spec in sorted_specs:
            plot_data = df_hist[spec].tail(CHART_DAYS)
            
            # 오늘 10위 안에 들었으면 굵게, 아니면 얇게 (가독성 유지)
            is_top_10 = latest_ranks[spec] <= VIEW_RANK_LIMIT
            line_width = 3.5 if is_top_10 else 1.0
            line_alpha = 1.0 if is_top_10 else 0.2 # 10위 밖은 배경처럼 흐리게
            
            plt.plot(plot_data.index, plot_data.values, marker='o', 
                     markersize=4 if is_top_10 else 0, # 10위 밖은 마커 생략
                     linewidth=line_width, alpha=line_alpha, label=spec)

        plt.title(f"{target}+ {mode.upper()} Top 10 Meta Focus (Last {CHART_DAYS} Days)", fontsize=20, pad=30)
        plt.ylabel("Rank", fontsize=14)
        plt.xlabel("Date", fontsize=14)
        
        # Y축 반전 및 1~10위로 뷰포트 고정
        plt.gca().invert_yaxis()
        plt.ylim(VIEW_RANK_LIMIT + 0.5, 0.5) # 10.5위 ~ 0.5위까지 보여줌으로써 1~10위를 중앙에 배치
        
        plt.yticks(range(1, VIEW_RANK_LIMIT + 1))
        plt.xticks(rotation=45)
        plt.grid(True, axis='y', linestyle='--', alpha=0.3)
        
        # 2. 범례 최신 순위순으로 표시 (4열로 배치하여 공간 절약)
        plt.legend(title="Specs (Ranked Today)", bbox_to_anchor=(0.5, -0.15), 
                   loc='upper center', ncol=4, fontsize=9, frameon=True)
        
        plt.tight_layout()
        plt.savefig(f"plots/{mode}_{target}_trend.png", dpi=150)
        plt.close()

print(f"\n🎉 작업 완료! {CHART_DAYS}일간의 전체 데이터를 바탕으로 1~10위 집중 그래프가 생성되었습니다.")
