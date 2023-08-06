import logging
from typing import Tuple
import os
import urllib
import urllib.parse
import os
import json
import builtins
        
def read_infinstor_config_json_key(jsonkey:str):
    infin_token_dir:str = None
    if 'INFINSTOR_TOKEN_FILE_DIR' in os.environ:
        infin_token_dir = os.environ['INFINSTOR_TOKEN_FILE_DIR']
    else:
        if 'MLFLOW_PARALLELS_URI' in os.environ:
            infin_token_dir= os.path.join(os.path.expanduser("~"), ".mlflow-parallels")
        else:
            infin_token_dir = os.path.join(os.path.expanduser("~"), ".infinstor")
    
    keyval = None
    # if token file is stored in memory (INFINSTOR_REFRESH_TOKEN), then we pretend as if config.json doesn't exist: always return None value for any key
    if infin_token_dir:
        config_json_path = os.path.join(infin_token_dir,'config.json')
        if os.path.exists(config_json_path): 
            with open(config_json_path, 'r') as fh:
                config_json:dict = json.load(fh)
                keyval = config_json.get(jsonkey, None)
    return keyval

def get_log_level_from_config_json(module_name:str) -> int:
    """
    Get the loglevel (integer) that correpsonds to the specified module_name, by looking into ~/.infinstor/config.json
    """
    
    loglevel_str:str = read_infinstor_config_json_key('loglevel.' + module_name)
    
    loglevel_int = logging.INFO
    # if config.json has loglevel defined for the specified module    
    if loglevel_str:
        loglevel_int:int = getattr(logging, loglevel_str.upper(), None)
    
    return loglevel_int

def _get_logger(name:str) -> logging.Logger:
    loglevel_int:int = get_log_level_from_config_json(name)
    # do not use force=True since it is only supported in Python 3.8 and higher.  Python 3.7 does not support it.
    logging.basicConfig(level=loglevel_int, format="%(asctime)s - %(process)d - %(name)s - %(levelname)s - %(message)s")
    logger = logging.getLogger(name)
    if loglevel_int:
        logger.setLevel(loglevel_int)
        
    if loglevel_int == logging.DEBUG:
        from http.client import HTTPConnection
        HTTPConnection.debuglevel = 1
    
    return logger

# set the root logger to the loglevel specified in config.json
_root_logger:logging.Logger = _get_logger("root")
_logger:logging.Logger = _get_logger(__name__)

def set_builtins_with_serverside_config(server_config:dict):
    builtins.clientid = server_config.get('clientid', "default_unknown")
    builtins.appclientid = server_config.get('appclientid', "default_unknown")
    builtins.mlflowserver = server_config.get('mlflowserver', "default_unknown")
    builtins.mlflowuiserver = server_config.get('mlflowuiserver', "default_unknown")
    builtins.mlflowstaticserver = server_config.get('mlflowstaticserver', "default_unknown")
    builtins.apiserver = server_config.get('apiserver', "default_unknown")
    builtins.serviceserver = server_config.get('serviceserver', "default_unknown")
    builtins.service = server_config.get('service', "default_unknown")
    builtins.region = server_config.get('region', "default_unknown")
    # server_config (from server) has the string 'true' or 'false' and not boolean True or False
    builtins.isexternalauth = server_config.get('isexternalauth', False)

