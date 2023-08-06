import requests
from requests_ntlm import HttpNtlmAuth
from pathlib import Path
from datetime import datetime, timedelta

def get_YTDPDF(username, password, groupnum,
               start = datetime.today().strftime('01/01/%Y'),
               end = (datetime.today()-timedelta(days=1)).strftime('%m/%d/%Y'),
               url = 'https://dbapps.optimedhp.com/reports/request_report/file_reports',
               download = False,
               downloadDir = None):
    '''
    Parameters
    ----------
    username (str):
        Your Windows username as a string. \n
    password (str):
        Your Windows password as a string. \n
    groupnum (str):
        Group number matching table entry as specified by django view. \n
    start (str):
        Date string in MM/DD/YYYY format for report start.
        Default is the first of the year. \n
    end (str):
        Date string in MM/DD/YYYY format for report end.
        Default is yesterday. \n
    url (str):
        The URL of our website's post form as a string.
        Default is 'https://dbapps.optimedhp.com/reports/request_report/file_reports' \n
    download (boolean, optional):
        If set to True, the pdf will be downloaded to either Path.home()/Downloads 
        or downloadDir (if supplied as below), and the response obj will not be returned.
        Default is False \n
    downloadDir (WindowsPath object or str accepted as Path() input, optional):
        If supplied along with download == True, the pdf will be downloaded here.
        Default is None \n
    Returns
    -------
    Either a requests lib response obj with YTDPDF under .content or a download confirmation str.
    '''
    
    client = requests.Session()
    client.get(url, auth = HttpNtlmAuth('AD\\{}'.format(username), '{}'.format(password)))
    headers = {'Referer':url}
    form = {'Report_Type':'YTDPDF',
            'Group_Number':groupnum,
            'Start_Date':start,
            'End_Date':end,
            'csrfmiddlewaretoken':client.cookies['csrftoken']}
    response = client.post(url,
                           data=form,
                           headers=headers)
    
    if response.status_code != 200:
        raise Exception('Sorry, status code {}'.format(response.status_code))
    else:
        if download == True:
            disposition = response.headers['Content-Disposition']
            if downloadDir:
                filepath = Path(downloadDir) / disposition[disposition.find('"'):].replace('"', '')
            else:
                filepath = Path(Path.home()) / 'Downloads' / disposition[disposition.find('"'):].replace('"', '')
            with open(filepath,
                      'wb') as f:
                f.write(response.content)
            return 'YTD Style PDF downloaded: ' + str(filepath)
        else:
            return response
    
    
def get_csv(username, password,
            model = 'Claims',
            params = None,
            url = 'https://dbapps.optimedhp.com/testdb/view_',
            download = False,
            downloadDir = None):
    '''
    Parameters
    ----------
    username (str):
        Your Windows username as a string. \n
    password (str):
        Your Windows password as a string. \n
    model (str):
        Name of a model specified in dbUI's testdb app, case sensitive.
        Default is 'Claims' \n
    params (dict, optional):
        URL parameters to follow ? as a dict where key = parameter name, value = parameter value.
        Parameters must map to testdb's model fields (keys) and filter values (values).
        Default is None \n
    url (str):
        Partial URL of our website's post form as a string.
        Default is 'https://dbapps.optimedhp.com/testdb/view_' \n
    download (boolean, optional):
        If set to True, the csv will be downloaded to either Path.home()/Downloads 
        or downloadDir (if supplied as below), and the response obj will not be returned.
        Default is False \n
    downloadDir (WindowsPath object or str accepted as Path() input, optional):
        If supplied along with download == True, the csv will be downloaded here.
        Default is None \n
    Returns
    -------
    Either a requests lib response obj with csv string under .text or a download confirmation str.
    '''
    
    url = url + model + '/'
    if params:
        url = url + '?'
        for i, (k, v) in enumerate(params.items()):
            if i > 0:
                url = url + '&'
            url = url + k + '=' + v
            
    client = requests.Session()
    client.get(url, auth = HttpNtlmAuth('AD\\{}'.format(username), '{}'.format(password)))
    headers = {'Referer':url}
    form = {'csrfmiddlewaretoken': client.cookies['csrftoken']}
    response = client.post(url, data=form, headers=headers)
    
    if response.status_code != 200:
        raise Exception('Sorry, status code {}'.format(response.status_code))
    else:
        if download == True:
            if params:
                filename = model
                for k, v in params.items():
                    filename = filename + '_' + k + '=' + v
                filename = filename + '.csv'
            else:
                filename = model + '.csv'
            
            if downloadDir:
                filepath = Path(downloadDir) / filename
            else:
                filepath = Path(Path.home()) / 'Downloads' / filename
            with open(filepath,
                      'wb') as f:
                f.write(response.content)
            return 'CSV query downloaded: ' + str(filepath)
        else:
            return response
