"""
Financial Information & Education Section.

Comprehensive guide to financial terminologies and concepts used in the application.
Written in beginner-friendly language for young adults.
"""

import streamlit as st
from typing import Dict, List


def render_info_section() -> None:
    """Main info section component with all financial education content."""
    
    st.header("📚 Financial Education Hub")
    
    st.markdown("""
    Welcome! This section explains all the financial terms and concepts you'll see throughout the app.
    Think of this as your personal finance dictionary, written in plain English.
    """)
    
    # Navigation tabs for different categories
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "🎯 Basics", 
        "📊 Portfolio Terms", 
        "📈 Performance Metrics",
        "💰 Investment Types",
        "🧮 Calculations",
        "💡 Strategies"
    ])
    
    with tab1:
        render_basics_tab()
    
    with tab2:
        render_portfolio_terms_tab()
    
    with tab3:
        render_performance_metrics_tab()
    
    with tab4:
        render_investment_types_tab()
    
    with tab5:
        render_calculations_tab()
    
    with tab6:
        render_strategies_tab()


def render_basics_tab() -> None:
    """Basic financial concepts."""
    
    st.subheader("🎯 Financial Basics")
    
    concepts = {
        "Risk Tolerance": {
            "definition": "How comfortable you are with the possibility of losing money in exchange for potential gains.",
            "example": "If you panic when your investments drop 10%, you have low risk tolerance. If you're okay with ups and downs, you have high risk tolerance.",
            "why_matters": "It helps determine what types of investments are right for you. High risk = potentially higher returns, but more volatility.",
            "in_app": "You'll select this when creating your profile. It affects what portfolio we recommend for you."
        },
        "Investment Horizon": {
            "definition": "How long you plan to keep your money invested before you need it.",
            "example": "If you're 25 and saving for retirement at 65, your horizon is 40 years. If you're saving for a house in 3 years, your horizon is 3 years.",
            "why_matters": "Longer horizons let you take more risk because you have time to recover from market downturns.",
            "in_app": "This is one of the questions in your profile. Longer horizons typically mean more stocks in your portfolio."
        },
        "Emergency Fund": {
            "definition": "Money set aside for unexpected expenses (like medical bills, car repairs, or job loss).",
            "example": "If you spend $2,000/month, an emergency fund of $12,000 covers 6 months of expenses.",
            "why_matters": "Prevents you from having to sell investments at a bad time or go into debt when emergencies happen.",
            "in_app": "We calculate if your savings are enough for an emergency fund based on your income."
        },
        "Savings Rate": {
            "definition": "The percentage of your income that you save instead of spend.",
            "example": "If you make $50,000/year and save $10,000, your savings rate is 20%.",
            "why_matters": "Higher savings rate = faster wealth building. The general rule is to save at least 20% of income.",
            "in_app": "We calculate this automatically: (Your Savings / Your Income) × 100%"
        },
        "Compound Interest": {
            "definition": "Earning interest on your interest. Your money grows faster over time because you earn returns on previous returns.",
            "example": "If you invest $1,000 at 10% per year: Year 1 = $1,100, Year 2 = $1,210 (you earned $10 on the $100 from year 1), Year 3 = $1,331, and so on.",
            "why_matters": "It's how wealth builds over time. The longer you invest, the more powerful compound interest becomes.",
            "in_app": "All our goal calculators use compound interest to show how your money will grow."
        },
        "Diversification": {
            "definition": "Not putting all your eggs in one basket. Spreading your money across different types of investments.",
            "example": "Instead of buying only tech stocks, you might buy stocks, bonds, and international investments.",
            "why_matters": "If one investment does poorly, others might do well, reducing your overall risk.",
            "in_app": "Our recommendations always include diversification across stocks, bonds, and sometimes international markets."
        }
    }
    
    for term, info in concepts.items():
        with st.expander(f"**{term}**"):
            st.markdown(f"""
            **What it means:**
            {info['definition']}
            
            **Real-world example:**
            {info['example']}
            
            **Why it matters:**
            {info['why_matters']}
            
            **How we use it in this app:**
            {info['in_app']}
            """)


