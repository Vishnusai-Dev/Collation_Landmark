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

# User-defined limits
st.sidebar.header("⚙️ Data Limits")
ROW_LIMIT = st.sidebar.number_input("Max rows per file", min_value=100, max_value=10000, value=3000)
COL_LIMIT = st.sidebar.number_input("Max columns per file", min_value=10, max_value=1000, value=200)

# Upload multiple files
uploaded_files = st.file_uploader("Upload files (CSV, XLSX, or XLSB)", type=["csv", "xlsx", "xlsb"], accept_multiple_files=True)

# Read data into DataFrames with validation
REQUIRED_COLUMN = "Product Code"

def read_files(uploaded_files):
    dfs = {}
    status_logs = []
    previews = {}
    exclude_flags = {}
    progress_bar = st.progress(0, text="Reading files...")

    for i, uploaded_file in enumerate(uploaded_files):
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
                df = df.iloc[:ROW_LIMIT, :COL_LIMIT]  # apply row and column limits
                dfs[file_name] = df
                previews[file_name] = df.head(5)
                exclude_flags[file_name] = False
                status_logs.append((file_name, f"✅ Loaded ({df.shape[0]} rows, {df.shape[1]} columns)"))
        except Exception as e:
            tb = traceback.format_exc()
            status_logs.append((file_name, f"❌ Error: {str(e)}\n{tb}"))

        progress_bar.progress((i + 1) / len(uploaded_files), text=f"Processed {i + 1}/{len(uploaded_files)} files")

    progress_bar.empty()
    return dfs, status_logs, previews, exclude_flags

# Merge DataFrames
def merge_dataframes(dfs, exclude_flags):
    result = None
    for name, df in dfs.items():
        if exclude_flags.get(name):
            continue

        df_renamed = df.copy()
        # Add file name as first row, not in column names
        file_label_row = pd.DataFrame([[name if col != REQUIRED_COLUMN else "" for col in df.columns]], columns=df.columns)
        df_renamed = pd.concat([file_label_row, df_renamed], ignore_index=True)

        if result is None:
            result = df_renamed
        else:
            result = pd.merge(result, df_renamed, on=REQUIRED_COLUMN, how="outer")
    return result

# Process and display output
if uploaded_files:
    dfs, logs, previews, exclude_flags = read_files(uploaded_files)

    with st.expander("📋 File Upload Status"):
        for filename, status in logs:
            st.write(f"- `{filename}` → {status}")

    if previews:
        with st.expander("👀 Preview Uploaded Files"):
            selected_preview = st.selectbox("Select a file to preview:", list(previews.keys()))
            st.dataframe(previews[selected_preview])

    with st.expander("🚫 Exclude Files from Merge"):
        for file in list(dfs.keys()):
            exclude_flags[file] = st.checkbox(f"Exclude `{file}`", value=False)

    if dfs:
        try:
            merge_progress = st.progress(0, text="Merging data...")
            merged_df = merge_dataframes(dfs, exclude_flags)
            merge_progress.progress(1.0, text="Merge complete!")
            merge_progress.empty()

            st.success("✅ Files merged successfully!")

            with st.expander("🔍 Preview Merged Data"):
                st.dataframe(merged_df.head(20))
                st.write("✅ Merged DataFrame shape:", merged_df.shape)

            if len(merged_df) > 50000:
                st.warning("⚠️ Merged file too large to download directly as Excel. You can split input or use CSV.")
                csv_buffer = io.StringIO()
                merged_df.to_csv(csv_buffer, index=False)
                st.download_button(
                    label="📥 Download as CSV",
                    data=csv_buffer.getvalue(),
                    file_name="Merged_SKU_Data.csv",
                    mime="text/csv"
                )
            else:
                buffer = io.BytesIO()
                merged_df.to_excel(buffer, engine="openpyxl", index=False)
                buffer.seek(0)
                st.download_button(
                    label="📥 Download as Excel",
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
