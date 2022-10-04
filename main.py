# Main file of documentation check module

import os
import argparse


if __name__ == "__main__":
  parser = argparse.ArgumentParser(description="Check source repository and search for README file and comments in source code.")

  parser.add_argument("--repository", type=str, metavar="Source repository", nargs=1, dest="repo", default="",\
  help="Path to repository to analyse")
  
  args = parser.parse_args()
  repo_path = str(args.repo[0])
    
  
  # search for readme file
  for root, dirs, files in os.walk(repo_path):
    for file in files:
 
        # search Markdown files
        if file.endswith('.md'):
            print ("Markdown file found here:")
            print (root+'/'+str(file))
        
        # search file named readme
        if os.path.basename(file).casefold() == "readme":
          print ("README found here:")
          print (root+'/'+str(file))