def render_portfolio_terms_tab() -> None:
    """Portfolio allocation and related terms."""
    
    st.subheader("📊 Portfolio Terms")
    
    concepts = {
        "Portfolio": {
            "definition": "Your collection of investments. Think of it as your investment 'basket'.",
            "example": "Your portfolio might include 60% stocks, 30% bonds, and 10% cash.",
            "why_matters": "A well-balanced portfolio helps you reach your goals while managing risk.",
            "in_app": "We show your current portfolio and recommend a target portfolio based on your profile."
        },
        "Asset Allocation": {
            "definition": "How you divide your money between different types of investments (stocks, bonds, cash).",
            "example": "A 60/30/10 allocation means 60% stocks, 30% bonds, 10% cash.",
            "why_matters": "This is the most important factor in determining your returns and risk level.",
            "in_app": "We calculate the optimal allocation for you based on your age, goals, and risk tolerance."
        },
        "Stocks (Equities)": {
            "definition": "Ownership shares in companies. When you buy a stock, you own a tiny piece of that company.",
            "example": "If you buy Apple stock, you own a small part of Apple. If Apple does well, your stock value goes up.",
            "why_matters": "Stocks have historically provided the highest returns (about 10% per year) but with more ups and downs.",
            "in_app": "We recommend stock percentages based on your risk tolerance and time horizon."
        },
        "Bonds (Fixed Income)": {
            "definition": "Loans you make to companies or governments. They pay you interest and return your money after a set time.",
            "example": "You lend $1,000 to the government for 10 years at 5% interest. You get $50/year and your $1,000 back in 10 years.",
            "why_matters": "Bonds are more stable than stocks but typically offer lower returns (about 5% per year).",
            "in_app": "Bonds provide stability to your portfolio, especially important as you get closer to retirement."
        },
        "Cash (Cash Equivalents)": {
            "definition": "Money in savings accounts, money market funds, or other very safe, liquid investments.",
            "example": "Your emergency fund in a high-yield savings account earning 4% interest.",
            "why_matters": "Cash is safe but grows slowly. It's for emergencies and short-term needs, not long-term growth.",
            "in_app": "We typically recommend keeping 5-10% in cash for emergencies and opportunities."
        },
        "Rebalancing": {
            "definition": "Adjusting your portfolio back to your target allocation when it drifts due to market movements.",
            "example": "Your target is 60% stocks, but after a good year, stocks are now 70%. Rebalancing means selling some stocks to get back to 60%.",
            "why_matters": "Keeps your risk level where you want it and can help you 'buy low, sell high'.",
            "in_app": "Our action plan includes rebalancing recommendations when your current allocation differs from target."
        }
    }
    
    for term, info in concepts.items():
        with st.expander(f"**{term}**"):
            st.markdown(f"""
            **What it means:**
            {info['definition']}
            
            **Real-world example:**
            {info['example']}
            
            **Why it matters:**
            {info['why_matters']}
            
            **How we use it in this app:**
            {info['in_app']}
            """)


