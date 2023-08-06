import argparse
from os import getenv

from app.mfa_auth import login
from app import clicode

command_type = None
description = """Start AWS CLI session

This is a small helper script to start an AWS CLI session with MFA enabled."""
parser = argparse.ArgumentParser(description=description)
subparsers = parser.add_subparsers(dest="command")
subparsers.required = True

loginp = subparsers.add_parser('login', help='Login with MFA to your account')
loginp.add_argument('--aws-account', default=getenv('AWS_ACCOUNT'),
                    help='This is the account you use to login to AWS, usually an email address or username. If not specified this will default to the environment variable AWS_ACCOUNT')
loginp.add_argument('--mfa-arn', default=None,
                    help='ARN for the MFA device, if not specified it will be discovered')
loginp.add_argument('--profile', default=getenv('AWS_PROFILE'),
                    help='Default profile reference used to get information about available MFA tokens')
loginp.add_argument('--save-as-profile', default='mfa',
                    help='Name for the profile created with MFA access tokens')

loginp.add_argument('--region', default="eu-west-2",
                    help='AWS region')
loginp.add_argument('--display', action="store_true",
                    help='Display the token on the screen')
loginp.add_argument('--duration', default=60,
                    help='Token duration in minutes')

assumep = subparsers.add_parser('assume-role', help='Assume a different role in AWS')
assumep.add_argument('--role-arn', default=getenv('AWS_ASSUME_ROLE_ARN'),
                     help='ARN for the role to assume')
assumep.add_argument('--role-name', default="AssumeRoleSession",
                     help='Name to be used while assuming the role used in CloudTrail logs')
assumep.add_argument('--profile', default=getenv('AWS_PROFILE'),
                     help='AWS profile to use to authorise the role assume')
assumep.add_argument('--save-as-profile', default=False,
                     help='Name of the profile created with the assumed role data')

assumep.add_argument('--region', default="eu-west-2",
                     help='AWS region')
assumep.add_argument('--display', action="store_true",
                     help='Display the token on the screen')
assumep.add_argument('--duration', default=60,
                     help='Token duration in minutes')

exportp = subparsers.add_parser('export-profile', help='Export a profile to your shell environment')
exportp.add_argument('--profile', default=getenv('AWS_PROFILE'),
                     help='AWS profile to export')
exportp.add_argument('--region', default="eu-west-2",
                     help='AWS region')

args = parser.parse_args()
try:
    auth = login(
        profile=args.profile,
        region=args.region
    )
    if args.command == 'login':
        auth.mfaLogin(args.aws_account, args.mfa_arn, args.duration)
    elif args.command == 'assume-role':
        role_name = args.role_name
        if role_name == 'AssumeRoleSession':
            role_name = input(
                f'Enter a name for your assumed role session (visible in cloud trail logs) [{role_name}]: ') or role_name
        auth.assumeRole(args.role_arn, role_name)
    elif args.command == 'export-profile':
        auth.exportProfile(args.profile)
    else:
        raise Exception('Command not supported')

    if hasattr(args, 'display') and args.display:
        print(
            f'Access Key: {auth.generated_access_key_id}\nSecret Key: {auth.generated_secret_access_key}\nSession Token: {auth.generated_session_token}')
    if hasattr(args, 'save_as_profile'):
        create_profile = args.save_as_profile
        if create_profile is False:
            create_profile = input(
                f'Enter a name for your profile to be saved as or leave blank to ignore: ')
        if create_profile is True:
            auth.storeGeneratedConfig(create_profile)
            print(f'{clicode.clicode.OKGREEN}Add `EXPORT AWS_PROFILE={create_profile}` to your ~/.zshrc file or use `--profile {create_profile}` when executing AWS CLI to use the new token. The token will be active for {args.duration} minutes{clicode.clicode.ENDC}')

except Exception as e:
    print(f'{clicode.clicode.FAIL}{e}{clicode.clicode.ENDC}')
    exit(1)

exit(0)
