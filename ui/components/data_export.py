"""
Data Export Component.

Export portfolio data to Excel and CSV formats.
Includes holdings, allocation, recommendations, and historical data.
"""

import streamlit as st
import pandas as pd
import numpy as np
from io import BytesIO
from datetime import datetime
from typing import Dict, Any, List, Optional


def create_portfolio_summary_df(profile: Dict[str, Any], recommendation: Dict[str, Any], format_for_display: bool = False) -> pd.DataFrame:
    """Create portfolio summary dataframe."""
    
    # Store raw values for proper serialization
    income = profile.get('income', 0)
    savings = profile.get('savings', 0)
    age = profile.get('age', 'N/A')
    risk_tolerance = profile.get('risk_tolerance', 'N/A')
    horizon = profile.get('investment_horizon_years', 'N/A')
    risk_score = recommendation.get('risk_profile', {}).get('score', 'N/A')
    risk_label = recommendation.get('risk_profile', {}).get('label', 'N/A')
    
    if format_for_display:
        # Format for display/export
        income_str = f"${income:,.0f}" if isinstance(income, (int, float)) else str(income)
        savings_str = f"${savings:,.0f}" if isinstance(savings, (int, float)) else str(savings)
        horizon_str = f"{horizon} years" if isinstance(horizon, (int, float)) else str(horizon)
        risk_score_str = f"{risk_score}/100" if isinstance(risk_score, (int, float)) else str(risk_score)
        
        data = {
            'Metric': [
                'Age',
                'Annual Income',
                'Current Savings',
                'Risk Tolerance',
                'Investment Horizon',
                'Risk Score',
                'Risk Profile',
            ],
            'Value': [
                str(age),
                income_str,
                savings_str,
                str(risk_tolerance),
                horizon_str,
                risk_score_str,
                str(risk_label),
            ]
        }
    else:
        # Keep numeric values as numbers for proper serialization
        data = {
            'Metric': [
                'Age',
                'Annual Income',
                'Current Savings',
                'Risk Tolerance',
                'Investment Horizon',
                'Risk Score',
                'Risk Profile',
            ],
            'Value': [
                age if isinstance(age, (int, float)) else 'N/A',
                income,
                savings,
                risk_tolerance,
                horizon if isinstance(horizon, (int, float)) else 'N/A',
                risk_score if isinstance(risk_score, (int, float)) else 'N/A',
                risk_label,
            ]
        }
    
    return pd.DataFrame(data)


def create_allocation_df(profile: Dict[str, Any], recommendation: Dict[str, Any]) -> pd.DataFrame:
    """Create allocation comparison dataframe."""
    
    current = profile.get('current_portfolio', {})
    target = recommendation.get('target_allocation', {})
    gaps = recommendation.get('allocation_gaps', {})
    
    data = {
        'Asset Class': ['Stocks', 'Bonds', 'Cash'],
        'Current (%)': [
            current.get('stocks', 0),
            current.get('bonds', 0),
            current.get('cash', 0),
        ],
        'Target (%)': [
            target.get('stocks', 0),
            target.get('bonds', 0),
            target.get('cash', 0),
        ],
        'Adjustment Needed (%)': [
            gaps.get('stocks', 0),
            gaps.get('bonds', 0),
            gaps.get('cash', 0),
        ],
    }
    
    return pd.DataFrame(data)


def create_action_plan_df(recommendation: Dict[str, Any]) -> pd.DataFrame:
    """Create action plan dataframe."""
    
    actions = recommendation.get('action_plan', [])
    
    data = {
        'Priority': list(range(1, len(actions) + 1)),
        'Action Item': actions,
        'Status': ['Pending'] * len(actions),
    }
    
    return pd.DataFrame(data)


def create_sectors_df(recommendation: Dict[str, Any]) -> pd.DataFrame:
    """Create recommended sectors dataframe."""
    
    sectors = recommendation.get('suggested_sectors', [])
    
    data = {
        'Rank': list(range(1, len(sectors) + 1)),
        'Sector': sectors,
        'Notes': ['Recommended based on profile'] * len(sectors),
    }
    
    return pd.DataFrame(data)