def render_performance_metrics_tab() -> None:
    """Performance metrics and ratios."""
    
    st.subheader("📈 Performance Metrics")
    
    concepts = {
        "Return": {
            "definition": "How much money you made (or lost) on your investment, usually shown as a percentage.",
            "example": "If you invest $1,000 and it becomes $1,100, your return is 10%.",
            "why_matters": "This is the bottom line - did your investment make money?",
            "in_app": "We show your portfolio return compared to benchmarks like the S&P 500."
        },
        "Annualized Return": {
            "definition": "Your return adjusted to show what you'd earn per year if the rate stayed constant.",
            "example": "If you made 20% over 2 years, your annualized return is about 9.5% per year (not 10%, because of compounding).",
            "why_matters": "Lets you compare investments over different time periods fairly.",
            "in_app": "All our performance metrics show annualized returns so you can compare apples to apples."
        },
        "Volatility": {
            "definition": "How much your investment value jumps around. High volatility = big swings up and down.",
            "example": "A stock that goes from $100 to $120 to $90 to $110 has high volatility. A bond that stays around $100 has low volatility.",
            "why_matters": "High volatility can be stressful and might cause you to sell at the wrong time.",
            "in_app": "We show volatility so you can see if your portfolio is too bumpy for your comfort level."
        },
        "Sharpe Ratio": {
            "definition": "A score that shows how much return you're getting for the risk you're taking. Higher is better.",
            "example": "A Sharpe ratio of 1.0 is good, 2.0 is excellent. It means you're getting good returns without taking crazy risks.",
            "why_matters": "Two investments might have the same return, but one might be much riskier. Sharpe ratio shows which is better.",
            "in_app": "We calculate this to show if your portfolio is efficiently using risk to generate returns."
        },
        "Sortino Ratio": {
            "definition": "Like Sharpe ratio, but only counts 'bad' volatility (downside risk). Higher is better.",
            "example": "If two portfolios have the same Sharpe ratio, but one has a higher Sortino ratio, it means less downside risk.",
            "why_matters": "You probably care more about avoiding big losses than missing big gains. Sortino focuses on that.",
            "in_app": "We show this alongside Sharpe ratio to give you a complete picture of risk-adjusted returns."
        },
        "Alpha": {
            "definition": "How much better (or worse) your portfolio performed compared to a benchmark like the S&P 500.",
            "example": "If the S&P 500 returned 10% and your portfolio returned 12%, your alpha is +2%.",
            "why_matters": "Shows if your investment strategy is actually working or if you'd be better off just buying the market.",
            "in_app": "We compare your portfolio to the S&P 500 and show your alpha in the Performance section."
        },
        "Beta": {
            "definition": "How much your portfolio moves compared to the overall market. Beta of 1.0 = moves with market.",
            "example": "Beta of 1.2 means if the market goes up 10%, your portfolio goes up 12%. Beta of 0.8 means it goes up 8%.",
            "why_matters": "Helps you understand how sensitive your portfolio is to market movements.",
            "in_app": "We calculate beta in the Compare section to show your portfolio's market sensitivity."
        },
        "Max Drawdown": {
            "definition": "The biggest drop from a peak to a low point. Shows the worst-case scenario you experienced.",
            "example": "If your portfolio went from $10,000 to $12,000, then dropped to $9,000, your max drawdown is 25% (from $12k to $9k).",
            "why_matters": "Shows how much you might lose during bad times. Helps you prepare mentally for market crashes.",
            "in_app": "We show this in performance metrics so you know what to expect during market downturns."
        },
        "Correlation": {
            "definition": "How closely two investments move together. 1.0 = move perfectly together, 0 = no relationship, -1.0 = move opposite.",
            "example": "Tech stocks often have high correlation (they all move together). Stocks and bonds usually have low correlation.",
            "why_matters": "Low correlation between investments helps with diversification - when one drops, the other might not.",
            "in_app": "We show correlation between your portfolio and benchmarks to explain diversification benefits."
        },
        "Win Rate": {
            "definition": "The percentage of days (or periods) when your investment had a positive return.",
            "example": "A win rate of 55% means your investment made money 55% of the time and lost money 45% of the time.",
            "why_matters": "Even with a good overall return, a low win rate might mean you're taking too much risk.",
            "in_app": "We show this in the Compare section to give you a sense of how often your portfolio is 'winning'."
        }
    }
    
    for term, info in concepts.items():
        with st.expander(f"**{term}**"):
            st.markdown(f"""
            **What it means:**
            {info['definition']}
            
            **Real-world example:**
            {info['example']}
            
            **Why it matters:**
            {info['why_matters']}
            
            **How we use it in this app:**
            {info['in_app']}
            """)


