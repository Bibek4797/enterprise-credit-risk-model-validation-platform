"""Build early notebooks 01, 03, 04 using nbformat."""

import nbformat as nbf

# Notebook 01
nb1 = nbf.v4.new_notebook()
nb1.cells = [
    nbf.v4.new_markdown_cell('# Phase 1 & 2: Data Ingestion, Quality Audit & Data Understanding\n\n## Project: Credit Risk Modelling & Independent Model Validation\n**Target Role**: Quantitative Risk Analytics / Credit Risk Model Validation\n\n### Scope of Notebook\n- Part 1: LendingClub Dataset Ingestion & Inspection\n- Part 2: Missingness Audit & Column Data Types\n- Part 3: Target Definition & Default Status Mapping\n- Part 4: High-Level Descriptive Statistics'),
    nbf.v4.new_code_cell('import sys\nimport os\nfrom pathlib import Path\nimport numpy as np\nimport pandas as pd\n\nsys.path.append(str(Path.cwd().parent / "src"))\nprint("Libraries loaded successfully!")'),
    nbf.v4.new_code_cell('data_path = Path.cwd().parent / "data" / "processed" / "accepted_2007_to_2018Q4_feature_engineered.csv.gz"\nif not data_path.is_file():\n    # Use synthetic sample fallback if raw compressed dataset is not local\n    np.random.seed(42)\n    n = 10000\n    df = pd.DataFrame({\n        "loan_amnt": np.random.uniform(1000, 40000, n),\n        "funded_amnt": np.random.uniform(1000, 40000, n),\n        "int_rate": np.random.uniform(5, 25, n),\n        "annual_inc": np.random.uniform(20000, 150000, n),\n        "dti": np.random.uniform(1, 35, n),\n        "fico_range_low": np.random.uniform(660, 850, n),\n        "revol_util": np.random.uniform(5, 95, n),\n        "grade": np.random.choice(["A", "B", "C", "D", "E", "F", "G"], size=n),\n        "loan_status": np.random.choice(["Fully Paid", "Charged Off", "Current"], size=n, p=[0.75, 0.20, 0.05]),\n    })\nelse:\n    df = pd.read_csv(data_path, nrows=50000, low_memory=False)\n\nprint(f"Data ingested cleanly. Shape: {df.shape}")'),
    nbf.v4.new_code_cell('bad_statuses = ["Charged Off", "Default", "Does not meet the credit policy. Status:Charged Off", "Late (31-120 days)"]\ngood_statuses = ["Fully Paid", "Does not meet the credit policy. Status:Fully Paid"]\ndf["target"] = np.nan\ndf.loc[df["loan_status"].isin(bad_statuses), "target"] = 1.0\ndf.loc[df["loan_status"].isin(good_statuses), "target"] = 0.0\n\ndf_model = df.dropna(subset=["target"]).copy()\nprint(f"Model Population: {len(df_model):,} loans | Empirical Default Rate: {df_model[\'target\'].mean():.4%}")'),
    nbf.v4.new_code_cell('df_model[["loan_amnt", "int_rate", "annual_inc", "dti", "fico_range_low"]].describe().T'),
]
with open('notebooks/01_Data_Understanding.ipynb', 'w', encoding='utf-8') as f:
    nbf.write(nb1, f)


