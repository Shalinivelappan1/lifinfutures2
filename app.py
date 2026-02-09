import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

st.set_page_config(layout="wide")
st.title("Futures Trading & Hedging Lab")

# =====================================================
# HELPERS
# =====================================================
def payoff_matrix(x, y, label="P&L"):
    df = pd.DataFrame({"Price": x, label: y})
    st.dataframe(df, use_container_width=True)

# =====================================================
# SIDEBAR
# =====================================================
topic = st.sidebar.radio(
    "Select Module",
    [
        "1. What is Futures?",
        "2. Futures Pricing",
        "3. MTM & Margin Calls",
        "4. Trading P&L",
        "5. Hedging Strategy Builder",
        "6. Optimal Hedge Ratio",
        "7. Basis & Convergence",
        "8. Basis Risk",
        "9. Rolling Futures",
        "10. Matching System",
        "11. Real-World Cases",
        "12. Advanced Strategies",
        "13. Quiz & Certificate"
    ]
)

# =====================================================
# 1 FUTURES BASICS
# =====================================================
if topic == "1. What is Futures?":
    st.header("What is a Futures Contract?")

    st.write("""
A futures contract is an agreement to buy or sell an asset at a predetermined price on a future date.
""")

    st.subheader("Key Components")
    st.write("""
• Underlying asset  
• Contract size  
• Expiry  
• Margin  
• Mark-to-market  
""")

    entry = st.number_input("Entry price", 22000)
    prices = np.linspace(entry-2000, entry+2000, 8)
    pnl = prices-entry

    fig, ax = plt.subplots()
    ax.plot(prices, pnl)
    ax.axhline(0)
    st.pyplot(fig)

    payoff_matrix(prices, pnl)

# =====================================================
# 2 PRICING
# =====================================================
elif topic == "2. Futures Pricing":
    st.header("Futures Pricing")

    S = st.slider("Spot price", 100, 1000, 500)
    r = st.slider("Interest rate %", 0, 15, 8)/100
    T = st.slider("Time to maturity", 0.1, 1.0, 0.5)

    discrete = S*(1+r)**T
    continuous = S*np.exp(r*T)

    st.metric("Discrete pricing", round(discrete,2))
    st.metric("Continuous pricing", round(continuous,2))

    df = pd.DataFrame({
        "Method":["Discrete","Continuous"],
        "Futures":[discrete,continuous]
    })
    st.dataframe(df)

# =====================================================
# 3 MTM LONG/SHORT
# =====================================================
elif topic == "3. MTM & Margin Calls":

    st.header("MTM & Margin Calls")

    position = st.radio("Position", ["Long","Short"])

    entry = st.number_input("Entry", 22000)
    contracts = st.slider("Contracts",1,20,5)
    size = 50

    init_margin = st.number_input("Initial margin",150000)
    maint_margin = st.number_input("Maintenance margin",100000)

    prices = np.linspace(entry-2000, entry+2000, 8)

    balances=[]
    status=[]

    for p in prices:
        if position=="Long":
            pnl=(p-entry)*contracts*size
        else:
            pnl=(entry-p)*contracts*size

        bal=init_margin+pnl
        balances.append(bal)

        if bal<maint_margin:
            status.append("MARGIN CALL")
        else:
            status.append("OK")

    fig, ax = plt.subplots()
    ax.plot(prices,balances)
    ax.axhline(maint_margin,linestyle="--")
    st.pyplot(fig)

    df=pd.DataFrame({
        "Price":prices,
        "Margin balance":balances,
        "Status":status
    })
    st.dataframe(df)

# =====================================================
# 4 TRADING PNL
# =====================================================
elif topic == "4. Trading P&L":

    st.header("Trading P&L")

    entry = st.number_input("Entry",22000)
    contracts = st.slider("Contracts",1,20,5)
    size=50

    prices=np.linspace(entry-2000,entry+2000,8)

    long=(prices-entry)*contracts*size
    short=(entry-prices)*contracts*size

    fig, ax = plt.subplots()
    ax.plot(prices,long,label="Long")
    ax.plot(prices,short,label="Short")
    ax.legend()
    st.pyplot(fig)

    df=pd.DataFrame({
        "Price":prices,
        "Long":long,
        "Short":short
    })
    st.dataframe(df)

