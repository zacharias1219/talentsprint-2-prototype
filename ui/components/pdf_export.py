"""
PDF Export Component for Financial Advisor.

Generates downloadable PDF reports with user profile and recommendations.
"""

import streamlit as st
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path
import io

try:
    from fpdf import FPDF
    FPDF_AVAILABLE = True
except ImportError:
    FPDF_AVAILABLE = False


class FinancialReportPDF(FPDF):
    """Custom PDF class for financial reports."""
    
    def __init__(self):
        super().__init__()
        self.set_auto_page_break(auto=True, margin=15)
    
    def header(self):
        """Page header."""
        self.set_font('Helvetica', 'B', 16)
        self.set_text_color(0, 51, 102)  # Dark blue
        self.cell(0, 10, 'AI Financial Advisor Report', 0, 1, 'C')
        self.set_font('Helvetica', '', 10)
        self.set_text_color(128, 128, 128)
        self.cell(0, 5, f'Generated: {datetime.now().strftime("%B %d, %Y at %I:%M %p")}', 0, 1, 'C')
        self.ln(5)
        # Line separator
        self.set_draw_color(0, 51, 102)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(10)
    
    def footer(self):
        """Page footer with disclaimer."""
        self.set_y(-25)
        self.set_font('Helvetica', 'I', 8)
        self.set_text_color(128, 128, 128)
        self.multi_cell(0, 4, 
            'DISCLAIMER: This report is for informational purposes only and does not constitute '
            'financial advice. Please consult a licensed financial advisor before making investment decisions.',
            align='C')
        self.cell(0, 5, f'Page {self.page_no()}', 0, 0, 'C')
    
    def section_title(self, title: str):
        """Add a section title."""
        self.set_font('Helvetica', 'B', 14)
        self.set_text_color(0, 51, 102)
        self.cell(0, 10, title, 0, 1, 'L')
        self.set_text_color(0, 0, 0)
    
    def section_subtitle(self, subtitle: str):
        """Add a subsection title."""
        self.set_font('Helvetica', 'B', 11)
        self.set_text_color(51, 51, 51)
        self.cell(0, 8, subtitle, 0, 1, 'L')
        self.set_text_color(0, 0, 0)
    
    def key_value(self, key: str, value: str, bold_value: bool = False):
        """Add a key-value pair."""
        self.set_font('Helvetica', '', 10)
        self.cell(60, 7, f'{key}:', 0, 0, 'L')
        if bold_value:
            self.set_font('Helvetica', 'B', 10)
        self.cell(0, 7, str(value), 0, 1, 'L')
    
    def add_table(self, headers: list, rows: list):
        """Add a simple table."""
        self.set_font('Helvetica', 'B', 10)
        self.set_fill_color(0, 51, 102)
        self.set_text_color(255, 255, 255)
        
        col_width = 190 / len(headers)
        for header in headers:
            self.cell(col_width, 8, header, 1, 0, 'C', fill=True)
        self.ln()
        
        self.set_font('Helvetica', '', 10)
        self.set_text_color(0, 0, 0)
        
        for row in rows:
            for cell in row:
                self.cell(col_width, 7, str(cell), 1, 0, 'C')
            self.ln()
    
    def add_bullet_list(self, items: list):
        """Add a bullet list."""
        self.set_font('Helvetica', '', 10)
        for item in items:
            self.cell(5, 6, chr(149), 0, 0)  # Bullet character
            self.multi_cell(0, 6, str(item))


