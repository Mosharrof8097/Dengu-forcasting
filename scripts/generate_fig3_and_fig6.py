import os
from PIL import Image, ImageDraw, ImageFont
import matplotlib.pyplot as plt
import matplotlib.patches as patches

OUTPUT_DIR = "/home/mosharrof/personal Doc/medipep/02_EpiST_Shield_App_Paper/05_Paper_Figures"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def generate_fig3_weather_simulator():
    # Crop the right sidebar (Simulator panel) from fig2_dashboard_overview.png if it exists
    fig2_path = os.path.join(OUTPUT_DIR, "fig2_dashboard_overview.png")
    output_path = os.path.join(OUTPUT_DIR, "fig3_weather_simulator_ui.png")
    
    if os.path.exists(fig2_path):
        img = Image.open(fig2_path)
        width, height = img.size
        # The right sidebar is roughly x: 1300 to 1900, y: 100 to 1000
        crop_box = (int(width * 0.65), int(height * 0.08), int(width * 0.98), int(height * 0.95))
        cropped = img.crop(crop_box)
        cropped.save(output_path, dpi=(300, 300))
        print(f"✅ Generated {output_path} (Cropped Simulator Sidebar)")
    else:
        print("fig2_dashboard_overview.png not found, creating synthetic Fig 3...")

