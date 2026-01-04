"""
Goal-Based Planning Calculator Component.

Interactive calculator for retirement, home purchase, education, etc.
Uses compound interest formulas and visual timelines.
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, Any, Optional


def calculate_future_value(
    present_value: float,
    monthly_contribution: float,
    annual_rate: float,
    years: int
) -> float:
    """
    Calculate future value with monthly contributions using compound interest formulas.
    
    Mathematical Formula:
    FV = PV × (1 + r)^n + PMT × [((1 + r)^n - 1) / r]
    
    Where:
    - FV = Future Value
    - PV = Present Value (initial amount)
    - PMT = Monthly Payment (contribution)
    - r = Monthly interest rate (annual_rate / 12)
    - n = Number of periods (years × 12)
    
    This combines:
    1. Future value of present value: PV × (1 + r)^n
    2. Future value of annuity: PMT × [((1 + r)^n - 1) / r]
    """
    if years <= 0:
        return present_value
    
    monthly_rate = annual_rate / 12
    months = years * 12
    
    # Future value of present value (compound interest)
    # FV_PV = PV × (1 + r)^n
    fv_pv = present_value * (1 + monthly_rate) ** months
    
    # Future value of annuity (monthly contributions)
    # FV_annuity = PMT × [((1 + r)^n - 1) / r]
    if abs(monthly_rate) > 1e-10:  # Avoid division by zero
        fv_annuity = monthly_contribution * (((1 + monthly_rate) ** months - 1) / monthly_rate)
    else:
        # When rate is 0, FV = PMT × n (simple accumulation)
        fv_annuity = monthly_contribution * months
    
    return fv_pv + fv_annuity


def calculate_required_monthly_savings(
    target_amount: float,
    present_value: float,
    annual_rate: float,
    years: int
) -> float:
    """
    Calculate required monthly savings to reach a target amount.
    
    Mathematical Formula (solving annuity formula for PMT):
    PMT = (FV - PV × (1 + r)^n) × r / ((1 + r)^n - 1)
    
    Where:
    - PMT = Required Monthly Payment
    - FV = Target Future Value
    - PV = Present Value
    - r = Monthly interest rate (annual_rate / 12)
    - n = Number of periods (years × 12)
    
    This solves: FV = PV × (1 + r)^n + PMT × [((1 + r)^n - 1) / r]
    for PMT.
    """
    if years <= 0 or target_amount <= 0:
        return 0.0
    
    monthly_rate = annual_rate / 12
    months = years * 12
    
    # Future value of present value
    # FV_PV = PV × (1 + r)^n
    fv_pv = present_value * (1 + monthly_rate) ** months
    
    # Remaining amount needed from contributions
    remaining = target_amount - fv_pv
    
    if remaining <= 0:
        # Already have enough, no additional savings needed
        return 0.0
    
    # Calculate required monthly payment using annuity formula
    # PMT = remaining × r / ((1 + r)^n - 1)
    if abs(monthly_rate) > 1e-10:  # Avoid division by zero
        denominator = (1 + monthly_rate) ** months - 1
        if abs(denominator) > 1e-10:
            monthly_payment = remaining * monthly_rate / denominator
        else:
            # Fallback for very small rates
            monthly_payment = remaining / months
    else:
        # When rate is 0, PMT = remaining / n
        monthly_payment = remaining / months
    
    return max(0.0, monthly_payment)


@st.cache_data(ttl=300)  # Cache for 5 minutes
def generate_projection_data(
    initial: float,
    monthly: float,
    rate: float,
    years: int,
    target: float
) -> pd.DataFrame:
    """
    Generate month-by-month projection data using compound interest calculations.
    
    Mathematical Process:
    For each month m:
    - Balance[m] = Balance[m-1] × (1 + r) + PMT
    - Contributions[m] = Initial + (m × PMT)
    - Growth[m] = Balance[m] - Contributions[m]
    
    Where:
    - r = monthly_rate = annual_rate / 12
    - PMT = monthly contribution
    """
    if years <= 0:
        return pd.DataFrame({
            'month': [0],
            'year': [0],
            'balance': [initial],
            'contributions': [initial],
            'growth': [0.0],
            'target': [target]
        })
    
    months = years * 12
    monthly_rate = rate / 12
    
    data = []
    balance = initial
    total_contributions = initial
    
    for month in range(months + 1):
        year = month / 12.0  # More precise year calculation
        
        # Calculate contributions (sum of initial + all monthly contributions)
        contributions = initial + (month * monthly)
        
        # Calculate growth (compound interest earned)
        growth = balance - contributions
        
        data.append({
            'month': month,
            'year': year,
            'balance': balance,
            'contributions': contributions,
            'growth': growth,
            'target': target
        })
        
        # Update balance for next month using compound interest formula
        # Balance[t+1] = Balance[t] × (1 + r) + PMT
        if month < months:
            balance = balance * (1 + monthly_rate) + monthly
    
    return pd.DataFrame(data)


def render_projection_chart(df: pd.DataFrame, goal_name: str) -> None:
    """Render goal projection chart."""
    fig = go.Figure()
    
    # Balance area
    fig.add_trace(go.Scatter(
        x=df['year'],
        y=df['balance'],
        mode='lines',
        name='Projected Balance',
        line=dict(color='#2E86AB', width=3),
        fill='tozeroy',
        fillcolor='rgba(46, 134, 171, 0.2)'
    ))
    
    # Contributions line
    fig.add_trace(go.Scatter(
        x=df['year'],
        y=df['contributions'],
        mode='lines',
        name='Your Contributions',
        line=dict(color='#F18F01', width=2, dash='dot')
    ))
    
    # Target line
    fig.add_trace(go.Scatter(
        x=df['year'],
        y=df['target'],
        mode='lines',
        name='Target',
        line=dict(color='#C73E1D', width=2, dash='dash')
    ))
    
    # Check if goal is reached
    goal_reached_year = df[df['balance'] >= df['target']]['year'].min()
    if pd.notna(goal_reached_year):
        fig.add_vline(
            x=goal_reached_year,
            line_dash="dot",
            line_color="green",
            annotation_text=f"Goal reached!",
            annotation_position="top"
        )
    
    fig.update_layout(
        title=f"📈 {goal_name} Projection",
        xaxis_title="Years from Now",
        yaxis_title="Amount ($)",
        height=450,
        template="plotly_white",
        hovermode='x unified',
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01
        )
    )
    
    # Format y-axis with dollar signs
    fig.update_yaxes(tickformat="$,.0f")
    
    st.plotly_chart(fig, use_container_width=True)


def render_milestone_timeline(df: pd.DataFrame, milestones: Dict[int, str]) -> None:
    """Render milestone timeline."""
    fig = go.Figure()
    
    for year, label in milestones.items():
        if year <= df['year'].max():
            balance_at_year = df[df['year'] == year]['balance'].values[0]
            fig.add_trace(go.Scatter(
                x=[year],
                y=[balance_at_year],
                mode='markers+text',
                name=label,
                text=[label],
                textposition='top center',
                marker=dict(size=15, symbol='star', color='gold'),
                showlegend=False
            ))
    
    fig.update_layout(
        title="🎯 Milestones",
        xaxis_title="Years",
        yaxis_title="Balance ($)",
        height=250,
        template="plotly_white"
    )
    
    st.plotly_chart(fig, use_container_width=True)


def render_retirement_calculator() -> None:
    """Render retirement planning calculator."""
    st.subheader("🏖️ Retirement Planning")
    
    col1, col2 = st.columns(2)
    
    with col1:
        current_age = st.number_input("Current Age", 18, 80, 30)
        retirement_age = st.number_input("Desired Retirement Age", current_age + 1, 100, 65)
        current_savings = st.number_input("Current Savings ($)", 0, 10000000, 50000, step=5000)
    
    with col2:
        monthly_contribution = st.number_input("Monthly Contribution ($)", 0, 50000, 500, step=100)
        target_amount = st.number_input("Retirement Goal ($)", 100000, 50000000, 1000000, step=100000)
        expected_return = st.slider("Expected Annual Return (%)", 1.0, 15.0, 7.0, 0.5) / 100
    
    years_to_retirement = retirement_age - current_age
    
    # Calculate projections
    projected_amount = calculate_future_value(
        current_savings, monthly_contribution, expected_return, years_to_retirement
    )
    
    required_monthly = calculate_required_monthly_savings(
        target_amount, current_savings, expected_return, years_to_retirement
    )
    
    gap = target_amount - projected_amount
    
    st.divider()
    
    # Results
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "Projected at Retirement",
            f"${projected_amount:,.0f}",
            delta=f"${gap:+,.0f} from goal" if gap != 0 else "Goal reached!",
            delta_color="normal" if projected_amount >= target_amount else "inverse"
        )
    
    with col2:
        st.metric(
            "Required Monthly",
            f"${required_monthly:,.0f}",
            delta=f"${required_monthly - monthly_contribution:+,.0f} more needed" if required_monthly > monthly_contribution else "On track!",
            delta_color="inverse" if required_monthly > monthly_contribution else "normal"
        )
    
    with col3:
        st.metric(
            "Years to Retirement",
            f"{years_to_retirement}",
            help=f"You'll be {retirement_age} years old"
        )
    
    # Generate and display chart
    df = generate_projection_data(
        current_savings, monthly_contribution, expected_return,
        years_to_retirement, target_amount
    )
    
    render_projection_chart(df, "Retirement Savings")
    
    # Analysis
    st.subheader("📊 Analysis")
    
    if projected_amount >= target_amount:
        surplus = projected_amount - target_amount
        st.success(f"""
        🎉 **Congratulations!** You're on track to exceed your retirement goal by **${surplus:,.0f}**!
        
        At your current pace:
        - Total contributions: **${current_savings + monthly_contribution * 12 * years_to_retirement:,.0f}**
        - Investment growth: **${projected_amount - current_savings - monthly_contribution * 12 * years_to_retirement:,.0f}**
        """)
    else:
        additional_monthly = required_monthly - monthly_contribution
        st.warning(f"""
        ⚠️ **You're ${abs(gap):,.0f} short** of your retirement goal.
        
        **Options to close the gap:**
        1. Increase monthly savings by **${additional_monthly:,.0f}** to **${required_monthly:,.0f}**
        2. Delay retirement by **{max(1, int(np.ceil(np.log(target_amount / projected_amount) / np.log(1 + expected_return))))} years** (if projected > 0)
        3. Reduce your target by **${abs(gap):,.0f}**
        4. Seek higher returns (current: {expected_return*100:.1f}%)
        
        **Mathematical Note:** Years to delay = log(FV_target / FV_current) / log(1 + rate)
        """)


def render_home_purchase_calculator() -> None:
    """Render home purchase planning calculator."""
    st.subheader("🏠 Home Purchase Planning")
    
    col1, col2 = st.columns(2)
    
    with col1:
        home_price = st.number_input("Target Home Price ($)", 100000, 10000000, 500000, step=50000)
        down_payment_pct = st.slider("Down Payment (%)", 3, 50, 20)
        years_to_save = st.number_input("Years to Save", 1, 30, 5)
    
    with col2:
        current_savings = st.number_input("Current Savings ($)", 0, 5000000, 20000, step=5000, key="home_savings")
        monthly_savings = st.number_input("Monthly Savings ($)", 0, 50000, 1000, step=100, key="home_monthly")
        savings_rate = st.slider("Savings Account Rate (%)", 0.0, 10.0, 4.0, 0.5) / 100
    
    down_payment_target = home_price * (down_payment_pct / 100)
    closing_costs = home_price * 0.03  # Estimate 3% closing costs
    total_needed = down_payment_target + closing_costs
    
    # Calculate projections
    projected_savings = calculate_future_value(
        current_savings, monthly_savings, savings_rate, years_to_save
    )
    
    required_monthly = calculate_required_monthly_savings(
        total_needed, current_savings, savings_rate, years_to_save
    )
    
    st.divider()
    
    # Results
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Down Payment", f"${down_payment_target:,.0f}", help=f"{down_payment_pct}% of home price")
    
    with col2:
        st.metric("Est. Closing Costs", f"${closing_costs:,.0f}", help="~3% of home price")
    
    with col3:
        st.metric("Total Needed", f"${total_needed:,.0f}")
    
    with col4:
        st.metric(
            "Projected Savings",
            f"${projected_savings:,.0f}",
            delta=f"${projected_savings - total_needed:+,.0f}",
            delta_color="normal" if projected_savings >= total_needed else "inverse"
        )
    
    # Generate and display chart
    df = generate_projection_data(
        current_savings, monthly_savings, savings_rate,
        years_to_save, total_needed
    )
    
    render_projection_chart(df, "Home Down Payment")
    
    # Monthly mortgage preview
    st.subheader("🏦 Monthly Mortgage Preview")
    
    mortgage_rate = st.slider("Estimated Mortgage Rate (%)", 3.0, 10.0, 6.5, 0.1) / 100
    loan_term = st.selectbox("Loan Term", [15, 30], index=1)
    
    loan_amount = home_price - down_payment_target
    monthly_rate = mortgage_rate / 12
    num_payments = loan_term * 12
    
    # Mortgage payment formula: M = P × [r(1+r)^n] / [(1+r)^n - 1]
    # Where: M = monthly payment, P = principal, r = monthly rate, n = number of payments
    if abs(monthly_rate) > 1e-10:  # Avoid division by zero
        numerator = monthly_rate * (1 + monthly_rate) ** num_payments
        denominator = (1 + monthly_rate) ** num_payments - 1
        monthly_payment = loan_amount * (numerator / denominator)
    else:
        # When rate is 0, simple division
        monthly_payment = loan_amount / num_payments
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Loan Amount", f"${loan_amount:,.0f}")
    
    with col2:
        st.metric("Est. Monthly Payment", f"${monthly_payment:,.0f}", help="Principal + Interest only")
    
    with col3:
        total_paid = monthly_payment * num_payments
        total_interest = total_paid - loan_amount
        st.metric("Total Interest", f"${total_interest:,.0f}", help=f"Over {loan_term} years")


def render_education_calculator() -> None:
    """Render education savings calculator."""
    st.subheader("🎓 Education Savings (529 Plan)")
    
    col1, col2 = st.columns(2)
    
    with col1:
        child_age = st.number_input("Child's Current Age", 0, 17, 5)
        college_start_age = st.number_input("College Start Age", child_age + 1, 25, 18)
        years_of_college = st.selectbox("Years of College", [2, 4, 6], index=1)
    
    with col2:
        annual_cost = st.number_input("Annual College Cost ($)", 10000, 100000, 30000, step=5000)
        current_529 = st.number_input("Current 529 Balance ($)", 0, 500000, 10000, step=1000)
        monthly_contribution = st.number_input("Monthly Contribution ($)", 0, 5000, 300, step=50, key="edu_monthly")
    
    # Education cost inflation: 5% annually (historical average)
    edu_inflation = 0.05
    expected_return = 0.07  # 7% expected return for 529 plans
    
    years_to_college = college_start_age - child_age
    
    # Calculate future cost with inflation using compound growth formula
    # Future_Value = Present_Value × (1 + inflation_rate)^years
    future_annual_cost = annual_cost * (1 + edu_inflation) ** years_to_college
    total_future_cost = future_annual_cost * years_of_college
    
    # Calculate projected savings
    projected_savings = calculate_future_value(
        current_529, monthly_contribution, expected_return, years_to_college
    )
    
    required_monthly = calculate_required_monthly_savings(
        total_future_cost, current_529, expected_return, years_to_college
    )
    
    st.divider()
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "Est. Total College Cost",
            f"${total_future_cost:,.0f}",
            help=f"At {edu_inflation*100:.0f}% annual inflation"
        )
    
    with col2:
        st.metric(
            "Projected 529 Balance",
            f"${projected_savings:,.0f}",
            delta=f"{projected_savings/total_future_cost*100:.0f}% of cost"
        )
    
    with col3:
        st.metric(
            "Required Monthly",
            f"${required_monthly:,.0f}",
            delta=f"${required_monthly - monthly_contribution:+,.0f}" if required_monthly != monthly_contribution else "On track!"
        )
    
    # Generate and display chart
    df = generate_projection_data(
        current_529, monthly_contribution, expected_return,
        years_to_college, total_future_cost
    )
    
    render_projection_chart(df, "Education Savings")
    
    # Coverage analysis
    coverage_pct = min(100, (projected_savings / total_future_cost) * 100)
    
    st.subheader("📊 Coverage Analysis")
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=coverage_pct,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "Cost Coverage"},
        gauge={
            'axis': {'range': [0, 100]},
            'bar': {'color': "#2E86AB"},
            'steps': [
                {'range': [0, 50], 'color': "#FFCDD2"},
                {'range': [50, 80], 'color': "#FFF9C4"},
                {'range': [80, 100], 'color': "#C8E6C9"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 100
            }
        }
    ))
    
    fig.update_layout(height=300)
    st.plotly_chart(fig, use_container_width=True)


def render_goal_calculator() -> None:
    """Main goal calculator component."""
    st.header("🎯 Goal-Based Planning Calculator")
    
    st.markdown("""
    Plan your financial future with our mathematically rigorous calculators. 
    All calculations use standard financial formulas for compound interest, annuities, and loan amortization.
    
    **Key Mathematical Formulas Used:**
    - **Future Value**: `FV = PV × (1 + r)^n + PMT × [((1 + r)^n - 1) / r]`
    - **Required Savings**: `PMT = (FV - PV × (1 + r)^n) × r / ((1 + r)^n - 1)`
    - **Mortgage Payment**: `M = P × [r(1+r)^n] / [(1+r)^n - 1]`
    - **Inflation Adjustment**: `Future_Value = Present_Value × (1 + inflation)^years`
    """)
    
    # Goal type selector
    goal_type = st.selectbox(
        "Select Your Goal",
        ["🏖️ Retirement Planning", "🏠 Home Purchase", "🎓 Education Savings", "💰 Custom Goal"],
        index=0
    )
    
    st.divider()
    
    if goal_type == "🏖️ Retirement Planning":
        render_retirement_calculator()
    elif goal_type == "🏠 Home Purchase":
        render_home_purchase_calculator()
    elif goal_type == "🎓 Education Savings":
        render_education_calculator()
    else:
        render_custom_goal_calculator()


def render_custom_goal_calculator() -> None:
    """Render custom goal calculator."""
    st.subheader("💰 Custom Savings Goal")
    
    col1, col2 = st.columns(2)
    
    with col1:
        goal_name = st.text_input("Goal Name", "My Savings Goal")
        target_amount = st.number_input("Target Amount ($)", 1000, 100000000, 100000, step=10000)
        years = st.number_input("Years to Achieve", 1, 50, 10)
    
    with col2:
        current_savings = st.number_input("Current Savings ($)", 0, 10000000, 5000, step=1000, key="custom_savings")
        monthly_contribution = st.number_input("Monthly Savings ($)", 0, 50000, 500, step=100, key="custom_monthly")
        annual_return = st.slider("Expected Return (%)", 0.0, 15.0, 5.0, 0.5) / 100
    
    # Calculations
    projected = calculate_future_value(current_savings, monthly_contribution, annual_return, years)
    required = calculate_required_monthly_savings(target_amount, current_savings, annual_return, years)
    
    st.divider()
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "Projected Amount",
            f"${projected:,.0f}",
            delta=f"${projected - target_amount:+,.0f}",
            delta_color="normal" if projected >= target_amount else "inverse"
        )
    
    with col2:
        st.metric("Required Monthly", f"${required:,.0f}")
    
    with col3:
        if projected >= target_amount:
            st.metric("Status", "✅ On Track")
        else:
            shortfall_monthly = required - monthly_contribution
            st.metric("Monthly Shortfall", f"${shortfall_monthly:,.0f}")
    
    # Chart
    df = generate_projection_data(
        current_savings, monthly_contribution, annual_return,
        years, target_amount
    )
    
    render_projection_chart(df, goal_name)
    
    # Mathematical formulas reference
    with st.expander("📐 Mathematical Formulas Reference"):
        st.markdown("""
        ### **Compound Interest & Future Value Formulas:**
        
        **1. Future Value with Monthly Contributions:**
        ```
        FV = PV × (1 + r)^n + PMT × [((1 + r)^n - 1) / r]
        ```
        Where:
        - `FV` = Future Value
        - `PV` = Present Value (initial amount)
        - `PMT` = Monthly Payment/Contribution
        - `r` = Monthly interest rate (annual_rate ÷ 12)
        - `n` = Number of periods (years × 12)
        
        **2. Required Monthly Savings:**
        ```
        PMT = (FV - PV × (1 + r)^n) × r / ((1 + r)^n - 1)
        ```
        This solves the future value formula for PMT.
        
        **3. Mortgage Payment (Amortization):**
        ```
        M = P × [r(1+r)^n] / [(1+r)^n - 1]
        ```
        Where:
        - `M` = Monthly Payment
        - `P` = Principal (loan amount)
        - `r` = Monthly interest rate
        - `n` = Number of payments
        
        **4. Inflation Adjustment:**
        ```
        Future_Value = Present_Value × (1 + inflation_rate)^years
        ```
        
        **5. Years to Reach Goal (if adjusting timeline):**
        ```
        years = log(FV_target / FV_current) / log(1 + rate)
        ```
        
        ### **Key Concepts:**
        - **Compound Interest**: Interest earned on both principal and accumulated interest
        - **Annuity**: Series of equal payments made at regular intervals
        - **Present Value**: Current worth of a future sum of money
        - **Future Value**: Value of an investment at a future date
        - **Amortization**: Gradual repayment of a loan over time
        
        All calculations use these standard financial mathematics formulas.
        """)

