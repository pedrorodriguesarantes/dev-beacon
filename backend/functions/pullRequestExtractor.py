#!/usr/bin/env python3
"""
usage: python pullRequestExtractor.py ORG REPO API_KEY
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

def extract_pulls(org_name: str, repo_name: str, api_key: str) -> None:
    gh   = Github(api_key)
    repo = gh.get_organization(org_name).get_repo(repo_name)

    pull_rows, comment_rows = [], []

    for pr in repo.get_pulls(state="all"):
        pull_rows.append({
            # IDENTITY
            "number": pr.number,
            "id":     pr.id,

            # TEXT
            "title": pr.title,
            "body":  pr.body,

            # TIMESTAMPS
            "created_at": pr.created_at,
            "updated_at": pr.updated_at,
            "closed_at":  pr.closed_at,
            "merged_at":  pr.merged_at,

            # STATE / REVIEW
            "state":           pr.state,
            "draft":           pr.draft,
            "mergeable":       pr.mergeable,
            "mergeable_state": pr.mergeable_state,
            "merged":          pr.merged,
            "rebaseable":      pr.rebaseable,

            # COUNTS
            "commits":       pr.commits,
            "additions":     pr.additions,
            "deletions":     pr.deletions,
            "changed_files": pr.changed_files,

            # USERS & REFS
            "user":                 pr.user.login,
            "assignees":            [u.login for u in pr.assignees],
            "requested_reviewers":  [u.login for u in pr.requested_reviewers],
            "merged_by":            getattr(pr.merged_by, "email", None),

            # LABELS & MILESTONE
            "labels":    [lbl.name for lbl in pr.labels],
            "milestone": getattr(pr.milestone, "id", None),
        })

        # review comments (file‑anchored)
        for c in pr.get_comments():
            reactions = list(c.get_reactions())
            comment_rows.append({
                "pr_number":  pr.number,
                "id":         c.id,
                "user":       c.user.login,
                "created_at": c.created_at,
                "path":       c.path,
                "position":   c.position,
                "commit_id":  c.commit_id,
                "in_reply_to_id": c.in_reply_to_id,
                "body":       c.body,
                "reactions":        [r.content for r in reactions],
                "reaction_counts":  dict(Counter(r.content for r in reactions)),
            })

    pulls_df = clean_text_columns(pd.DataFrame(pull_rows).astype(str))
    comments_df = clean_text_columns(pd.DataFrame(comment_rows).astype(str))

    out_dir = Path(__file__).resolve().parents[1] / "files"
    out_dir.mkdir(exist_ok=True)

    pulls_df.to_excel(
        out_dir / f"{org_name.lower()}_{repo_name.lower()}_pulls.xlsx",
        engine="openpyxl"
    )

    comments_df.to_excel(
        out_dir / f"{org_name.lower()}_{repo_name.lower()}_pulls_comments.xlsx",
        engine="openpyxl"
    )

    print("Done ✔︎   →", out_dir)

if __name__ == "__main__":
    p = argparse.ArgumentParser(description="Export pull‑requests + review‑comments")
    p.add_argument("org_name"), p.add_argument("repo_name"), p.add_argument("api_key")
    args = p.parse_args()
    extract_pulls(args.org_name, args.repo_name, args.api_key)