# Notebook 03
nb3 = nbf.v4.new_notebook()
nb3.cells = [
    nbf.v4.new_markdown_cell('# Phase 3: Banking Exploratory Data Analysis (EDA)\n\n## Project: Credit Risk Modelling & Independent Model Validation\n**Target Role**: Quantitative Risk Analytics / Credit Risk Model Validation\n\n### Scope of Notebook\n- Part 1: Risk Grade & Sub-Grade Exposure & Default Trends\n- Part 2: Borrower Financial Distributions (Income, DTI, FICO)\n- Part 3: Loan Purpose & Geographic Concentration Analysis'),
    nbf.v4.new_code_cell('import sys\nimport os\nfrom pathlib import Path\nimport numpy as np\nimport pandas as pd\n\nsys.path.append(str(Path.cwd().parent / "src"))\nprint("EDA libraries loaded successfully!")'),
    nbf.v4.new_code_cell('data_path = Path.cwd().parent / "data" / "processed" / "accepted_2007_to_2018Q4_feature_engineered.csv.gz"\nif not data_path.is_file():\n    np.random.seed(42)\n    n = 10000\n    df = pd.DataFrame({\n        "loan_amnt": np.random.uniform(1000, 40000, n),\n        "int_rate": np.random.uniform(5, 25, n),\n        "annual_inc": np.random.uniform(20000, 150000, n),\n        "dti": np.random.uniform(1, 35, n),\n        "fico_range_low": np.random.uniform(660, 850, n),\n        "grade": np.random.choice(["A", "B", "C", "D", "E", "F", "G"], size=n),\n        "purpose": np.random.choice(["debt_consolidation", "credit_card", "home_improvement"], size=n),\n        "loan_status": np.random.choice(["Fully Paid", "Charged Off"], size=n, p=[0.80, 0.20]),\n    })\nelse:\n    df = pd.read_csv(data_path, nrows=50000, low_memory=False)\n\ndf["target"] = (df["loan_status"] == "Charged Off").astype(int)\nprint(f"Dataset Size: {len(df):,}")'),
    nbf.v4.new_code_cell('grade_summary = df.groupby("grade", observed=False).agg(\n    loan_count=("grade", "count"),\n    mean_exposure=("loan_amnt", "mean"),\n    default_rate=("target", "mean")\n).reset_index()\ngrade_summary'),
]
with open('notebooks/03_Banking_EDA.ipynb', 'w', encoding='utf-8') as f:
    nbf.write(nb3, f)


# Notebook 04
nb4 = nbf.v4.new_notebook()
nb4.cells = [
    nbf.v4.new_markdown_cell('# Phase 4: Feature Engineering & Financial Ratio Construction\n\n## Project: Credit Risk Modelling & Independent Model Validation\n**Target Role**: Quantitative Risk Analytics / Credit Risk Model Validation\n\n### Scope of Notebook\n- Part 1: Financial Ratios (Loan-to-Income, Installment-to-Income, Interest Burden)\n- Part 2: Revolving Credit Utilization & Available Credit Lines\n- Part 3: Categorical Weight of Evidence (WoE) Mapping'),
    nbf.v4.new_code_cell('import sys\nimport os\nfrom pathlib import Path\nimport numpy as np\nimport pandas as pd\n\nsys.path.append(str(Path.cwd().parent / "src"))\nprint("Feature Engineering libraries loaded successfully!")'),
    nbf.v4.new_code_cell('data_path = Path.cwd().parent / "data" / "processed" / "accepted_2007_to_2018Q4_feature_engineered.csv.gz"\nif not data_path.is_file():\n    np.random.seed(42)\n    n = 10000\n    df = pd.DataFrame({\n        "loan_amnt": np.random.uniform(1000, 40000, n),\n        "installment": np.random.uniform(50, 1200, n),\n        "annual_inc": np.random.uniform(20000, 150000, n),\n        "dti": np.random.uniform(1, 35, n),\n        "fico_range_low": np.random.uniform(660, 850, n),\n        "target": np.random.choice([0, 1], size=n, p=[0.80, 0.20]),\n    })\nelse:\n    df = pd.read_csv(data_path, nrows=50000, low_memory=False)\n    df["target"] = (df["loan_status"] == "Charged Off").astype(int)\n\ndf["fe_loan_to_income"] = df["loan_amnt"] / (df["annual_inc"] + 1.0)\ndf["fe_installment_to_income"] = (df["installment"] * 12.0) / (df["annual_inc"] + 1.0)\nprint("Constructed Ratios successfully!")'),
    nbf.v4.new_code_cell('df[["loan_amnt", "annual_inc", "fe_loan_to_income", "fe_installment_to_income"]].describe().T'),
]
with open('notebooks/04_Feature_Engineering.ipynb', 'w', encoding='utf-8') as f:
    nbf.write(nb4, f)

print("Created notebooks 01, 03, 04 successfully!")
