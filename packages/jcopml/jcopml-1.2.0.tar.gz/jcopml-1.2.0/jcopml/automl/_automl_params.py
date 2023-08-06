from jcopml.pipeline import num_pipe, cat_pipe
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.neighbors import KNeighborsRegressor, KNeighborsClassifier
from sklearn.svm import SVR, SVC
from xgboost import XGBRegressor, XGBClassifier
from sklearn.linear_model import ElasticNet, LogisticRegression
from jcopml.tuning import random_search_params as rsp, bayes_search_params as bsp

_reg_algo = ["rf", "knn", "svm", "xgb", "enet"]
_clf_algo = ["rf", "knn", "svm", "xgb", "logreg"]
_tree_algo = ["rf", "xgb"]
_impute = ["mean", "median", "knn"]


def _reg_map(algo, search_mode):
    f = rsp if search_mode == "random" else bsp

    _map = {
        "rf": (RandomForestRegressor(n_jobs=-1, random_state=42), f.rf_params, f.rf_poly_params),
        "knn": (KNeighborsRegressor(), f.knn_params, f.knn_poly_params),
        "svm": (SVR(max_iter=500), f.svm_params, f.svm_poly_params),
        "xgb": (XGBRegressor(n_jobs=-1, random_state=42), f.xgb_params, f.xgb_poly_params),
        "enet": (ElasticNet(), f.enet_params, f.enet_poly_params)
    }
    return _map[algo]


def _clf_map(algo, search_mode):
    f = rsp if search_mode == "random" else bsp

    _map = {
        "rf": (RandomForestClassifier(n_jobs=-1, random_state=42), f.rf_params, f.rf_poly_params),
        "knn": (KNeighborsClassifier(), f.knn_params, f.knn_poly_params),
        "svm": (SVC(max_iter=500), f.svm_params, f.svm_poly_params),
        "xgb": (XGBClassifier(n_jobs=-1, random_state=42), f.xgb_params, f.xgb_poly_params),
        "logreg": (LogisticRegression(), f.logreg_params, f.logreg_poly_params)
    }
    return _map[algo]


def _numeric_map(poly, scaling):
    if scaling:
        pipe = []
        for imp in _impute:
            if poly:
                pipe += [
                    num_pipe(impute=imp, poly=2, transform="yeo-johnson"),
                    num_pipe(impute=imp, poly=2, scaling="standard"),
                    num_pipe(impute=imp, poly=2, scaling="robust"),
                    num_pipe(impute=imp, poly=2, scaling="normalize"),
                    num_pipe(impute=imp, poly=2)
                ]
            else:
                pipe += [
                    num_pipe(impute=imp, transform="yeo-johnson"),
                    num_pipe(impute=imp, scaling="standard"),
                    num_pipe(impute=imp, scaling="robust"),
                    num_pipe(impute=imp, poly=2, scaling="normalize"),
                    num_pipe(impute=imp)
                ]
    else:
        if poly:
            pipe = [num_pipe(impute=imp, poly=2) for imp in _impute]
        else:
            pipe = [num_pipe(impute=imp) for imp in _impute]
    return pipe


def _categoric_map():
    return [cat_pipe(encoder="onehot")]


def autoreg_params(algo, search_mode, poly, scaling):
    if algo == "all":
        algo = _reg_algo
    elif algo == "tree":
        algo = _tree_algo

    params = []
    for a in algo:
        if a in _reg_algo:
            algorithm, param, poly_param = _reg_map(a, search_mode)
            p = poly_param if poly else param
            p["algo"] = [algorithm]
            p["prep__numeric"] = _numeric_map(poly, scaling)
            p["prep__categoric"] = _categoric_map()
            p["prep__numeric__imputer__add_indicator"] = [True, False]
            p["prep__categoric__imputer__add_indicator"] = [True, False]
            params.append(p)
        else:
            print(f"Available algorithms {tuple(_reg_algo)}. {a} is not available.")
    return params


def autoclf_params(algo, search_mode, poly, scaling):
    if algo == "all":
        algo = _clf_algo
    elif algo == "tree":
        algo = _tree_algo

    params = []
    for a in algo:
        if a in _clf_algo:
            algorithm, param, poly_param = _clf_map(a, search_mode)
            p = poly_param if poly else param
            p["algo"] = [algorithm]
            p["prep__numeric"] = _numeric_map(poly, scaling)
            p["prep__categoric"] = _categoric_map()
            p["prep__numeric__imputer__add_indicator"] = [True, False]
            p["prep__categoric__imputer__add_indicator"] = [True, False]
            params.append(p)
        else:
            print(f"Available algorithms {tuple(_clf_algo)}. {a} is not available.")
    return params
