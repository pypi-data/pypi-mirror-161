import boto3
import botocore.exceptions as botoexception
from os import path
import configparser
import botocore

from app import clicode


class login:

    region = 'eu-west-2'
    profile = 'default'

    access_key_id = None
    secret_access_key = None
    session_token = None
    session = None

    generated_access_key_id = None
    generated_secret_access_key = None
    generated_session_token = None

    def __init__(self, **kwargs):
        if 'profile' in kwargs and kwargs['profile']:
            self.profile = kwargs['profile']
        if 'region' in kwargs:
            self.region = kwargs['region']
        
        self.loadAWSConfig()
        self.getAccessKey(self.profile)
        
        self.session = boto3.Session(
            aws_access_key_id=self.access_key_id, aws_secret_access_key=self.secret_access_key, aws_session_token=self.session_token, region_name=self.region)

    def mfaLogin(self, account, mfaarn, duration=60):
        if mfaarn == None:
            if account == None:
                raise Exception('AWS account is required to detect your MFA ARN')
            mfaarn = self.loadMFA(account)
        
        token = self.startMfaSession(mfaarn, duration)

        self.generated_access_key_id = token['AccessKeyId']
        self.generated_secret_access_key = token['SecretAccessKey']
        self.generated_session_token = token['SessionToken']

    def storeGeneratedConfig(self, profile_name: str):
        self.creds[profile_name] = {
            "aws_access_key_id": self.generated_access_key_id,
            "aws_secret_access_key": self.generated_secret_access_key,
            "aws_session_token": self.generated_session_token,
        }

        with open(self.credsPath, 'w') as credsfile:
            self.creds.write(credsfile)

    def loadMFA(self, account):
        iamclient = self.session.client('iam')
        try:
            mfas = iamclient.list_mfa_devices(UserName=account)
        except botoexception.ClientError as err:
            raise Exception(err)

        if(len(mfas['MFADevices']) > 1):
            totalMfas = len(mfas['MFADevices'])
            prompt = f'More than one device was found on your account, please choose the serial number of the MFA device you want to use:\n'
            i = 0
            for mfa in mfas['MFADevices']:
                i = i+1
                serialNumber = mfa['SerialNumber']
                prompt += f'\t[{i}] {serialNumber}\n'
            isnumber = False
            print(prompt)
            while isnumber is False:
                mfaselect = input(
                    f'Please enter a number between 1 and {totalMfas}: ')
                if isinstance(mfaselect, int) and mfaselect > 0 and mfaselect <= len(mfas['MFADevices']):
                    isnumber = True
                    mfaarn = mfas['MFADevices'][(mfaselect+1)]['SerialNumber']
                else:
                    raise Exception(
                        f'Please enter a number between 1 and {totalMfas}:{clicode.clicode.ENDC}')
        else:
            mfaarn = mfas['MFADevices'][0]['SerialNumber']
        return mfaarn

    def loadAWSConfig(self):
        self.credsPath = path.join(path.expanduser('~'), '.aws/credentials')
        self.configPath = path.join(path.expanduser('~'), '.aws/config')
        self.creds = configparser.RawConfigParser()
        self.creds.read(self.credsPath)
        self.config = configparser.RawConfigParser()
        self.config.read(self.configPath)

    def getAccessKey(self, profile: str):
        if profile in self.creds:
            if 'aws_access_key_id' not in self.creds[profile] or 'aws_secret_access_key' not in self.creds[profile]:
                raise Exception(
                    f'AWS Access Key or Secret Access Key not found in profile {profile}')
            self.access_key_id = self.creds[profile]['aws_access_key_id']
            self.secret_access_key = self.creds[profile]['aws_secret_access_key']
            if 'aws_session_token' in self.creds[profile]:
                self.session_token = self.creds[profile]['aws_session_token']
        else:
            print(
                f'Profile [{profile}] not found, please specify account key and secret')
            self.access_key_id = input('AWS Access Key ID: ')
            self.secret_access_key = input('AWS Secret Access Key: ')            

    def startMfaSession(self, mfaarn, duration=60):
        tokenRetrieved = False
        i = 0
        while tokenRetrieved is False:
            i = i+1
            try:
                code = input(
                    'Please enter the 6 digit code from your MFA device: ')
                token = self.loadTokenFromSts(mfaarn, code, duration)
                tokenRetrieved = True
            except:
                if i > 2:
                    raise Exception('Total number of attempts failed.')
                print(
                    f'{clicode.clicode.FAIL}An error occurred getting your token, please try again.{clicode.clicode.ENDC}')
        return token

    def loadTokenFromSts(self, mfaarn: str, code: str, duration=60):
        stsclient = self.session.client('sts')
        getToken = stsclient.get_session_token(
            SerialNumber=mfaarn,
            TokenCode=code,
            DurationSeconds=(duration * 60)
        )
        return getToken['Credentials']

    def assumeRole(self, arn: str, name: str, **kwargs):
        stsclient = self.session.client('sts')
        getToken = stsclient.assume_role(
            RoleArn=arn,
            RoleSessionName=name
        )
        token = getToken['Credentials']

        self.generated_access_key_id = token['AccessKeyId']
        self.generated_secret_access_key = token['SecretAccessKey']
        self.generated_session_token = token['SessionToken']
    
    def exportProfile(self, profile: str):
        self.access_key_id = self.creds[profile]['aws_access_key_id']
        self.secret_access_key = self.creds[profile]['aws_secret_access_key']
        print(f'AWS_ACCESS_KEY_ID={self.access_key_id}')
        print(f'AWS_SECRET_ACCESS_KEY={self.secret_access_key}')
        if 'aws_session_token' in self.creds[profile]:
            self.session_token = self.creds[profile]['aws_session_token']
            print(f'AWS_SESSION_TOKEN={self.session_token}')
        print(f'AWS_PROFILE={profile}')