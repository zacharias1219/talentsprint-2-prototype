"""
Main Streamlit application.

AI-Powered Financial Advisor chat interface with personalized recommendations.
Features: Persistent profiles, chat memory, suggested prompts.
"""

import os
import sys
import json
import streamlit as st
from pathlib import Path
from datetime import datetime

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    project_root = Path(__file__).parent.parent
    load_dotenv(project_root / ".env")
except ImportError:
    pass  # dotenv not installed, continue without it

# Add scripts directory to path for imports
project_root = Path(__file__).parent.parent
scripts_path = project_root / "scripts"
sys.path.insert(0, str(scripts_path))

# Import inference class and personalization engine
from inference import FinancialAdvisorInference
from personalization_engine import PersonalizationEngine

# ============================================================================
# CONFIGURATION
# ============================================================================

# Directory for persisting user data
USER_DATA_DIR = project_root / "data" / "user_sessions"
USER_DATA_DIR.mkdir(parents=True, exist_ok=True)

# Suggested prompts for users
SUGGESTED_PROMPTS = [
    "Should I invest in ETFs or mutual funds?",
    "What do you think about Apple stock?",
    "How should I rebalance my portfolio?",
    "Is $NVDA a good investment right now?",
    "Compare Tesla vs Microsoft for my portfolio",
    "What's the current price of SPY?",
    "How can I save more for retirement?",
    "What sectors should I focus on given my goals?",
]

# Number of previous messages to include in context
CHAT_MEMORY_SIZE = 6  # Last 3 exchanges (user + assistant)

# ============================================================================
# PAGE CONFIG
# ============================================================================

st.set_page_config(
    page_title="AI Financial Advisor",
    page_icon="💰",
    layout="wide",
)

# ============================================================================
# PERSISTENCE FUNCTIONS (WITH ENCRYPTION)
# ============================================================================

# Try to import encryption module (graceful fallback if not available)
try:
    sys.path.insert(0, str(project_root / "src"))
    from security.encryption import ProfileEncryptor, get_encryptor
    ENCRYPTION_AVAILABLE = True
except ImportError:
    ENCRYPTION_AVAILABLE = False
    print("[Security] Encryption module not available. Using unencrypted storage.")


def get_session_file_path(session_id: str, encrypted: bool = True) -> Path:
    """Get the file path for a user session."""
    if encrypted and ENCRYPTION_AVAILABLE:
        return USER_DATA_DIR / f"{session_id}.encrypted"
    return USER_DATA_DIR / f"{session_id}.json"


def save_user_session(session_id: str, data: dict) -> None:
    """Save user session data to disk (encrypted if available)."""
    data["last_updated"] = datetime.now().isoformat()
    
    if ENCRYPTION_AVAILABLE:
        try:
            encryptor = get_encryptor()
            file_path = get_session_file_path(session_id, encrypted=True)
            encrypted_data = encryptor.encrypt_data(data)
            file_path.write_bytes(encrypted_data)
            return
        except Exception as e:
            print(f"[Security] Encryption failed, falling back to plain: {e}")
    
    # Fallback to unencrypted
    file_path = get_session_file_path(session_id, encrypted=False)
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=2)


def load_user_session(session_id: str) -> dict:
    """Load user session data from disk (decrypting if necessary)."""
    
    # Try encrypted file first
    if ENCRYPTION_AVAILABLE:
        encrypted_path = get_session_file_path(session_id, encrypted=True)
        if encrypted_path.exists():
            try:
                encryptor = get_encryptor()
                encrypted_data = encrypted_path.read_bytes()
                return encryptor.decrypt_data(encrypted_data)
            except Exception as e:
                print(f"[Security] Decryption failed: {e}")
    
    # Fallback to unencrypted file
    plain_path = get_session_file_path(session_id, encrypted=False)
    if plain_path.exists():
        try:
            with open(plain_path, 'r') as f:
                data = json.load(f)
            
            # Auto-migrate to encrypted if possible
            if ENCRYPTION_AVAILABLE:
                save_user_session(session_id, data)
                plain_path.unlink()  # Remove unencrypted version
                print(f"[Security] Migrated {session_id} to encrypted storage")
            
            return data
        except:
            return {}
    
    return {}


