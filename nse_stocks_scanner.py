import streamlit as st
from tvDatafeed import TvDatafeed, Interval
import pandas as pd
import concurrent.futures

st.set_page_config(page_title="NSE Stocks Scanner", layout="wide")
st.title("NSE Stocks Scanner")

# Initialize TvDatafeed in guest mode
@st.cache_resource
def get_tv_datafeed():
    return TvDatafeed()

tv = get_tv_datafeed()

# nse symbol 
symbols = ['360ONE', 'ABB', 'ABCAPITAL', 'ADANIENSOL', 'ADANIENT', 'ADANIGREEN', 'ADANIPORTS', 'ALKEM', 'AMBER', 'AMBUJACEM', 'ANGELONE', 'APLAPOLLO', 'APOLLOHOSP', 'ASHOKLEY', 'ASIANPAINT', 'ASTRAL','AUBANK', 'AUROPHARMA', 'AXISBANK', 'BAJAJFINSV', 'BAJAJHLDNG', 'BAJFINANCE', 'BANDHANBNK', 'BANKBARODA', 'BANKINDIA', 'BDL', 'BEL', 'BHARATFORG', 'BHARTIARTL', 'BHEL', 'BIOCON', 'BLUESTARCO', 'BOSCHLTD', 'BPCL', 'BRITANNIA', 'BSE', 'CAMS', 'CANBK', 'CDSL', 'CGPOWER', 'CHOLAFIN', 'CIPLA', 'COALINDIA', 'COFORGE', 'COLPAL', 'CONCOR', 'CROMPTON', 'CUMMINSIND', 'DABUR', 'DALBHARAT', 'DELHIVERY', 'DIVISLAB', 'DIXON', 'DLF', 'DMART', 'DRREDDY', 'EICHERMOT', 'ETERNAL', 'EXIDEIND', 'FEDERALBNK', 'FORTIS', 'GAIL', 'GLENMARK', 'GMRAIRPORT', 'GODREJCP', 'GODREJPROP', 'GRASIM', 'HAL', 'HAVELLS', 'HCLTECH', 'HDFCAMC', 'HDFCBANK', 'HDFCLIFE', 'HEROMOTOCO', 'HINDALCO', 'HINDPETRO', 'HINDUNILVR', 'HINDZINC', 'HUDCO', 'ICICIBANK', 'ICICIGI', 'ICICIPRULI', 'IDEA', 'IDFCFIRSTB', 'IEX',  'INDHOTEL', 'INDIANB', 'INDIGO', 'INDUSINDBK', 'INDUSTOWER', 'INFY', 'INOXWIND', 'IOC','IREDA', 'IRFC', 'ITC', 'JINDALSTEL', 'JIOFIN', 'JSWENERGY', 'JSWSTEEL', 'JUBLFOOD', 'KALYANKJIL', 'KAYNES', 'KEI', 'KFINTECH', 'KOTAKBANK', 'KPITTECH','LAURUSLABS', 'LICHSGFIN', 'LICI', 'LODHA', 'LT', 'LTF', 'LTIM', 'LUPIN', 'MANAPPURAM', 'MANKIND', 'MARICO', 'MARUTI', 'MAXHEALTH', 'MAZDOCK', 'MCX', 'MFSL', 'MOTHERSON', 'MPHASIS', 'MUTHOOTFIN', 'NATIONALUM', 'NAUKRI', 'NBCC', 'NESTLEIND', 'NHPC', 'NMDC', 'NTPC', 'NUVAMA', 'NYKAA', 'OBEROIRLTY', 'OFSS', 'OIL', 'ONGC', 'PAGEIND', 'PATANJALI', 'PAYTM', 'PERSISTENT', 'PETRONET', 'PFC', 'PGEL', 'PHOENIXLTD', 'PIDILITIND', 'PIIND', 'PNB', 'PNBHOUSING', 'POLICYBZR', 'POLYCAB', 'POWERGRID', 'POWERINDIA', 'PPLPHARMA', 'PREMIERENE', 'PRESTIGE', 'RBLBANK', 'RECLTD', 'RELIANCE', 'RVNL', 'SAIL', 'SAMMAANCAP', 'SBICARD', 'SBILIFE', 'SBIN', 'SHREECEM', 'SHRIRAMFIN', 'SIEMENS', 'SOLARINDS', 'SONACOMS', 'SRF', 'SUNPHARMA', 'SUPREMEIND', 'SUZLON', 'SWIGGY', 'SYNGENE', 'TATACONSUM', 'TATAELXSI', 'TATAPOWER', 'TATASTEEL', 'TATATECH', 'TCS', 'TECHM', 'TIINDIA', 'TITAN', 'TMPV', 'TORNTPHARM', 'TORNTPOWER', 'TRENT', 'TVSMOTOR', 'ULTRACEMCO', 'UNIONBANK', 'UNITDSPR', 'UNOMINDA', 'UPL', 'VBL', 'VEDL', 'VOLTAS', 'WAAREEENER', 'WIPRO', 'YESBANK', 'ZYDUSLIFE']