# =====================================================
# 5 HEDGING BUILDER
# =====================================================
elif topic == "5. Hedging Strategy Builder":

    st.header("Hedging Strategy Builder (Realistic)")

    V = st.number_input("Portfolio value", 5_000_000)
    beta = st.slider("Portfolio beta", 0.5, 1.5, 1.0)
    F = st.number_input("Futures price", 22000)
    size = 50

    # Optimal hedge
    optimal_contracts = (beta * V) / (F * size)

    st.metric("Optimal contracts", round(optimal_contracts,2))

    hedge_type = st.radio(
        "Hedge type",
        ["Optimal Hedge", "Under Hedge", "Over Hedge"]
    )

    if hedge_type == "Optimal Hedge":
        contracts = optimal_contracts
    elif hedge_type == "Under Hedge":
        contracts = optimal_contracts * 0.5
    else:
        contracts = optimal_contracts * 1.5

    st.write(f"Using contracts: {round(contracts,2)}")

    # market moves
    moves = np.linspace(-0.1, 0.1, 20)

    portfolio = V * beta * moves
    futures = -contracts * size * F * moves
    net = portfolio + futures

    # chart
    fig, ax = plt.subplots()
    ax.plot(moves*100, portfolio, label="Unhedged")
    ax.plot(moves*100, net, label="Hedged")
    ax.axhline(0)
    ax.set_xlabel("Market move %")
    ax.set_ylabel("P&L")
    ax.legend()
    st.pyplot(fig)

    # payoff table
    df = pd.DataFrame({
        "Market move %": moves*100,
        "Unhedged P&L": portfolio,
        "Futures P&L": futures,
        "Net hedged P&L": net
    })
    st.dataframe(df, use_container_width=True)

    st.info("""
Optimal hedge → flattest line  
Under hedge → still risky  
Over hedge → reverses exposure  
At expiry → futures & spot converge
""")

# =====================================================
# 6 OPTIMAL HEDGE
# =====================================================
elif topic == "6. Optimal Hedge Ratio":

    st.header("Optimal Hedge Ratio")

    V=st.number_input("Portfolio",5_000_000)
    beta=st.slider("Beta",0.5,1.5,1.0)
    F=st.number_input("Futures",22000)

    N=(beta*V)/(F*50)
    st.metric("Contracts",round(N,2))

# =====================================================
# 7 BASIS + CONVERGENCE
# =====================================================
elif topic == "7. Basis & Convergence":

    st.header("Basis & Convergence at Expiry")

    spot = st.number_input("Current Spot Price", 22000)
    futures = st.number_input("Current Futures Price", 22150)

    basis = spot - futures
    st.metric("Current Basis (S − F)", basis)

    st.subheader("Market Structure")
    market_type = st.radio(
        "Structure",
        ["Contango (F > S)", "Backwardation (F < S)"]
    )

    days = st.slider("Days to expiry", 5, 60, 30)

    # simulate convergence
    time = np.arange(days)

    if market_type == "Contango (F > S)":
        basis_path = np.linspace(basis, 0, days)
    else:
        basis_path = np.linspace(basis, 0, days)

    fig, ax = plt.subplots()
    ax.plot(time, basis_path)
    ax.set_title("Basis Converges to Zero at Expiry")
    ax.set_xlabel("Days")
    ax.set_ylabel("Basis")
    st.pyplot(fig)

    st.subheader("Impact on Hedged Portfolio")

    V = st.number_input("Portfolio value", 5_000_000)
    beta = st.slider("Beta", 0.5, 1.5, 1.0)
    size = 50

    contracts = (beta * V) / (futures * size)

    moves = np.linspace(-0.05, 0.05, 10)

    portfolio = V * beta * moves
    futures_pnl = -contracts * size * futures * moves

    net = portfolio + futures_pnl

    fig2, ax2 = plt.subplots()
    ax2.plot(moves*100, portfolio, label="Unhedged")
    ax2.plot(moves*100, net, label="Hedged")
    ax2.legend()
    ax2.set_title("Effect of Convergence on Hedge")
    st.pyplot(fig2)

    df = pd.DataFrame({
        "Market Move %": moves*100,
        "Unhedged": portfolio,
        "Hedged": net
    })
    st.dataframe(df, use_container_width=True)

    st.info("""
Key teaching points:

• Basis = Spot − Futures  
• Basis → 0 at expiry  
• Hedge effectiveness improves as expiry nears  
• Imperfect convergence creates basis risk  
""")


