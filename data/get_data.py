from pathlib import Path
import shutil

import kagglehub

# Download latest version
path = kagglehub.dataset_download("muhammadshahidazeem/customer-churn-dataset")

download_dir = Path(path)
raw_file = Path(__file__).resolve().parent / "raw.csv"

csv_files = sorted(download_dir.glob("*.csv"))
if not csv_files:
	raise FileNotFoundError(f"No CSV file found in {download_dir}")

shutil.copy2(csv_files[0], raw_file)

print("Path to dataset files:", path)
print("Saved raw CSV to:", raw_file)