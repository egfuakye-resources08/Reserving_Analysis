import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

# Load KPI Summary and Claims Data
kpi_summary = pd.read_excel("kpi_summary.xlsx")
claims_df = pd.read_excel("cleaned_claims_data.xlsx")

# Generate the PDF report with visualizations
pdf_path = "reserving_analysis_report_final.pdf"

with PdfPages(pdf_path) as pdf:
    # Reserve Timeliness by Region
    plt.figure(figsize=(12, 6))
    plt.bar(kpi_summary['Claim Prov'], kpi_summary['Reserve_Timely'], color='#4C72B0')
    plt.axhline(90, color='red', linestyle='--', linewidth=2, label='Target: 90%')
    plt.xlabel("Region")
    plt.ylabel("Reserve Timeliness (%)")
    plt.title("Reserve Timeliness by Region")
    plt.legend()
    pdf.savefig()
    plt.close()

    # Mapping Accuracy by Region
    plt.figure(figsize=(12, 6))
    plt.bar(kpi_summary['Claim Prov'], kpi_summary['Mapping_Correct'], color='#55A868')
    plt.axhline(95, color='red', linestyle='--', linewidth=2, label='Target: 95%')
    plt.xlabel("Region")
    plt.ylabel("Mapping Accuracy (%)")
    plt.title("Mapping Accuracy by Region")
    plt.legend()
    pdf.savefig()
    plt.close()

    # Days to Reserve Distribution
    plt.figure(figsize=(12, 6))
    plt.hist(claims_df['Days_to_Reserve'].dropna(), bins=30, color='#C44E52', edgecolor='black')
    plt.axvline(7, color='blue', linestyle='dashed', linewidth=2, label="7-Day Standard")
    plt.xlabel("Days to Reserve")
    plt.ylabel("Frequency")
    plt.title("Distribution of Days to Reserve")
    plt.legend()
    pdf.savefig()
    plt.close()

    # Summary Text Page
    plt.figure(figsize=(10, 5))
    plt.axis('off')
    summary_text = (
        "Reserving Standards Analysis Report\n\n"
        "Key Findings:\n"
        "1. Reserve Timeliness: 4.2% (Target: 90%)\n"
        "2. Mapping Accuracy: 11.71% (Target: 95%)\n"
        "3. Average Days to Reserve: 25.56 Days (Target: 7 Days)\n\n"
        "Recommendations:\n"
        "- Implement automated alerts for reserve delays.\n"
        "- Train adjusters on Reserve Mapping standards.\n"
        "- Streamline workflows and prioritize high-value claims.\n"
    )
    plt.text(0.5, 0.5, summary_text, fontsize=12, ha='center', va='center')
    pdf.savefig()
    plt.close()

print(f"PDF report generated successfully: {pdf_path}")
