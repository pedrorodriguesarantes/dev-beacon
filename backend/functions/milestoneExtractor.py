#!/usr/bin/env python3
"""
usage: python milestoneExtractor.py org_name repo_name apiKey
"""

import argparse
import os
import re
import pandas as pd

from dotenv import load_dotenv
from github import Github
from utils.dataCleaning import *
from pathlib import Path

def extract_milestones(org_name: str, repo_name: str, apiKey: str) -> None:
    gh = Github(apiKey)
    org  = gh.get_organization(org_name)
    repo = org.get_repo(repo_name)

    milestones = []

    for milestone in repo.get_milestones(state = "all"):
        milestones.append(
            {
                "id": milestone.id,
                "title": milestone.title,
                "created_at": milestone.created_at,
                "closed_at": milestone.closed_at,
                "created_by": milestone.creator.url,
                "description": milestone.description,
            }
        )

    out_dir = Path(__file__).resolve().parents[1] / "files"
    out_dir.mkdir(exist_ok=True)

    pd.DataFrame(milestones).astype(str).to_excel(
        f"{out_dir}/{org_name.lower()}_{repo_name.lower()}_milestones.xlsx",
        engine="openpyxl",
    )

    print("Done ✔︎")
    

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Export GitHub milestones")
    parser.add_argument("org_name",  help="GitHub organization / user name")
    parser.add_argument("repo_name", help="Repository name")
    parser.add_argument("api_key", help="Github API Key")
    args = parser.parse_args()

    extract_milestones(args.org_name, args.repo_name, args.api_key)