# Main file of documentation check module

import os
import argparse
import json

# Comments parser
from comment_parser import comment_parser

def has_paper (json_data):
   if json_data["Metadata"]["paper"]:
      return True
   return False

def has_homepage (json_data):
   if json_data["Metadata"]["homepage"]:
      return True
   return False

# Return comment verification block
def evaluate_comments_1_file (source_file_path):

    score = 0.
    ncomments = 0
    nlines = 0
    errors = []
    log = []
    ncomments = 0
    n_empty_lines = 0
    with open(source_file_path) as f:
      # Count number of lines
      for iline in f.readlines():
        # Count number of not empty lines
        nlines += 1 if iline.split() else 0
        # Count number of empty lines
        n_empty_lines += 1 if not iline.split() else 0
    
    try:
      ncomments = len(comment_parser.extract_comments(source_file_path))
      # Count number of not empty code lines
      nlines -= ncomments
      score = ncomments*100./nlines
      log.append (source_file_path.basename + ": n empty lines = " + str(n_empty_lines))
    except Exception as e:
       errors.append(e)

    return {"score": score, "nlines": nlines, "ncomments": ncomments, "errors": errors, "log": log}


def evaluate_comments (source_folder_path, report_block):
    blocks = []
    for root, dirs, files in os.walk(repo_path):
        for file in files:
            blocks.append(evaluate_comments_1_file (file))
    report_block["files"] = blocks
    report_block["nlines"] = sum(iblock["nlines"] for iblock in blocks)
    report_block["ncomments"] = sum(iblock["ncomments"] for iblock in blocks)
    for iblock in blocks:
       if iblock["errors"]: report_block["errors"].append (iblock["errors"])
       if iblock["log"]: report_block["log"].append (iblock["log"])

    # Compute global ratio comments/code lines
    report_block["ratio comments"] = sum(iblock["score"] for iblock in blocks)/len(blocks)
    
    return report_block
    
                
def has_readme (source_folder_path):
    for root, dirs, files in os.walk(source_folder_path):
      for filename in files:
          if "readme" in filename.lower():
              return True

    return False


if __name__ == "__main__":
  parser = argparse.ArgumentParser(description="Check source repository and search for README file and comments in source code.")

  parser.add_argument("--repository", type=str, metavar="Source repository", nargs=1, dest="repo", default="", help="Path to repository to analyse")
  parser.add_argument('--json', type=argparse.FileType('r'), metavar='json', nargs=1,
                        help='JSON File containing metadata of model and files to analyze')
  parser.add_argument('--out', type=argparse.FileType('w'), metavar='out', nargs=1,
                        help='JSON File containing results of documentation analysis')

  args = parser.parse_args()
  repo_path = str(args.repo[0])
  jsonfile = args.json[0] if args.json else None
  jsonfile_out = args.out[0] if args.out else None
  json_data = None
  with open(jsonfile, "r") as f:
        json_data = json.load (f)

  report_data = {"score": 0.,
                  "readme": False,
                  "nlines": 0,
                  "ncomments": 0,
                  "ratio comments": 0.,
                  "files": [],
                  "paper": False,
                  "homepage": False,
                  "errors": [],
                  "log": []}


  # search README
  report_data["readme"] = has_readme(repo_path)

  # search Homepage
  report_data["homepage"] = has_homepage(json_data)
 
  # seach paper
  report_data["paper"] = has_paper(json_data)
   
  # Analyze comments in source files
  report_data = evaluate_comments (repo_path, report_data)

  # Compute main score, mean score
  report_data["score"] = ((100. if report_data["readme"] else 0.)
                          + (100. if report_data["homepage"] else 0.)
                          + (100. if report_data["paper"] else 0.)
                          + report_data["ratio comments"]) / 4

  # Write data in JSON file
  with open(jsonfile_out, "w") as f:    
      json_data_out = {}
      json_data_out["Verification Method Documentation Analysis"] = report_data
      # Method's report
      json.dump(json_data_out, f, indent=4)
  