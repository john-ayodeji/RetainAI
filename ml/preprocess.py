from pathlib import Path

import pandas as pd
import json
import joblib
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from imblearn.over_sampling import SMOTE

def load_data(train_path, test_path=None):
    """
    Loads training CSV (and optional test CSV) into a single DataFrame.
    The dataset ships as two files: training-master and testing-master.
    We merge them so we control the split ourselves.
    """
    train = pd.read_csv(train_path)
    if test_path:
        test = pd.read_csv(test_path)
        df = pd.concat([train, test], ignore_index=True)
    else:
        df = train
    return df


def preprocess_dataset(raw_path='data/raw.csv', processed_path='data/processed.csv'):
    """
    Runs the full preprocessing pipeline on the raw dataset and saves the result.
    """
    df = load_data(raw_path)
    df = clean_data(df)
    df = engineer_features(df)
    df = encode_features(df)

    processed_path = Path(processed_path)
    processed_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(processed_path, index=False)

    print(f"Processed dataset saved to {processed_path}")
    return df

def clean_data(df):
    """
    Handles nulls, types, duplicates, and impossible values.
    Even if the dataset looks clean, we enforce this defensively
    so the pipeline doesn't break on real-world data.
    """
    df = df.copy()

    df = df.drop_duplicates()

    if 'CustomerID' in df.columns:
        df = df.drop(columns=['CustomerID'])

    df['Age'] = pd.to_numeric(df['Age'], errors='coerce')
    df['Tenure'] = pd.to_numeric(df['Tenure'], errors='coerce')
    df['Usage Frequency'] = pd.to_numeric(df['Usage Frequency'], errors='coerce')
    df['Support Calls'] = pd.to_numeric(df['Support Calls'], errors='coerce')
    df['Payment Delay'] = pd.to_numeric(df['Payment Delay'], errors='coerce')
    df['Total Spend'] = pd.to_numeric(df['Total Spend'], errors='coerce')
    df['Last Interaction'] = pd.to_numeric(df['Last Interaction'], errors='coerce')

    numeric_cols = ['Age', 'Tenure', 'Usage Frequency', 'Support Calls',
                    'Payment Delay', 'Total Spend', 'Last Interaction']
    for col in numeric_cols:
        df[col] = df[col].fillna(df[col].median())

    categorical_cols = ['Gender', 'Subscription Type', 'Contract Length']
    for col in categorical_cols:
        df[col] = df[col].fillna(df[col].mode()[0])

    df = df[df['Age'] > 0]
    df = df[df['Tenure'] >= 0]
    df = df[df['Support Calls'] >= 0]
    df = df[df['Payment Delay'] >= 0]
    df = df[df['Total Spend'] >= 0]
    df = df[df['Last Interaction'] >= 0]
    df = df[df['Usage Frequency'] >= 0]

    df['Gender'] = df['Gender'].str.strip().str.title()
    df['Subscription Type'] = df['Subscription Type'].str.strip().str.title()
    df['Contract Length'] = df['Contract Length'].str.strip().str.title()

    return df

def engineer_features(df):
    """
    Creates new features derived from existing columns.
    These often have more predictive power than raw values.
    """
    df = df.copy()

    df['spend_per_tenure'] = df['Total Spend'] / (df['Tenure'] + 1)

    df['support_call_rate'] = df['Support Calls'] / (df['Tenure'] + 1)

    df['usage_per_tenure'] = df['Usage Frequency'] / (df['Tenure'] + 1)

    df['is_dormant'] = (df['Last Interaction'] > 30).astype(int)

    df['has_payment_issues'] = (df['Payment Delay'] > 0).astype(int)

    df['spend_tier'] = pd.cut(
        df['Total Spend'],
        bins=[0, 200, 500, float('inf')],
        labels=[0, 1, 2]
    ).astype(int)

    df['age_group'] = pd.cut(
        df['Age'],
        bins=[0, 25, 40, 60, float('inf')],
        labels=[0, 1, 2, 3]
    ).astype(int)

    return df

