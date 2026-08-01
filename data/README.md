# Dataset Download & Preprocessing Guide

**Dataset Name**: LendingClub Accepted Loan Originations (2007–2018 Q4)  
**Official Source**: [Kaggle — LendingClub Loan Data](https://www.kaggle.com/datasets/wordsforthewise/lending-club)  
**License**: Public Domain / Open Data License  

---

## 1. Overview & Dataset Description

This repository utilizes the **LendingClub Accepted Loan Originations** dataset spanning 2007 to 2018 Q4, comprising $1,370,945$ mature binary credit records.

Due to GitHub's file size limit ($100\text{ MB}$ per file), the raw compressed dataset (`accepted_2007_to_2018Q4.csv.gz`, ~230 MB compressed / ~1.6 GB uncompressed) is excluded from version control via `.gitignore`.

---

## 2. Instructions to Obtain the Dataset

### Step 1: Download Raw Dataset
1. Visit the Kaggle LendingClub dataset page: [https://www.kaggle.com/datasets/wordsforthewise/lending-club](https://www.kaggle.com/datasets/wordsforthewise/lending-club).
2. Download `accepted_2007_to_2018Q4.csv.gz`.
3. Place the file inside the `data/raw/` directory:
   ```
   c:\Users\BIBEK\OneDrive\Desktop\Credit-Risk-Modelling\data\raw\accepted_2007_to_2018Q4.csv.gz
   ```

### Step 2: Automated Preprocessing & Synthetic Sample Generation
If running without downloading the full 1.6 GB dataset, the dashboard and test suites automatically generate a synthetic baseline sample for demonstration and verification via `dashboard/utils/data_loader.py`.

---

## 3. Directory Layout

```
data/
├── README.md               # Dataset documentation & acquisition instructions
├── raw/                    # Place raw accepted_2007_to_2018Q4.csv.gz here (git-ignored)
└── processed/              # Processed feature-engineered dataset output (git-ignored)
```