def _validate_infin_mlflow_tracking_uri_exit(tracking_uri=None, do_exit=False) -> Tuple[str, urllib.parse.ParseResult]:
    """
    attemps to get the MLFLOW_TRACKING_URI from one of these 3 locations:  mlflow.get_tracking_uri(), MlflowClient(tracking_uri=xxxx) and MLFLOW_TRACKING_URI env variable.  And validates if the scheme of the URI is 'infinstor'.  If not, exit()s with an error message

    _extended_summary_

    Args:
        tracking_uri (_type_, optional): The tracking_uri as a string. Will be parsed to ascertain if the scheme is infinstor. Defaults to None.

    Returns:
        Tuple[str, urllib.parse.ParseResult]: A tuple of infinstor MLFLOW_TRACKING_URI as str and the result of urllib.urlparse() of this infinstor tracking URI
    """
    ##########
    #  TODO: a copy exists in 
    #  infinstor-mlflow/plugin/infinstor_mlflow_plugin/login.py 
    #  infinstor-mlflow/processors/singlevm/scripts/rclocal.py
    #  infinstor-jupyterlab/server-extension/jupyterlab_infinstor/__init__.py
    #  infinstor-jupyterlab/server-extension/jupyterlab_infinstor/cognito_utils.py
    #  infinstor-jupyterlab/clientlib/infinstor/bootstrap.py
    #  infinstor-jupyterlab/infinstor_py_bootstrap_project/infinstor_py_bootstrap/infinstor_py_bootstrap.py
    #  Need to see how to share code between two pypi packages to eliminate this duplication
    #  when refactoring this code, also refactor the copies
    ############

    # Note that there are 3 ways to inject MLFLOW_TRACKING_URI: mlflow.set_tracking_uri(), MlflowClient(tracking_uri=xxxx) and MLFLOW_TRACKING_URI env variable.  
    # all 3 are used below (Note that 'tracking_uri' argument of this function, set by caller CognitoAuthenticatedRestStore::__init__(), is derived MlflowClient(tracking_uri=xxxx) ).
    muri:str = tracking_uri
    pmuri:urllib.parse.ParseResult = urllib.parse.urlparse(muri)   # even if tracking_uri is None, a pmuri is returned. No exceptions raised
    if pmuri.scheme.lower() != 'infinstor':
        # /home/dev/miniconda3/envs/infinstor/lib/python3.8/site-packages/mlflow/tracking/_tracking_service/utils.py:151: UserWarning: Failure attempting to register store for scheme "infinstor": cannot import name '_validate_infin_mlflow_tracking_uri_exit' from partially initialized module 'infinstor_mlflow_plugin.utils' (most likely due to a circular import) (/home/dev/dev/infinstor/infinstor-mlflow/plugin/infinstor_mlflow_plugin/utils.py)
        #   _tracking_store_registry.register_entrypoints()
        #
        # /home/dev/miniconda3/envs/infinstor/lib/python3.8/site-packages/mlflow/store/artifact/artifact_repository_registry.py:89: UserWarning: Failure attempting to register artifact repository for scheme "s3": cannot import name '_validate_infin_mlflow_tracking_uri_exit' from partially initialized module 'infinstor_mlflow_plugin.utils' (most likely due to a circular import) (/home/dev/dev/infinstor/infinstor-mlflow/plugin/infinstor_mlflow_plugin/utils.py)
        #   _artifact_repository_registry.register_entrypoints()
        #
        # if 'import mlflow' is at the top of the file, see the errors above.  Probably due to this chain: some code imports 'import infinstor_mlflow_plugin.utils' --> import mlflow --> .. -> import infinstor_mlflow_plugin.coginto_authenticated_rest_store --> import infinstor_mlflow_plugin.tokenfile --> import infinstor_mlflow_plugin.utils.  So import it selectively here and not at the top
        import mlflow
        
        muri = mlflow.get_tracking_uri()
        pmuri = urllib.parse.urlparse(muri)
        if pmuri.scheme.lower() != 'infinstor':
            muri = os.getenv('MLFLOW_TRACKING_URI')
            pmuri = urllib.parse.urlparse(muri)
            if (pmuri.scheme.lower() != 'infinstor' and do_exit):
                # do not raise an exception since we want to display a user friendly error message. Printing the stack trace is not user friendly.  So print message and exit() instead
                #raise Exception("Error: MLFLOW_TRACKING_URI must be set to infinstor://.... to bootstrap infinstor mlflow client.  Please check documentation for details. Set the environment variable and retry.")
                _logger.error(f"Error: 'infinstor' scheme (for example infinstor://mlflow.infinstor.com) not detected for MLFLOW_TRACKING_URI: Set one of these to infinstor scheme and retry: MLFLOW_TRACKING_URI environment variable (currently set to {os.getenv('MLFLOW_TRACKING_URI')}) or MlflowClient(tracking_uri) (currently set to {tracking_uri}) or mlflow.set_tracking_uri() (currently set to {mlflow.get_tracking_uri()}).  Check documentation for further details.")
                exit(1)
    
    return muri, pmuri