def render_investment_types_tab() -> None:
    """Types of investments explained."""
    
    st.subheader("💰 Investment Types")
    
    concepts = {
        "ETF (Exchange-Traded Fund)": {
            "definition": "A basket of investments (like stocks or bonds) that you can buy and sell like a single stock.",
            "example": "The SPY ETF contains all 500 stocks in the S&P 500. When you buy SPY, you own a tiny piece of all 500 companies.",
            "why_matters": "ETFs give you instant diversification and are usually cheaper than buying individual stocks.",
            "in_app": "We recommend specific ETFs based on your profile. They're the easiest way to build a diversified portfolio."
        },
        "Index Fund": {
            "definition": "A type of ETF or mutual fund that tries to match a market index (like the S&P 500) rather than beat it.",
            "example": "An S&P 500 index fund buys all 500 stocks in the S&P 500 in the same proportions as the index.",
            "why_matters": "Index funds are cheap, diversified, and historically outperform most actively managed funds.",
            "in_app": "Many of our ETF recommendations are index funds because they're the best choice for most investors."
        },
        "Expense Ratio": {
            "definition": "The annual fee you pay to own an ETF or mutual fund, shown as a percentage of your investment.",
            "example": "An expense ratio of 0.03% means you pay $3 per year for every $10,000 invested.",
            "why_matters": "Lower fees = more money in your pocket. Over 30 years, a 1% fee difference can cost you hundreds of thousands.",
            "in_app": "We show expense ratios for all recommended ETFs and calculate your total annual fees."
        },
        "Dividend": {
            "definition": "A portion of a company's profits paid to shareholders. Like getting a small bonus for owning the stock.",
            "example": "If you own 100 shares of a stock that pays $1 per share in dividends, you get $100 per year.",
            "why_matters": "Dividends provide income and can be reinvested to grow your investment faster.",
            "in_app": "We recommend dividend ETFs for investors who want income or are closer to retirement."
        },
        "REIT (Real Estate Investment Trust)": {
            "definition": "A company that owns and operates real estate. You can invest in real estate without buying property.",
            "example": "A REIT might own apartment buildings, shopping malls, or office buildings. You get a share of the rental income.",
            "why_matters": "Adds real estate diversification to your portfolio without the hassle of being a landlord.",
            "in_app": "We might recommend REIT ETFs for diversification, especially for income-focused portfolios."
        },
        "Bond ETF": {
            "definition": "An ETF that holds bonds instead of stocks. Gives you exposure to the bond market.",
            "example": "A bond ETF might hold hundreds of government and corporate bonds, paying you interest regularly.",
            "why_matters": "Provides stability and income to your portfolio. Bonds typically go up when stocks go down.",
            "in_app": "We recommend bond ETFs (like BND) as part of your portfolio for stability and diversification."
        },
        "International ETF": {
            "definition": "An ETF that invests in companies outside your home country. Diversifies you globally.",
            "example": "A US investor buying an international ETF would own companies from Europe, Asia, and other regions.",
            "why_matters": "The US is only part of the global economy. International investments reduce your dependence on one country.",
            "in_app": "We typically recommend 10-20% in international ETFs to reduce country-specific risk."
        }
    }
    
    for term, info in concepts.items():
        with st.expander(f"**{term}**"):
            st.markdown(f"""
            **What it means:**
            {info['definition']}
            
            **Real-world example:**
            {info['example']}
            
            **Why it matters:**
            {info['why_matters']}
            
            **How we use it in this app:**
            {info['in_app']}
            """)


