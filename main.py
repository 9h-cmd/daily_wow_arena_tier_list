import requests
import pandas as pd
import time
import os
from datetime import datetime
import matplotlib.pyplot as plt

# 서버 환경 및 폰트 설정
plt.switch_backend('Agg')
plt.rcParams['font.sans-serif'] = ['DejaVu Sans']

# --- [설정 및 색상 정의] ---
CHART_DAYS = 60
VIEW_RANK_LIMIT = 20

# 와우 직업별 공식 색상 (Hex Code)
CLASS_COLORS = {
    "Death Knight": "#C41E3A", "Demon Hunter": "#A330C9", "Druid": "#FF7C0A",
    "Evoker": "#33937F", "Hunter": "#AAD372", "Mage": "#3FC7EB",
    "Monk": "#00FF98", "Paladin": "#F48CBA", "Priest": "#FFFFFF",
    "Rogue": "#FFF468", "Shaman": "#0070DD", "Warlock": "#8788EE",
    "Warrior": "#C69B6D"
}
# ---------------------------

today = datetime.now().strftime("%Y-%m-%d")
print(f"📅 [기능 데이터 확장] {today} - 순위와 상위 %를 동시에 기록 및 시각화합니다.")

# 1. 고정 폴더 생성
base_folders = [
    "3v3_percentile", "shuffle_percentile", 
    "3v3_tier_list", "shuffle_tier_list",
    "rank_history", "plots"
]
for folder in base_folders:
    os.makedirs(folder, exist_ok=True)

# 직업 및 특성 정의
wow_classes = {
    "death-knight": ["blood", "frost", "unholy"],
    "demon-hunter": ["havoc", "vengeance", "devour"],
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
        
        # [데이터 확장] 오늘자 순위와 %를 딕셔너리로 결합
        today_data = {}
        for spec in ranks.index:
            today_data[f"{spec} (Rank)"] = ranks[spec]
            today_data[f"{spec} (%)"] = round(top_pct[spec], 3)
        df_rank_today = pd.DataFrame([today_data], index=[today])
        
        hist_file = f"rank_history/{mode}_{target}_history.csv"
        
        if os.path.exists(hist_file):
            df_hist = pd.read_csv(hist_file, index_col=0)
            # 만약 기존 구버전 파일(괄호 없는 옛날 포맷)이면 구조 충돌 방지를 위해 새로 리셋
            if not any("(Rank)" in col for col in df_hist.columns):
                df_hist = df_rank_today
            else:
                if today in df_hist.index:
                    df_hist.loc[today] = df_rank_today.loc[today]
                else:
                    df_hist = pd.concat([df_hist, df_rank_today])
        else:
            df_hist = df_rank_today
        df_hist.to_csv(hist_file, encoding="utf-8-sig")

        # 4. 그래프 생성 (Plots)
        plt.figure(figsize=(16, 9), facecolor='#1e1e1e')
        ax = plt.gca()
        ax.set_facecolor('#1e1e1e')
        
        latest_ranks = ranks.sort_values()
        sorted_specs = latest_ranks.index

        for spec in sorted_specs:
            # 그래프 선은 (Rank) 데이터를 추적해서 그림
            plot_data = df_hist[f"{spec} (Rank)"].tail(CHART_DAYS)
            is_top_10 = latest_ranks[spec] <= VIEW_RANK_LIMIT
            
            class_name = spec.split(" - ")[0]
            line_color = CLASS_COLORS.get(class_name, "#888888")
            
            if is_top_10:
                # 범례(Legend) 포맷 변경: [1위] 특성명 (상위 0.45%)
                current_pct = today_data[f"{spec} (%)"]
                plt.plot(plot_data.index, plot_data.values, marker='o', 
                         markersize=6, linewidth=3.5, color=line_color, 
                         alpha=1.0, label=f"[{int(latest_ranks[spec])}위] {spec} ({current_pct}%)")
            else:
                plt.plot(plot_data.index, plot_data.values, color=line_color, 
                         linewidth=0.8, alpha=0.15)

        plt.title(f"{target}+ {mode.upper()} Top {VIEW_RANK_LIMIT} Trend", fontsize=20, pad=30, color='white')
        plt.ylabel("Rank", fontsize=14, color='white')
        
        plt.gca().invert_yaxis()
        plt.ylim(VIEW_RANK_LIMIT + 0.5, 0.5)
        plt.yticks(range(1, VIEW_RANK_LIMIT + 1), color='white')
        plt.xticks(rotation=45, color='white')
        
        plt.grid(True, axis='y', linestyle='--', alpha=0.2, color='white')
        for spine in ax.spines.values():
            spine.set_edgecolor('#444444')
            
        if not df_hist.empty:
            plt.legend(title=f"Top {VIEW_RANK_LIMIT} Specs (Rank & Top %)", bbox_to_anchor=(1.02, 1),
                       loc='upper left', fontsize=11, facecolor='#2d2d2d', 
                       edgecolor='#444444', labelcolor='white')
        
        plt.tight_layout()
        plt.savefig(f"plots/{mode}_{target}_trend.png", dpi=150, facecolor='#1e1e1e')
        plt.close()

    # 통합 티어 리스트 저장 (tier_list 폴더)
    if 2100 in current_df.index:
        df_tier = (100 - current_df.loc[[r-100 for r in target_ratings if r-100 in current_df.index]]).T
        df_tier.columns = [f"{int(r)}+ 상위 (%)" for r in target_ratings if r-100 in current_df.index]
        sort_col = df_tier.columns[2] if len(df_tier.columns)>2 else df_tier.columns[0]
        df_tier.sort_values(by=sort_col, ascending=False).to_csv(f"{mode}_tier_list/ranking_{today}.csv", encoding="utf-8-sig")

print("\n🎉 순위 및 백분위 확장 데이터 저장 완료!")
