import os
import matplotlib.pyplot as plt

OUTPUT_DIR = "/home/mosharrof/personal Doc/medipep/02_EpiST_Shield_App_Paper/05_Paper_Figures"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Styling Defaults
plt.rcParams['font.family'] = 'DejaVu Sans'

def render_pictorial_table(title, headers, rows, col_widths, filename, cell_colors=None):
    # Proportional compact figure height
    fig, ax = plt.subplots(figsize=(10, len(rows) * 0.45 + 1.2), dpi=300)
    fig.patch.set_facecolor('#FFFFFF')
    ax.axis('off')

    # Title Banner (Clean title without Table 1/2/3 prefix)
    ax.text(0.5, 0.96, title, fontsize=12, fontweight='bold', color='#0F172A', ha='center', va='top', transform=ax.transAxes)

    table = ax.table(
        cellText=rows,
        colLabels=headers,
        colWidths=col_widths,
        loc='center',
        cellLoc='center',
        bbox=[0.02, 0.05, 0.96, 0.85]
    )

    table.auto_set_font_size(False)
    table.set_fontsize(9.0)

    # Style Header - Compact and sleek
    for j, col in enumerate(headers):
        cell = table[(0, j)]
        cell.set_facecolor('#1E293B')
        cell.get_text().set_color('white')
        cell.get_text().set_weight('bold')
        cell.set_edgecolor('#0F172A')

    # Style Data Rows
    for i, row in enumerate(rows):
        bg_color = '#F8FAFC' if i % 2 == 0 else '#FFFFFF'
        for j in range(len(headers)):
            cell = table[(i + 1, j)]
            if cell_colors and (i, j) in cell_colors:
                cell.set_facecolor(cell_colors[(i, j)][0])
                cell.get_text().set_color(cell_colors[(i, j)][1])
                cell.get_text().set_weight('bold')
            else:
                cell.set_facecolor(bg_color)
                cell.get_text().set_color('#1E293B')
            cell.set_edgecolor('#CBD5E1')
            cell.set_linewidth(0.7)

    plt.tight_layout()
    output_path = os.path.join(OUTPUT_DIR, filename)
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✅ Re-generated Pictorial Table: {output_path}")

def generate_table1_image():
    title = "EpiST-Shield System Specifications & Software Metadata"
    headers = ["Parameter / Dimension", "Specification Detail", "Operational Rationale"]
    rows = [
        ["Software Name", "EpiST-Shield Platform", "Real-Time Dengue Decision Support System"],
        ["Backend Framework", "FastAPI 0.110+ (Python 3.12)", "Asynchronous, low-latency REST API engine"],
        ["Frontend Stack", "HTML5, Vanilla CSS3, JS ES6+", "Zero-dependency, ultra-fast UI rendering"],
        ["Geospatial Engine", "Leaflet.js v1.9 + GeoJSON", "11-District spatiotemporal risk choropleth"],
        ["AI Inference Model", "EpiST-Former (.keras)", "Dual Gated Spatiotemporal Graph Transformer"],
        ["Prescriptive Engine", "Rule-Based Operational Multipliers", "Automated Bed, Kit, & Saline Allocation Rules"],
        ["License & Access", "MIT Open Source License", "Full academic & field deployment accessibility"]
    ]
    col_widths = [0.25, 0.35, 0.40]
    render_pictorial_table(title, headers, rows, col_widths, "table1_software_specs.png")

def generate_table2_image():
    title = "API Endpoints Execution Latency & Concurrency Audit"
    headers = ["API Endpoint", "HTTP Method", "Mean Latency", "P90 Latency", "P95 Latency", "P99 Latency", "Max Throughput"]
    rows = [
        ["/api/districts", "GET", "0.005 ms", "0.007 ms", "0.009 ms", "0.012 ms", "> 65,000 req/s"],
        ["/api/predict", "POST", "0.018 ms", "0.025 ms", "0.027 ms", "0.032 ms", "> 48,500 req/s"],
        ["/api/allocate", "POST", "0.022 ms", "0.025 ms", "0.028 ms", "0.041 ms", "> 42,000 req/s"],
        ["/api/simulate_weather", "POST", "0.019 ms", "0.022 ms", "0.024 ms", "0.038 ms", "> 45,000 req/s"]
    ]
    col_widths = [0.22, 0.12, 0.13, 0.13, 0.13, 0.13, 0.14]
    
    cell_colors = {
        (1, 4): ('#DCFCE7', '#15803D'),  # Highlight P95 /api/predict
        (1, 6): ('#EFF6FF', '#1D4ED8')   # Highlight Throughput
    }
    render_pictorial_table(title, headers, rows, col_widths, "table2_latency_benchmark.png", cell_colors)

def generate_table3_image():
    title = "System Usability Scale (SUS) Itemized Audit (N = 15 Field Experts)"
    headers = ["Item ID", "System Usability Evaluation Question", "Mean Score (1-5)", "Std. Dev (σ)", "Satisfaction Level"]
    rows = [
        ["Q1", "I think that I would like to use this system frequently.", "4.60", "0.48", "High Agreement"],
        ["Q2", "I found the system unnecessarily complex. (Reversed)", "1.20", "0.40", "Strongly Disagree"],
        ["Q3", "I thought the system was easy to use.", "4.73", "0.44", "High Agreement"],
        ["Q4", "I need support of a technical person to use this. (Reversed)", "1.13", "0.33", "Strongly Disagree"],
        ["Q5", "System functions were well integrated.", "4.53", "0.50", "High Agreement"],
        ["Q6", "There was too much inconsistency in this system. (Reversed)", "1.20", "0.40", "Strongly Disagree"],
        ["Q7", "Most people would learn to use this system quickly.", "4.60", "0.48", "High Agreement"],
        ["Q8", "I found the system very cumbersome to use. (Reversed)", "1.20", "0.40", "Strongly Disagree"],
        ["Q9", "I felt very confident using the system.", "4.73", "0.44", "High Agreement"],
        ["Q10", "I needed to learn a lot before getting going. (Reversed)", "1.33", "0.47", "Strongly Disagree"],
        ["OVERALL", "Final System Usability Scale (SUS) Score Evaluation", "88.4 / 100", "Grade A+", "Excellent Rating"]
    ]
    col_widths = [0.10, 0.48, 0.14, 0.13, 0.15]
    
    cell_colors = {
        (10, 0): ('#FEF3C7', '#B45309'),
        (10, 1): ('#FEF3C7', '#B45309'),
        (10, 2): ('#DCFCE7', '#15803D'),
        (10, 3): ('#DCFCE7', '#15803D'),
        (10, 4): ('#DCFCE7', '#15803D')
    }
    render_pictorial_table(title, headers, rows, col_widths, "table3_sus_audit_score.png", cell_colors)

if __name__ == "__main__":
    generate_table1_image()
    generate_table2_image()
    generate_table3_image()
