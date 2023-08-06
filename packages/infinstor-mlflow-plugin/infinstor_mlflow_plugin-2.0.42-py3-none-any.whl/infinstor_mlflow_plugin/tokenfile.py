from typing import Tuple
import requests
from requests.exceptions import HTTPError
import json
import time
import os
import logging
import posixpath
from urllib.parse import urlparse
import urllib
import io
import builtins

from .utils import _validate_infin_mlflow_tracking_uri_exit, _get_logger

logger:logging.Logger = _get_logger(__name__)

# in memory token file contents as a str.  Used when INFINSTOR_REFRESH_TOKEN environment variable is in use.
g_tokfile_contents:str=""
def get_token_file_obj(mode:str, exit_on_error=True) -> io.TextIOWrapper:
    """
    if INFINSTOR_REFRESH_TOKEN is set
        return in memory token file object
    else if INFINSTOR_TOKEN_FILE_DIR is set
        return $INFINSTOR_TOKEN_FILE_DIR/token file object
    else 
         return ~/.infinstor/token file object or ~/.mlflow-parallels/token 

    _extended_summary_
    
    Args:
        mode[str]: must be 'r' or 'w'
        exit_on_error(bool):  Default True.  If True, when an error is encountered, prints an error and exit()s.  If False, prints an error and returns None

    Returns:
        io.TextIOWrapper: file object for the token file. file object is opened for read only ('r').  Need to call close() on this file object when done with it.  May return 'None' if an error is encountered and exit_on_error=False
    """
    
    if mode != 'r' and mode != 'w': raise ValueError(f"Invalid value for mode: must be 'r' or 'w' only: {mode}")
        
    global g_tokfile_contents
    fh:io.TextIOWrapper = None
    if 'INFINSTOR_REFRESH_TOKEN' in os.environ:
        # if 'reading' the file, use the in memory file contents to create the file object
        # if writing the file, clear the current in memory file contents and return the file object
        if (mode == 'w'): g_tokfile_contents = ""
        fh = io.StringIO(g_tokfile_contents) 
    elif 'INFINSTOR_TOKEN_FILE_DIR' in os.environ:
        tokfile = os.path.join(os.environ['INFINSTOR_TOKEN_FILE_DIR'], "token")
        if mode == 'w': os.makedirs(os.path.dirname(tokfile), exist_ok=True)
        # if we are attempting to read the token file, ensure that the token file exists
        if mode == 'r' and not os.path.exists(tokfile):
            logger.error(f"Unable to read token file {tokfile} when INFINSTOR_TOKEN_FILE_DIR={os.environ['INFINSTOR_TOKEN_FILE_DIR']}.  run login_infinstor cli command to login or place a valid token file as {tokfile}")
        else: 
            fh = open(tokfile, mode)
    else:
        if 'MLFLOW_PARALLELS_URI' in os.environ:
            tokfile = os.path.join(os.path.expanduser("~"), ".mlflow-parallels", "token")
            if mode == 'w': os.makedirs(os.path.dirname(tokfile), exist_ok=True)
            # if we are attempting to read the token file, ensure that the token file exists
            if mode == 'r' and not os.path.exists(tokfile):
                logger.error(f"Unable to read token file {tokfile} when MLFLOW_PARALLELS_URI={os.environ['MLFLOW_PARALLELS_URI']}.  run login_infinstor cli command to login or place a valid token file as {tokfile}")
            else: 
                fh = open(tokfile, mode)
        else:
            tokfile = os.path.join(os.path.expanduser("~"), ".infinstor", "token")
            if mode == 'w': os.makedirs(os.path.dirname(tokfile), exist_ok=True)
            # if we are attempting to read the token file, ensure that the token file exists
            if mode == 'r' and not os.path.exists(tokfile):
                logger.error(f"Unable to read token file {tokfile}.  run login_infinstor cli command to login or place a valid token file as {tokfile}")
            else:
                fh = open(tokfile, mode)
    
    if not fh and exit_on_error:
        # exit() so that we print an user friendly message instead of the exception that will be thrown if open() is called with a file that doesn't exist
        exit()

    return fh

def read_token_file(exit_on_error=True) -> Tuple[str, str, str, str, str, str, str]:
    """reads and returns the following from the tokenfile: access_token, refresh_token, token_time, client_id, service, token_type, id_token
    The file from which these are read from can be a file in the filesystem or an in memory file: see get_token_file_obj() for details.

    Args:
        exit_on_error(bool): Default is True.  if an error is encountered during reading token file.  print an error message and call exit(), if True.  If False, returned values may be None.
    Returns:
        [tuple]: returns the tuple (access_token, refresh_token, token_time, client_id, service, token_type, id_token)
    """
    with get_token_file_obj( 'r', exit_on_error ) as fp:
        # check if this is an in-memory token file (INFINSTOR_REFRESH_TOKEN is set) and if this file is empty.  If so, create the in-memory tokenfile.  
        # Note that this is needed, since when INFINSTOR_REFRESH_TOKEN is used, performing a cli login to create filesystem tokenfile or placing the 'token' file in the filesystem will not work.  
        # Instead the in-memory token file needs to be created whenever anyone attempts to read the token file.
        #
        # if in memory token file is in use and it is empty
        if fp and isinstance(fp, io.StringIO) and not fp.getvalue():
            # renew the token, which creates the in-memory token file
            renew_token(builtins.region, os.getenv('INFINSTOR_REFRESH_TOKEN','INFINSTOR_REFRESH_TOKEN not set'), os.getenv('INFINSTOR_COGNITO_CLIENTID','INFINSTOR_COGNITO_CLIENTID not set'), builtins.service)
            
    fclient_id = None
    ftoken = None
    frefresh_token = None
    ftoken_time = None
    token_type = None
    id_token = None
    with get_token_file_obj( 'r', exit_on_error) as fp:
        if fp:
            for count, line in enumerate(fp):
                if (line.startswith('ClientId=')):
                    fclient_id = line[len('ClientId='):].rstrip()
                if (line.startswith('Token=')):
                    ftoken = line[len('Token='):].rstrip()
                if (line.startswith('RefreshToken=')):
                    frefresh_token = line[len('RefreshToken='):].rstrip()
                if (line.startswith('TokenTimeEpochSeconds=')):
                    ftoken_time = int(line[len('TokenTimeEpochSeconds='):].rstrip())
                if (line.startswith('TokenType=')):
                    token_type = line[len('TokenType='):].rstrip()
                if (line.strip().lower().startswith('idtoken=')):
                    # read the content after '='
                    id_token = line.split('=')[1].strip()
    if (token_type == None):
        if ftoken != None: token_type = 'Custom' if ftoken.startswith('Custom ') else 'Bearer'
        
    # extract service
    muri:str; pmuri:urllib.parse.ParseResult;
    muri, pmuri = _validate_infin_mlflow_tracking_uri_exit(do_exit=exit_on_error)
    if pmuri:  fservice = pmuri.hostname[pmuri.hostname.index('.')+1:]
    return ftoken, frefresh_token, ftoken_time, fclient_id, fservice, token_type, id_token