def list_saved_sessions() -> list:
    """List all saved session IDs (both encrypted and plain)."""
    sessions = set()
    
    # Find encrypted sessions
    for f in USER_DATA_DIR.glob("*.encrypted"):
        sessions.add(f.stem)
    
    # Find plain sessions (for migration)
    for f in USER_DATA_DIR.glob("*.json"):
        sessions.add(f.stem)
    
    return sorted(list(sessions))

# ============================================================================
# MODEL LOADING (CACHED)
# ============================================================================

@st.cache_resource
def load_inference_model():
    """Load the fine-tuned model (cached to avoid reloading)."""
    model_path = project_root / "models" / "fine_tuned" / "financial_advisor"
    return FinancialAdvisorInference(
        model_path=str(model_path),
        base_model="TinyLlama/TinyLlama-1.1B-Chat-v1.0"
    )


@st.cache_resource
def load_personalization_engine():
    """Load the personalization engine."""
    return PersonalizationEngine()

# ============================================================================
# SESSION STATE INITIALIZATION
# ============================================================================

def init_session_state():
    """Initialize all session state variables."""
    # Authentication state
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if "current_user" not in st.session_state:
        st.session_state.current_user = None
    
    # Only load heavy resources if authenticated
    if st.session_state.authenticated:
        if "advisor" not in st.session_state:
            with st.spinner("Loading AI model..."):
                st.session_state.advisor = load_inference_model()
        
        if "engine" not in st.session_state:
            st.session_state.engine = load_personalization_engine()
    
    if "session_id" not in st.session_state:
        st.session_state.session_id = None
    
    if "user_profile" not in st.session_state:
        st.session_state.user_profile = None
    
    if "user_recommendation" not in st.session_state:
        st.session_state.user_recommendation = None
    
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    if "pending_prompt" not in st.session_state:
        st.session_state.pending_prompt = None


init_session_state()

# ============================================================================
# CHAT MEMORY - BUILD CONTEXT WITH HISTORY
# ============================================================================

def build_context_with_memory(profile: dict, rec: dict, messages: list) -> str:
    """Build context string including chat history for memory."""
    
    # Base context from profile
    context = f"""
User Profile:
- Age: {profile['age']}
- Risk Tolerance: {profile['risk_tolerance']}
- Investment Horizon: {profile['investment_horizon_years']} years
- Financial Goals: {', '.join(profile['financial_goals'])}
- Current Portfolio: Stocks {profile['current_portfolio']['stocks']}%, Bonds {profile['current_portfolio']['bonds']}%, Cash {profile['current_portfolio']['cash']}%

Risk Profile: {rec['risk_profile']['label']} (Score: {rec['risk_profile']['score']}/100)
Target Allocation: Stocks {rec['target_allocation']['stocks']}%, Bonds {rec['target_allocation']['bonds']}%, Cash {rec['target_allocation']['cash']}%
Recommended Sectors: {', '.join(rec['suggested_sectors'][:3]) if rec['suggested_sectors'] else 'None'}

Action Plan:
{chr(10).join(f'- {action}' for action in rec['action_plan'])}
"""
    
    # Add chat memory (last N messages)
    if messages:
        recent_messages = messages[-CHAT_MEMORY_SIZE:]
        if recent_messages:
            context += "\n\nRecent Conversation History:\n"
            for msg in recent_messages:
                role = "User" if msg["role"] == "user" else "Advisor"
                # Truncate long messages in history
                content = msg["content"][:200] + "..." if len(msg["content"]) > 200 else msg["content"]
                # Remove disclaimers from history
                if "---" in content:
                    content = content.split("---")[0].strip()
                context += f"{role}: {content}\n"
    
    return context

# ============================================================================
# UI COMPONENTS
# ============================================================================

