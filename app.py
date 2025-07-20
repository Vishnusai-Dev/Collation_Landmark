
import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="SKU Data Merger", layout="wide")
st.title("🔗 SKU Data Merger")
st.write("Upload any number of files for a single SKU and get a combined Excel output.")

# Upload multiple files
uploaded_files = st.file_uploader("Upload files (CSV, XLSX, or XLSB)", type=["csv", "xlsx", "xlsb"], accept_multiple_files=True)

# Read data into DataFrames
def read_files(uploaded_files):
    dfs = {}
    for uploaded_file in uploaded_files:
        file_name = uploaded_file.name
        try:
            if file_name.endswith(".xlsx"):
                df = pd.read_excel(uploaded_file)
            elif file_name.endswith(".xlsb"):
                df = pd.read_excel(uploaded_file, engine="pyxlsb")
            elif file_name.endswith(".csv"):
                df = pd.read_csv(uploaded_file)
            else:
                st.warning(f"Unsupported file type: {file_name}")
                continue
            dfs[file_name] = df
        except Exception as e:
            st.error(f"Error reading {file_name}: {e}")
    return dfs

# Merge DataFrames
def merge_dataframes(dfs):
    result = None
    for name, df in dfs.items():
        if "Product Code" not in df.columns:
            st.warning(f"'{name}' does not contain 'Product Code' column and will be skipped.")
            continue

        df_renamed = df.copy()
        df_renamed.columns = [f"{name}_{col}" if col != "Product Code" else col for col in df.columns]

        if result is None:
            result = df_renamed
        else:
            result = pd.merge(result, df_renamed, on="Product Code", how="outer")

    return result

# Process and display output
if uploaded_files:
    dfs = read_files(uploaded_files)
    if dfs:
        merged_df = merge_dataframes(dfs)
        st.success("✅ Files merged successfully!")

        with st.expander("🔍 Preview Merged Data"):
            st.dataframe(merged_df.head(20))

        buffer = io.BytesIO()
        merged_df.to_excel(buffer, index=False)
        st.download_button(
            label="📥 Download Merged File",
            data=buffer.getvalue(),
            file_name="Merged_SKU_Data.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
else:
    st.info("⬆️ Please upload one or more files to begin.")
