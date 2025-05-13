#!/usr/bin/env python3
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os

# --- Page Configuration ---
st.set_page_config(
    page_title="Boxing Match Analysis",
    page_icon="🥊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Personal Information Header ---
with st.container():
    img_col, text_col = st.columns([1, 4]) 
    with img_col:
        st.image("https://www.gravatar.com/avatar/00000000000000000000000000000000?d=mp&f=y&s=150", width=100, caption="Karl Siaka") 
    with text_col:
        st.markdown("### Built with love by Karl Siaka")
        st.markdown("**Email:** siakatayoukarlwilliam@gmail.com")
        st.markdown("**Phone:** 2406608395")
    st.markdown("---    ") 

st.title("🥊 Boxing Match Statistics Analyzer")

# --- Analysis Functions ---
def calculate_match_aggregates(df_match, boxer_a, boxer_b):
    """Calculates aggregate statistics for the entire match."""
    df_agg = df_match.groupby("Boxer").agg(
        total_punches_thrown=("Punches Thrown", "sum"),
        total_punches_landed=("Punches Landed", "sum"),
        total_sig_punches_thrown=("Significant Punches Thrown", "sum"),
        total_sig_punches_landed=("Significant Punches Landed", "sum"),
        total_head_punches_landed=("Head Punches Landed", "sum"),
        total_body_punches_landed=("Body Punches Landed", "sum"),
        avg_ring_control=("Ring Control %", "mean")
    ).reset_index()

    df_agg["punch_accuracy_pct"] = (df_agg["total_punches_landed"] * 100 / df_agg["total_punches_thrown"].replace(0, 1)).round(1)
    df_agg["sig_punch_accuracy_pct"] = (df_agg["total_sig_punches_landed"] * 100 / df_agg["total_sig_punches_thrown"].replace(0, 1)).round(1)
    df_agg = df_agg.fillna(0)
    df_agg = df_agg[["Boxer", "total_punches_thrown", "total_punches_landed", "punch_accuracy_pct",
                     "total_sig_punches_thrown", "total_sig_punches_landed", "sig_punch_accuracy_pct",
                     "total_head_punches_landed", "total_body_punches_landed", "avg_ring_control"]]
    stats_a = df_agg[df_agg["Boxer"] == boxer_a].iloc[0] if not df_agg[df_agg["Boxer"] == boxer_a].empty else None
    stats_b = df_agg[df_agg["Boxer"] == boxer_b].iloc[0] if not df_agg[df_agg["Boxer"] == boxer_b].empty else None
    return stats_a, stats_b, df_agg

# --- Plotting Functions ---
def plot_round_punch_stats(df_round, boxer_a, boxer_b):
    df_plot = df_round[df_round["Boxer"].isin([boxer_a, boxer_b])]
    fig = px.bar(df_plot, x="Boxer", y=["Punches Thrown", "Punches Landed"], 
                 title=f"Round {df_round['Round'].iloc[0]}: Punches Thrown vs Landed",
                 labels={"value": "Number of Punches", "variable": "Punch Type"},
                 barmode="group", color_discrete_map={"Punches Thrown": "lightblue", "Punches Landed": "blue"})
    fig.update_layout(legend_title_text="Punch Type")
    return fig

def plot_round_sig_punches(df_round, boxer_a, boxer_b):
    df_plot = df_round[df_round["Boxer"].isin([boxer_a, boxer_b])]
    if "Head Punches Landed" not in df_plot.columns or "Body Punches Landed" not in df_plot.columns or (df_plot["Head Punches Landed"].sum() == 0 and df_plot["Body Punches Landed"].sum() == 0):
        fig = px.bar(df_plot, x="Boxer", y="Significant Punches Landed",
                     title=f"Round {df_round['Round'].iloc[0]}: Significant Punches Landed",
                     labels={"value": "Number of Punches"},
                     color_discrete_sequence=px.colors.qualitative.Pastel)
        fig.update_layout(showlegend=False)
        st.caption("Note: Head/Body punch breakdown not available for this dataset.")
        return fig
    fig = px.bar(df_plot, x="Boxer", y=["Head Punches Landed", "Body Punches Landed"], 
                 title=f"Round {df_round['Round'].iloc[0]}: Significant Punches Landed (Head vs Body)",
                 labels={"value": "Number of Punches", "variable": "Target Area"},
                 barmode="stack", color_discrete_map={"Head Punches Landed": "red", "Body Punches Landed": "darkred"})
    fig.update_layout(legend_title_text="Target Area")
    return fig

def plot_round_ring_control(df_round, boxer_a, boxer_b):
    df_plot = df_round[df_round["Boxer"].isin([boxer_a, boxer_b])]
    if "Ring Control %" not in df_plot.columns or df_plot["Ring Control %"].sum() == 0:
        fig = go.Figure()
        fig.update_layout(
            title=f"Round {df_round['Round'].iloc[0]}: Ring Control Data Not Available",
            annotations=[dict(text="Ring control data not available for this fight", showarrow=False, xref="paper", yref="paper", x=0.5, y=0.5)]
        )
        return fig
    fig = px.pie(df_plot, values="Ring Control %", names="Boxer", 
                 title=f"Round {df_round['Round'].iloc[0]}: Ring Control Percentage", hole=0.3)
    fig.update_traces(textposition="inside", textinfo="percent+label")
    return fig

def plot_total_punch_trends(df_match, boxer_a, boxer_b):
    df_plot = df_match[df_match["Boxer"].isin([boxer_a, boxer_b])]
    fig = px.line(df_plot, x="Round", y="Punches Landed", color="Boxer", 
                  title="Total Punches Landed per Round",
                  labels={"Punches Landed": "Punches Landed", "Round": "Round Number"}, markers=True)
    return fig

def plot_total_sig_punch_trends(df_match, boxer_a, boxer_b):
    df_plot = df_match[df_match["Boxer"].isin([boxer_a, boxer_b])]
    fig = px.line(df_plot, x="Round", y="Significant Punches Landed", color="Boxer", 
                  title="Significant Punches Landed per Round",
                  labels={"Significant Punches Landed": "Sig. Punches Landed", "Round": "Round Number"}, markers=True)
    return fig

def plot_total_ring_control_trends(df_match, boxer_a, boxer_b):
    if "Ring Control %" not in df_match.columns or df_match["Ring Control %"].sum() == 0:
        fig = go.Figure()
        fig.update_layout(
            title="Ring Control Percentage per Round - Data Not Available",
            annotations=[dict(text="Ring control data not available for this fight", showarrow=False, xref="paper", yref="paper", x=0.5, y=0.5)]
        )
        return fig
    df_plot = df_match[df_match["Boxer"] == boxer_a]
    fig = px.line(df_plot, x="Round", y="Ring Control %", 
                  title=f"Ring Control Percentage per Round ({boxer_a})",
                  labels={"Ring Control %": f"{boxer_a} Control %", "Round": "Round Number"}, markers=True)
    fig.update_layout(yaxis_range=[0,100])
    return fig

# --- Load Data ---
@st.cache_data
def load_data(filepath):
    try:
        base_path = os.path.dirname(__file__)
        full_path = os.path.join(base_path, filepath)
        df = pd.read_csv(full_path)
        required_cols = ["Round", "Boxer", "Punches Thrown", "Punches Landed", "Significant Punches Thrown", "Significant Punches Landed"]
        optional_cols = ["Ring Control %", "Head Punches Landed", "Body Punches Landed", "Jabs Landed", "Power Punches Landed"]
        if not all(col in df.columns for col in required_cols):
            st.error(f"CSV file {full_path} missing required columns. Need at least: {required_cols}")
            return None
        for col in optional_cols:
            if col not in df.columns:
                df[col] = 0 
        return df
    except FileNotFoundError:
        st.error(f"Error: The file {full_path} was not found. Please ensure it exists in the correct directory.")
        return None
    except Exception as e:
        st.error(f"Error loading data from {full_path}: {e}")
        return None

# --- Main Application ---

st.sidebar.title("Navigation")
app_mode = st.sidebar.radio("Choose a View", ["Individual Fight Analysis", "Fight Comparison"])

available_datasets = {
    "Sample Data (Generated)": "boxing_match_data.csv",
    "Real Fight: Davis vs Garcia (Jan 2023)": "davis_garcia_stats.csv",
    "Real Fight: Davis vs Roach (Mar 2025)": "davis_roach_stats.csv",
    "Real Fight: Lopez vs Barboza (May 2025)": "lopez_barboza_stats.csv",
    "Real Fight: Garcia vs Romero (May 2025)": "garcia_romero_stats.csv",
    "Real Fight: Canelo vs Scull (May 2025)": "canelo_scull_stats.csv",
    "Real Fight: Eubank Jr. vs Benn (Apr 2025)": "eubank_benn_stats.csv"
}

if app_mode == "Individual Fight Analysis":
    # Simplified markdown for debugging
    st.markdown("📊 Analyze round-by-round boxing match statistics. 🥊 Dive into the numbers! 🔢") 
    dataset_options = list(available_datasets.keys())
    selected_dataset_key = st.sidebar.selectbox(
        "Fights Data 📊",
        options=dataset_options,
        index=0 
    )
    data_path = available_datasets[selected_dataset_key]
    df = load_data(data_path)

    if df is not None:
        st.sidebar.header("Match Filters")
        boxers = sorted(df["Boxer"].unique())
        if len(boxers) >= 2:
            boxer_a_default_name, boxer_b_default_name = None, None
            if selected_dataset_key == "Real Fight: Davis vs Garcia (Jan 2023)": boxer_a_default_name, boxer_b_default_name = "Gervonta Davis", "Hector Luis Garcia"
            elif selected_dataset_key == "Real Fight: Davis vs Roach (Mar 2025)": boxer_a_default_name, boxer_b_default_name = "Gervonta Davis", "Lamont Roach"
            elif selected_dataset_key == "Real Fight: Lopez vs Barboza (May 2025)": boxer_a_default_name, boxer_b_default_name = "Teofimo Lopez", "Arnold Barboza Jr"
            elif selected_dataset_key == "Real Fight: Garcia vs Romero (May 2025)": boxer_a_default_name, boxer_b_default_name = "Ryan Garcia", "Rolando Romero"
            elif selected_dataset_key == "Real Fight: Canelo vs Scull (May 2025)": boxer_a_default_name, boxer_b_default_name = "Canelo Alvarez", "William Scull"
            elif selected_dataset_key == "Real Fight: Eubank Jr. vs Benn (Apr 2025)": boxer_a_default_name, boxer_b_default_name = "Chris Eubank Jr.", "Conor Benn"
            else: boxer_a_default_name, boxer_b_default_name = "Lightning Lewis", "Thunder Thompson"
            
            try: boxer_a_default_index = boxers.index(boxer_a_default_name) if boxer_a_default_name in boxers else 0
            except ValueError: boxer_a_default_index = 0
            try: 
                potential_b_index = boxers.index(boxer_b_default_name) if boxer_b_default_name in boxers else (1 if boxer_a_default_index == 0 and len(boxers)>1 else 0)
                boxer_b_default_index = potential_b_index if potential_b_index != boxer_a_default_index else (1 if boxer_a_default_index == 0 and len(boxers)>1 else 0)
            except ValueError: boxer_b_default_index = 1 if boxer_a_default_index == 0 and len(boxers)>1 else 0

            boxer_a = st.sidebar.selectbox("Select Boxer A", options=boxers, index=boxer_a_default_index, key=f"boxer_a_select_{selected_dataset_key}")
            boxer_b_options = [b for b in boxers if b != boxer_a]
            if boxer_b_options:
                 boxer_b_default_value = boxers[boxer_b_default_index] if boxer_b_default_index < len(boxers) and boxers[boxer_b_default_index] in boxer_b_options else boxer_b_options[0]
                 boxer_b = st.sidebar.selectbox("Select Boxer B", options=boxer_b_options, index=boxer_b_options.index(boxer_b_default_value), key=f"boxer_b_select_{selected_dataset_key}")
            else:
                 st.sidebar.warning("Only one boxer found in the data.")
                 boxer_b = None
        else:
            st.sidebar.warning("Not enough boxers in the data for comparison.")
            boxer_a = boxers[0] if boxers else None
            boxer_b = None

        if boxer_a and boxer_b:
            df_filtered = df[df["Boxer"].isin([boxer_a, boxer_b])].copy()
            df_filtered.sort_values(by=["Round", "Boxer"], inplace=True)
            rounds = sorted(df_filtered["Round"].unique())
            selected_round = st.sidebar.select_slider("Select Round", options=["All Rounds"] + rounds, value="All Rounds", key=f"round_select_{selected_dataset_key}")
            st.sidebar.markdown("--- Central")
            st.sidebar.info(f"Analyzing Match: **{boxer_a}** vs **{boxer_b}**")

            if selected_dataset_key == "Real Fight: Davis vs Garcia (Jan 2023)": st.info("📊 **Real CompuBox Data**: Gervonta Davis vs Hector Luis Garcia (Jan 2023). Source: BoxingScene.com")
            elif selected_dataset_key == "Real Fight: Davis vs Roach (Mar 2025)": st.info("📊 **Real CompuBox Data**: Gervonta Davis vs Lamont Roach (Mar 2025). Source: BoxingScene.com")
            elif selected_dataset_key == "Real Fight: Lopez vs Barboza (May 2025)": st.info("📊 **Real CompuBox Data**: Teofimo Lopez vs Arnold Barboza Jr (May 2025). Source: BoxingScene.com")
            elif selected_dataset_key == "Real Fight: Garcia vs Romero (May 2025)": st.info("📊 **Real CompuBox Data**: Ryan Garcia vs Rolando Romero (May 2025). Source: BoxingScene.com")
            elif selected_dataset_key == "Real Fight: Canelo vs Scull (May 2025)": st.info("📊 **Real CompuBox Data**: Canelo Alvarez vs William Scull (May 2025). Source: Approx. from news reports.")
            elif selected_dataset_key == "Real Fight: Eubank Jr. vs Benn (Apr 2025)": st.info("📊 **Real CompuBox Data**: Chris Eubank Jr. vs Conor Benn (Apr 2025). Source: Approx. from news reports.")
            else: st.info("📊 **Sample Data**: Generated sample data for demonstration purposes.")

            st.header("Raw Round Data")
            if selected_round == "All Rounds": st.dataframe(df_filtered, height=300)
            else: st.dataframe(df_filtered[df_filtered["Round"] == selected_round])

            st.header("Round-by-Round Visualizations")
            if selected_round == "All Rounds":
                st.subheader("Match Trends")
                col1, col2 = st.columns(2)
                with col1:
                    st.plotly_chart(plot_total_punch_trends(df_filtered, boxer_a, boxer_b), use_container_width=True)
                    st.plotly_chart(plot_total_ring_control_trends(df_filtered, boxer_a, boxer_b), use_container_width=True)
                with col2:
                    st.plotly_chart(plot_total_sig_punch_trends(df_filtered, boxer_a, boxer_b), use_container_width=True)
            else:
                st.subheader(f"Statistics for Round {selected_round}")
                df_round_data = df_filtered[df_filtered["Round"] == selected_round]
                if not df_round_data.empty:
                    col1, col2 = st.columns(2)
                    with col1:
                        st.plotly_chart(plot_round_punch_stats(df_round_data, boxer_a, boxer_b), use_container_width=True)
                        st.plotly_chart(plot_round_ring_control(df_round_data, boxer_a, boxer_b), use_container_width=True)
                    with col2:
                        st.plotly_chart(plot_round_sig_punches(df_round_data, boxer_a, boxer_b), use_container_width=True)
                else: st.warning(f"No data available for Round {selected_round}.")

            st.header("Overall Match Analysis")
            stats_a, stats_b, df_agg_display = calculate_match_aggregates(df_filtered, boxer_a, boxer_b)
            if stats_a is not None and stats_b is not None:
                st.subheader("Total Match Statistics")
                col1, col2, col3, col4 = st.columns(4)
                with col1: 
                    st.metric(label=f"{boxer_a} Sig. Landed", value=int(stats_a["total_sig_punches_landed"]))
                    st.metric(label=f"{boxer_b} Sig. Landed", value=int(stats_b["total_sig_punches_landed"]), delta=f"{int(stats_b['total_sig_punches_landed'] - stats_a['total_sig_punches_landed'])}")
                with col2:
                    st.metric(label=f"{boxer_a} Accuracy %", value=f"{stats_a['punch_accuracy_pct']}%" )
                    st.metric(label=f"{boxer_b} Accuracy %", value=f"{stats_b['punch_accuracy_pct']}%", delta=f"{round(stats_b['punch_accuracy_pct'] - stats_a['punch_accuracy_pct'], 1)}%")
                with col3:
                    st.metric(label=f"{boxer_a} Sig. Accuracy %", value=f"{stats_a['sig_punch_accuracy_pct']}%" )
                    st.metric(label=f"{boxer_b} Sig. Accuracy %", value=f"{stats_b['sig_punch_accuracy_pct']}%", delta=f"{round(stats_b['sig_punch_accuracy_pct'] - stats_a['sig_punch_accuracy_pct'], 1)}%")
                with col4:
                    st.metric(label=f"{boxer_a} Head Landed", value=int(stats_a["total_head_punches_landed"]))
                    st.metric(label=f"{boxer_b} Head Landed", value=int(stats_b["total_head_punches_landed"]), delta=f"{int(stats_b['total_head_punches_landed'] - stats_a['total_head_punches_landed'])}")
                
                st.subheader("Detailed Aggregate Stats Table")
                st.dataframe(df_agg_display.set_index("Boxer"))

                winner = stats_a["Boxer"] if stats_a["total_sig_punches_landed"] > stats_b["total_sig_punches_landed"] else stats_b["Boxer"]
                loser = stats_b["Boxer"] if stats_a["total_sig_punches_landed"] > stats_b["total_sig_punches_landed"] else stats_a["Boxer"]
                if stats_a["total_sig_punches_landed"] == stats_b["total_sig_punches_landed"]:
                    st.info("The match is a draw based on significant punches landed.")
                else:
                    st.success(f"🏆 Based on Significant Punches Landed, the likely winner is: **{winner}** over **{loser}**.")
            else:
                st.warning("Could not calculate overall match statistics. Ensure both boxers are selected and data is available.")
        else:
            st.info("Select two boxers from the sidebar to view detailed analysis.")
    else:
        st.warning("Please select a valid data source to begin analysis.")

elif app_mode == "Fight Comparison":
    st.markdown("Compare statistics across different boxing matches.")
    
    all_fight_data = {}
    for fight_name, file_path in available_datasets.items():
        df_fight = load_data(file_path)
        if df_fight is not None:
            boxers_in_fight = df_fight["Boxer"].unique()
            if len(boxers_in_fight) >= 2:
                 # Attempt to get the primary two boxers, handling cases with more than 2 if necessary
                boxer1_name = boxers_in_fight[0]
                boxer2_name = boxers_in_fight[1]
                stats1, stats2, _ = calculate_match_aggregates(df_fight, boxer1_name, boxer2_name)
                if stats1 is not None and stats2 is not None:
                    all_fight_data[fight_name] = {
                        f"{boxer1_name} (Total Thrown)": stats1["total_punches_thrown"],
                        f"{boxer1_name} (Total Landed)": stats1["total_punches_landed"],
                        f"{boxer1_name} (Sig. Thrown)": stats1["total_sig_punches_thrown"],
                        f"{boxer1_name} (Sig. Landed)": stats1["total_sig_punches_landed"],
                        f"{boxer1_name} (Accuracy %)": stats1["punch_accuracy_pct"],
                        f"{boxer1_name} (Sig. Accuracy %)": stats1["sig_punch_accuracy_pct"],
                        f"{boxer2_name} (Total Thrown)": stats2["total_punches_thrown"],
                        f"{boxer2_name} (Total Landed)": stats2["total_punches_landed"],
                        f"{boxer2_name} (Sig. Thrown)": stats2["total_sig_punches_thrown"],
                        f"{boxer2_name} (Sig. Landed)": stats2["total_sig_punches_landed"],
                        f"{boxer2_name} (Accuracy %)": stats2["punch_accuracy_pct"],
                        f"{boxer2_name} (Sig. Accuracy %)": stats2["sig_punch_accuracy_pct"],
                        "Combined Total Punches Thrown": stats1["total_punches_thrown"] + stats2["total_punches_thrown"],
                        "Combined Total Punches Landed": stats1["total_punches_landed"] + stats2["total_punches_landed"],
                        "Combined Sig. Punches Thrown": stats1["total_sig_punches_thrown"] + stats2["total_sig_punches_thrown"],
                        "Combined Sig. Punches Landed": stats1["total_sig_punches_landed"] + stats2["total_sig_punches_landed"],
                        "Overall Punch Accuracy %": round(((stats1["total_punches_landed"] + stats2["total_punches_landed"]) * 100) / 
                                                        (stats1["total_punches_thrown"] + stats2["total_punches_thrown"] if (stats1["total_punches_thrown"] + stats2["total_punches_thrown"]) > 0 else 1), 1),
                        "Overall Sig. Punch Accuracy %": round(((stats1["total_sig_punches_landed"] + stats2["total_sig_punches_landed"]) * 100) / 
                                                             (stats1["total_sig_punches_thrown"] + stats2["total_sig_punches_thrown"] if (stats1["total_sig_punches_thrown"] + stats2["total_sig_punches_thrown"]) > 0 else 1), 1)
                    }
    
    if not all_fight_data:
        st.warning("No fight data available for comparison or data is not in the expected format.")
    else:
        comparison_df = pd.DataFrame.from_dict(all_fight_data, orient="index")
        
        st.sidebar.header("Comparison Metric")
        comparison_metrics = [
            "Combined Total Punches Thrown", 
            "Combined Total Punches Landed",
            "Combined Sig. Punches Thrown",
            "Combined Sig. Punches Landed",
            "Overall Punch Accuracy %",
            "Overall Sig. Punch Accuracy %"
        ]
        selected_metric = st.sidebar.selectbox("Select Metric to Compare", comparison_metrics)

        st.subheader(f"Fight Comparison by: {selected_metric}")
        
        # Sort by selected metric for better visualization
        sorted_comparison_df = comparison_df.sort_values(by=selected_metric, ascending=False)
        
        st.dataframe(sorted_comparison_df)

        fig_comp = px.bar(sorted_comparison_df, 
                            x=sorted_comparison_df.index, 
                            y=selected_metric, 
                            color=selected_metric,
                            labels={selected_metric: selected_metric, "index": "Fight"},
                            title=f"Comparison of Fights by {selected_metric}")
        fig_comp.update_layout(xaxis_title="Fight", yaxis_title=selected_metric)
        st.plotly_chart(fig_comp, use_container_width=True)

st.sidebar.markdown("--- Central")
st.sidebar.info("Created by Karl Siaka with Manus AI")