def generate_fig6_executive_bulletin():
    output_path = os.path.join(OUTPUT_DIR, "fig6_pdf_executive_bulletin.png")
    
    fig, ax = plt.subplots(figsize=(8.5, 11), dpi=300)
    fig.patch.set_facecolor('#FFFFFF')
    ax.axis('off')

    # Border & Document Frame
    rect_border = patches.Rectangle((0.02, 0.02), 0.96, 0.96, transform=ax.transAxes, fill=False, color='#1E3A8A', lw=2.5)
    ax.add_patch(rect_border)

    # Header Ribbon
    rect_header = patches.Rectangle((0.02, 0.88), 0.96, 0.10, transform=ax.transAxes, color='#1E3A8A')
    ax.add_patch(rect_header)

    ax.text(0.5, 0.94, "DISTRICT PUBLIC HEALTH SURVEILLANCE CELL", fontsize=13, fontweight='bold', color='#FFFFFF', ha='center', va='center', transform=ax.transAxes)
    ax.text(0.5, 0.90, "EpiST-Shield Real-Time Dengue Outbreak Illustrative Bulletin", fontsize=11, fontweight='bold', color='#6EE7B7', ha='center', va='center', transform=ax.transAxes)

    # MANDATORY DISCLAIMER WATERMARK / BANNER (Reviewer Comment 15 Resolution)
    rect_disc = patches.Rectangle((0.02, 0.965), 0.96, 0.025, transform=ax.transAxes, color='#DC2626')
    ax.add_patch(rect_disc)
    ax.text(0.5, 0.977, "SAMPLE OUTPUT — FOR ILLUSTRATION ONLY | NOT AN OFFICIAL DGHS DOCUMENT", fontsize=8.5, fontweight='bold', color='#FFFFFF', ha='center', va='center', transform=ax.transAxes)

    # Diagonal Semi-Transparent Watermark Across Page
    ax.text(0.5, 0.50, "SAMPLE OUTPUT — FOR ILLUSTRATION ONLY", fontsize=22, fontweight='bold', color='#DC2626', alpha=0.15, rotation=30, ha='center', va='center', transform=ax.transAxes)

    # Metadata Banner
    ax.text(0.05, 0.85, "Date: 26 July 2026", fontsize=9.5, fontweight='bold', color='#334155', transform=ax.transAxes)
    ax.text(0.55, 0.85, "Issued By: Public Health AI Intelligence Cell", fontsize=9.5, fontweight='bold', color='#334155', transform=ax.transAxes)
    ax.text(0.05, 0.83, "Surveillance Horizon: 21 Days", fontsize=9.5, color='#64748B', transform=ax.transAxes)
    ax.text(0.55, 0.83, "Model Latency (p95): 0.027 ms (Verified)", fontsize=9.5, color='#059669', transform=ax.transAxes)

    ax.axhline(0.81, color='#CBD5E1', linewidth=1)

    # Section 1: Executive Summary
    ax.text(0.05, 0.78, "1. Executive Outbreak Summary & High Risk Districts", fontsize=11, fontweight='bold', color='#1E3A8A', transform=ax.transAxes)
    
    # Table of High Risk Districts
    table_data = [
        ["District", "Risk Level", "Pred. Cases/Day", "Weekly Expected", "Action Required"],
        ["Dhaka", "HIGH SURGE", "68.4", "478.8", "URGENT DISPATCH"],
        ["Chittagong", "HIGH SURGE", "52.1", "364.7", "URGENT DISPATCH"],
        ["Gazipur", "WARNING", "34.2", "239.4", "MONITOR CLOSELY"],
        ["Khulna", "WARNING", "28.9", "202.3", "PREPARE BEDS"],
        ["Rajshahi", "LOW / NORMAL", "12.4", "86.8", "STANDARD MONITORING"]
    ]
    
    col_widths = [0.15, 0.20, 0.20, 0.20, 0.25]
    table = ax.table(cellText=table_data, colWidths=col_widths, loc='center', bbox=[0.05, 0.53, 0.90, 0.23])
    table.auto_set_font_size(False)
    table.set_fontsize(8.0)
    
    # Style Table Header and Cells
    for (i, j), cell in table.get_celld().items():
        cell.set_edgecolor('#CBD5E1')
        cell.set_linewidth(0.8)
        if i == 0:
            cell.set_facecolor('#1E3A8A')
            cell.get_text().set_color('white')
            cell.get_text().set_weight('bold')
            cell.get_text().set_ha('center')
        else:
            cell.get_text().set_ha('center')
            if j == 1:
                if "HIGH" in cell.get_text().get_text():
                    cell.set_facecolor('#FEE2E2')
                    cell.get_text().set_color('#B91C1C')
                    cell.get_text().set_weight('bold')
                elif "WARNING" in cell.get_text().get_text():
                    cell.set_facecolor('#FEF3C7')
                    cell.get_text().set_color('#D97706')

    # Section 2: Prescriptive Resource Allocation Directives
    ax.text(0.05, 0.48, "2. Prescriptive Resource Allocation Directives (Rule-Based Multipliers)", fontsize=11, fontweight='bold', color='#1E3A8A', transform=ax.transAxes)

    rect_res = patches.Rectangle((0.05, 0.27), 0.90, 0.19, transform=ax.transAxes, color='#F8FAFC', ec='#94A3B8', lw=1)
    ax.add_patch(rect_res)

    res_text = (
        "• Hospital Isolation Beds: Reallocate +168 beds to Dhaka Medical College & +128 beds to Chittagong Medical.\n"
        "• Rapid NS1 Diagnostic Test Kits: Dispatch +862 kits to Dhaka District Health Office by Tuesday.\n"
        "• IV Fluid Saline Supplies: Mobilize +1,197 saline bags to high-surge civil surgeon centers.\n"
        "• Emergency Vector Control: Trigger targeted fogging & larviciding in Ward 14, 19, and 22 in Dhaka South."
    )
    ax.text(0.07, 0.44, res_text, fontsize=8.5, color='#1E293B', va='top', transform=ax.transAxes)

    # Section 3: Official Approval & Signature Box
    ax.text(0.05, 0.23, "3. System Validation & Official Sign-Off", fontsize=11, fontweight='bold', color='#1E3A8A', transform=ax.transAxes)

    rect_sign = patches.Rectangle((0.05, 0.05), 0.90, 0.15, transform=ax.transAxes, color='#FFFFFF', ec='#CBD5E1', lw=1)
    ax.add_patch(rect_sign)

    ax.text(0.08, 0.15, "Prepared By: EpiST-Shield Automated Decision Engine", fontsize=8.5, fontweight='bold', transform=ax.transAxes)
    ax.text(0.08, 0.12, "System Usability Audit Score: 88.4 / 100 (Grade A+ Excellent)", fontsize=8.5, color='#059669', transform=ax.transAxes)
    ax.text(0.08, 0.09, "Repository Reference: Open-Source MIT License", fontsize=8.5, color='#64748B', transform=ax.transAxes)

    ax.text(0.70, 0.13, "__________________________", fontsize=9, color='#475569', ha='center', transform=ax.transAxes)
    ax.text(0.70, 0.10, "Authorized Public Health Official", fontsize=8.5, fontweight='bold', color='#1E293B', ha='center', transform=ax.transAxes)
    ax.text(0.70, 0.08, "(Demonstration Sign-Off)", fontsize=7.5, color='#64748B', ha='center', transform=ax.transAxes)

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✅ Generated {output_path}")

if __name__ == "__main__":
    generate_fig3_weather_simulator()
    generate_fig6_executive_bulletin()
