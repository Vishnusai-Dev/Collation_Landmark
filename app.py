import os
import streamlit as st
import pandas as pd
import io
import traceback

# Disable file watcher explicitly for safety
os.environ["STREAMLIT_FILE_WATCHER_TYPE"] = "none"

st.set_page_config(page_title="SKU Data Merger", layout="wide")
st.title("🔗 SKU Data Merger")
st.write("Upload any number of files for a single SKU and get a combined Excel output.")

# Upload multiple files
uploaded_files = st.file_uploader("Upload files (CSV, XLSX, or XLSB)", type=["csv", "xlsx", "xlsb"], accept_multiple_files=True)

# Read data into DataFrames with validation
REQUIRED_COLUMN = "Product Code"

def read_files(uploaded_files):
    dfs = {}
    status_logs = []
    previews = {}
    for uploaded_file in uploaded_files:
        file_name = uploaded_file.name
        try:
            if file_name.endswith(".xlsx"):
                df = pd.read_excel(uploaded_file)
            elif file_name.endswith(".xlsb"):
                try:
                    df = pd.read_excel(uploaded_file, engine="pyxlsb")
                except Exception as e:
                    status_logs.append((file_name, f"❌ pyxlsb error: {str(e)}"))
                    continue
            elif file_name.endswith(".csv"):
                df = pd.read_csv(uploaded_file)
            else:
                status_logs.append((file_name, "❌ Unsupported file type"))
                continue

            if REQUIRED_COLUMN not in df.columns:
                status_logs.append((file_name, f"⚠️ Missing '{REQUIRED_COLUMN}' column"))
            else:
                dfs[file_name] = df
                previews[file_name] = df.head(5)
                status_logs.append((file_name, "✅ Loaded successfully"))
        except Exception as e:
            tb = traceback.format_exc()
            status_logs.append((file_name, f"❌ Error: {str(e)}\n{tb}"))
    return dfs, status_logs, previews

# Merge DataFrames
def merge_dataframes(dfs):
    result = None
    for name, df in dfs.items():
        df_renamed = df.copy()
        df_renamed.columns = [f"{name}_{col}" if col != REQUIRED_COLUMN else col for col in df.columns]

        if result is None:
            result = df_renamed
        else:
            result = pd.merge(result, df_renamed, on=REQUIRED_COLUMN, how="outer")

    return result

# Process and display output
if uploaded_files:
    dfs, logs, previews = read_files(uploaded_files)

    with st.expander("📋 File Upload Status"):
        for filename, status in logs:
            st.write(f"- `{filename}` → {status}")

    if previews:
        with st.expander("👀 Preview Uploaded Files"):
            selected_preview = st.selectbox("Select a file to preview:", list(previews.keys()))
            st.dataframe(previews[selected_preview])

    if dfs:
        try:
            merged_df = merge_dataframes(dfs)
            st.success("✅ Files merged successfully!")

            with st.expander("🔍 Preview Merged Data"):
                st.dataframe(merged_df.head(20))
                st.write("✅ Merged DataFrame shape:", merged_df.shape)

            buffer = io.BytesIO()
            merged_df.to_excel(buffer, index=False)
            buffer.seek(0)  # Important for download
            st.download_button(
                label="📥 Download Merged File",
                data=buffer.getvalue(),
                file_name="Merged_SKU_Data.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        except Exception as e:
            st.error(f"❌ Error while merging or generating output: {str(e)}")
            st.exception(e)
    else:
        st.warning("⚠️ No valid files with 'Product Code' column found.")
else:
    st.info("⬆️ Please upload one or more files to begin.")