def generate_financial_report(profile: Dict[str, Any], recommendation: Dict[str, Any], 
                               session_name: Optional[str] = None) -> bytes:
    """
    Generate a comprehensive PDF financial report.
    
    Args:
        profile: User profile data
        recommendation: Generated recommendations
        session_name: Optional session identifier
        
    Returns:
        PDF file as bytes
    """
    if not FPDF_AVAILABLE:
        raise ImportError("fpdf2 not installed. Run: pip install fpdf2")
    
    pdf = FinancialReportPDF()
    pdf.add_page()
    
    # ========== EXECUTIVE SUMMARY ==========
    pdf.section_title("Executive Summary")
    pdf.set_font('Helvetica', '', 10)
    
    risk_label = recommendation['risk_profile']['label']
    risk_score = recommendation['risk_profile']['score']
    
    summary = (
        f"Based on your financial profile, you have been categorized as a {risk_label} investor "
        f"with a risk score of {risk_score}/100. This report provides personalized investment "
        f"recommendations tailored to your goals, time horizon, and risk tolerance."
    )
    pdf.multi_cell(0, 6, summary)
    pdf.ln(5)
    
    # ========== USER PROFILE ==========
    pdf.section_title("Your Financial Profile")
    
    pdf.section_subtitle("Demographics")
    pdf.key_value("Age", str(profile.get('age', 'N/A')))
    pdf.key_value("Annual Income", f"${profile.get('income', 0):,.0f}")
    pdf.key_value("Current Savings", f"${profile.get('savings', 0):,.0f}")
    pdf.key_value("Investment Horizon", f"{profile.get('investment_horizon_years', 'N/A')} years")
    pdf.key_value("Stated Risk Tolerance", profile.get('risk_tolerance', 'N/A'))
    pdf.ln(3)
    
    pdf.section_subtitle("Financial Goals")
    goals = profile.get('financial_goals', [])
    if goals:
        pdf.add_bullet_list(goals)
    else:
        pdf.set_font('Helvetica', 'I', 10)
        pdf.cell(0, 6, 'No goals specified', 0, 1)
    pdf.ln(3)
    
    pdf.section_subtitle("Current Portfolio")
    current = profile.get('current_portfolio', {})
    pdf.add_table(
        ['Asset Class', 'Current Allocation'],
        [
            ['Stocks', f"{current.get('stocks', 0)}%"],
            ['Bonds', f"{current.get('bonds', 0)}%"],
            ['Cash', f"{current.get('cash', 0)}%"],
        ]
    )
    pdf.ln(5)
    
    # ========== RISK ASSESSMENT ==========
    pdf.section_title("Risk Assessment")
    
    pdf.key_value("Calculated Risk Score", f"{risk_score}/100", bold_value=True)
    pdf.key_value("Risk Profile Category", risk_label, bold_value=True)
    pdf.ln(3)
    
    # Risk score visualization (text-based)
    pdf.set_font('Helvetica', '', 10)
    pdf.cell(0, 6, 'Risk Spectrum:', 0, 1)
    
    # Simple text-based risk bar
    pdf.set_font('Courier', '', 8)
    bar_length = 50
    filled = int((risk_score / 100) * bar_length)
    bar = '[' + '=' * filled + '-' * (bar_length - filled) + ']'
    pdf.cell(0, 5, f'Conservative {bar} Aggressive', 0, 1, 'C')
    pdf.ln(5)
    
    # ========== RECOMMENDATIONS ==========
    pdf.section_title("Investment Recommendations")
    
    pdf.section_subtitle("Target Portfolio Allocation")
    target = recommendation.get('target_allocation', {})
    pdf.add_table(
        ['Asset Class', 'Target %', 'Current %', 'Change Needed'],
        [
            ['Stocks', f"{target.get('stocks', 0)}%", f"{current.get('stocks', 0)}%", 
             f"{recommendation['allocation_gaps'].get('stocks', 0):+.0f}%"],
            ['Bonds', f"{target.get('bonds', 0)}%", f"{current.get('bonds', 0)}%",
             f"{recommendation['allocation_gaps'].get('bonds', 0):+.0f}%"],
            ['Cash', f"{target.get('cash', 0)}%", f"{current.get('cash', 0)}%",
             f"{recommendation['allocation_gaps'].get('cash', 0):+.0f}%"],
        ]
    )
    pdf.ln(5)
    
    # Sectors
    sectors = recommendation.get('suggested_sectors', [])
    if sectors:
        pdf.section_subtitle("Recommended Sectors")
        pdf.add_bullet_list(sectors)
        pdf.ln(3)
    
    # ========== ACTION PLAN ==========
    pdf.section_title("Your Action Plan")
    
    actions = recommendation.get('action_plan', [])
    if actions:
        for i, action in enumerate(actions, 1):
            pdf.set_font('Helvetica', 'B', 10)
            pdf.cell(10, 7, f"{i}.", 0, 0)
            pdf.set_font('Helvetica', '', 10)
            pdf.multi_cell(0, 7, action)
    else:
        pdf.set_font('Helvetica', 'I', 10)
        pdf.cell(0, 6, 'No specific actions recommended at this time.', 0, 1)
    
    pdf.ln(5)
    
    # ========== NEXT STEPS ==========
    pdf.section_title("Next Steps")
    
    next_steps = [
        "Review this report and consider how recommendations align with your personal situation",
        "Consult with a licensed financial advisor before making major investment changes",
        "Set up automatic contributions to maintain your target allocation",
        "Review and rebalance your portfolio quarterly or when allocation drifts >5%",
        "Update your profile in the app if your circumstances change significantly"
    ]
    pdf.add_bullet_list(next_steps)
    
    # Session info
    if session_name:
        pdf.ln(10)
        pdf.set_font('Helvetica', 'I', 8)
        pdf.set_text_color(128, 128, 128)
        pdf.cell(0, 5, f'Session: {session_name}', 0, 1, 'C')
    
    # Return PDF as bytes
    return pdf.output()


def render_pdf_export_button(profile: Dict[str, Any], recommendation: Dict[str, Any],
                              session_name: Optional[str] = None) -> None:
    """
    Render a PDF export button in Streamlit.
    
    Args:
        profile: User profile data
        recommendation: Generated recommendations
        session_name: Optional session name for filename
    """
    if not FPDF_AVAILABLE:
        st.warning("PDF export requires fpdf2. Run: `pip install fpdf2`")
        return
    
    st.subheader("📄 Export Report")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.write("Download a comprehensive PDF report with your profile and recommendations.")
    
    with col2:
        try:
            pdf_bytes = generate_financial_report(profile, recommendation, session_name)
            
            filename = f"financial_report_{session_name or 'advisor'}_{datetime.now().strftime('%Y%m%d')}.pdf"
            
            st.download_button(
                label="📥 Download PDF",
                data=pdf_bytes,
                file_name=filename,
                mime="application/pdf",
                use_container_width=True
            )
        except Exception as e:
            st.error(f"Error generating PDF: {e}")


def render_export_section(profile: Dict[str, Any], recommendation: Dict[str, Any],
                          session_name: Optional[str] = None) -> None:
    """
    Render complete export section with multiple format options.
    """
    st.divider()
    st.header("📤 Export Your Data")
    
    tab1, tab2 = st.tabs(["📄 PDF Report", "📋 JSON Data"])
    
    with tab1:
        render_pdf_export_button(profile, recommendation, session_name)
    
    with tab2:
        import json
        
        st.write("Export raw data as JSON for use in other applications.")
        
        export_data = {
            "generated_at": datetime.now().isoformat(),
            "session_name": session_name,
            "profile": profile,
            "recommendation": recommendation
        }
        
        json_str = json.dumps(export_data, indent=2)
        
        st.download_button(
            label="📥 Download JSON",
            data=json_str,
            file_name=f"financial_data_{session_name or 'advisor'}_{datetime.now().strftime('%Y%m%d')}.json",
            mime="application/json"
        )
        
        with st.expander("Preview JSON"):
            st.json(export_data)


