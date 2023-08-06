import numpy as np
import optuna
import sklearn.datasets
import sklearn.metrics
import xgboost as xgb
from sklearn.model_selection import train_test_split


def objective(trial):
    # Load our dataset
    X, y = sklearn.datasets.load_breast_cancer(return_X_y=True)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25)
    dtrain = xgb.DMatrix(X_train, label=y_train)
    dtest = xgb.DMatrix(X_test, label=y_test)

    # Get set of hyperparameters
    param = {
        "silent": 1,
        "objective": "binary:logistic",
        "booster": trial.suggest_categorical("booster", ["gbtree", "dart"]),
        "lambda": trial.suggest_float("lambda", 1e-8, 1.0, log=True),
        "alpha": trial.suggest_float("alpha", 1e-8, 1.0, log=True),
        "max_depth": trial.suggest_int("max_depth", 1, 9),
        "eta": trial.suggest_float("eta", 1e-8, 1.0, log=True),
        "gamma": trial.suggest_float("gamma", 1e-8, 1.0, log=True),
        "grow_policy": trial.suggest_categorical(
            "grow_policy", ["depthwise", "lossguide"]
        ),
    }

    # Train XGBoost model
    bst = xgb.train(param, dtrain)
    preds = bst.predict(dtest)

    # Compute and return model accuracy
    pred_labels = np.rint(preds)
    accuracy = sklearn.metrics.accuracy_score(y_test, pred_labels)
    return accuracy


import coiled
import dask_optuna
import joblib
from dask.distributed import Client

# Create a Dask cluster with Coiled
cluster = coiled.Cluster(n_workers=10, software="optuna-example", name="optuna-example")
# Connect Dask to our cluster
client = Client(cluster)
print(f"Dask dashboard is available at {client.dashboard_link}")

# Create Dask-compatible Optuna storage class
storage = dask_optuna.DaskStorage()

# Run 500 optimizations trial on our cluster
study = optuna.create_study(direction="maximize", storage=storage)
with joblib.parallel_backend("dask"):
    study.optimize(objective, n_trials=500, n_jobs=-1)

# once your computation is done, close the cluster
cluster.close()
# Close the client
client.close()