# =====================================================
# 8 BASIS RISK
# =====================================================
elif topic == "8. Basis Risk":

    st.header("Basis Risk")

    corr=st.slider("Correlation",0.0,1.0,0.8)
    st.metric("Effectiveness %",corr*100)

# =====================================================
# 9 ROLLING
# =====================================================
elif topic == "9. Rolling Futures":

    st.header("Rolling Hedge")

    near=st.number_input("Near contract",22000)
    far=st.number_input("Next contract",22150)

    st.metric("Roll cost",far-near)

# =====================================================
# 10 MATCHING
# =====================================================
elif topic == "10. Matching System":

    st.header("Matching Engine")

    buyers=st.slider("Buy orders",0,100,60)
    sellers=st.slider("Sell orders",0,100,50)

    st.metric("Trades executed",min(buyers,sellers))
# =====================================================
# 11 REAL WORLD CASES
# =====================================================
elif topic == "11. Real-World Cases":

    st.header("Real-World Hedging & Trading Cases")

    case = st.selectbox(
        "Select Case",
        [
            "Equity Portfolio Hedge",
            "Airline Fuel Hedge",
            "Exporter Currency Hedge",
            "Commodity Producer Hedge",
            "Calendar Spread Trading Desk",
            "Arbitrage Desk"
        ]
    )

    # -------------------------------------------
    if case == "Equity Portfolio Hedge":
        st.subheader("Equity Portfolio Hedge")

        V = st.number_input("Portfolio value", 5_000_000)
        F = st.number_input("Futures price", 22000)
        size = 50

        N = V/(F*size)
        st.metric("Contracts to short", round(N,1))

        moves = np.linspace(-0.1,0.1,8)
        portfolio = V*moves
        futures = -N*50*F*moves
        net = portfolio + futures

        fig, ax = plt.subplots()
        ax.plot(moves*100, portfolio, label="Unhedged")
        ax.plot(moves*100, net, label="Hedged")
        ax.legend()
        st.pyplot(fig)

        df = pd.DataFrame({
            "Market Move %": moves*100,
            "Unhedged": portfolio,
            "Hedged": net
        })
        st.dataframe(df)

    # -------------------------------------------
    elif case == "Airline Fuel Hedge":
        st.subheader("Airline Fuel Hedge")

        fuel_cost = st.number_input("Fuel exposure", 10_000_000)
        hedge_ratio = st.slider("Hedge %", 0, 100, 70)/100

        moves = np.linspace(-0.2,0.2,8)
        unhedged = fuel_cost*moves
        hedged = unhedged*(1-hedge_ratio)

        fig, ax = plt.subplots()
        ax.plot(moves*100, unhedged, label="Unhedged")
        ax.plot(moves*100, hedged, label="Hedged")
        ax.legend()
        st.pyplot(fig)

        df = pd.DataFrame({
            "Fuel price change %": moves*100,
            "Unhedged": unhedged,
            "Hedged": hedged
        })
        st.dataframe(df)

    # -------------------------------------------
    elif case == "Exporter Currency Hedge":
        st.subheader("Exporter Currency Hedge")

        exposure = st.number_input("USD exposure", 1_000_000)
        rate = st.number_input("Current rate", 83.0)

        moves = np.linspace(-5,5,8)
        unhedged = exposure*moves
        hedged = np.zeros_like(unhedged)

        fig, ax = plt.subplots()
        ax.plot(moves, unhedged, label="Unhedged")
        ax.plot(moves, hedged, label="Hedged")
        ax.legend()
        st.pyplot(fig)

        df = pd.DataFrame({
            "FX move": moves,
            "Unhedged": unhedged,
            "Hedged": hedged
        })
        st.dataframe(df)

    # -------------------------------------------
    elif case == "Commodity Producer Hedge":
        st.subheader("Commodity Producer Hedge")

        output = st.number_input("Output quantity", 1000)
        price = st.number_input("Current price", 5000)

        moves = np.linspace(-0.2,0.2,8)
        revenue = output*price*(1+moves)

        fig, ax = plt.subplots()
        ax.plot(moves*100, revenue)
        st.pyplot(fig)

        df = pd.DataFrame({
            "Price change %": moves*100,
            "Revenue": revenue
        })
        st.dataframe(df)

    # -------------------------------------------
    elif case == "Calendar Spread Trading Desk":
        st.subheader("Calendar Spread Desk")

        near = st.number_input("Near contract", 22000)
        far = st.number_input("Far contract", 22200)

        spread = far - near
        st.metric("Spread", spread)

        prices = np.linspace(near-1000, near+1000, 8)
        pnl = (far-near) - (prices-near)

        fig, ax = plt.subplots()
        ax.plot(prices, pnl)
        st.pyplot(fig)

        payoff_matrix(prices, pnl, "Spread P&L")

    # -------------------------------------------
    elif case == "Arbitrage Desk":
        st.subheader("Cash-and-Carry Arbitrage")

        spot = st.number_input("Spot", 1000)
        futures = st.number_input("Futures", 1050)
        r = st.slider("Interest %", 0, 15, 8)/100

        fair = spot*(1+r)
        st.metric("Fair value", round(fair,2))

        prices = np.linspace(spot-200, spot+200, 8)
        pnl = futures - prices

        fig, ax = plt.subplots()
        ax.plot(prices, pnl)
        st.pyplot(fig)

        payoff_matrix(prices, pnl)

