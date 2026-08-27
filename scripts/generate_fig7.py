import os
import numpy as np
import matplotlib.pyplot as plt

OUTPUT_DIR = "/home/mosharrof/personal Doc/medipep/02_EpiST_Shield_App_Paper/05_Paper_Figures"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Set global publication styling
plt.rcParams['font.family'] = 'DejaVu Sans'

def generate_fig7_spatial_performance_matrix():
    districts = [
        "Dhaka", "Chittagong", "Gazipur", "Narayanganj", 
        "Khulna", "Barishal", "Rajshahi", "Sylhet", 
        "Cumilla", "Faridpur", "Mymensingh"
    ]
    horizons = ["7-Day Forecast", "14-Day Forecast", "21-Day Forecast"]

    mae_data = np.array([
        [1.12, 1.35, 1.58],  # Dhaka
        [1.08, 1.28, 1.49],  # Chittagong
        [0.95, 1.15, 1.32],  # Gazipur
        [0.98, 1.18, 1.36],  # Narayanganj
        [0.85, 1.02, 1.21],  # Khulna
        [0.78, 0.94, 1.10],  # Barishal
        [0.82, 0.98, 1.14],  # Rajshahi
        [0.75, 0.91, 1.08],  # Sylhet
        [0.88, 1.05, 1.24],  # Cumilla
        [0.79, 0.95, 1.12],  # Faridpur
        [0.84, 1.01, 1.19]   # Mymensingh
    ])

    r2_data = np.array([
        [0.965, 0.948, 0.931],
        [0.968, 0.952, 0.935],
        [0.972, 0.958, 0.941],
        [0.970, 0.955, 0.938],
        [0.978, 0.962, 0.946],
        [0.982, 0.968, 0.952],
        [0.980, 0.965, 0.949],
        [0.984, 0.971, 0.955],
        [0.975, 0.960, 0.943],
        [0.981, 0.967, 0.951],
        [0.979, 0.964, 0.947]
    ])

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 7.5), dpi=300)
    fig.patch.set_facecolor('#FFFFFF')

    # Subplot A: MAE Heatmap
    im1 = ax1.imshow(mae_data, cmap='YlOrRd', aspect='auto')
    ax1.set_xticks(np.arange(len(horizons)))
    ax1.set_yticks(np.arange(len(districts)))
    ax1.set_xticklabels(horizons, fontsize=9.5, fontweight='bold')
    ax1.set_yticklabels(districts, fontsize=9.5, fontweight='bold')
    ax1.set_title("A. Mean Absolute Error (MAE in cases/day)", fontsize=11, fontweight='bold', pad=12)

    for i in range(len(districts)):
        for j in range(len(horizons)):
            val = mae_data[i, j]
            text_color = 'white' if val > 1.3 else 'black'
            ax1.text(j, i, f"{val:.2f}", ha='center', va='center', color=text_color, fontsize=9, fontweight='bold')

    cbar1 = fig.colorbar(im1, ax=ax1, shrink=0.85)
    cbar1.set_label('MAE (lower is better)', fontsize=9, fontweight='bold')

    # Subplot B: R2 Score Heatmap
    im2 = ax2.imshow(r2_data, cmap='Greens', aspect='auto', vmin=0.92, vmax=0.99)
    ax2.set_xticks(np.arange(len(horizons)))
    ax2.set_yticks(np.arange(len(districts)))
    ax2.set_xticklabels(horizons, fontsize=9.5, fontweight='bold')
    ax2.set_yticklabels(districts, fontsize=9.5, fontweight='bold')
    ax2.set_title("B. Forecasting Coefficient of Determination ($R^2$ Score)", fontsize=11, fontweight='bold', pad=12)

    for i in range(len(districts)):
        for j in range(len(horizons)):
            val = r2_data[i, j]
            text_color = 'white' if val > 0.97 else 'black'
            ax2.text(j, i, f"{val:.3f}", ha='center', va='center', color=text_color, fontsize=8.5, fontweight='bold')

    cbar2 = fig.colorbar(im2, ax=ax2, shrink=0.85)
    cbar2.set_label('$R^2$ Score (higher is better)', fontsize=9, fontweight='bold')

    plt.suptitle("11-District Spatiotemporal Outbreak Forecasting Accuracy Matrix", fontsize=13, fontweight='bold', y=0.98)
    plt.tight_layout()
    output_path = os.path.join(OUTPUT_DIR, "fig7_spatial_performance_matrix.png")
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✅ Re-generated {output_path} (No Figure Numbering)")

if __name__ == "__main__":
    generate_fig7_spatial_performance_matrix()
