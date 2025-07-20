# SKU Data Merger 🧩

A Streamlit-based tool to merge product data from five sources using `Product Code` as the primary key.

## 📁 Input Files (Required)
- Attribute Dump (.xlsx)
- Dimensions (.csv)
- Image Links (.csv)
- Myntra & Ajio Upload (.xlsb)
- Overview (.csv)

## 🚀 How to Run Locally
```bash
git clone https://github.com/your-org/sku-data-merger.git
cd sku-data-merger
pip install -r requirements.txt
streamlit run app.py
```

## 🌐 Usage
1. Upload the five files via the Streamlit interface.
2. Preview merged data.
3. Download the final merged Excel output.