def render_session_manager():
    """Render session management in sidebar."""
    st.subheader("💾 Your Sessions")
    
    # Security status indicator
    if ENCRYPTION_AVAILABLE:
        st.caption("🔒 Data encrypted at rest")
    else:
        st.caption("⚠️ Encryption not available")
    
    saved_sessions = list_saved_sessions()
    
    # Create new session or load existing
    col1, col2 = st.columns(2)
    
    with col1:
        new_name = st.text_input("Session name", placeholder="my_portfolio", label_visibility="collapsed")
    
    with col2:
        if st.button("➕ New", use_container_width=True):
            if new_name:
                st.session_state.session_id = new_name
                st.session_state.user_profile = None
                st.session_state.user_recommendation = None
                st.session_state.messages = []
                st.success(f"Created: {new_name}")
                st.rerun()
    
    # Load existing sessions
    if saved_sessions:
        selected = st.selectbox(
            "Load saved session",
            options=[""] + saved_sessions,
            format_func=lambda x: "Select a session..." if x == "" else x
        )
        
        if selected and selected != st.session_state.session_id:
            session_data = load_user_session(selected)
            if session_data:
                st.session_state.session_id = selected
                st.session_state.user_profile = session_data.get("profile")
                st.session_state.user_recommendation = session_data.get("recommendation")
                st.session_state.messages = session_data.get("messages", [])
                st.success(f"Loaded: {selected}")
                st.rerun()
    
    # Show current session
    if st.session_state.session_id:
        st.info(f"📁 Current: **{st.session_state.session_id}**")


def render_profile_input():
    """Render the user profile input form in sidebar."""
    st.header("👤 Your Profile")
    
    # Check if profile exists
    if st.session_state.user_profile:
        profile = st.session_state.user_profile
        rec = st.session_state.user_recommendation
        
        st.success("✅ Profile Created")
        st.metric("Risk Score", f"{rec['risk_profile']['score']}/100")
        st.metric("Profile Type", rec['risk_profile']['label'])
        
        if st.button("🔄 Update Profile", use_container_width=True):
            st.session_state.user_profile = None
            st.session_state.user_recommendation = None
            st.rerun()
        return
    
    # Profile input form
    with st.form("profile_form"):
        st.subheader("Demographics")
        age = st.number_input("Age", min_value=18, max_value=100, value=35)
        income = st.number_input("Annual Income ($)", min_value=0, value=75000, step=5000)
        savings = st.number_input("Current Savings ($)", min_value=0, value=25000, step=1000)
        
        st.subheader("Risk Tolerance")
        risk_tolerance = st.selectbox(
            "How would you describe your risk tolerance?",
            ["Low", "Moderate", "High", "Very High"],
            index=1
        )
        
        investment_horizon = st.slider(
            "Investment Horizon (years)",
            min_value=1,
            max_value=40,
            value=15
        )
        
        st.subheader("Financial Goals")
        goals = st.multiselect(
            "Select your financial goals",
            ["Retirement", "Home Purchase", "Wealth Generation", "Education", "Emergency Fund"],
            default=["Retirement", "Wealth Generation"]
        )
        
        st.subheader("Current Portfolio")
        col1, col2, col3 = st.columns(3)
        with col1:
            stocks_pct = st.number_input("Stocks %", 0, 100, 40)
        with col2:
            bonds_pct = st.number_input("Bonds %", 0, 100, 30)
        with col3:
            cash_pct = st.number_input("Cash %", 0, 100, 30)
        
        submitted = st.form_submit_button("🚀 Generate Recommendations", use_container_width=True)
        
        if submitted:
            total = stocks_pct + bonds_pct + cash_pct
            if total != 100:
                st.error(f"Portfolio must sum to 100% (currently {total}%)")
            else:
                profile = {
                    "user_id": st.session_state.session_id or "current_user",
                    "age": age,
                    "income": float(income),
                    "savings": float(savings),
                    "risk_tolerance": risk_tolerance,
                    "investment_horizon_years": investment_horizon,
                    "financial_goals": goals,
                    "current_portfolio": {
                        "stocks": stocks_pct,
                        "bonds": bonds_pct,
                        "cash": cash_pct
                    }
                }
                
                with st.spinner("Generating recommendations..."):
                    recommendation = st.session_state.engine.generate_recommendation(profile)
                
                st.session_state.user_profile = profile
                st.session_state.user_recommendation = recommendation
                
                # Auto-save if session exists
                if st.session_state.session_id:
                    save_user_session(st.session_state.session_id, {
                        "profile": profile,
                        "recommendation": recommendation,
                        "messages": st.session_state.messages
                    })
                
                st.success("✅ Recommendations generated!")
                st.rerun()


