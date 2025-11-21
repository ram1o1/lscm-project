import streamlit as st
import pandas as pd
import plotly.express as px

# Set page configuration
st.set_page_config(
    page_title="Comprehensive EDA Web App",
    page_icon="📊",
    layout="wide"
)

# --- Helper Functions ---

@st.cache_data
def load_data(uploaded_file):
    """Loads data from uploaded CSV or Excel file."""
    if uploaded_file.name.endswith('.csv'):
        # Added on_bad_lines='skip' for robustness
        df = pd.read_csv(uploaded_file, on_bad_lines='skip') 
    else:
        df = pd.read_excel(uploaded_file)
    return df

def display_overview(df):
    """Displays the dataset overview (head, shape, dtypes)."""
    st.header("Dataset Overview")
    
    st.write("### First 5 rows")
    st.dataframe(df.head())
    
    st.write("### Dataset Shape")
    st.write(f"Rows: {df.shape[0]}, Columns: {df.shape[1]}")
    
    st.write("### Column Types")
    st.dataframe(df.dtypes.astype(str))

def display_statistics(df):
    """Displays descriptive statistics and missing values, including categorical analysis."""
    st.header("Statistical Summary")
    
    # Descriptive Statistics for Numeric Data
    st.write("### Descriptive Statistics (Numeric Data)")
    numeric_df = df.select_dtypes(include=['float64', 'int64'])
    if not numeric_df.empty:
        st.dataframe(numeric_df.describe())
    else:
        st.info("No numeric columns found for descriptive statistics.")

    # Missing Values
    st.write("### Missing Values")
    missing_data = df.isnull().sum()
    missing_data = missing_data[missing_data > 0].sort_values(ascending=False)
    if not missing_data.empty:
        st.dataframe(missing_data.rename("Missing Count"))
    else:
        st.success("No missing values found!")

    # Categorical Analysis (New Feature)
    st.write("### Categorical Column Analysis")
    # Also include boolean types for categorical analysis
    categorical_columns = df.select_dtypes(include=['object', 'category', 'bool']).columns.tolist()
    if categorical_columns:
        cat_stats = []
        for col in categorical_columns:
            cat_stats.append({
                'Column': col,
                'Unique Values': df[col].nunique(),
                # Get the most frequent value (mode), handling potential NaNs
                'Most Frequent Value': df[col].mode().iloc[0] if not df[col].mode().empty else 'N/A' 
            })
        st.dataframe(pd.DataFrame(cat_stats).set_index('Column'))
        
        # Display value counts for a selected categorical column
        st.markdown("---")
        st.subheader("Value Counts")
        cat_col = st.selectbox("Select Categorical Column for Value Counts", categorical_columns, key="stat_cat_col")
        st.dataframe(df[cat_col].value_counts().rename("Count"))
    else:
        st.info("No categorical columns found for detailed analysis.")


