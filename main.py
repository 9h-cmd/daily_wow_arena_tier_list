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
CHART_DAYS = 60  # 그래프에 보여줄 기간 (원하시는 대로 숫자를 키우세요!)
TOP_N = 10       # 순위권 몇 위까지 보여줄지
# ------------------

today = datetime.now().strftime("%Y-%m-%d")
print(f"📅 [분석 시작] {today} - 최근 {CHART_DAYS}일간의 트렌드 분석을 시작합니다.")

# 폴더 생성
for folder in ["3v3_percentile", "shuffle_percentile", "3v3_tier_list", "shuffle_tier_list", "rank_history", "plots"]:
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
            # 중복 데이터 방지 (오늘 이미 실행했다면 덮어쓰기)
            if today in df_hist.index:
                df_hist.loc[today] = df_rank_today.loc[today]
            else:
                df_hist = pd.concat([df_hist, df_rank_today])
        else:
            df_hist = df_rank_today
        df_hist.to_csv(hist_file, encoding="utf-8-sig")

        # --- 그래프 생성 최적화 ---
        current_top_n = ranks.sort_values().head(TOP_N).index
        plt.figure(figsize=(15, 9)) # 가로 길이를 더 늘려 시원하게 만듦
        
        for spec in current_top_n:
            # 설정한 기간만큼 데이터 슬라이싱
            plot_data = df_hist[spec].tail(CHART_DAYS)
            plt.plot(plot_data.index, plot_data.values, marker='o', markersize=4, linewidth=2.5, label=spec)
            
        plt.title(f"{target}+ {mode.upper()} Top {TOP_N} Rank Trend (Last {CHART_DAYS} Days)", fontsize=18, pad=25)
        plt.ylabel("Rank", fontsize=14)
        plt.xlabel("Date", fontsize=14)
        plt.gca().invert_yaxis()
        
        # 가독성을 위해 Y축 범위를 1위부터 15위 정도로 고정
        plt.yticks(range(1, 16))
        
        # X축 날짜가 많아질 경우 글자가 겹치지 않게 45도 회전
        plt.xticks(rotation=45)
        
        plt.grid(True, axis='y', linestyle='--', alpha=0.5)
        plt.legend(title="Specs", bbox_to_anchor=(1.02, 1), loc='upper left', fontsize=11)
        
        plt.tight_layout()
        plt.savefig(f"plots/{mode}_{target}_trend.png", dpi=150)
        plt.close()

    # 통합 티어 리스트 저장 (가장 최신 날짜 기준)
    if 2100 in current_df.index:
        df_tier = (100 - current_df.loc[[r-100 for r in target_ratings if r-100 in current_df.index]]).T
        df_tier.columns = [f"{int(r)}+ 상위 (%)" for r in target_ratings if r-100 in current_df.index]
        sort_col = df_tier.columns[2] if len(df_tier.columns)>2 else df_tier.columns[0]
        df_tier.sort_values(by=sort_col, ascending=False).to_csv(f"{mode}_tier_list/ranking_{today}.csv", encoding="utf-8-sig")

print(f"\n🎉 분석 완료! 최근 {CHART_DAYS}일간의 트렌드가 plots 폴더에 업데이트되었습니다.")
