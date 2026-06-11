import urllib.request  
import json  
import re  
import time  
  
# --- 1. 라이브러리 없는 순수 파이썬 기술 지표 연산 ---  
def calculate_indicators(prices):  
    if len(prices) < 20:  
        return {"rsi": 50, "bb_high": prices[-1], "bb_low": prices[-1]}  
      
    # 1-1. RSI(14) 계산  
    period = 14  
    gains = []  
    losses = []  
    for i in range(1, len(prices)):  
        diff = prices[i] - prices[i-1]  
        gains.append(diff if diff > 0 else 0)  
        losses.append(abs(diff) if diff < 0 else 0)  
          
    avg_gain = sum(gains[:period]) / period  
    avg_loss = sum(losses[:period]) / period  
      
    for i in range(period, len(gains)):  
        avg_gain = (avg_gain * (period - 1) + gains[i]) / period  
        avg_loss = (avg_loss * (period - 1) + losses[i]) / period  
          
    rsi = 100 - (100 / (1 + (avg_gain / avg_loss))) if avg_loss != 0 else 100  
      
    # 1-2. 볼린저 밴드(20, 2) 계산  
    recent_prices = prices[-20:]  
    mid = sum(recent_prices) / 20  
    variance = sum((x - mid) ** 2 for x in recent_prices) / 20  
    std_dev = variance ** 0.5  
    high = mid + (std_dev * 2)  
    low = mid - (std_dev * 2)  
      
    return {"rsi": rsi, "bb_high": high, "bb_low": low}  
  
# --- 2. 순수 HTTP 통신으로 실시간 금융 데이터 및 기술지표 파싱 ---  
def get_market_data(ticker):  
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?interval=1d&range=1mo"  
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})  
    try:  
        with urllib.request.urlopen(req) as response:  
            res_data = json.loads(response.read().decode('utf-8'))  
          
        result = res_data['chart']['result'][0]  
        prices = [p for p in result['indicators']['quote'][0]['close'] if p is not None]  
          
        if not prices:  
            return None  
              
        current_price = prices[-1]  
        indicators = calculate_indicators(prices)  
          
        # 간이 변동성 계산  
        returns = [(prices[i] - prices[i-1])/prices[i-1] for i in range(1, len(prices))]  
        mean_return = sum(returns) / len(returns)  
        var_return = sum((r - mean_return)**2 for r in returns) / len(returns)  
        daily_volatility = (var_return ** 0.5) * 100  
          
        return {  
            "price": current_price,  
            "rsi": indicators["rsi"],  
            "bb_high": indicators["bb_high"],  
            "bb_low": indicators["bb_low"],  
            "daily_volatility": daily_volatility  
        }  
    except Exception as e:  
        print(f"데이터 파싱 에러: {e}")  
        return None  
  
# --- 3. 순수 HTTP 통신으로 무료 Gemini API 구동 (Gemma 대체) ---  
def query_gemini_pure(api_key, system_prompt, user_prompt):  
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"  
    payload = {  
        "systemInstruction": {  
            "parts": [{"text": system_prompt}]  
        },  
        "contents": [{  
            "parts": [{"text": user_prompt}]  
        }]  
    }  
    req = urllib.request.Request(  
        url,  
        data=json.dumps(payload).encode('utf-8'),  
        headers={'Content-Type': 'application/json'},  
        method='POST'  
    )  
    try:  
        with urllib.request.urlopen(req) as response:  
            res_json = json.loads(response.read().decode('utf-8'))  
        return res_json['candidates'][0]['content']['parts'][0]['text']  
    except Exception as e:  
        return f"통신 장애 또는 API 한계 도과: {e}"  
  
# --- 4. 에이전트 파이프라인 콘솔 제어부 ---  
def run_mobile_pipeline():  
    print("=" * 45)  
    print("📱 Mobile TradingAgents System v1.0")  
    print("=" * 45)  
      
    api_key = input("🔑 Google Gemini API Key를 입력하세요: ").strip()  
    ticker = input("📈 분석 자산 입력 (예: BTC-USD, AAPL): ").strip().upper() or "BTC-USD"  
      
    print("\n[진행] 실시간 야후 파이낸스 데이터 수집 중...")  
    data = get_market_data(ticker)  
    if not data:  
        print("❌ 데이터를 수집할 수 없습니다. 심볼명을 다시 확인하세요.")  
        return  
          
    print(f"-> 현재가: ${data['price']:,.2f} | RSI: {data['rsi']:.1f} | 변동성: {data['daily_volatility']:.2f}%")  
    print("-" * 45)  
      
    # 에이전트 1: Fundamentals & Technical Analyst 통합팀  
    print("[에이전트] 1. Analyst Team 종합 분석 수립 중...")  
    sys_p = "너는 금융 리서치 수석 에널리스트야. 시장 원자 데이터와 기술적 지표를 대조하여 한국어로 정량적 한 줄 요약을 제공해줘."  
    user_p = f"자산: {ticker}, 가격: {data['price']:.2f}, RSI: {data['rsi']:.2f}, 밴드상단: {data['bb_high']:.2f}, 밴드하단: {data['bb_low']:.2f}, 일 변동성: {data['daily_volatility']:.2f}%"  
    analyst_res = query_gemini_pure(api_key, sys_p, user_p)  
    print(f"\n🔍 [Analyst Team]: {analyst_res}\n")  
    time.sleep(1) # API 레이트 제한 보호  
      
    # 에이전트 2: Bull vs Bear Debate Loop  
    print("[에이전트] 2. Bull vs Bear 가상 토론 진행 중...")  
    sys_bull = "너는 강력한 성장 지향론자이자 Bull_Researcher야."  
    bull_res = query_gemini_pure(api_key, sys_bull, f"이 지표 상황에서 반드시 매수(BUY)해야 하는 이유를 한 문장으로 제시해: {analyst_res}")  
      
    sys_bear = "너는 극도의 안전 보수주의자이자 Bear_Researcher야."  
    bear_res = query_gemini_pure(api_key, sys_bear, f"이 지표 상황에서 당장 후퇴하거나 관망(HOLD)해야 하는 근거를 한 문장으로 제시해: {analyst_res}")  
      
    print(f"🐂 [Bull]: {bull_res}")  
    print(f"🐻 [Bear]: {bear_res}\n")  
    time.sleep(1)  
      
    # 에이전트 3: Trader & Risk Manager 통합 중재  
    print("[에이전트] 3. Trader & Risk 컴플라이언스 통합 심사 중...")  
    sys_risk = "너는 위험 조율을 전담하는 투자 리스크 책임자이자 최고 거래 의사결정권자야."  
    user_risk = f"Bull 측: {bull_res}\nBear 측: {bear_res}\n변동성 수치는 {data['daily_volatility']:.2f}%야. 이를 조율하여 최종 매매 액션(BUY, SELL, HOLD 중 선택), 추천 비중(0%~100%), 엄격한 손절가, 그리고 그에 상응하는 최종 결론을 한국어 2문장 내로 정밀 선언해줘."  
    risk_res = query_gemini_pure(api_key, sys_risk, user_risk)  
    print(f"💼 [Final Decision & Risk Report]\n{risk_res}")  
    print("=" * 45)  
  
if __name__ == "__main__":  
    run_mobile_pipeline()  
