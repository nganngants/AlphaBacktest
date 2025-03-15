from openbb import obb
import os
from dotenv import load_dotenv
import argparse

def login(env_file):
    load_dotenv(env_file)
    token = os.getenv("OPENBB_TOKEN")
    obb.account.login(pat=token)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--env", type=str, default=".env")
    args = parser.parse_args()
    login(args.env)