def render_suggested_prompts():
    """Render clickable suggested prompts."""
    st.markdown("**💡 Try asking:**")
    
    cols = st.columns(2)
    for i, prompt in enumerate(SUGGESTED_PROMPTS):
        col = cols[i % 2]
        with col:
            if st.button(f"📝 {prompt[:35]}...", key=f"prompt_{i}", use_container_width=True):
                st.session_state.pending_prompt = prompt
                st.rerun()


def render_chat_tab():
    """Render the chat interface tab."""
    from components.chat_interface import render_chat_history
    
    st.header("💬 Chat with your Financial Advisor")
    
    if not st.session_state.user_profile:
        st.warning("👈 Please create or select a session in the sidebar first to get personalized advice.")
        
        # Show suggested prompts anyway for preview
        st.divider()
        st.caption("Once you create a profile, you can ask questions like:")
        for prompt in SUGGESTED_PROMPTS[:3]:
            st.markdown(f"- *{prompt}*")
        return
    
    # Show suggested prompts
    with st.expander("💡 Suggested Questions", expanded=len(st.session_state.messages) == 0):
        render_suggested_prompts()
    
    st.divider()
    
    # Toggle for showing context
    show_context = st.checkbox("Show context used in responses", value=False)
    
    # Display chat history
    render_chat_history(st.session_state.messages, show_context=show_context)
    
    # Handle pending prompt from button click
    prompt = st.session_state.pending_prompt
    st.session_state.pending_prompt = None
    
    # Chat input
    if not prompt:
        prompt = st.chat_input("Ask me about your finances...")
    
    if prompt:
        # Import stock price detection
        from components.stock_price_card import detect_stock_symbols, get_stock_context_for_chat, render_stock_card
        
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Generate response
        with st.chat_message("assistant"):
            placeholder = st.empty()
            placeholder.markdown("💭 *Thinking...*")
            
            try:
                profile = st.session_state.user_profile
                rec = st.session_state.user_recommendation
                
                # Detect stock symbols in query
                detected_symbols = detect_stock_symbols(prompt)
                stock_context = ""
                stock_quotes = []
                
                if detected_symbols:
                    placeholder.markdown("📊 *Fetching live market data...*")
                    stock_context, stock_quotes, rate_status = get_stock_context_for_chat(detected_symbols)
                    if rate_status and "Rate limit" in rate_status:
                        st.warning(rate_status)
                
                # Build context WITH chat memory AND stock data
                context = build_context_with_memory(
                    profile, 
                    rec, 
                    st.session_state.messages[:-1]  # Exclude current message
                )
                
                # Add stock context if available
                if stock_context:
                    context = context + "\n" + stock_context
                
                placeholder.markdown("🤖 *Generating personalized advice...*")
                response_text = st.session_state.advisor.generate_response_with_context(
                    context,
                    prompt,
                    max_length=300,
                    temperature=0.7
                )
                
                placeholder.empty()
                
                # Display stock price cards if detected
                if stock_quotes:
                    st.markdown("**📊 Live Market Data:**")
                    for quote in stock_quotes:
                        render_stock_card(quote)
                    st.divider()
                
                # Add compliance disclaimer
                disclaimer = "\n\n---\n*⚠️ This is AI-generated content for informational purposes only. Please consult a licensed financial advisor before making investment decisions.*"
                response_text = response_text + disclaimer
                
                st.markdown(response_text)
                
                if show_context:
                    with st.expander("📊 Context Used"):
                        st.text(context)
                
                # Add to history
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": response_text,
                    "context": context if show_context else None,
                    "metadata": {
                        "model": "TinyLlama-1.1B-finetuned",
                        "temperature": 0.7,
                        "max_length": 300
                    }
                })
                
                # Auto-save conversation
                if st.session_state.session_id:
                    save_user_session(st.session_state.session_id, {
                        "profile": st.session_state.user_profile,
                        "recommendation": st.session_state.user_recommendation,
                        "messages": st.session_state.messages
                    })
                    
            except Exception as e:
                placeholder.empty()
                error_msg = f"I encountered an error: {str(e)}"
                st.error(error_msg)
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": error_msg,
                })