# input interval minimum 15 minute  
# interval = Interval.in_15_minute
# interval = Interval.in_5_minute

interval_selection = st.selectbox("Select Interval", ["5 Minute", "15 Minute", "Daily"])

if interval_selection == "5 Minute":
    selected_interval = Interval.in_5_minute
    n_bars = 3
elif interval_selection == "15 Minute":
    selected_interval = Interval.in_15_minute
    n_bars = 3
else:
    selected_interval = Interval.in_daily
    n_bars = 2

# Display n_bars as a fixed text input (read-only, no +/- buttons)
st.text_input("Number of Bars", value=str(n_bars), disabled=True)

# Stock selection logic
if interval_selection in ["5 Minute", "15 Minute"]:
    selected_symbols = st.multiselect("Select Stocks (Max 5)", symbols, max_selections=5)
    if not selected_symbols:
        st.warning("Please select at least one stock to scan.")
else:
    st.info(f"Scanning all {len(symbols)} stocks for Daily interval.")
    selected_symbols = symbols

def process_symbol(symbol, interval, n_bars):
    try:
        data = tv.get_hist(symbol=symbol,exchange='NSE',interval=interval,n_bars=n_bars)  
        
        if data is None:
            return None

        df = data[['open', 'high', 'low', 'close']]
        
        open_0 = df['open'].iloc[0]
        high_0 = df['high'].iloc[0]
        low_0 = df['low'].iloc[0]
        close_0 = df['close'].iloc[0]

        open_1 = df['open'].iloc[1]
        high_1 = df['high'].iloc[1]
        low_1 = df['low'].iloc[1]
        close_1 = df['close'].iloc[1]

        if open_0 > close_0 and low_0 > low_1 and open_1 < close_1 and high_0 < close_1:
            return {'Symbol': symbol, 'Signal': 'BUY'}
            
        elif open_0 < close_0 and high_0 < high_1 and open_1 > close_1 and low_0 > close_1:
            return {'Symbol': symbol, 'Signal': 'SELL'}
            
    except Exception as e:
        return None
    return None

if st.button("Scan Symbols"):
    if not selected_symbols:
        st.error("No stocks selected!")
        st.stop()

    results = []
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    status_text.text(f"Scanning symbols ({interval_selection}, {n_bars} bars)...")
    
    # Use ThreadPoolExecutor for parallel execution
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        # Submit all tasks
        future_to_symbol = {executor.submit(process_symbol, symbol, selected_interval, n_bars): symbol for symbol in selected_symbols}
        
        completed_count = 0
        total_symbols = len(selected_symbols)
        
        for future in concurrent.futures.as_completed(future_to_symbol):
            result = future.result()
            if result:
                results.append(result)
            
            completed_count += 1
            progress_bar.progress(completed_count / total_symbols)
            status_text.text(f"Scanning... {completed_count}/{total_symbols}")

    status_text.text("Scan complete!")
    progress_bar.empty()

    if results:
        df_results = pd.DataFrame(results)
        st.success(f"Found {len(results)} signals!")
        # st.dataframe(df_results, use_container_width=True)
        st.dataframe(df_results)
    else:
        st.warning("No signals found.")
