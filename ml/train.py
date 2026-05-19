from preprocess import (
    preprocess_dataset, 
    split_data, 
    scale_features, 
    handle_imbalance, 
    select_and_save_features
)

df = preprocess_dataset()
select_and_save_features(df)
X_train, X_cv, X_test, y_train, y_cv, y_test = split_data(df)
X_train, X_cv, X_test = scale_features(X_train, X_cv, X_test)
X_train, y_train = handle_imbalance(X_train, y_train)