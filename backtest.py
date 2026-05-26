import yfinance as yf

def backtest_strategy(pair):
    # Bozor ma'lumotlarini yuklab olish
    ticker = yf.Ticker(f"{pair}=X")
    data = ticker.history(period="5d", interval="1m")
    
    if len(data) < 20:
        return 0

    wins = 0
    total = 0
    
    # Strategiyani tarixiy ma'lumotlarda sinash
    for i in range(10, len(data) - 1):
        momentum = data['Close'].iloc[i] - data['Close'].iloc[i-5]
        prediction = "BUY" if momentum > 0 else "SELL"
        actual = "BUY" if data['Close'].iloc[i+1] > data['Close'].iloc[i] else "SELL"
        
        if prediction == actual:
            wins += 1
        total += 1
            
    return (wins / total) * 100

# Asosiy natijalarni ko'rsatish
print(f"EURUSD aniqligi: {backtest_strategy('EURUSD'):.2f}%")
print(f"GBPUSD aniqligi: {backtest_strategy('GBPUSD'):.2f}%")