def render_portfolio_tab():
    """Render portfolio analysis tab."""
    from components.visualizations import (
        render_portfolio_allocation,
        render_risk_return_chart
    )
    
    st.header("📊 Your Portfolio Analysis")
    
    if not st.session_state.user_recommendation:
        st.warning("👈 Please create or select a session in the sidebar first.")
        return
    
    rec = st.session_state.user_recommendation
    profile = st.session_state.user_profile
    
    # Key Metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Risk Score", f"{rec['risk_profile']['score']}/100")
    with col2:
        st.metric("Profile Type", rec['risk_profile']['label'])
    with col3:
        st.metric("Horizon", f"{profile['investment_horizon_years']} years")
    with col4:
        st.metric("Goals", f"{len(profile['financial_goals'])} active")
    
    st.divider()
    
    # Charts
    col1, col2 = st.columns(2)
    with col1:
        render_portfolio_allocation(rec)
    with col2:
        render_risk_return_chart(rec)
    
    st.divider()
    
    # Current vs Target
    st.subheader("📈 Current vs Target Allocation")
    
    current = profile['current_portfolio']
    target = rec['target_allocation']
    gaps = rec['allocation_gaps']
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        delta = gaps['stocks']
        st.metric(
            "Stocks", 
            f"{target['stocks']}% target",
            delta=f"{'+' if delta > 0 else ''}{delta}%",
            delta_color="normal" if delta >= 0 else "inverse"
        )
        st.caption(f"Current: {current['stocks']}%")
    
    with col2:
        delta = gaps['bonds']
        st.metric(
            "Bonds",
            f"{target['bonds']}% target",
            delta=f"{'+' if delta > 0 else ''}{delta}%",
            delta_color="normal" if delta >= 0 else "inverse"
        )
        st.caption(f"Current: {current['bonds']}%")
    
    with col3:
        delta = gaps['cash']
        st.metric(
            "Cash",
            f"{target['cash']}% target",
            delta=f"{'+' if delta > 0 else ''}{delta}%",
            delta_color="inverse" if delta > 0 else "normal"
        )
        st.caption(f"Current: {current['cash']}%")
    
    st.divider()
    
    # Sectors
    if rec['suggested_sectors']:
        st.subheader("🏢 Recommended Sectors")
        cols = st.columns(min(len(rec['suggested_sectors']), 5))
        for i, sector in enumerate(rec['suggested_sectors'][:5]):
            with cols[i]:
                st.info(f"**{sector}**")
    
    st.divider()
    
    # Action Plan
    st.subheader("✅ Your Action Plan")
    for i, action in enumerate(rec['action_plan'], 1):
        st.markdown(f"**{i}.** {action}")