def create_historical_performance_df(profile: Dict[str, Any], months: int = 12) -> pd.DataFrame:
    """Create calculated historical performance data based on actual portfolio allocation."""
    
    try:
        from components.portfolio_calculations import generate_portfolio_performance
        
        allocation = profile.get('current_portfolio', {'stocks': 50, 'bonds': 30, 'cash': 20})
        initial_value = float(profile.get('savings', 10000))
        
        # Generate calculated performance data
        df = generate_portfolio_performance(
            allocation=allocation,
            initial_value=initial_value,
            months=months,
            include_benchmarks=True
        )
        
        # Convert to monthly data for export
        monthly_df = df.resample('M', on='date').last()
        
        # Calculate monthly returns
        portfolio_monthly_returns = monthly_df['portfolio'].pct_change().fillna(0) * 100
        sp500_monthly_returns = monthly_df['sp500'].pct_change().fillna(0) * 100
        
        return pd.DataFrame({
            'Date': monthly_df['date'].dt.strftime('%Y-%m'),
            'Portfolio Value ($)': monthly_df['portfolio'].round(2),
            'Portfolio Return (%)': portfolio_monthly_returns.round(2),
            'S&P 500 Value ($)': monthly_df['sp500'].round(2),
            'S&P 500 Return (%)': sp500_monthly_returns.round(2),
            'Outperformance (%)': (portfolio_monthly_returns - sp500_monthly_returns).round(2),
        })
    except ImportError:
        # Fallback to simple calculation if import fails
        dates = pd.date_range(end=datetime.now(), periods=months, freq='ME')
        allocation = profile.get('current_portfolio', {'stocks': 50, 'bonds': 30, 'cash': 20})
        initial_value = float(profile.get('savings', 10000))
        
        # Use realistic monthly returns based on allocation
        stock_monthly = 0.10 / 12  # 10% annual / 12 months
        bond_monthly = 0.05 / 12
        cash_monthly = 0.03 / 12
        
        portfolio_monthly = (
            allocation['stocks'] / 100 * stock_monthly +
            allocation['bonds'] / 100 * bond_monthly +
            allocation['cash'] / 100 * cash_monthly
        )
        
        portfolio_values = initial_value * np.power(1 + portfolio_monthly, np.arange(1, months + 1))
        sp500_values = initial_value * np.power(1 + 0.10/12, np.arange(1, months + 1))
        
        return pd.DataFrame({
            'Date': dates.strftime('%Y-%m'),
            'Portfolio Value ($)': portfolio_values.round(2),
            'Portfolio Return (%)': [portfolio_monthly * 100] * months,
            'S&P 500 Value ($)': sp500_values.round(2),
            'S&P 500 Return (%)': [0.10/12 * 100] * months,
            'Outperformance (%)': [(portfolio_monthly - 0.10/12) * 100] * months,
        })


def create_goals_df(profile: Dict[str, Any]) -> pd.DataFrame:
    """Create financial goals dataframe."""
    
    goals = profile.get('financial_goals', [])
    
    data = {
        'Goal': goals,
        'Priority': ['High'] * len(goals),
        'Target Date': ['TBD'] * len(goals),
        'Status': ['In Progress'] * len(goals),
    }
    
    return pd.DataFrame(data)