def write_token_file(token_time, token, refresh_token, client_id, idToken:str):
    with get_token_file_obj('w') as wfile:
        wfile.write("Token=" + token + "\n")
        wfile.write("RefreshToken=" + refresh_token + "\n")
        wfile.write("ClientId=" + client_id + "\n")
        wfile.write("TokenTimeEpochSeconds=" + str(token_time) + "\n")
        wfile.write("IdToken=" + idToken + "\n")
        
        global g_tokfile_contents
        # if we are writing to an in-memory file (StringIO), then extract the contents before closing
        if isinstance(wfile, io.StringIO): g_tokfile_contents = wfile.getvalue()
        
        wfile.close()

def renew_token(region, refresh_token, client_id, service):
    payload = "{\n"
    payload += "    \"AuthParameters\" : {\n"
    payload += "        \"REFRESH_TOKEN\" : \"" + refresh_token + "\"\n"
    payload += "    },\n"
    payload += "    \"AuthFlow\" : \"REFRESH_TOKEN_AUTH\",\n"
    payload += "    \"ClientId\" : \"" + client_id + "\"\n"
    payload += "}\n"

    url = 'https://cognito-idp.' +region +'.amazonaws.com:443/'

    headers = {
            'Content-Type': 'application/x-amz-json-1.1',
            'X-Amz-Target' : 'AWSCognitoIdentityProviderService.InitiateAuth'
            }

    try:
        response:requests.Response = requests.post(url, data=payload, headers=headers)
        if not response.ok: logger.error(f"HTTP Error {response.status_code} occurred while trying to renew token: url={response.url}; reason={response.reason}; response={response.text}")
        response.raise_for_status()
    except HTTPError as http_err:
        logger.info(f'HTTP error occurred while trying to renew token: {http_err}')
        raise
    except Exception as err:
        logger.info(f'Other error occurred while trying to renew token: {err}')
        raise
    else:
        authres = response.json()['AuthenticationResult']
        token = authres['AccessToken']
        idToken = authres['IdToken']        
        token_time = int(time.time())
        write_token_file(token_time, token, refresh_token, client_id, idToken)

def get_id_token(region):
    """returns the idToken if available.. Also may return a custom token

    Returns:
        [tuple]: ( idToken or CustomToken, service )
    """
    # read the idToken
    ( access_token, refresh_token, token_time, client_id, service, token_type, id_token) = read_token_file()

    if (token_type == "Custom"):
        logger.debug("get_token(): Custom Infinstor token")
        return access_token, service
    
    time_now = int(time.time())
    # we have so many copies of tokenfile writing code in our codebase, there is a chance that not all copies write idToken.  handle this with 'if not id_token' below.
    if ((token_time + (30 * 60)) < time_now) or not id_token:
        logger.info(f'get_id_token(): InfinStor token has expired or id_token not found in tokenfile: Calling renew: id_token found in token file={id_token == None} token_time={token_time}; (token_time + (30 * 60)={token_time + (30 * 60)}; time_now={time_now}')
        renew_token(region, refresh_token, client_id, service)
        token, refresh_token, token_time, client_id, service, token_type, id_token = read_token_file()
        
    return id_token, service

def get_token(region, force_renew):
    token = None
    refresh_token = None
    token_time = None
    client_id = None
    service = None

    token, refresh_token, token_time, client_id, service, token_type, id_token = read_token_file()

    if (token_type == "Custom"):
        logger.debug("get_token(): Custom Infinstor token")
        return token, service

    if (force_renew == True):
        logger.info("get_token(): Forcing renewal of infinstor token")
        renew_token(region, refresh_token, client_id, service)
        token, refresh_token, token_time, client_id, service, token_type, id_token = read_token_file()
        return token, service

    time_now = int(time.time())
    if ((token_time + (30 * 60)) < time_now):
        logger.debug(f'get_token(): InfinStor token has expired. Calling renew: token_time={token_time}; (token_time + (30 * 60)={(token_time + (30 * 60))}; time_now={time_now}')
        renew_token(region, refresh_token, client_id, service)
        token, refresh_token, token_time, client_id, service, token_type, id_token = read_token_file()
        return token, service
    else:
        logger.debug(f'get_token(): InfinStor token has not expired: token_time={token_time}; time_now={time_now}')
        return token, service
