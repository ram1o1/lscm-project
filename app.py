import streamlit as st
import pandas as pd
import plotly.express as px

# Set page configuration
st.set_page_config(
    page_title="EDA Web App",
    page_icon="📊",
    layout="wide"
)

def main():
    st.title("📊 Exploratory Data Analysis Web App")
    st.markdown("""
    Welcome to the EDA Web App! Upload your dataset (CSV or Excel) to get started.
    This app allows you to:
    - View dataset overview and statistics
    - Visualize data distributions and relationships
    """)

    # Sidebar for file upload
    st.sidebar.header("Upload your dataset")
    uploaded_file = st.sidebar.file_uploader("Choose a file", type=["csv", "xlsx"])

    if uploaded_file is not None:
        try:
            # Load data
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)
            
            st.sidebar.success("File uploaded successfully!")
            
            # Create tabs for different sections
            tab1, tab2, tab3 = st.tabs(["📄 Overview", "📈 Statistics", "🎨 Visualization"])
            
            with tab1:
                st.header("Dataset Overview")
                st.write("### First 5 rows")
                st.dataframe(df.head())
                
                st.write("### Dataset Shape")
                st.write(f"Rows: {df.shape[0]}, Columns: {df.shape[1]}")
                
                st.write("### Column Types")
                st.dataframe(df.dtypes.astype(str))

            with tab2:
                st.header("Statistical Summary")
                st.write("### Descriptive Statistics")
                st.dataframe(df.describe())
                
                st.write("### Missing Values")
                missing_data = df.isnull().sum()
                st.dataframe(missing_data[missing_data > 0])

            with tab3:
                st.header("Data Visualization")
                
                # Select columns for visualization
                numeric_columns = df.select_dtypes(include=['float64', 'int64']).columns.tolist()
                all_columns = df.columns.tolist()
                
                if not numeric_columns:
                    st.warning("No numeric columns found for visualization.")
                else:
                    viz_type = st.selectbox(
                        "Choose Visualization Type",
                        ["Histogram", "Scatter Plot", "Box Plot", "Correlation Heatmap"]
                    )
                    
                    if viz_type == "Histogram":
                        col = st.selectbox("Select Column", numeric_columns)
                        fig = px.histogram(df, x=col, title=f"Histogram of {col}")
                        st.plotly_chart(fig, use_container_width=True)
                        
                    elif viz_type == "Scatter Plot":
                        col_x = st.selectbox("Select X Axis", numeric_columns, index=0)
                        col_y = st.selectbox("Select Y Axis", numeric_columns, index=1 if len(numeric_columns) > 1 else 0)
                        color_col = st.selectbox("Color by (Optional)", ["None"] + all_columns)
                        
                        if color_col == "None":
                            fig = px.scatter(df, x=col_x, y=col_y, title=f"Scatter Plot: {col_x} vs {col_y}")
                        else:
                            fig = px.scatter(df, x=col_x, y=col_y, color=color_col, title=f"Scatter Plot: {col_x} vs {col_y} by {color_col}")
                        st.plotly_chart(fig, use_container_width=True)
                        
                    elif viz_type == "Box Plot":
                        col = st.selectbox("Select Column", numeric_columns)
                        fig = px.box(df, y=col, title=f"Box Plot of {col}")
                        st.plotly_chart(fig, use_container_width=True)
                        
                    elif viz_type == "Correlation Heatmap":
                        st.write("### Correlation Matrix")
                        corr = df[numeric_columns].corr()
                        fig = px.imshow(corr, text_auto=True, title="Correlation Heatmap")
                        st.plotly_chart(fig, use_container_width=True)

        except Exception as e:
            st.error(f"Error loading file: {e}")
    else:
        st.info("Awaiting file upload. Please upload a CSV or Excel file from the sidebar.")

if __name__ == "__main__":
    main()
