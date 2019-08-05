import argparse
import json
import sys

import colorama
import boto3

from awsume.awsumepy.lib.aws_files import get_aws_files, read_aws_file
from awsume.awsumepy import hookimpl, safe_print

@hookimpl
def add_arguments(parser: argparse.ArgumentParser):
    try:
        parser.add_argument('--rotate-access-keys',
            action='store_true',
            dest='rotate_access_keys',
            help='Rotate access keys',
        )
        parser.add_argument('--force-rotate-access-keys',
            action='store_true',
            dest='force_rotate_access_keys',
            help='Rotate access keys without prompt',
        )
    except argparse.ArgumentError:
        pass


@hookimpl
def post_add_arguments(config: dict, arguments: argparse.Namespace, parser: argparse.ArgumentParser):
    if arguments.rotate_access_keys or arguments.force_rotate_access_keys:
        _, credentials_file = get_aws_files(arguments, config)
        profiles = read_aws_file(credentials_file)
        target_profile = profiles.get(arguments.target_profile_name)
        if not target_profile:
            safe_print('Profile {} not found'.format(arguments.target_profile_name), color=colorama.Fore.RED)
            exit(1)
        if 'aws_access_key_id' not in target_profile or 'aws_secret_access_key' not in target_profile:
            safe_print('Cannot rotate {}, must have keys to rotate'.format(arguments.target_profile_name), color=colorama.Fore.RED)
            exit(1)
        if 'aws_session_token' in target_profile:
            safe_print('Cannot rotate {}, must be a user profile'.format(arguments.target_profile_name), color=colorama.Fore.RED)
            exit(1)

        session = boto3.Session(
            aws_access_key_id=target_profile.get('aws_access_key_id'),
            aws_secret_access_key=target_profile.get('aws_secret_access_key'),
        )
        display_access_keys(session)

        if not arguments.force_rotate_access_keys:
            safe_print(
                'Are you sure you want to rotate access key [{}] for profile {} (y/N)?\n> '.format(
                    target_profile.get('aws_access_key_id'),
                    arguments.target_profile_name,
                ),
                end='',
            )
            choice = input()
            if choice.lower() != 'y':
                exit(0)

        safe_print('Rotating access keys for profile: {}'.format(arguments.target_profile_name), color=colorama.Fore.YELLOW)
        safe_print('Creating a new set of access keys...', color=colorama.Fore.GREEN)
        # todo
        safe_print('Updating credentials file {}...'.format(credentials_file), color=colorama.Fore.GREEN)
        # todo
        # also, update profiles that share the same key, but prompt each time
        safe_print('Deleting previous keys...', color=colorama.Fore.GREEN)
        # todo

        exit(0)


def display_access_keys(session: boto3.Session):
    target_key = session.get_credentials().access_key
    iam = session.client('iam')
    response = iam.list_access_keys()['AccessKeyMetadata']
    safe_print('Displaying Access Keys'.center(45, '='))
    safe_print('ACCESS KEY ID'.ljust(20), end='  ')
    safe_print('STATUS'.ljust(10), end='  ')
    safe_print('CREATE DATE'.ljust(10))
    for key_metadata in response:
        color = None if target_key != key_metadata.get('AccessKeyId') else colorama.Fore.MAGENTA
        safe_print(key_metadata.get('AccessKeyId'), end='  ', color=color)
        safe_print('[{}]'.format(key_metadata.get('Status')).ljust(10), end='  ', color=color)
        safe_print('{}'.format(key_metadata.get('CreateDate').strftime('%d/%M/%Y')).ljust(10), color=color)
    safe_print(''.center(45, '='))
