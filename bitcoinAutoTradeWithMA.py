import time
import pyupbit
import datetime

access = "v0Wa2AgyF5BRwVCAMJibAPCPXFjgLiLND380U78a"
secret = "g0N2HywCHpoWmXOqa3W5hxa1BEmqQ3AlrTiXNGX8"

def get_target_price(ticker, k):
    """변동성 돌파 전략으로 매수 목표가 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=2048)
    target_price = df.iloc[0]['close'] + (df.iloc[0]['high'] - df.iloc[0]['low']) * k
    return target_price

def get_start_time(ticker):
    """시작 시간 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="minute", count=5)
    start_time = df.index[0]
    return start_time

def get_ma15(ticker):
    """15일 이동 평균선 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=2466)
    ma15 = df['close'].rolling(15).mean().iloc[-1]
    return ma15

def get_balance(ticker):
    """잔고 조회"""
    balances = upbit.get_balances()
    for b in balances:
        if b['currency'] == ticker:
            if b['balance'] is not None:
                return float(b['balance'])
            else:
                return 0

def get_current_price(ticker):
    """현재가 조회"""
    return pyupbit.get_orderbook(tickers=ticker)[0]["orderbook_units"][0]["ask_price"]

# 로그인
upbit = pyupbit.Upbit(access, secret)
print("autotrade start")

# 자동매매(08시59분50초 전량매도 ->  09시 전량매수)
while True:
    try:
        now = datetime.datetime.now()
        start_time = get_start_time("KRW-XRP")
        end_time = start_time + datetime.timedelta(minutes=5) #09:00 +5분

        # 09:00 < 현재 < 08:59 일 경우 #08:59:50에 전량매도 후 09:00 전량매수
        if start_time < now < end_time - datetime.timedelta(seconds=10):         #작동시간 설정(6분 -10초 전에 전량매도, 시작시간 매수확인)
            target_price = get_target_price("KRW-XRP", 0.5)                      #변동성 돌파전략 파악
            ma15 = get_ma15("KRW-XRP")                                           #15일 이동평균선 파악
            current_price = get_current_price("KRW-XRP")                         #리플 현재가 조회
            if target_price < current_price and ma15 < current_price:            #만약 리플 현재가가 변돌 / 이평선 조건에 맞을 경우
                krw = get_balance("KRW")                                         #보유 KRW 잔고 조회를 하고
                if krw > 5000:                                                   #남은 KRW 잔고와
                    upbit.buy_market_order("KRW-XRP", krw*0.9995)                #업비트 수수료에 맞춰 매수 진행
        else:                                                                    #하지만
            btc = get_balance("XRP")                                             #btc(리플)의 잔고를 조회해서
            if btc > 0.005:                                                      #잔고가 전보다 0.005 이상 늘었을 경우
                upbit.sell_market_order("KRW-XRP", btc*0.9995)                   #수수료에 맞춰서 전량 매도주문을 걸어놓는다.
        time.sleep(1)                                                            #1초간 일시정지
    except Exception as e:                                                       #예외가 발생했습니다.
        print(e)                                                                 #예외(에러) 발생 시 출력
        time.sleep(1)                                                            #1초간 일시정지
