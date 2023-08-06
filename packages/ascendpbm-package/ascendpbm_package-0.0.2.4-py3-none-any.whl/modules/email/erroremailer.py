def erroremailer(job, error, path="C:/Users/SFTPSVC/Scripts/SFTP/", attname=''):
    from O365 import Account, FileSystemTokenBackend
    import os, datetime
    import pandas as pd
    # Authenticate first, using below ID, secret key, and scopes:
    azureid = os.getenv('azureid')
    azuresec = os.getenv('azuresec')
    credentials = (azureid, azuresec)
    token_backend = FileSystemTokenBackend(token_path=path, token_filename='o365_token.txt')
    account = Account(credentials, token_backend=token_backend)
    if account.con.refresh_token() != True:
        account.authenticate(scopes=['basic', 'message_all'])
        print('Authenticated!')

    # visit URL prompted by console, give the report acct username and pass (like you'd log into O365),
    # Azure should send a post request to your browser that redirects you, finally paste posted URL to console, then run:

    # Report acct mailbox and folder
    mailbox = account.mailbox()
    ###inbox = mailbox.inbox_folder()

    # grab e-mail list
    emaillistname = 'erroremaillist.xlsx'
    emailfile = pd.read_excel(path + emaillistname, dtype=str)
    currentd = datetime.datetime.now().strftime('%m/%d/%Y')
    emailfile[currentd] = ''

    # loop through e-mail list
    for idx, value in emailfile.iterrows():
        ### Getting recipients and writing subject/body ###
        m = mailbox.new_message()
        m.to.add(value['Email'])
        m.subject = '{} - {}'.format(value['Subject'], currentd)
        m.body = ("Automated Error Report: job {} has produced error {} on date {}.".format(job, error, currentd))
        ### For attachments: ###
        m.attachments.add(attname)
        try:
            m.send()
            print('Sent E-mail:' + value['Email'])
            emailfile.loc[idx, currentd] = 'sent'
        except Exception as e:
            print(e)
            break
    print('Loop finished. Index: ' + str(idx) +', Group: ' + value['Group'] + ', Email: ' + value['Email'])
    emailfile.to_excel(path + emaillistname, index=False)
