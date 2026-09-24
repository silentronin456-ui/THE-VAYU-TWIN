# SPASHT AI - Diagnostic Model Training (XGBoost)

> [!NOTE]
> **TO THE AI TRAINING TEAM:**
> The Diagnostic Model is a Supervised `XGBClassifier`. Its job is to look at a single 1Hz snapshot of the features (including the anomaly scores from the Health Engine) and instantly classify the specific failure mode.

## 1. Data Preprocessing (Handling the Phase Tag & Anomaly Scores)
*   Load all the generated fault `.csv` files and concatenate them into a massive Pandas DataFrame.
*   **Target (y):** Pop the `fault_label` column (Categorical String like "COOLANT_SYSTEM_LEAK") off the dataset. You will need to use `Scikit-Learn LabelEncoder` to turn these strings into integers for XGBoost.
*   **Features (X):** You must feed the 53 physical parameters, the 3 `anomaly_score` columns, **AND** the `flight.phase` tag to the model. Because XGBoost prefers numeric data, you must One-Hot Encode the phase column using Pandas before training:
    ```python
    # This turns the 1 string column into 7 binary columns (e.g. flight.phase_WARMUP = 1)
    # Total input features will now be 53 (Raw) + 3 (Anomaly Scores) + 7 (Phases) = 63.
    X = pd.get_dummies(X, columns=['flight.phase'])
    ```
*   Use `train_test_split` (80/20).

## 2. Model Architecture
Do not use PyTorch/Neural Networks for this. We need ultra-fast, lightweight inference for 1Hz data. Use XGBoost.

```python
import xgboost as xgb

# Initialize the XGBoost Classifier for Multi-class classification
model = xgb.XGBClassifier(
    objective='multi:softprob',
    num_class=19,  # 0 to 18
    max_depth=6,
    learning_rate=0.1,
    n_estimators=100,
    subsample=0.8,
    colsample_bytree=0.8,
    random_state=42,
    tree_method='hist' # Highly recommended for large datasets
)

# Train the model
model.fit(X_train, y_train)
```

## 3. Evaluation
*   Generate a **Confusion Matrix** to ensure the model isn't confusing a Coolant Leak (3) with a Radiator Blockage (4).
*   Ensure Accuracy > 95%.

## 4. Exporting to ONNX
You must export the trained XGBoost model to `.onnx` for the backend. Ensure the input shape matches the One-Hot Encoded feature count (63).

```python
from skl2onnx import convert_sklearn
from skl2onnx.common.data_types import FloatTensorType

# Define input shape (1 row, 63 features)
initial_type = [('float_input', FloatTensorType([None, 63]))]

# Convert
onnx_model = convert_sklearn(model, initial_types=initial_type)

# Save
with open("diagnostic_xgboost_v1.onnx", "wb") as f:
    f.write(onnx_model.SerializeToString())
```
