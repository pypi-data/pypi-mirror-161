#!/bin/bash

# ~/bin/mlflow_run_infin_backend.sh --param-list alpha=0.1
[ -z "$1" ] && { echo "Usage: $0 <path_to_MLproject> <additional_args_to_MLproject>"; echo "    Example: $0 . --param-list alpha=0.1"; exit 1; } 

set -x

# from https://docs.infinstor.com/files/mlflow-projects-usage/#running-an-mlflow-project-in-a-single-vm-in-the-cloud-using-the-infinstor-backend
# 
# example: ~/bin/mlflow_run_infin_backend.sh --param-list alpha=0.1
mlproject_path="$1"; shift
mlflow run -b infinstor-backend --backend-config '{"instance_type": "t3.large"}' "$mlproject_path" $*