def display_visualization(df):
    """
    Handles data visualization based on user selection.
    Uses a fixed height of 500px for consistency.
    """
    st.header("Comprehensive Data Visualization")
    
    # Default plot height
    DEFAULT_HEIGHT = 500
    
    numeric_columns = df.select_dtypes(include=['float64', 'int64']).columns.tolist()
    categorical_columns = df.select_dtypes(include=['object', 'category', 'bool']).columns.tolist()
    date_columns = df.select_dtypes(include=['datetime64', 'datetime64[ns]']).columns.tolist()
    all_columns = df.columns.tolist()
    
    # Determine available visualizations based on data types
    available_viz = ["Correlation Heatmap"]
    if numeric_columns:
        available_viz.extend(["Histogram (Distribution)", "Scatter Plot (Relationship)", "Box Plot (Outliers/Comparison)", "Violin Plot (Density/Distribution)", "Scatter Matrix (Multivariate)"])
    if categorical_columns:
        available_viz.append("Count Plot (Bar Chart)")
    if date_columns and numeric_columns:
        available_viz.append("Time Series Plot (Line Chart)")
    if len(categorical_columns) >= 2:
        available_viz.extend(["Sunburst Chart (Hierarchy)", "Treemap (Hierarchy)"])
    
    if not available_viz:
        st.warning("No suitable columns found for visualization.")
        return
        
    viz_type = st.selectbox(
        "Choose Visualization Type",
        available_viz
    )
    
    # --- Visualization Logic for Selected Type ---

    if viz_type == "Histogram (Distribution)":
        if not numeric_columns: st.warning("Requires numeric columns."); return
        col = st.selectbox("Select Numeric Column", numeric_columns)
        color_col = st.selectbox("Color by (Optional Categorical)", ["None"] + categorical_columns)
        
        if color_col == "None":
            fig = px.histogram(df, x=col, title=f"Histogram of {col}", height=DEFAULT_HEIGHT)
        else:
            fig = px.histogram(df, x=col, color=color_col, title=f"Histogram of {col} grouped by {color_col}", marginal="box", height=DEFAULT_HEIGHT)
        st.plotly_chart(fig, use_container_width=True)
        
    elif viz_type == "Scatter Plot (Relationship)":
        if len(numeric_columns) < 2: st.warning("Requires at least two numeric columns."); return
        col_x = st.selectbox("Select X Axis", numeric_columns, index=0)
        col_y = st.selectbox("Select Y Axis", numeric_columns, index=1 if len(numeric_columns) > 1 else 0)
        color_col = st.selectbox("Color by (Optional)", ["None"] + all_columns)
        
        if color_col == "None":
            fig = px.scatter(df, x=col_x, y=col_y, title=f"Scatter Plot: {col_x} vs {col_y}", height=DEFAULT_HEIGHT)
        else:
            fig = px.scatter(df, x=col_x, y=col_y, color=color_col, title=f"Scatter Plot: {col_x} vs {col_y} by {color_col}", height=DEFAULT_HEIGHT)
        st.plotly_chart(fig, use_container_width=True)

    elif viz_type == "Scatter Matrix (Multivariate)":
        if len(numeric_columns) < 3: st.warning("Requires at least three numeric columns for an effective matrix."); return
        cols_to_plot = st.multiselect("Select Numeric Columns to Plot (3+ recommended)", numeric_columns, default=numeric_columns[:min(5, len(numeric_columns))])
        color_col = st.selectbox("Color by (Optional Categorical)", ["None"] + categorical_columns)
        
        if len(cols_to_plot) >= 2:
            if color_col == "None":
                fig = px.scatter_matrix(df, dimensions=cols_to_plot, title="Scatter Matrix", height=DEFAULT_HEIGHT)
            else:
                fig = px.scatter_matrix(df, dimensions=cols_to_plot, color=color_col, title=f"Scatter Matrix colored by {color_col}", height=DEFAULT_HEIGHT)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Please select at least two columns.")

    elif viz_type == "Box Plot (Outliers/Comparison)":
        if not numeric_columns: st.warning("Requires numeric columns."); return
        col = st.selectbox("Select Numeric Column (Y-axis)", numeric_columns)
        group_col = st.selectbox("Group by (Optional Categorical Column for X-axis)", ["None"] + categorical_columns) 
        
        if group_col == "None":
            fig = px.box(df, y=col, title=f"Box Plot of {col}", height=DEFAULT_HEIGHT)
        else:
            fig = px.box(df, x=group_col, y=col, title=f"Box Plot of {col} grouped by {group_col}", height=DEFAULT_HEIGHT)
        st.plotly_chart(fig, use_container_width=True)
        
    elif viz_type == "Violin Plot (Density/Distribution)":
        if not numeric_columns: st.warning("Requires numeric columns."); return
        col = st.selectbox("Select Numeric Column (Y-axis)", numeric_columns, key="violin_y")
        group_col = st.selectbox("Group by (Optional Categorical Column for X-axis)", ["None"] + categorical_columns, key="violin_x") 
        
        if group_col == "None":
            fig = px.violin(df, y=col, box=True, points="all", title=f"Violin Plot of {col}", height=DEFAULT_HEIGHT)
        else:
            fig = px.violin(df, x=group_col, y=col, color=group_col, box=True, points="all", title=f"Violin Plot of {col} grouped by {group_col}", height=DEFAULT_HEIGHT)
        st.plotly_chart(fig, use_container_width=True)

    elif viz_type == "Count Plot (Bar Chart)":
        if not categorical_columns: st.warning("Requires categorical columns."); return
        col = st.selectbox("Select Categorical Column", categorical_columns)
        fig = px.histogram(df, x=col, title=f"Count Plot of {col}", height=DEFAULT_HEIGHT)
        st.plotly_chart(fig, use_container_width=True)
        
    elif viz_type == "Time Series Plot (Line Chart)":
        if not date_columns or not numeric_columns: st.warning("Requires at least one Date and one Numeric column."); return
        date_col = st.selectbox("Select Date Column (X-axis)", date_columns)
        value_col = st.selectbox("Select Value Column (Y-axis)", numeric_columns)
        color_col = st.selectbox("Group/Color by (Optional Categorical)", ["None"] + categorical_columns)
        
        # Ensure the date column is in datetime format before plotting
        df_copy = df.copy()
        try:
            df_copy[date_col] = pd.to_datetime(df_copy[date_col], errors='coerce') 
        except:
            st.error(f"Could not convert column '{date_col}' to datetime format.")
            return

        if color_col == "None":
            fig = px.line(df_copy, x=date_col, y=value_col, title=f"Time Series of {value_col} over {date_col}", height=DEFAULT_HEIGHT)
        else:
            fig = px.line(df_copy, x=date_col, y=value_col, color=color_col, title=f"Time Series of {value_col} over {date_col} by {color_col}", height=DEFAULT_HEIGHT)
        st.plotly_chart(fig, use_container_width=True)

    elif viz_type == "Correlation Heatmap":
        if numeric_columns:
            st.write("### Correlation Matrix")
            corr = df[numeric_columns].corr()
            fig = px.imshow(corr, text_auto=True, title="Correlation Heatmap", color_continuous_scale=px.colors.sequential.Inferno, height=DEFAULT_HEIGHT)
            st.plotly_chart(fig, use_container_width=True) 
        else:
            st.warning("No numeric columns found to compute a Correlation Heatmap.")

    elif viz_type in ["Sunburst Chart (Hierarchy)", "Treemap (Hierarchy)"]:
        if len(categorical_columns) < 2: 
            st.warning("Requires at least two categorical columns for hierarchical plots.")
            return
            
        path_cols = st.multiselect("Select Categorical Columns for Hierarchy Path (order matters)", categorical_columns, default=categorical_columns[:min(3, len(categorical_columns))])
        value_col = st.selectbox("Select Numeric Column for Values (Optional)", ["Count"] + numeric_columns)

        if not path_cols:
            st.info("Please select columns for the hierarchy path.")
            return

        values = None if value_col == "Count" else value_col

        if viz_type == "Sunburst Chart (Hierarchy)":
            fig = px.sunburst(df, path=path_cols, values=values, title="Sunburst Chart", height=DEFAULT_HEIGHT)
        else:
            fig = px.treemap(df, path=path_cols, values=values, title="Treemap", height=DEFAULT_HEIGHT)
            
        st.plotly_chart(fig, use_container_width=True)


