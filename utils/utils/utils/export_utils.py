import streamlit as st
import pandas as pd
import io
import matplotlib.pyplot as plt

def download_buttons(df: pd.DataFrame, filename: str):
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Download CSV", csv, f"{filename}.csv", "text/csv")

    excel = io.BytesIO()
    with pd.ExcelWriter(excel, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Data")
    st.download_button("⬇️ Download Excel", excel.getvalue(), f"{filename}.xlsx")

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