def encode_features(df):
    """
    Converts categorical columns to numbers.
    One-hot for nominal (no order), label for binary.
    """
    df = df.copy()

    df['Gender'] = df['Gender'].map({'Male': 0, 'Female': 1})

    df = pd.get_dummies(df, columns=['Subscription Type'], prefix='sub', drop_first=False)

    df = pd.get_dummies(df, columns=['Contract Length'], prefix='contract', drop_first=False)

    dummy_cols = [c for c in df.columns if c.startswith('sub_') or c.startswith('contract_')]
    df[dummy_cols] = df[dummy_cols].astype(int)

    return df

def scale_features(X_train, X_cv=None, X_test=None, save_path='ml/artifacts/scaler.pkl'):
    """
    Fits scaler on training data only, then transforms the validation and test sets
    with the same fitted scaler.
    Saves fitted scaler so the API can use it during inference.
    """
    scaler = StandardScaler()

    cols_to_scale = [
        'Age', 'Tenure', 'Usage Frequency', 'Support Calls',
        'Payment Delay', 'Total Spend', 'Last Interaction',
        'spend_per_tenure', 'support_call_rate', 'usage_per_tenure'
    ]

    cols_to_scale = [c for c in cols_to_scale if c in X_train.columns]

    X_train[cols_to_scale] = scaler.fit_transform(X_train[cols_to_scale])

    if X_cv is not None:
        X_cv[cols_to_scale] = scaler.transform(X_cv[cols_to_scale])

    if X_test is not None:
        X_test[cols_to_scale] = scaler.transform(X_test[cols_to_scale])

    joblib.dump(scaler, save_path)
    print(f"Scaler saved to {save_path}")

    if X_cv is not None and X_test is not None:
        return X_train, X_cv, X_test
    if X_test is not None:
        return X_train, X_test
    if X_cv is not None:
        return X_train, X_cv
    return X_train

def handle_imbalance(X_train, y_train):
    """
    Applies SMOTE to oversample the minority class (churned customers).
    Only applied to training data — never test data.
    """
    smote = SMOTE(random_state=42)
    X_resampled, y_resampled = smote.fit_resample(X_train, y_train)

    original_churn_rate = y_train.mean()
    new_churn_rate = y_resampled.mean()
    print(f"Churn rate before SMOTE: {original_churn_rate:.1%}")
    print(f"Churn rate after SMOTE:  {new_churn_rate:.1%}")

    return X_resampled, y_resampled

def select_and_save_features(df, target_col='Churn',
                              save_path='ml/artifacts/feature_names.json'):
    """
    Drops the target and any leakage columns.
    Saves the final feature list so the API knows exactly what columns to expect.
    """
    drop_cols = [target_col]

    feature_cols = [c for c in df.columns if c not in drop_cols]

    with open(save_path, 'w') as f:
        json.dump(feature_cols, f, indent=2)

    print(f"Feature list saved: {len(feature_cols)} features")
    return feature_cols

def split_data(df, target_col='Churn', cv_size=0.15, test_size=0.15, random_state=42):
    """
    Stratified split into train, cross-validation, and test sets.
    Returns X_train, X_cv, X_test, y_train, y_cv, y_test.
    """
    X = df.drop(columns=[target_col])
    y = df[target_col]

    X_train, X_temp, y_train, y_temp = train_test_split(
        X,
        y,
        test_size=cv_size + test_size,
        stratify=y,
        random_state=random_state,
    )

    cv_ratio = cv_size / (cv_size + test_size)

    X_cv, X_test, y_cv, y_test = train_test_split(
        X_temp,
        y_temp,
        test_size=1 - cv_ratio,
        stratify=y_temp,
        random_state=random_state,
    )

    print(f"Train: {len(X_train)} rows | CV: {len(X_cv)} rows | Test: {len(X_test)} rows")
    print(
        f"Train churn rate: {y_train.mean():.1%} | CV churn rate: {y_cv.mean():.1%} | "
        f"Test churn rate: {y_test.mean():.1%}"
    )

    return X_train, X_cv, X_test, y_train, y_cv, y_test