def render_calculations_tab() -> None:
    """Financial calculations explained simply."""
    
    st.subheader("🧮 Financial Calculations")
    
    st.markdown("""
    ### **How We Calculate Things**
    
    All our calculations use standard financial formulas. Here's what they mean in plain English:
    """)
    
    calculations = {
        "Future Value": {
            "formula": "FV = PV × (1 + r)^n + PMT × [((1 + r)^n - 1) / r]",
            "explanation": "How much your money will be worth in the future if you invest a certain amount now and add money regularly.",
            "simple_explanation": "Start with some money, add more each month, and let it grow with compound interest. This formula tells you the total.",
            "example": "If you start with $1,000, add $100/month for 10 years at 7% return, you'll have about $18,000.",
            "in_app": "Used in all goal calculators (retirement, home purchase, education) to show how much you'll have."
        },
        "Required Monthly Savings": {
            "formula": "PMT = (FV - PV × (1 + r)^n) × r / ((1 + r)^n - 1)",
            "explanation": "How much you need to save each month to reach a specific goal.",
            "simple_explanation": "We work backwards: if you want $X in Y years, how much do you need to save each month?",
            "example": "To have $1 million in 30 years starting from $10,000 at 7% return, you need to save about $800/month.",
            "in_app": "Shown in goal calculators when you're short of your target. Tells you exactly how much more to save."
        },
        "Weighted Expected Return": {
            "formula": "Expected Return = (Stocks% × 10%) + (Bonds% × 5%) + (Cash% × 3%)",
            "explanation": "Your portfolio's expected return based on how much you have in each asset class.",
            "simple_explanation": "Multiply each percentage by its expected return, then add them up. That's your overall expected return.",
            "example": "60% stocks (10% return) + 30% bonds (5% return) + 10% cash (3% return) = 8.3% expected return.",
            "in_app": "We calculate this for your current and target portfolios to show the expected improvement."
        },
        "Sharpe Ratio": {
            "formula": "Sharpe = (Return - Risk-Free Rate) / Volatility",
            "explanation": "Your excess return (above a safe investment) divided by how risky your investment is.",
            "simple_explanation": "Are you getting paid enough for the risk you're taking? Higher Sharpe = better risk-adjusted returns.",
            "example": "If you earn 10% when a safe investment earns 4%, and your volatility is 15%, your Sharpe is (10-4)/15 = 0.4.",
            "in_app": "Calculated automatically in the Performance and Compare sections to evaluate your portfolio efficiency."
        },
        "Beta": {
            "formula": "β = Covariance(Portfolio, Market) / Variance(Market)",
            "explanation": "How much your portfolio moves compared to the overall market.",
            "simple_explanation": "If the market goes up 10%, does your portfolio go up 10% (β=1.0), more (β>1.0), or less (β<1.0)?",
            "example": "Beta of 1.2 means your portfolio is 20% more volatile than the market. Beta of 0.8 means 20% less volatile.",
            "in_app": "Shown in the Compare section to explain how your portfolio relates to market movements."
        },
        "Compound Interest": {
            "formula": "A = P(1 + r)^n",
            "explanation": "Your money grows exponentially because you earn returns on your returns.",
            "simple_explanation": "Each year, you earn interest not just on your original money, but on all the interest you've earned before.",
            "example": "$1,000 at 10% for 3 years: Year 1 = $1,100, Year 2 = $1,210 (earned $10 on the $100), Year 3 = $1,331.",
            "in_app": "The foundation of all our growth calculations. This is why starting early is so powerful."
        }
    }
    
    for calc_name, info in calculations.items():
        with st.expander(f"**{calc_name}**"):
            st.markdown(f"""
            **The Formula:**
            ```
            {info['formula']}
            ```
            
            **What it means:**
            {info['explanation']}
            
            **In simple terms:**
            {info['simple_explanation']}
            
            **Example:**
            {info['example']}
            
            **Where you'll see it:**
            {info['in_app']}
            """)


