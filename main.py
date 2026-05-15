import requests
import pandas as pd
import time
import os
from datetime import datetime
import matplotlib.pyplot as plt

# 서버 환경(GUI 없음)에서 그래프 생성을 위한 설정
plt.switch_backend('Agg')
plt.rcParams['font.sans-serif'] = ['DejaVu Sans'] 

today = datetime.now().strftime("%Y-%m-%d")
print(f"📅 [분석 시작] {today} - 티어 리스트 및 순위 변동 그래프를 생성합니다.")

# 1. 폴더 구조 설정
target_ratings = [2000, 2100, 2200, 2300, 2400, 2500]
modes = ["3v3", "shuffle"]

for mode in modes:
    for r in target_ratings:
        os.makedirs(f"{r}_{mode}_tier_list", exist_ok=True)
    os.makedirs(f"{mode}_percentile", exist_ok=True)

# 직업/특성 리스트
wow_classes = {
    "death-knight": ["blood", "frost", "unholy"], "demon-hunter": ["havoc", "vengeance"],
    "druid": ["balance", "feral", "guardian", "restoration"], "evoker": ["augmentation", "devastation", "preservation"],
    "hunter": ["beast-mastery", "marksmanship", "survival"], "mage": ["arcane", "fire", "frost"],
    "monk": ["brewmaster", "mistweaver", "windwalker"], "paladin": ["holy", "protection", "retribution"],
    "priest": ["discipline", "holy", "shadow"], "rogue": ["assassination", "outlaw", "subtlety"],
    "shaman": ["elemental", "enhancement", "restoration"], "warlock": ["affliction", "demonology", "destruction"],
    "warrior": ["arms", "fury", "protection"]
}

ratings_idx = list(range(1000, 2700, 100))
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

# 2. 데이터 크롤링 및 분석
for mode in modes:
    url_part = "leaderboard-distrubution" if mode == "3v3" else "shuffle-distrubution"
    print(f"\n--- {mode.upper()} 수집 중 ---")
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

    # 3. 점수대별 순위 계산 및 그래프 그리기
    for target in target_ratings:
        calc_r = target - 100
        folder = f"{target}_{mode}_tier_list"
        
        # 상위 % 계산 및 순위 매기기 (비율이 높을수록 1위)
        top_pct = 100 - current_df.loc[calc_r]
        ranks = top_pct.rank(ascending=False, method='min')
        
        # 히스토리 업데이트
        hist_file = f"{folder}/history_rank.csv"
        df_rank_today = pd.DataFrame(ranks).T
        df_rank_today.index = [today]
        
        if os.path.exists(hist_file):
            df_hist = pd.read_csv(hist_file, index_col=0)
            df_hist.loc[today] = df_rank_today.loc[today]
        else:
            df_hist = df_rank_today
        df_hist.to_csv(hist_file, encoding="utf-8-sig")

        # 4. 순위 변동 그래프 (Bump Chart) 생성
        # 오늘 기준 Top 10 특성 추출
        current_top10 = ranks.sort_values().head(10).index
        
        plt.figure(figsize=(12, 7))
        for spec in current_top10:
            # 최근 최대 14일치 데이터만 시각화
            plot_data = df_hist[spec].tail(14)
            plt.plot(plot_data.index, plot_data.values, marker='o', linewidth=3, label=spec)
            
            # 선 끝에 특성 이름 표시
            plt.text(len(plot_data)-0.5, plot_data.values[-1], spec, fontsize=9, va='center')

        plt.title(f"{target}+ {mode.upper()} Top 10 Rank Trend", fontsize=15, pad=20)
        plt.ylabel("Rank", fontsize=12)
        plt.xlabel("Date", fontsize=12)
        
        # Y축 반전 (1위가 맨 위로)
        plt.gca().invert_yaxis()
        
        # Y축 눈금을 1위부터 20위 정도까지만 표시 (가독성)
        plt.yticks(range(1, 21))
        plt.grid(True, axis='y', linestyle='--', alpha=0.6)
        plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.15), ncol=3, fontsize=9)
        plt.tight_layout()

        plt.savefig(f"{folder}/rank_trend_graph.png", dpi=150)
        plt.close()
        print(f"✅ {folder} 업데이트 완료")

print("\n🎉 모든 작업이 완료되었습니다!")
