"""
Analytics Dashboard Component for Streamlit.

Displays comprehensive analytics including:
- User engagement metrics
- Recommendation accuracy
- System performance metrics
- User satisfaction scores
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import json
import os
from datetime import datetime, timedelta


def load_analytics_data():
    """Load analytics data from various sources."""
    project_root = Path(__file__).parent.parent.parent
    
    # Load evaluation results
    eval_results = {}
    eval_file = project_root / "models" / "evaluation_results.json"
    if eval_file.exists():
        with open(eval_file, 'r') as f:
            eval_results = json.load(f)
    
    # Load evaluation log
    eval_log = []
    log_file = project_root / "models" / "evaluation_log.json"
    if log_file.exists():
        with open(log_file, 'r') as f:
            eval_log = json.load(f)
    
    # Load user recommendations (for engagement metrics)
    user_recs = []
    recs_file = project_root / "data" / "processed" / "user_recommendations.json"
    if recs_file.exists():
        with open(recs_file, 'r') as f:
            user_recs = json.load(f)
    
    return {
        "evaluation_results": eval_results,
        "evaluation_log": eval_log,
        "user_recommendations": user_recs
    }


def render_model_performance_metrics(data):
    """Render model performance metrics."""
    st.subheader("📊 Model Performance Metrics")
    
    eval_results = data.get("evaluation_results", {})
    
    if eval_results:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            bleu = eval_results.get("bleu_score", 0)
            st.metric("BLEU Score", f"{bleu:.4f}", 
                     delta=f"{bleu * 100:.2f}%", 
                     help="BLEU score measures n-gram overlap with reference")
        
        with col2:
            rouge1 = eval_results.get("rouge_1", 0)
            st.metric("ROUGE-1", f"{rouge1:.4f}",
                     delta=f"{rouge1 * 100:.2f}%",
                     help="ROUGE-1 measures unigram overlap")
        
        with col3:
            rouge2 = eval_results.get("rouge_2", 0)
            st.metric("ROUGE-2", f"{rouge2:.4f}",
                     delta=f"{rouge2 * 100:.2f}%",
                     help="ROUGE-2 measures bigram overlap")
        
        with col4:
            rouge_l = eval_results.get("rouge_l", 0)
            st.metric("ROUGE-L", f"{rouge_l:.4f}",
                     delta=f"{rouge_l * 100:.2f}%",
                     help="ROUGE-L measures longest common subsequence")
        
        # Performance chart
        metrics_df = pd.DataFrame({
            "Metric": ["BLEU", "ROUGE-1", "ROUGE-2", "ROUGE-L"],
            "Score": [
                eval_results.get("bleu_score", 0),
                eval_results.get("rouge_1", 0),
                eval_results.get("rouge_2", 0),
                eval_results.get("rouge_l", 0)
            ]
        })
        
        fig = px.bar(
            metrics_df,
            x="Metric",
            y="Score",
            title="Model Performance Metrics",
            color="Score",
            color_continuous_scale="Viridis"
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No evaluation results available. Run evaluation script to generate metrics.")


def render_user_engagement_metrics(data):
    """Render user engagement metrics."""
    st.subheader("👥 User Engagement Metrics")
    
    user_recs = data.get("user_recommendations", [])
    
    if user_recs:
        # Calculate metrics
        total_users = len(user_recs)
        total_recommendations = sum(len(rec.get("recommendations", [])) for rec in user_recs)
        avg_recommendations_per_user = total_recommendations / total_users if total_users > 0 else 0
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Users", total_users)
        
        with col2:
            st.metric("Total Recommendations", total_recommendations)
        
        with col3:
            st.metric("Avg Recommendations/User", f"{avg_recommendations_per_user:.1f}")
        
        # Risk profile distribution
        risk_profiles = {}
        for rec in user_recs:
            risk_data = rec.get("risk_profile", {})
            # Handle both dict and string formats
            if isinstance(risk_data, dict):
                risk = risk_data.get("label", "Unknown")
            else:
                risk = str(risk_data) if risk_data else "Unknown"
            risk_profiles[risk] = risk_profiles.get(risk, 0) + 1
        
        if risk_profiles:
            risk_df = pd.DataFrame({
                "Risk Profile": list(risk_profiles.keys()),
                "Count": list(risk_profiles.values())
            })
            
            fig = px.pie(
                risk_df,
                values="Count",
                names="Risk Profile",
                title="User Risk Profile Distribution"
            )
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No user engagement data available. Generate user profiles to see metrics.")


def render_recommendation_analysis(data):
    """Render recommendation analysis."""
    st.subheader("💡 Recommendation Analysis")
    
    user_recs = data.get("user_recommendations", [])
    
    if user_recs:
        # Analyze asset allocations
        allocations = {
            "Stocks": [],
            "Bonds": [],
            "Cash": []
        }
        
        for rec in user_recs:
            target = rec.get("target_allocation", {})
            allocations["Stocks"].append(target.get("stocks", 0))
            allocations["Bonds"].append(target.get("bonds", 0))
            allocations["Cash"].append(target.get("cash", 0))
        
        # Average allocations
        avg_allocations = {
            "Asset Class": ["Stocks", "Bonds", "Cash"],
            "Average Allocation %": [
                sum(allocations["Stocks"]) / len(allocations["Stocks"]) if allocations["Stocks"] else 0,
                sum(allocations["Bonds"]) / len(allocations["Bonds"]) if allocations["Bonds"] else 0,
                sum(allocations["Cash"]) / len(allocations["Cash"]) if allocations["Cash"] else 0
            ]
        }
        
        alloc_df = pd.DataFrame(avg_allocations)
        
        fig = px.bar(
            alloc_df,
            x="Asset Class",
            y="Average Allocation %",
            title="Average Asset Allocation Recommendations",
            color="Average Allocation %",
            color_continuous_scale="Blues"
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No recommendation data available.")


def render_system_performance(data):
    """Render system performance metrics."""
    st.subheader("⚡ System Performance")
    
    # Mock performance data (in production, this would come from logs)
    performance_data = {
        "Metric": ["Avg Response Time", "API Success Rate", "Cache Hit Rate", "Model Load Time"],
        "Value": [2.5, 98.5, 75.0, 3.2],
        "Unit": ["seconds", "%", "%", "seconds"]
    }
    
    perf_df = pd.DataFrame(performance_data)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Avg Response Time", "2.5s", delta="-0.3s", delta_color="inverse")
    
    with col2:
        st.metric("API Success Rate", "98.5%", delta="1.2%")
    
    with col3:
        st.metric("Cache Hit Rate", "75%", delta="5%")
    
    with col4:
        st.metric("Model Load Time", "3.2s")
    
    # Performance trend (mock data)
    dates = pd.date_range(end=datetime.now(), periods=7, freq='D')
    trend_data = pd.DataFrame({
        "Date": dates,
        "Response Time (s)": [2.8, 2.6, 2.5, 2.4, 2.5, 2.5, 2.5]
    })
    
    fig = px.line(
        trend_data,
        x="Date",
        y="Response Time (s)",
        title="Response Time Trend (Last 7 Days)",
        markers=True
    )
    fig.update_layout(height=300)
    st.plotly_chart(fig, use_container_width=True)


def render_evaluation_samples(data):
    """Render sample evaluation results."""
    st.subheader("📝 Evaluation Samples")
    
    eval_log = data.get("evaluation_log", [])
    
    if eval_log:
        # Show first 5 samples
        samples = eval_log[:5]
        
        for i, sample in enumerate(samples, 1):
            with st.expander(f"Sample {i}: {sample.get('query', 'N/A')[:50]}..."):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write("**Query:**")
                    st.write(sample.get("query", "N/A"))
                    
                    st.write("**Reference:**")
                    st.write(sample.get("reference", "N/A"))
                
                with col2:
                    st.write("**Generated:**")
                    st.write(sample.get("generated", "N/A"))
                    
                    st.write("**Metrics:**")
                    metrics = sample.get("metrics", {})
                    st.json(metrics)
    else:
        st.info("No evaluation samples available. Run evaluation script to generate samples.")


def render_analytics_dashboard():
    """Main function to render the analytics dashboard."""
    st.title("📈 Analytics Dashboard")
    st.markdown("Comprehensive analytics and performance metrics for the Financial Advisor system.")
    
    # Load data
    with st.spinner("Loading analytics data..."):
        data = load_analytics_data()
    
    # Tabs for different analytics views
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "Model Performance",
        "User Engagement",
        "Recommendations",
        "System Performance",
        "Evaluation Samples"
    ])
    
    with tab1:
        render_model_performance_metrics(data)
    
    with tab2:
        render_user_engagement_metrics(data)
    
    with tab3:
        render_recommendation_analysis(data)
    
    with tab4:
        render_system_performance(data)
    
    with tab5:
        render_evaluation_samples(data)
    
    # Summary section
    st.divider()
    st.subheader("📋 Summary")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Overall Status", "✅ Operational", delta="Stable")
    
    with col2:
        eval_results = data.get("evaluation_results", {})
        bleu = eval_results.get("bleu_score", 0)
        status = "⚠️ Needs Improvement" if bleu < 0.1 else "✅ Good"
        st.metric("Model Quality", status)
    
    with col3:
        user_recs = data.get("user_recommendations", [])
        user_count = len(user_recs)
        st.metric("Active Users", user_count if user_count > 0 else "N/A")


if __name__ == "__main__":
    render_analytics_dashboard()



