## KEY SETTINGS
#####################################

DIR = ".../CBRNet"
DATA_NAME = "drybean_1"
EXP_NAME = "exp_reg_impact"

# Chg os and sys path
import os
import sys
os.chdir(DIR)
sys.path.append(DIR)

# Num of experiments per data configuration
NUM_ITERATIONS = 10
reg_strengths = [0.0, 0.0001, 0.0003, 0.001, 0.003, 0.01, 0.03, 0.1, 0.3, 1.]


# LOAD MODULES
#####################################

# Standard library
import warnings

# Third party
from tqdm import tqdm

# Proprietary
from src.data.drybean_1 import load_data
from src.methods.neural import CBRNet, MLP
from src.methods.utils.cbrnet_utils import MMD, Wasserstein
from src.utils.metrics import mise_metric
from src.utils.setup import (
    add_dict,
)
from src.utils.training import train_val_tuner


## SETUP
#####################################

# Disable device summaries
import logging
logging.getLogger("lightning.pytorch").setLevel(logging.ERROR)
logger = logging.getLogger("lightning.pytorch.core")
logger.addHandler(logging.FileHandler("core.log"))

# Disable warnings
warnings.filterwarnings("ignore")


## CUSTOM FUNCTIONS
#####################################

def update_dict(dict, data, model, name):
    mise = mise_metric(data.x_test, data.t_test, data.ground_truth, model)
    dict.update({f"MISE {name}": mise})


## ITERATE OVER DATA COMBINATIONS
#####################################

seeds = range(NUM_ITERATIONS)

for seed in tqdm(seeds):
    for strength in reg_strengths:
        results = {}
        results.update({
            "seed": seed,
            "reg_strength": strength,
        })
        
        data = load_data(
            bias_inter=0.66,
            bias_intra=3,
            seed=seed,
        )
        
        # TRAIN MODELS
        
        # cbrnet rbf
        name="cbrnet-rbf"
        model = CBRNet(
            input_size=data.x.shape[1],
            learning_rate=0.01,
            batch_size=512,
            num_steps=5000,
            IPM=MMD("rbf"),
            regularization_ipm=strength,
        )
        model.fit(data.x_train, data.y_train, data.d_train, data.t_train)
        
        update_dict(results, data, model, name)
        
        # cbrnet lin
        name="cbrnet-lin"
        model = CBRNet(
            input_size=data.x.shape[1],
            learning_rate=0.01,
            batch_size=512,
            num_steps=5000,
            IPM=MMD("linear"),
            regularization_ipm=strength,
        )
        model.fit(data.x_train, data.y_train, data.d_train, data.t_train)
        
        update_dict(results, data, model, name)
        
        # cbrnet was
        name="cbrnet-was"
        model = CBRNet(
            input_size=data.x.shape[1],
            learning_rate=0.01,
            batch_size=512,
            num_steps=5000,
            IPM=Wasserstein(),
            regularization_ipm=strength,
        )
        model.fit(data.x_train, data.y_train, data.d_train, data.t_train)
        
        update_dict(results, data, model, name)
        
        # FINALIZE ITERATION
        add_dict("res/"+EXP_NAME+".csv", results)