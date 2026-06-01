import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import anthropic

# Page config
st.set_page_config(
    page_title="Equity Research Platform",
    page_icon="📈",
    layout="wide"
)

st.title("📈 Equity Research + Portfolio Optimization Platform")
st.caption("Built by Pratyush | MBA - Banking & Financial Engineering | CU")

# Sidebar
st.sidebar.title("🔧 Navigation")
page = st.sidebar.radio("Go to", [
    "📊 Stock Screener",
    "🔍 AI Research Assistant", 
    "💼 Portfolio Tracker"
])

# ─── PAGE 1: STOCK SCREENER ───
if page == "📊 Stock Screener":
    st.header("📊 Stock Screener")
    col1, col2 = st.columns(2)
    with col1:
        ticker = st.text_input("Enter Stock Symbol", value="RELIANCE.NS", 
                               help="India: RELIANCE.NS | US: AAPL")
    with col2:
        period = st.selectbox("Period", ["1mo", "3mo", "6mo", "1y", "2y"])
    
    if st.button("🔍 Fetch Stock Data"):
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period=period)
            info = stock.info
            
            # Key metrics
            st.subheader(f"📌 {info.get('longName', ticker)}")
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Current Price", f"₹{info.get('currentPrice', 'N/A')}")
            m2.metric("Market Cap", f"{info.get('marketCap', 'N/A'):,}" if isinstance(info.get('marketCap'), int) else "N/A")
            m3.metric("P/E Ratio", info.get('trailingPE', 'N/A'))
            m4.metric("52W High", info.get('fiftyTwoWeekHigh', 'N/A'))
            
            # Price chart
            fig = go.Figure()
            fig.add_trace(go.Candlestick(
                x=hist.index, open=hist['Open'],
                high=hist['High'], low=hist['Low'], close=hist['Close']
            ))
            fig.update_layout(title=f"{ticker} Price Chart", height=400)
            st.plotly_chart(fig, use_container_width=True)
            
        except Exception as e:
            st.error(f"Error: {e}")

# ─── PAGE 2: AI RESEARCH ASSISTANT ───
elif page == "🔍 AI Research Assistant":
    st.header("🔍 AI Research Assistant")
    
    api_key = st.text_input("Enter Anthropic API Key", type="password")
    company = st.text_input("Company Name", value="Dixon Technologies")
    question = st.text_area("Your Research Question", 
                            value="Give me a brief equity research note on this company including business model, key risks, and valuation outlook.")
    
    if st.button("🤖 Generate Research"):
        if not api_key:
            st.warning("Please enter your API key!")
        else:
            with st.spinner("Generating research..."):
                try:
                    client = anthropic.Anthropic(api_key=api_key)
                    message = client.messages.create(
                        model="claude-sonnet-4-20250514",
                        max_tokens=1024,
                        messages=[{
                            "role": "user",
                            "content": f"You are an expert Equity Research Analyst. Company: {company}. Question: {question}"
                        }]
                    )
                    st.success("Research Generated!")
                    st.markdown(message.content[0].text)
                except Exception as e:
                    st.error(f"Error: {e}")

# ─── PAGE 3: PORTFOLIO TRACKER ───
elif page == "💼 Portfolio Tracker":
    st.header("💼 Portfolio Tracker")
    
    st.subheader("Add Your Holdings")
    col1, col2, col3 = st.columns(3)
    with col1:
        p_ticker = st.text_input("Stock Symbol", value="DIXON.NS")
    with col2:
        p_qty = st.number_input("Quantity", min_value=1, value=10)
    with col3:
        p_buy = st.number_input("Buy Price (₹)", min_value=1.0, value=1000.0)
    
    if 'portfolio' not in st.session_state:
        st.session_state.portfolio = []
    
    if st.button("➕ Add to Portfolio"):
        st.session_state.portfolio.append({
            "Ticker": p_ticker, "Qty": p_qty, "Buy Price": p_buy
        })
        st.success(f"Added {p_ticker}!")
    
    if st.session_state.portfolio:
        df = pd.DataFrame(st.session_state.portfolio)
        
        results = []
        for _, row in df.iterrows():
            try:
                stock = yf.Ticker(row['Ticker'])
                cmp = stock.info.get('currentPrice', row['Buy Price'])
                pnl = (cmp - row['Buy Price']) * row['Qty']
                pct = ((cmp - row['Buy Price']) / row['Buy Price']) * 100
                results.append({
                    "Ticker": row['Ticker'],
                    "Qty": row['Qty'],
                    "Buy Price": row['Buy Price'],
                    "CMP": round(cmp, 2),
                    "P&L (₹)": round(pnl, 2),
                    "Return %": round(pct, 2)
                })
            except:
                pass
        
        if results:
            result_df = pd.DataFrame(results)
            st.dataframe(result_df, use_container_width=True)
            
            total_pnl = sum([r['P&L (₹)'] for r in results])
            st.metric("Total P&L", f"₹{total_pnl:,.2f}", 
                      delta="Profit" if total_pnl > 0 else "Loss")
            