def render_strategies_tab() -> None:
    """Investment strategies and best practices."""
    
    st.subheader("💡 Investment Strategies & Best Practices")
    
    st.markdown("""
    ### **Key Principles for Young Investors**
    """)
    
    strategies = {
        "Start Early": {
            "content": """
            **Why it matters:** Time is your biggest advantage. Starting at 20 vs 30 can mean hundreds of thousands more at retirement.
            
            **The math:** If you invest $200/month starting at 20, you'll have more at 65 than someone who invests $400/month starting at 30.
            
            **Action:** Even if you can only save $50/month, start now. Compound interest will do the heavy lifting.
            """
        },
        "Dollar-Cost Averaging": {
            "content": """
            **What it is:** Investing a fixed amount regularly (like $500/month) regardless of market conditions.
            
            **Why it works:** You automatically buy more shares when prices are low and fewer when prices are high. This averages out your purchase price.
            
            **Example:** If a stock is $100, you buy 5 shares. If it drops to $50, you buy 10 shares. Your average cost is $66.67, not $75.
            
            **Action:** Set up automatic monthly investments. Don't try to time the market.
            """
        },
        "Stay the Course": {
            "content": """
            **What it means:** Don't panic and sell when the market drops. Stick to your plan.
            
            **Why it matters:** The biggest losses come from selling at the bottom and missing the recovery. Markets always recover eventually.
            
            **Example:** If you invested in 2008 (financial crisis) and held on, you'd be way ahead today. If you sold in panic, you locked in losses.
            
            **Action:** When markets crash, remind yourself: this is normal, temporary, and actually a buying opportunity if you have cash.
            """
        },
        "Keep Costs Low": {
            "content": """
            **What it means:** Choose investments with low fees (expense ratios under 0.20%).
            
            **Why it matters:** Fees eat into your returns. A 1% fee difference over 40 years can cost you $500,000+.
            
            **Example:** Two funds both return 8%, but one charges 0.03% and the other charges 1%. After 40 years, the low-fee fund gives you $200,000 more.
            
            **Action:** Always check expense ratios. We recommend ETFs with low fees (under 0.10%).
            """
        },
        "Diversify, Don't Concentrate": {
            "content": """
            **What it means:** Spread your money across many investments, not just a few.
            
            **Why it matters:** If one company or sector fails, you won't lose everything. Diversification reduces risk without reducing returns much.
            
            **Example:** Instead of buying 10 individual tech stocks, buy a tech ETF that owns 100+ tech companies. Much safer.
            
            **Action:** Use ETFs and index funds. They give you instant diversification across hundreds or thousands of companies.
            """
        },
        "Rebalance Regularly": {
            "content": """
            **What it means:** Adjust your portfolio back to your target allocation (like 60% stocks, 30% bonds) when it drifts.
            
            **Why it matters:** Over time, winning investments grow and take up more of your portfolio, increasing your risk. Rebalancing keeps risk in check.
            
            **Example:** Your target is 60% stocks, but after a good year, stocks are now 70%. Sell some stocks to get back to 60%.
            
            **Action:** Rebalance once a year or when your allocation is off by more than 5%. We'll remind you in your action plan.
            """
        },
        "Emergency Fund First": {
            "content": """
            **What it means:** Build an emergency fund (6 months of expenses) before investing heavily.
            
            **Why it matters:** Prevents you from having to sell investments at a bad time or go into debt when emergencies happen.
            
            **Example:** If you lose your job and need $12,000 to cover 6 months, you don't want to sell investments that are down 20%.
            
            **Action:** Save 6 months of expenses in a high-yield savings account. Then invest everything else.
            """
        },
        "Tax-Advantaged Accounts": {
            "content": """
            **What they are:** Retirement accounts (401k, IRA) that give you tax benefits.
            
            **Why they matter:** You either don't pay taxes on contributions (traditional) or on withdrawals (Roth). This can save you thousands.
            
            **Example:** If you're in the 22% tax bracket, a $5,000 contribution to a traditional 401k saves you $1,100 in taxes now.
            
            **Action:** Max out employer 401k match (free money!), then contribute to IRA. We factor this into your recommendations.
            """
        }
    }
    
    for strategy, content in strategies.items():
        with st.expander(f"**{strategy}**"):
            st.markdown(content)
    
    st.divider()
    
    st.subheader("🎓 Common Mistakes to Avoid")
    
    mistakes = [
        "**Trying to time the market** - Nobody can predict when to buy and sell. Time in the market beats timing the market.",
        "**Checking your portfolio daily** - This leads to emotional decisions. Check monthly or quarterly.",
        "**Chasing hot stocks** - By the time you hear about it, the opportunity is usually gone. Stick to your plan.",
        "**Selling when markets drop** - This locks in losses. Markets recover. Stay invested.",
        "**Paying high fees** - Actively managed funds rarely beat index funds but charge 10x more. Go with low-cost index funds.",
        "**Not starting because you don't have 'enough'** - Even $50/month matters. Start with what you can.",
        "**Ignoring international markets** - The US is only 60% of global markets. Diversify globally.",
        "**Taking too much or too little risk** - Match your risk to your time horizon and goals. We help you with this."
    ]
    
    for mistake in mistakes:
        st.markdown(f"• {mistake}")
    
    st.divider()
    
    st.subheader("📖 Recommended Reading")
    
    st.markdown("""
    **For Beginners:**
    - "The Simple Path to Wealth" by JL Collins
    - "A Random Walk Down Wall Street" by Burton Malkiel
    - "The Bogleheads' Guide to Investing" by Taylor Larimore
    
    **Key Concepts:**
    - Index investing beats active management
    - Low costs matter enormously
    - Time in market > timing the market
    - Stay the course during volatility
    
    **Remember:** You don't need to be a financial expert to be a successful investor. 
    Keep it simple: low-cost index funds, regular contributions, and patience.
    """)