def render_profile_summary_tab():
    """Render comprehensive profile summary with mathematical calculations."""
    st.header("👤 Your Complete Profile")
    
    if not st.session_state.user_profile:
        st.warning("👈 Please create or select a session in the sidebar first.")
        return
    
    profile = st.session_state.user_profile
    rec = st.session_state.user_recommendation
    
    if not rec:
        st.warning("Recommendations not available. Please generate recommendations first.")
        return
    
    # Overview Metrics
    st.subheader("📊 Profile Overview")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Age", f"{profile['age']}")
    with col2:
        st.metric("Annual Income", f"${profile['income']:,.0f}")
    with col3:
        st.metric("Current Savings", f"${profile['savings']:,.0f}")
    with col4:
        savings_rate = (profile['savings'] / profile['income']) * 100 if profile['income'] > 0 else 0
        st.metric("Savings Rate", f"{savings_rate:.1f}%", help="Savings as % of income")
    
    st.divider()
    
    # Main Content
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📋 Personal Details")
        
        details_data = {
            "Age": profile['age'],
            "Annual Income": f"${profile['income']:,.0f}",
            "Current Savings": f"${profile['savings']:,.0f}",
            "Risk Tolerance": profile['risk_tolerance'],
            "Investment Horizon": f"{profile['investment_horizon_years']} years",
        }
        
        for key, value in details_data.items():
            st.write(f"**{key}:** {value}")
        
        # Financial calculations
        st.subheader("💰 Financial Metrics")
        
        # Calculate emergency fund adequacy (6 months expenses)
        monthly_expenses = profile['income'] / 12 * 0.7  # Assume 70% of income is expenses
        emergency_fund_target = monthly_expenses * 6
        emergency_fund_ratio = (profile['savings'] / emergency_fund_target) * 100 if emergency_fund_target > 0 else 0
        
        st.metric(
            "Emergency Fund",
            f"${profile['savings']:,.0f}",
            delta=f"{emergency_fund_ratio:.0f}% of 6-month target",
            delta_color="normal" if emergency_fund_ratio >= 100 else "inverse",
            help="Target: 6 months of expenses"
        )
        
        # Calculate investable assets
        investable_assets = profile['savings'] * 0.8  # Assume 80% is investable (20% emergency fund)
        st.metric(
            "Estimated Investable",
            f"${investable_assets:,.0f}",
            help="Assuming 80% of savings is investable"
        )
        
        st.subheader("🎯 Financial Goals")
        if profile.get('financial_goals'):
            for i, goal in enumerate(profile['financial_goals'], 1):
                st.write(f"{i}. {goal}")
        else:
            st.info("No specific goals set")
    
    with col2:
        st.subheader("📊 Risk Assessment")
        
        score = rec['risk_profile']['score']
        label = rec['risk_profile']['label']
        
        # Risk score visualization
        st.progress(score / 100)
        st.metric("Risk Score", f"{score}/100", help="Calculated based on age, income, goals, and risk tolerance")
        st.metric("Risk Profile", label)
        
        # Risk level indicator
        risk_colors = {
            "Conservative": "#4CAF50",
            "Moderate": "#FFC107",
            "Aggressive": "#FF9800",
            "Very Aggressive": "#F44336"
        }
        risk_color = risk_colors.get(label, "#888")
        st.markdown(f"""
        <div style="
            background: {risk_color}22;
            border-left: 4px solid {risk_color};
            padding: 12px;
            border-radius: 4px;
            margin: 8px 0;
        ">
            <strong>Risk Level:</strong> {label}<br>
            <small>This profile is suitable for {label.lower()} investors</small>
        </div>
        """, unsafe_allow_html=True)
        
        st.subheader("💼 Portfolio Allocation")
        
        # Current vs Target comparison
        current = profile.get('current_portfolio', {})
        target = rec.get('target_allocation', {})
        gaps = rec.get('allocation_gaps', {})
        
        # Calculate total allocation to ensure it sums to 100%
        current_total = sum(current.values())
        target_total = sum(target.values())
        
        if current_total != 100 and current_total > 0:
            st.warning(f"⚠️ Current allocation sums to {current_total}% (should be 100%)")
        if target_total != 100 and target_total > 0:
            st.warning(f"⚠️ Target allocation sums to {target_total}% (should be 100%)")
        
        # Display allocation with gaps
        allocation_data = []
        for asset in ['stocks', 'bonds', 'cash']:
            current_val = current.get(asset, 0)
            target_val = target.get(asset, 0)
            gap = gaps.get(asset, 0)
            
            col_a, col_b, col_c = st.columns([2, 1, 1])
            with col_a:
                st.write(f"**{asset.capitalize()}**")
            with col_b:
                st.metric("", f"{current_val}%", delta=f"{gap:+.1f}%", label_visibility="collapsed")
            with col_c:
                st.caption(f"Target: {target_val}%")
    
    st.divider()
    
    # Allocation Visualization
    st.subheader("📈 Allocation Comparison")
    
    from components.visualizations import render_allocation_comparison
    render_allocation_comparison(rec, profile)
    
    st.divider()
    
    # Action Plan
    if rec.get('action_plan'):
        st.subheader("📋 Recommended Action Plan")
        action_plan = rec['action_plan']
        for i, action in enumerate(action_plan, 1):
            st.write(f"**{i}.** {action}")
    
    # Suggested Sectors
    if rec.get('suggested_sectors'):
        st.subheader("🏢 Recommended Sectors")
        sectors = rec['suggested_sectors']
        st.write(", ".join(sectors))
    
    st.divider()
    
    # Mathematical Summary
    with st.expander("📐 Portfolio Mathematics"):
        st.markdown("""
        ### **Allocation Calculations:**
        
        **Current Portfolio:**
        - Stocks: {stocks_c}% × Expected Return: 10% = {stocks_c * 0.10:.2f}% contribution
        - Bonds: {bonds_c}% × Expected Return: 5% = {bonds_c * 0.05:.2f}% contribution
        - Cash: {cash_c}% × Expected Return: 3% = {cash_c * 0.03:.2f}% contribution
        - **Weighted Expected Return:** {expected_current:.2f}%
        
        **Target Portfolio:**
        - Stocks: {stocks_t}% × Expected Return: 10% = {stocks_t * 0.10:.2f}% contribution
        - Bonds: {bonds_t}% × Expected Return: 5% = {bonds_t * 0.05:.2f}% contribution
        - Cash: {cash_t}% × Expected Return: 3% = {cash_t * 0.03:.2f}% contribution
        - **Weighted Expected Return:** {expected_target:.2f}%
        
        **Expected Improvement:** {improvement:+.2f}% annual return
        
        Formula: Weighted Return = Σ(Allocation% × Asset Return%)
        """.format(
            stocks_c=current.get('stocks', 0),
            bonds_c=current.get('bonds', 0),
            cash_c=current.get('cash', 0),
            stocks_t=target.get('stocks', 0),
            bonds_t=target.get('bonds', 0),
            cash_t=target.get('cash', 0),
            expected_current=(current.get('stocks', 0) * 0.10 + current.get('bonds', 0) * 0.05 + current.get('cash', 0) * 0.03),
            expected_target=(target.get('stocks', 0) * 0.10 + target.get('bonds', 0) * 0.05 + target.get('cash', 0) * 0.03),
            improvement=(target.get('stocks', 0) * 0.10 + target.get('bonds', 0) * 0.05 + target.get('cash', 0) * 0.03) - (current.get('stocks', 0) * 0.10 + current.get('bonds', 0) * 0.05 + current.get('cash', 0) * 0.03)
        ))
    
    # Session info
    if st.session_state.session_id:
        st.divider()
        st.subheader("💾 Session Information")
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**Session ID:** `{st.session_state.session_id}`")
            st.write(f"**Messages:** {len(st.session_state.messages)}")
        with col2:
            session_data = load_user_session(st.session_state.session_id)
            if session_data.get("last_updated"):
                from datetime import datetime
                last_updated = session_data['last_updated']
                if isinstance(last_updated, str):
                    try:
                        dt = datetime.fromisoformat(last_updated.replace('Z', '+00:00'))
                        st.write(f"**Last Saved:** {dt.strftime('%Y-%m-%d %H:%M:%S')}")
                    except:
                        st.write(f"**Last Saved:** {last_updated}")
                else:
                    st.write(f"**Last Saved:** {last_updated}")
    
    st.divider()
    
    # Full Data View
    with st.expander("🔍 View Raw Data"):
        tab1, tab2 = st.tabs(["Profile", "Recommendations"])
        with tab1:
            st.json(profile)
        with tab2:
            st.json(rec)


