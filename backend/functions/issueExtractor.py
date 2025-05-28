#!/usr/bin/env python3
"""
usage: python issueExtractor.py org_name repo_name apiKey
"""

import argparse
import os
import re
import pandas as pd

from collections import Counter
from dotenv import load_dotenv
from github import Github
from utils.dataCleaning import *
from pathlib import Path

def extract_issues(org_name: str, repo_name: str, apiKey: str) -> None:
    gh = Github(apiKey)
    org  = gh.get_organization(org_name)
    repo = org.get_repo(repo_name)

    issues, comments = [], []

    for issue in repo.get_issues(state="all"):
        if issue.pull_request:
            continue

        issues.append({
            # IDENTITY
            "number":     issue.number,
            "id":         issue.id,
            "html_url":   issue.html_url,

            # TEXT
            "title":      issue.title,
            "body":       issue.body,

            # TIMESTAMPS
            "created_at": issue.created_at,
            "updated_at": issue.updated_at,
            "closed_at":  issue.closed_at,

            # STATE / REVIEW
            "state":      issue.state,
            "locked":     issue.locked,
            "author":     issue.user.login,

            # labels & milestone
            "labels":     [lbl.name for lbl in issue.labels],
            "milestone":  getattr(issue.milestone, "title", None),

            # USERS & REFS
            "assignees":  [u.login for u in issue.assignees],
            "comments":   issue.comments, 
            "reactions":  dict(Counter(r.content for r in list(issue.get_reactions()))),
        })

        for c in issue.get_comments():
            creactions = list(c.get_reactions())
            comments.append({
                "issue_number": issue.number,
                "comment_id": c.id,
                "user": c.user.login,
                "created_at": c.created_at,
                "body": c.body,
                "reactions": dict(Counter(r.content for r in creactions)),
            })

    issues_df = clean_text_columns(pd.DataFrame(issues).astype(str))
    comments_df  = clean_text_columns(pd.DataFrame(comments).astype(str))

    out_dir = Path(__file__).resolve().parents[1] / "files"
    out_dir.mkdir(exist_ok=True)

    issues_df.to_excel(
        f"{out_dir}/{org_name.lower()}_{repo_name.lower()}_issues.xlsx",
        engine="openpyxl",
    )
    comments_df.to_excel(
        f"{out_dir}/{org_name.lower()}_{repo_name.lower()}_issues_comments.xlsx",
        engine="openpyxl",
    )
    print("Done ✔︎")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Export GitHub issues + comments.")
    parser.add_argument("org_name",  help="GitHub organization / user name")
    parser.add_argument("repo_name", help="Repository name")
    parser.add_argument("api_key", help="Github API Key")
    args = parser.parse_args()

    extract_issues(args.org_name, args.repo_name, args.api_key)