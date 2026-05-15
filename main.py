import requests
import pandas as pd
import time
from datetime import datetime

# 1. 오늘 날짜 가져오기 (예: 2026-05-16)
today = datetime.now().strftime("%Y-%m-%d")
print(f"📅 [오늘의 날짜] {today} - 와우 PvP 데이터 분석을 시작합니다.")

# 2. 직업 및 특성 매핑
wow_classes = {
    "death-knight": ["blood", "frost", "unholy"],
    "demon-hunter": ["havoc", "vengeance"],
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

ratings = list(range(1000, 2700, 100))
# 보고 싶은 컷오프 기준
target_ratings = [1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500] 

# 누적 계산을 위해 실제로 조회할 점수대 (타겟 점수 - 100)
calc_ratings = [r - 100 for r in target_ratings]

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

# 3. 브라켓 설정 (파일명에 today 변수 추가)
brackets = {
    "3v3": {
        "url_part": "leaderboard-distrubution", 
        "raw_name": f"drustvar_3v3_raw_{today}.csv", 
        "tier_name": f"wow_3v3_tier_ranking_{today}.csv"
    },
    "shuffle": {
        "url_part": "shuffle-distrubution", 
        "raw_name": f"drustvar_shuffle_raw_{today}.csv", 
        "tier_name": f"wow_shuffle_tier_ranking_{today}.csv"
    }
}

# 4. 크롤링 및 분석 실행
for bracket_name, info in brackets.items():
    print(f"\n--- {bracket_name.upper()} 데이터 수집 시작 ---")
    
    # 매 브라켓마다 새로운 빈 데이터프레임 생성
    current_df = pd.DataFrame(index=ratings)
    
    for cls, specs in wow_classes.items():
        for spec in specs:
            column_name = f"{cls.replace('-', ' ').title()} - {spec.replace('-', ' ').title()}"
            
            url = f"https://drustvar.com/api/v1/leaderboard/{info['url_part']}?search[region]=all&search[bracket]={bracket_name}&search[role]=spec&search[cc]={cls}&search[cs]={spec}"
            
            try:
                response = requests.get(url, headers=headers, timeout=10)
                if response.status_code == 200:
                    data = response.json().get("stats", [])
                    for item in data:
                        rating = item["rating"]
                        if rating in current_df.index:
                            current_df.loc[rating, column_name] = item["percentile"]
            except Exception as e:
                print(f"[{column_name}] API 오류: {e}")
            time.sleep(0.5) # 서버 과부하 방지 (중요)

    # 결측치 보정
    current_df = current_df.ffill().fillna(0)
    current_df.index.name = "Rating"
    
    # 원본 누적 데이터 저장 (선택 사항: 원본 데이터가 너무 많이 쌓이는 게 싫다면 이 줄을 지우셔도 됩니다)
    current_df.to_csv(info["raw_name"], encoding="utf-8-sig")
    
    # 5. 티어 랭킹 계산 (오차 수정 완료 버전)
    valid_targets = []
    valid_calcs = []
    for target, calc in zip(target_ratings, calc_ratings):
        if calc in current_df.index:
            valid_targets.append(target)
            valid_calcs.append(calc)
            
    if valid_calcs:
        # 정확한 비율 계산 (예: 100 - 2100점 누적 = 2200점 이상 비율)
        df_top_pct = 100 - current_df.loc[valid_calcs]
        df_tier = df_top_pct.T
        
        # 열 이름을 원래 의도했던 타겟 점수로 변경
        df_tier.columns = [f"{int(r)}+ 상위 (%)" for r in valid_targets]
        
        # 정렬
        sort_col = f"{int(valid_targets[0])}+ 상위 (%)"
        df_tier = df_tier.sort_values(by=sort_col, ascending=False).round(3)
        df_tier.index.name = "Class - Spec"
        
        # 티어 랭킹 CSV 저장
        df_tier.to_csv(info["tier_name"], encoding="utf-8-sig")
        print(f"✅ {info['tier_name']} 저장 완료!")

print("\n🎉 오늘의 크롤링 및 분석이 모두 완료되었습니다!")
