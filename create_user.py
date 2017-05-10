import AEDeveloper.db as db
from AEDeveloper.developer_identity import create_user
import sys
import argparse


def generate_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('username', help='User\'s login.')
    parser.add_argument('password', help='User\'s login password.')
    parser.add_argument('fullname', help='The full name of the user, surrounded by quotes to capture spaces.')
    parser.add_argument('email', help='The email address of the user.')
    return parser


if __name__ == '__main__':
    db.init_db()
    parser = generate_parser()
    args = parser.parse_args()
    create_user(**vars(args))
    print('User added.')
