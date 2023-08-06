#!/usr/bin/python3

import os
import datetime

import boto3


#-------------------
# Possible TAGs on IAM Users
# email = [e-mail where to send notification]
# akm-mode = [SKIP, Any]
#       SKIP: Access Key Management (AKM) willl not be applied on this user
#       Any : AKM will be appled for any other value or if missing
#-------------------

DAYS_BEFORE_WARNING =  int(os.environ.get('DAYS_BEFORE_WARNING', 150))
DAYS_BEFORE_DISABLE =  int(os.environ.get('DAYS_BEFORE_DISABLE', 180))
WARNING_INTERVALL =  int(os.environ.get('WARNING_INTERVALL', 7))

client_iam = boto3.client('iam')

# Ref: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/iam.html

#*************************************************
#
#*************************************************
def SendEmail(toEmail, subject, message):

    email_client = boto3.client('ses', region_name='us-west-2')
    fromEmail = "from@generic.ca"

    resp = email_client.send_email(
        Source=fromEmail,
        Destination={'ToAddresses': [toEmail]},
        Message={
            'Subject': {'Data': subject, 'Charset': 'UTF-8'},
            'Body': {'Text': { 'Data': message,'Charset': 'UTF-8'} }
        }
    )
    print(f'    Sent Email to {toEmail} with subject {subject}')

#*************************************************
#
#*************************************************
def VerifyAccessKey(user):

    resp = client_iam.list_access_keys(UserName=user['name'])
    AccessKeys = resp['AccessKeyMetadata']

    id = 0
    for ak in AccessKeys :
        id += 1
        state = 'OK'
        #print(f'ak : {ak}')
        akId = ak['AccessKeyId']
        akStatus = ak['Status']
        createDate = ak['CreateDate']
        age = datetime.datetime.now(datetime.timezone.utc) - createDate
        days = age.days

        if akStatus == 'Active' :
            #----------------------
            # AK needs to be disable
            #----------------------
            if days >= DAYS_BEFORE_DISABLE :
                state = 'DISABLE'
                resp = client_iam.update_access_key(UserName=user['name'], AccessKeyId=akId,Status='Inactive')
                print(f'    Disable accesskey {akId}')

                if user['email']:
                    SendEmail(user['email'],
                    'Dragon - Disabling AWS Access Key',
                    f"Hello, {user['name']}!\n\n"+
                    f"Access key : {akId}\n"+
                    f"Has been deactivated since its age was more then {DAYS_BEFORE_DISABLE} days.\n"+
                    "Please create a new key pair in the AWS IAM console.\n"+
                    "If you need help, contact the administrators.\n\n"+
                    "Have a nice day! \n\n"+
                    "The friendly Dragon Administrators"
                    )

            #----------------------
            # AK Warning
            #----------------------
            elif days >= DAYS_BEFORE_WARNING :
                state = 'WARNING'
                days_left = DAYS_BEFORE_DISABLE - days
                if days_left % WARNING_INTERVALL == 0 and user['email']:
                    SendEmail(user['email'],
                    f'Dragon - Expiration of AWS Access Key in {days_left} days',
                    f"Hello, {user['name']}!\n\n"+
                    f"Access Key : {akId}\n"+
                    f"Needs to be replaced to meet our age policy of {DAYS_BEFORE_DISABLE} days.\n"+
                    f"It will automatically be deactivated in {days_left} days\n"+
                    "Please create a new key pair and delete the old one to ensure the our infrastructure security.\n\n"+
                    "If you need help, contact the administrators.\n\n"+
                    "Thanks ! \n\n"+
                    "The friendly Dragon Administrators"
                    )

        else : state = 'NOT-ACTIVE'

        print(f'    [{state}] access key: {akId}; age: {age.days} days; status: {akStatus}')


#*************************************************
#
#*************************************************
def VerifyMFA(user):

    resp = client_iam.list_mfa_devices(UserName=user['name'])
    mfas = resp['MFADevices']
    #print(f'VerifyMFA mfas: {mfas}')

    state = 'OK'

    if len(mfas) < 1 :
        state = 'FAIL'
        if user['email']:
            SendEmail(user['email'],
            'Dragon - MFA Device is missing for your AWS user',
            f"Hello, {user['name']}!\n\n"+
            "Having a Multi-Factor Authentification device attached to your account is an important measure to keep our infrastructure safe from possible intrusions.\n"+
            "Please activate this feature by visiting the IAM section of the AWS console.\n"+
            "Otherwise... we will bug you again tomorrow.\n\n"+
            "Have a nice day! \n\n"+
            "The friendly Dragon Administrators"
            )

    print(f'    [{state}] Multi-Factor is set for this user')

#*************************************************
#
#*************************************************
def ProcessUser(userRecord):

    #print(f'ProcessUser : {userRecord}')

    user = {
        "name" : userRecord['UserName'],
        "pwdUsed" : False,
        "mode" : 'OK',
        "email" : None
    }

    if 'PasswordLastUsed' in userRecord: user['pwdUsed'] = True

    #-------------------------
    # Get User Tags
    #-------------------------
    resp = client_iam.list_user_tags(UserName=user['name'])
    tags = resp['Tags']

    for tag in tags :
        if tag['Key'] == 'akm-mode' : user['mode']  = tag['Value']
        if tag['Key'] == 'email'    : user['email'] = tag['Value']

    print(f'User : {user}')

    # Check Mode
    if user['mode'] == 'SKIP' :
        print(f'    [SKIP] Account verification for this user')
        return 0

    #-------------------------
    # Verify Access Keys
    #-------------------------
    VerifyAccessKey(user)

    #-------------------------
    # Verify MFA Usage
    #-------------------------
    if user['pwdUsed'] :
        VerifyMFA(user)


#*************************************************
#
#*************************************************
def lambda_handler(event, context):


    print(f'Handler event {event}')

    # Get list of user in account
    resp = client_iam.list_users()
    users = resp['Users']

    #------------------------
    #  LOOP on all Users
    #------------------------
    for user in users : ProcessUser(user)

    return 0


#*************************************************
#
#*************************************************
if __name__ == "__main__":

    lambda_handler({'in': 1}, None)

