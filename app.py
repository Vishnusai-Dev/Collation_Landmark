
import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="SKU Data Merger", layout="wide")
st.title("🔗 SKU Data Merger")
st.write("Upload five files for a single SKU and get a combined Excel output.")

# Upload files
uploaded_files = {
    "Attribute Dump": st.file_uploader("Upload Attribute Dump (.xlsx)", type="xlsx"),
    "Dimensions": st.file_uploader("Upload Dimensions (.csv)", type="csv"),
    "Image Links": st.file_uploader("Upload Image Links (.csv)", type="csv"),
    "Myntra/Ajio Upload": st.file_uploader("Upload Myntra and Ajio Upload (.xlsb)", type="xlsb"),
    "Overview": st.file_uploader("Upload Overview (.csv)", type="csv")
}

# Read data into DataFrames
def read_files():
    dfs = {}
    try:
        if uploaded_files["Attribute Dump"]:
            dfs["Attribute"] = pd.read_excel(uploaded_files["Attribute Dump"])

        if uploaded_files["Dimensions"]:
            dfs["Dimensions"] = pd.read_csv(uploaded_files["Dimensions"])

        if uploaded_files["Image Links"]:
            dfs["Images"] = pd.read_csv(uploaded_files["Image Links"])

        if uploaded_files["Myntra/Ajio Upload"]:
            dfs["Upload"] = pd.read_excel(uploaded_files["Myntra/Ajio Upload"], engine="pyxlsb")

        if uploaded_files["Overview"]:
            dfs["Overview"] = pd.read_csv(uploaded_files["Overview"])
    except Exception as e:
        st.error(f"Error reading files: {e}")
        return None
    return dfs

# Merge DataFrames
def merge_dataframes(dfs):
    result = None
    for name, df in dfs.items():
        if "Product Code" not in df.columns:
            st.warning(f"'{name}' file does not contain 'Product Code' column and will be skipped.")
            continue

        df_renamed = df.copy()
        df_renamed.columns = [f"{name}_{col}" if col != "Product Code" else col for col in df.columns]

        if result is None:
            result = df_renamed
        else:
            result = pd.merge(result, df_renamed, on="Product Code", how="outer")

    return result

# Process and display output
if all(uploaded_files.values()):
    dfs = read_files()
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
    st.info("⬆️ Please upload all five files to begin.")
