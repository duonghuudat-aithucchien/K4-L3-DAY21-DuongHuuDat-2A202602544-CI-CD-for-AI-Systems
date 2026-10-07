import mlflow
import mlflow.sklearn
import pandas as pd
import yaml
import json
import joblib
import os
import numpy as np
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.metrics import accuracy_score, f1_score, confusion_matrix, classification_report

# Nguong chat luong cua lab nay la f1_score, KHONG phai accuracy.
# Ly do: bo du lieu Adult co ty le lop 75/25. Mot mo hinh doan bua
# "thu nhap thap" cho moi mau da dat accuracy 0.75 ma khong hoc duoc gi.
F1_THRESHOLD = 0.65


def train(
    params: dict,
    data_path: str = "data/train_batch1.csv",
    eval_path: str = "data/holdout.csv",
) -> float:
    """
    Huan luyen mo hinh va ghi nhan ket qua vao MLflow.
    """

    # Bonus 1: Tracking MLflow Tu Xa (Hoặc fallback về local nếu bỏ qua Bonus 1)
    tracking_uri = os.getenv("MLFLOW_TRACKING_URI") or "sqlite:///mlflow.db"
    mlflow.set_tracking_uri(tracking_uri)

    # TODO 1: Doc du lieu huan luyen va danh gia
    df_train = pd.read_csv(data_path)
    df_eval  = pd.read_csv(eval_path)

    # TODO 2: Tach dac trung (X) va nhan (y)
    X_train = df_train.drop(columns=["target"])
    y_train = df_train["target"]
    X_eval  = df_eval.drop(columns=["target"])
    y_eval  = df_eval["target"]

    # Bonus 5: Canh Bao Lech Lac Du Lieu
    pos_rate = y_train.mean()
    if abs(pos_rate - 0.248) > 0.05:
        print(f"WARNING: Ty le lop duong trong tap huan luyen ({pos_rate:.4f}) lech qua 5% so voi 0.248")

    with mlflow.start_run():

        # TODO 3: Ghi nhan cac sieu tham so
        mlflow.log_params(params)
        mlflow.log_metric("pos_rate", pos_rate)

        # TODO 4: Khoi tao va huan luyen GradientBoostingClassifier
        model = GradientBoostingClassifier(
            n_estimators=params["n_estimators"],
            learning_rate=params["learning_rate"],
            max_depth=params["max_depth"],
            random_state=42
        )
        model.fit(X_train, y_train)

        # Bonus 2: Dieu Chinh Nguong Quyet Dinh
        probs = model.predict_proba(X_eval)[:, 1]
        best_f1 = 0.0
        best_threshold = 0.5
        for threshold in np.arange(0.1, 0.95, 0.05):
            preds_thresh = (probs >= threshold).astype(int)
            f1_thresh = f1_score(y_eval, preds_thresh)
            if f1_thresh > best_f1:
                best_f1 = f1_thresh
                best_threshold = float(threshold)
        
        preds_default = (probs >= 0.5).astype(int)
        f1_default = f1_score(y_eval, preds_default)
        print(f"F1 default (0.5): {f1_default:.4f}")
        print(f"F1 best ({best_threshold:.2f}): {best_f1:.4f}")

        # Choose best for final metrics
        final_preds = (probs >= best_threshold).astype(int)
        acc = accuracy_score(y_eval, final_preds)

        # TODO 6: Ghi nhan chi so vao MLflow
        mlflow.log_metric("f1_score", best_f1)
        mlflow.log_metric("accuracy", acc)
        mlflow.log_metric("best_threshold", best_threshold)
        mlflow.sklearn.log_model(model, "model")

        # TODO 7: In ket qua ra man hinh
        print(f"F1: {best_f1:.4f} | Accuracy: {acc:.4f}")

        # Bonus 3: Bao Cao Precision / Recall Tu Dong
        cm = confusion_matrix(y_eval, final_preds)
        report_str = classification_report(y_eval, final_preds)
        
        os.makedirs("outputs", exist_ok=True)
        with open("outputs/detail.txt", "w") as f:
            f.write("Confusion Matrix:\n")
            f.write(str(cm) + "\n\n")
            f.write("Classification Report:\n")
            f.write(report_str + "\n\n")
            f.write("Giai thich:\n")
            f.write("- Bo sot nguoi thu nhap cao (Recall thap o lop 1): Mat co hoi tiep thi hoac cap tin dung.\n")
            f.write("- Gan nham nguoi thu nhap thap (Precision thap o lop 1): Ton chi phi tiep thi vo ich.\n")

        # TODO 8: Luu metrics ra file outputs/report.json
        with open("outputs/report.json", "w") as f:
            json.dump({
                "f1_score": best_f1, 
                "accuracy": acc, 
                "best_threshold": best_threshold, 
                "pos_rate": pos_rate
            }, f)

        # TODO 9: Luu mo hinh ra file models/model.joblib
        os.makedirs("models", exist_ok=True)
        joblib.dump(model, "models/model.joblib")

    # TODO 10: Tra ve f1
    return best_f1


if __name__ == "__main__":
    with open("params.yaml") as f:
        params = yaml.safe_load(f)
    train(params)