# --- Main App Logic ---

def main():
    st.title("📊 Comprehensive Data Visualization and EDA App")
    st.markdown("""
    Welcome to the EDA Web App! Upload your dataset (CSV or Excel) to get started.
    This app provides a wide range of analytical and visualization tools for deep data exploration.
    """)

    # Sidebar for file upload
    st.sidebar.header("Upload your dataset")
    uploaded_file = st.sidebar.file_uploader("Choose a file", type=["csv", "xlsx"])

    if uploaded_file is not None:
        try:
            with st.spinner("Loading and processing data..."):
                df = load_data(uploaded_file)
            
            st.sidebar.success("File uploaded successfully!")
            
            # Identify and convert obvious date columns that pandas might have missed
            for col in df.columns:
                if df[col].dtype == 'object':
                    try:
                        df[col] = pd.to_datetime(df[col], errors='coerce')
                        if df[col].notna().sum() > 0.5 * len(df):
                            st.sidebar.info(f"Converted column '{col}' to Datetime type.")
                    except:
                        pass
            
            # Created tabs with improved names
            tab1, tab2, tab3 = st.tabs(["📊 Data Overview", "📈 Data Statistics", "🔬 Data Visualization"])
            
            with tab1:
                display_overview(df)

            with tab2:
                display_statistics(df)

            with tab3:
                display_visualization(df)

        except Exception as e:
            st.error(f"Error loading file. Please ensure it's a valid CSV or Excel format: {e}")
    else:
        st.info("Awaiting file upload. Please upload a CSV or Excel file from the sidebar.")

if __name__ == "__main__":
    main()