def export_to_excel(profile: Dict[str, Any], recommendation: Dict[str, Any]) -> BytesIO:
    """Export all data to Excel file with multiple sheets."""
    
    output = BytesIO()
    
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        # Summary sheet - use formatted version for export
        summary_df = create_portfolio_summary_df(profile, recommendation, format_for_display=True)
        summary_df.to_excel(writer, sheet_name='Profile Summary', index=False)
        
        # Allocation sheet
        allocation_df = create_allocation_df(profile, recommendation)
        allocation_df.to_excel(writer, sheet_name='Allocation', index=False)
        
        # Action Plan sheet
        action_df = create_action_plan_df(recommendation)
        action_df.to_excel(writer, sheet_name='Action Plan', index=False)
        
        # Sectors sheet
        sectors_df = create_sectors_df(recommendation)
        sectors_df.to_excel(writer, sheet_name='Recommended Sectors', index=False)
        
        # Historical Performance sheet
        history_df = create_historical_performance_df(profile)
        history_df.to_excel(writer, sheet_name='Historical Performance', index=False)
        
        # Goals sheet
        goals_df = create_goals_df(profile)
        goals_df.to_excel(writer, sheet_name='Financial Goals', index=False)
        
        # Metadata sheet
        metadata = pd.DataFrame({
            'Field': ['Export Date', 'Session ID', 'App Version'],
            'Value': [datetime.now().strftime('%Y-%m-%d %H:%M'), 
                     profile.get('user_id', 'N/A'),
                     '1.0.0']
        })
        metadata.to_excel(writer, sheet_name='Export Info', index=False)
    
    output.seek(0)
    return output


def export_to_csv(profile: Dict[str, Any], recommendation: Dict[str, Any], data_type: str) -> str:
    """Export specific data to CSV format."""
    
    if data_type == 'summary':
        df = create_portfolio_summary_df(profile, recommendation, format_for_display=True)
    elif data_type == 'allocation':
        df = create_allocation_df(profile, recommendation)
    elif data_type == 'actions':
        df = create_action_plan_df(recommendation)
    elif data_type == 'performance':
        df = create_historical_performance_df(profile)
    else:
        df = create_portfolio_summary_df(profile, recommendation, format_for_display=True)
    
    return df.to_csv(index=False)


def render_export_section(profile: Optional[Dict[str, Any]], recommendation: Optional[Dict[str, Any]]) -> None:
    """Render the data export section."""
    
    st.subheader("📥 Export Data")
    
    if not profile or not recommendation:
        st.warning("Complete your profile to enable data export.")
        return
    
    st.markdown("Download your financial data for analysis in Excel or other tools.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📊 Excel Export")
        st.caption("Complete workbook with all data in separate sheets")
        
        try:
            excel_data = export_to_excel(profile, recommendation)
            
            st.download_button(
                label="📥 Download Excel (.xlsx)",
                data=excel_data,
                file_name=f"financial_report_{datetime.now().strftime('%Y%m%d')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
            
            st.caption("Includes: Profile, Allocation, Action Plan, Sectors, Performance History")
            
        except Exception as e:
            st.error(f"Excel export requires openpyxl: {e}")
            st.code("pip install openpyxl")
    
    with col2:
        st.markdown("### 📄 CSV Export")
        st.caption("Individual data files for specific analysis")
        
        csv_type = st.selectbox(
            "Select data to export",
            ["summary", "allocation", "actions", "performance"],
            format_func=lambda x: {
                "summary": "Profile Summary",
                "allocation": "Portfolio Allocation",
                "actions": "Action Plan",
                "performance": "Historical Performance"
            }[x]
        )
        
        csv_data = export_to_csv(profile, recommendation, csv_type)
        
        st.download_button(
            label="📥 Download CSV",
            data=csv_data,
            file_name=f"{csv_type}_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    # Preview section
    with st.expander("👁️ Preview Export Data"):
        preview_tab = st.radio(
            "Select data to preview",
            ["Profile", "Allocation", "Actions", "Performance"],
            horizontal=True
        )
        
        if preview_tab == "Profile":
            st.dataframe(create_portfolio_summary_df(profile, recommendation), use_container_width=True)
        elif preview_tab == "Allocation":
            st.dataframe(create_allocation_df(profile, recommendation), use_container_width=True)
        elif preview_tab == "Actions":
            st.dataframe(create_action_plan_df(recommendation), use_container_width=True)
        elif preview_tab == "Performance":
            st.dataframe(create_historical_performance_df(profile), use_container_width=True)


