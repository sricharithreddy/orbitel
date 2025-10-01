import streamlit as st
import pandas as pd
import io
import matplotlib.pyplot as plt
import base64
import streamlit.components.v1 as components

# -----------------------
# CSV / Excel Download
# -----------------------
def download_buttons(df: pd.DataFrame, filename: str):
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Download CSV", csv, f"{filename}.csv", "text/csv")

    excel = io.BytesIO()
    with pd.ExcelWriter(excel, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Data")
    st.download_button("⬇️ Download Excel", excel.getvalue(), f"{filename}.xlsx")

# -----------------------
# PNG Download (table as image)
# -----------------------
def table_to_png_download(df: pd.DataFrame, filename: str):
    fig, ax = plt.subplots(figsize=(len(df.columns)*1.5, len(df)*0.5+1))
    ax.axis("off")
    mpl_table = ax.table(cellText=df.values, colLabels=df.columns, loc="center", cellLoc="center")
    mpl_table.auto_set_font_size(False)
    mpl_table.set_fontsize(10)
    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format="png", bbox_inches="tight", dpi=200)
    st.download_button("🖼️ Download PNG", buf.getvalue(), f"{filename}.png", "image/png")

# -----------------------
# Copy Table as Image (Clipboard)
# -----------------------
def copy_table_as_image(df: pd.DataFrame):
    fig, ax = plt.subplots(figsize=(len(df.columns)*1.5, len(df)*0.5+1))
    ax.axis("off")
    mpl_table = ax.table(cellText=df.values, colLabels=df.columns, loc="center", cellLoc="center")
    mpl_table.auto_set_font_size(False)
    mpl_table.set_fontsize(10)
    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format="png", bbox_inches="tight", dpi=200)
    encoded = base64.b64encode(buf.getvalue()).decode("utf-8")

    components.html(f"""
    <button onclick="navigator.clipboard.write([
        new ClipboardItem({{'image/png': new Blob([Uint8Array.from(atob('{encoded}'), c => c.charCodeAt(0))], {{type: 'image/png'}})}})
    ])" 
    style="padding:8px; border:none; background:#FF9800; color:white; border-radius:5px; cursor:pointer;">
        📋 Copy Table (Image)
    </button>
    """, height=40)