# ============================================================================
# MAIN APP
# ============================================================================

def main():
    """Main application function."""
    # Import auth component
    from components.auth import render_login_signup
    
    # Check authentication - show login/signup if not authenticated
    if not st.session_state.authenticated:
        render_login_signup()
        return
    
    # Main app content (only shown if authenticated)
    st.title("💰 AI-Powered Financial Advisor")
    st.caption(f"Welcome back, **{st.session_state.current_user['username']}**! Get personalized investment advice based on your unique financial profile")
    
    # Import components at top to avoid repeated imports
    from components.portfolio_tracker import render_portfolio_tracker
    from components.goal_calculator import render_goal_calculator
    from components.benchmark_comparison import render_benchmark_comparison
    from components.data_export import render_export_section as render_data_export
    from components.investment_recommendations import render_investment_recommendations
    from components.info_section import render_info_section
    
    # Load user's session data if session_id matches username and data not loaded
    if st.session_state.session_id and st.session_state.current_user:
        if st.session_state.session_id == st.session_state.current_user["username"]:
            if st.session_state.user_profile is None:
                # Try to load saved session
                session_data = load_user_session(st.session_state.session_id)
                if session_data:
                    st.session_state.user_profile = session_data.get("profile")
                    st.session_state.user_recommendation = session_data.get("recommendation")
                    st.session_state.messages = session_data.get("messages", [])
    
    # Sidebar - Navigation + Session + Profile
    with st.sidebar:
        # User info at top
        st.info(f"👤 **{st.session_state.current_user['username']}**")
        
        # Logout button
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.authenticated = False
            st.session_state.current_user = None
            st.session_state.session_id = None
            st.session_state.user_profile = None
            st.session_state.user_recommendation = None
            st.session_state.messages = []
            st.rerun()
        
        st.divider()
        st.header("🧭 Navigation")
        page = st.radio(
            "Select Page",
            options=[
                "💬 Chat", 
                "📊 Portfolio", 
                "💼 Invest", 
                "📈 Performance",
                "⚖️ Compare", 
                "🎯 Goals", 
                "👤 Profile",
                "📚 Info"
            ],
            label_visibility="collapsed",
            key="page_nav"
        )
        
        st.divider()
        render_session_manager()
        st.divider()
        render_profile_input()
        
        # Clear conversation button
        if st.session_state.messages:
            st.divider()
            if st.button("🗑️ Clear Conversation", use_container_width=True):
                st.session_state.messages = []
                if st.session_state.session_id:
                    save_user_session(st.session_state.session_id, {
                        "profile": st.session_state.user_profile,
                        "recommendation": st.session_state.user_recommendation,
                        "messages": []
                    })
                st.rerun()
    
    # Main content - only render selected page (fixes duplicate tabs issue)
    if page == "💬 Chat":
        render_chat_tab()
    
    elif page == "📊 Portfolio":
        render_portfolio_tab()
    
    elif page == "💼 Invest":
        render_investment_recommendations(
            st.session_state.user_profile,
            st.session_state.user_recommendation
        )
    
    elif page == "📈 Performance":
        render_portfolio_tracker(
            st.session_state.session_id,
            st.session_state.user_profile,
            st.session_state.user_recommendation
        )
    
    elif page == "⚖️ Compare":
        render_benchmark_comparison(
            st.session_state.user_profile,
            st.session_state.user_recommendation
        )
    
    elif page == "🎯 Goals":
        render_goal_calculator()
    
    elif page == "👤 Profile":
        render_profile_summary_tab()
        st.divider()
        render_data_export(
            st.session_state.user_profile,
            st.session_state.user_recommendation
        )
    
    elif page == "📚 Info":
        render_info_section()


if __name__ == "__main__":
    main()
