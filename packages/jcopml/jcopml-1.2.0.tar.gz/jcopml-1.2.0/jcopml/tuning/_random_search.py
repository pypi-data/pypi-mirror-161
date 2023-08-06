from jcopml.tuning.space import Integer, Real


class RandomSearchParams:
    def __init__(self):
        self.rf_params = {
            "algo__n_estimators": Integer(100, 200),
            "algo__max_depth": Integer(20, 80),
            "algo__max_features": Real(0.1, 1),
            "algo__min_samples_leaf": Integer(1, 20)
        }

        self.knn_params = {
            "algo__n_neighbors": Integer(1, 40),
            "algo__weights": ['uniform', 'distance'],
            "algo__p": Real(1, 2)
        }

        self.svm_params = {
            "algo__gamma": Real(-3, 3, prior='log-uniform'),
            "algo__C": Real(-3, 3, prior='log-uniform')
        }

        self.xgb_params = {
            "algo__max_depth": Integer(1, 10),
            "algo__learning_rate": Real(-2, 0, prior='log-uniform'),
            "algo__n_estimators": Integer(100, 200),
            "algo__subsample": Real(0.3, 0.8),
            "algo__gamma": Integer(1, 10),
            "algo__colsample_bytree": Real(0.1, 1),
            "algo__reg_alpha": Real(-3, 1, prior='log-uniform'),
            "algo__reg_lambda": Real(-3, 1, prior='log-uniform')
        }

        self.linreg_params = {
            "algo__fit_intercept": [True, False]
        }

        self.enet_params = {
            "algo__fit_intercept": [True, False],
            "algo__alpha": Real(-4, 2, prior='log-uniform'),
            "algo__l1_ratio": Real(0, 1)
        }

        self.logreg_params = {
            "algo__fit_intercept": [True, False],
            "algo__C": Real(-3, 3, prior='log-uniform')
        }

        prep_poly_params = {
            "prep__numeric__poly__degree": Integer(1, 3),
            "prep__numeric__poly__interaction_only": [True, False]
        }

        self.rf_poly_params = {**prep_poly_params, **self.rf_params}

        self.knn_poly_params = {**prep_poly_params, **self.knn_params}

        self.svm_poly_params = {**prep_poly_params, **self.svm_params}

        self.xgb_poly_params = {**prep_poly_params, **self.xgb_params}

        self.linreg_poly_params = {**prep_poly_params, **self.linreg_params}

        self.enet_poly_params = {**prep_poly_params, **self.enet_params}

        self.logreg_poly_params = {**prep_poly_params, **self.logreg_params}


random_search_params = RandomSearchParams()
