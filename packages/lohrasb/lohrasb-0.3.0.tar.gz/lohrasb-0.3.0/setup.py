# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['lohrasb', 'lohrasb.examples', 'lohrasb.utils']

package_data = \
{'': ['*']}

install_requires = \
['catboost>=1.0.6,<2.0.0',
 'category-encoders>=2.5.0,<3.0.0',
 'feature-engine>=1.4.1,<2.0.0',
 'imblearn>=0.0,<0.1',
 'ipykernel>=6.15.1,<7.0.0',
 'lightgbm>=3.3.2,<4.0.0',
 'nox>=2022.1.7,<2023.0.0',
 'numpy>=1.23.0,<2.0.0',
 'optuna>=2.10.1,<3.0.0',
 'pandas>=1.4.3,<2.0.0',
 'scipy>=1.8.1,<2.0.0',
 'sklearn>=0.0,<0.1',
 'xgboost>=1.6.1,<2.0.0']

setup_kwargs = {
    'name': 'lohrasb',
    'version': '0.3.0',
    'description': 'Using optuna search optimizer to estimate best tree based estimator compatible with scikit-learn',
    'long_description': '# lohrasb\n\nlohrasb is a package built to ease machine learning development. It uses [Optuna](https://optuna.readthedocs.io/en/stable/index.html) to tune most of the tree-based estimators of sickit-learn. It is compatible with [scikit-learn](https://scikit-learn.org) pipeline.\n\n\n## Introduction\n\nBaseModel of lohrasb package can receive various parameters. From a tree-based estimator class to its tunning parameters and from Grid search, Random Search, or [Optuna](https://optuna.readthedocs.io/en/stable/index.html)  to their parameters. Samples will be split to train and validation set, and then optimization will estimate optimal related parameters.\n\n## Installation\n\nlohrasb package is available on PyPI and can be installed with pip:\n\n```sh\npip install lohrasb\n```\n\n\n## Supported estimators for this package\n\n- XGBRegressor  [XGBoost](https://github.com/dmlc/xgboost)\n- XGBClassifier [XGBoost](https://github.com/dmlc/xgboost)\n- RandomForestClassifier \n- RandomForestRegressor \n- CatBoostClassifier \n- CatBoostRegressor \n- BalancedRandomForestClassifier \n- LGBMClassifier [LightGBM](https://github.com/microsoft/LightGBM)\n- LGBMRegressor [LightGBM](https://github.com/microsoft/LightGBM)\n\n## Usage\n\n- Tunning best parameters of a tree-based model using [Optuna](https://optuna.readthedocs.io/en/stable/index.html) , [GridSearchCV](https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.GridSearchCV.html) or [RandomizedSearchCV](https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.RandomizedSearchCV.html).\n\n\n## Examples \n\nThere are some examples  available in the [examples](https://github.com/drhosseinjavedani/lohrasb/tree/main/lohrasb/examples). \n\n### Import required libraries\n```\nfrom lohrasb.best_estimator import BaseModel\nimport xgboost\nfrom optuna.pruners import HyperbandPruner\nfrom optuna.samplers._tpe.sampler import TPESampler\nfrom sklearn.model_selection import KFold,train_test_split\nimport pandas as pd\nfrom sklearn.pipeline import Pipeline\nfrom feature_engine.imputation import (\n    CategoricalImputer,\n    MeanMedianImputer\n    )\nfrom category_encoders import OrdinalEncoder\nfrom sklearn.linear_model import LogisticRegression\nfrom sklearn.metrics import (\n    classification_report,\n    confusion_matrix,\n    f1_score)\n```\n\n### Use Adult Data Set (a classification problem)\n```\nurldata= "https://archive.ics.uci.edu/ml/machine-learning-databases/adult/adult.data"\n# column names\ncol_names=[\n"age", "workclass", "fnlwgt" , "education" ,"education-num",\n"marital-status","occupation","relationship","race","sex","capital-gain",\n"capital-loss","hours-per-week","native-country","label"\n]\ndata.head()\n# read data\ndata = pd.read_csv(urldata,header=None,names=col_names,sep=\',\')\n```\n### Define labels\n```\ndata.loc[data[\'label\']==\'<=50K\',\'label\']=0\ndata.loc[data[\'label\']==\' <=50K\',\'label\']=0\n\ndata.loc[data[\'label\']==\'>50K\',\'label\']=1\ndata.loc[data[\'label\']==\' >50K\',\'label\']=1\n\ndata[\'label\']=data[\'label\'].astype(int)\n\n```\n\n### Train test split\n```\nX = data.loc[:, data.columns != "label"]\ny = data.loc[:, data.columns == "label"]\nX_train, X_test, y_train, y_test =train_test_split(X, y, \n    test_size=0.33, stratify=y[\'label\'], random_state=42)\n\n```\n\n### Find feature types for later use\n\n```\nint_cols =  X_train.select_dtypes(include=[\'int\']).columns.tolist()\nfloat_cols =  X_train.select_dtypes(include=[\'float\']).columns.tolist()\ncat_cols =  X_train.select_dtypes(include=[\'object\']).columns.tolist()\n\n```\n\n### Define estimator and set its arguments \n```\n\n\nSFC_XGBCLS_GRID = BaseModel(\n        estimator=xgboost.XGBClassifier(),\n        estimator_params={\n            "max_depth": [4, 5],\n            "min_child_weight": [0.1, 0.9],\n            "gamma": [1, 9],\n            "booster": ["gbtree"],\n        },\n        hyper_parameter_optimization_method="grid",\n        measure_of_accuracy="f1",\n        test_size=0.33,\n        cv=KFold(n_splits=3,random_state=42,shuffle=True),\n        with_stratified=True,\n        verbose=3,\n        random_state=42,\n        n_jobs=-1,\n        n_iter=100,\n        eval_metric="auc",\n        number_of_trials=10,\n        sampler=TPESampler(),\n        pruner=HyperbandPruner(),\n\n    )\n\n\n```\n\n### Build sklearn Pipeline  \n```\n\n\npipeline =Pipeline([\n            # int missing values imputers\n            (\'intimputer\', MeanMedianImputer(\n                imputation_method=\'median\', variables=int_cols)),\n            # category missing values imputers\n            (\'catimputer\', CategoricalImputer(variables=cat_cols)),\n            #\n            (\'catencoder\', OrdinalEncoder()),\n            # classification model\n            (\'xgboost\', SFC_XGBCLS_GRID)\n\n\n ])\n\n```\n### Run Pipeline  \n\n```\npipeline.fit(X_train,y_train)\ny_pred = pipeline.predict(X_test)\n```\n\n## License\nLicensed under the [BSD 2-Clause](https://opensource.org/licenses/BSD-2-Clause) License.',
    'author': 'drhosseinjavedani',
    'author_email': 'h.javedani@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/drhosseinjavedani/lohrasb',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<3.11',
}


setup(**setup_kwargs)