# =====================================================
# 12 ADVANCED STRATEGIES
# =====================================================
elif topic == "12. Advanced Strategies":

    st.header("Advanced Strategies Lab")

    strat = st.selectbox(
        "Choose",
        [
            "Directional Trade",
            "Calendar Spread",
            "Cross Hedging",
            "Rolling Hedge Over Time",
            "Strategy Comparison"
        ]
    )

    # -------------------------------------------
    if strat == "Directional Trade":

        entry = st.number_input("Entry price", 22000)
        prices = np.linspace(entry-2000, entry+2000, 8)
        pnl = prices-entry

        col1, col2 = st.columns(2)

        with col1:
            fig, ax = plt.subplots()
            ax.plot(prices, pnl)
            ax.axhline(0)
            st.pyplot(fig)

        with col2:
            payoff_matrix(prices, pnl)

    # -------------------------------------------
    elif strat == "Calendar Spread":

        near = st.number_input("Near", 22000)
        far = st.number_input("Far", 22200)

        prices = np.linspace(near-1000, near+1000, 8)
        pnl = (far-near)-(prices-near)

        col1, col2 = st.columns(2)
        with col1:
            fig, ax = plt.subplots()
            ax.plot(prices, pnl)
            st.pyplot(fig)

        with col2:
            payoff_matrix(prices, pnl)

    # -------------------------------------------
    elif strat == "Cross Hedging":

        st.subheader("Imperfect Hedge Simulation")

        corr = st.slider("Correlation", 0.0, 1.0, 0.7)
        exposure = st.number_input("Exposure", 1_000_000)

        moves = np.linspace(-0.1,0.1,8)
        unhedged = exposure*moves
        hedged = exposure*moves*(1-corr)

        fig, ax = plt.subplots()
        ax.plot(moves*100, unhedged, label="Unhedged")
        ax.plot(moves*100, hedged, label="Hedged")
        ax.legend()
        st.pyplot(fig)

        df = pd.DataFrame({
            "Move%": moves*100,
            "Unhedged": unhedged,
            "Hedged": hedged
        })
        st.dataframe(df)

    # -------------------------------------------
    elif strat == "Rolling Hedge Over Time":

        st.subheader("Multi-period Rolling Hedge")

        exposure = st.number_input("Exposure", 1_000_000)
        periods = st.slider("Periods", 1, 12, 6)

        pnl = np.random.normal(0, exposure*0.02, periods)
        cumulative = np.cumsum(pnl)

        fig, ax = plt.subplots()
        ax.plot(range(periods), cumulative)
        ax.set_title("Cumulative Hedge P&L")
        st.pyplot(fig)

        df = pd.DataFrame({
            "Period": range(periods),
            "PnL": pnl,
            "Cumulative": cumulative
        })
        st.dataframe(df)

    # -------------------------------------------
    elif strat == "Strategy Comparison":

        st.subheader("Compare Strategies")

        entry = st.number_input("Entry price", 22000)
        prices = np.linspace(entry-2000, entry+2000, 8)

        directional = prices-entry
        calendar = (entry+200)-(prices-entry)

        fig, ax = plt.subplots()
        ax.plot(prices, directional, label="Directional")
        ax.plot(prices, calendar, label="Calendar")
        ax.legend()
        st.pyplot(fig)

        df = pd.DataFrame({
            "Price": prices,
            "Directional": directional,
            "Calendar": calendar
        })
        st.dataframe(df)
# =====================================================
# 13 QUIZ & CERTIFICATE
# =====================================================
elif topic == "13. Quiz & Certificate":

    import io
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas
    from reportlab.lib.colors import HexColor

    st.header("Futures Lab Quiz")

    # ---------------- QUESTIONS ----------------
    q1 = st.radio("1. Market falls → who gains?", ["Long","Short"])
    q2 = st.radio("2. Basis at expiry becomes?", ["Zero","Large"])
    q3 = st.number_input("3. Spot=100, r=10%. Futures?")
    q4 = st.number_input("4. Buy 200→210, size 50. P&L?")
    q5 = st.number_input("5. Hedge contracts for ₹10L?")
    q6 = st.radio("6. MTM reduces?", ["Credit risk","Return"])
    q7 = st.radio("7. Futures>spot?", ["Contango","Backwardation"])
    q8 = st.radio("8. Best hedge correlation?", ["High","Low"])
    q9 = st.radio("9. Rolling means?", ["Close & reopen","Hold"])
    q10 = st.number_input("10. Short 500→520 size10 loss?")

    st.subheader("Student Details")
    student_name = st.text_input("Student Name")
    student_id = st.text_input("Student ID")

    # ---------------- SUBMIT ----------------
    if st.button("Submit Quiz"):

        score = 0
        if q1=="Short": score+=1
        if q2=="Zero": score+=1
        if abs(q3-110)<1: score+=1
        if abs(q4-500)<1: score+=1
        if abs(q5-1)<0.5: score+=1
        if q6=="Credit risk": score+=1
        if q7=="Contango": score+=1
        if q8=="High": score+=1
        if q9=="Close & reopen": score+=1
        if abs(q10-200)<1: score+=1

        st.success(f"Score: {score}/10")

        # ===============================
        # EXCEL DOWNLOAD
        # ===============================
        df = pd.DataFrame({
            "Student Name":[student_name]*10,
            "Student ID":[student_id]*10,
            "Question":[f"Q{i}" for i in range(1,11)],
            "Answer":[q1,q2,q3,q4,q5,q6,q7,q8,q9,q10]
        })

        excel_buffer = io.BytesIO()
        df.to_excel(excel_buffer, index=False)
        excel_buffer.seek(0)

        st.download_button(
            "📥 Download Excel Workings",
            excel_buffer,
            file_name=f"{student_id}_workings.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

        # ===============================
        # CERTIFICATE
        # ===============================
        if score >= 5 and student_name and student_id:

            buffer = io.BytesIO()
            c = canvas.Canvas(buffer, pagesize=letter)
            width, height = letter

            c.setStrokeColor(HexColor("#C9A227"))
            c.setLineWidth(4)
            c.rect(30,30,width-60,height-60)

            c.setFont("Helvetica-Bold",28)
            c.drawCentredString(width/2,height-140,
                                "Certificate of Completion")

            c.setFont("Helvetica",16)
            c.drawCentredString(width/2,height-180,
                                "Futures Trading & Hedging Lab")

            c.setFont("Helvetica-Bold",22)
            c.drawCentredString(width/2,height-240,student_name)

            c.drawCentredString(width/2,height-270,
                                f"Student ID: {student_id}")

            c.drawCentredString(width/2,height-300,
                                f"Score: {score}/10")

            from datetime import datetime
            today = datetime.today().strftime("%d %B %Y")
            c.drawCentredString(width/2,height-340,
                                f"Date: {today}")

            c.drawCentredString(width/2,height-380,
                                "Instructor: Prof. Shalini Velappan")

            c.save()
            buffer.seek(0)

            st.download_button(
                "📄 Download Certificate",
                buffer,
                file_name=f"{student_id}_certificate.pdf",
                mime="application/pdf"
            )
