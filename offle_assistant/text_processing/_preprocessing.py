import re
from typing import List
import pathlib
import os

import pypandoc


def latex_to_md(
    root_dir: pathlib.Path,
) -> str:

    tex_files = [f for f in os.listdir(root_dir) if f.endswith(".tex")]

    if not tex_files:
        return None

    documentclass_pattern = re.compile(r'\\documentclass')
    begin_document_pattern = re.compile(r'\\begin\{document\}')
    include_pattern = re.compile(r'\\(?:include|input)\{([^}]*)\}')

    scores = {}
    for tex_file in tex_files:
        path = os.path.join(root_dir, tex_file)
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()

        score = 0
        # Check for \documentclass
        if documentclass_pattern.search(content):
            score += 5
        # Check for \begin{document}
        if begin_document_pattern.search(content):
            score += 3
        # Count how many \include/\input references
        includes = include_pattern.findall(content)
        score += len(includes)  # Each reference adds 1 point

        # (Optional) Give bonus points for \end{document}, etc.
        # Or check for certain macros that typically appear in main files.

        scores[tex_file] = score

    # Sort files by their score in descending order
    sorted_by_score = sorted(scores.items(), key=lambda x: x[1], reverse=True)

    os.chdir(root_dir)
    # If the top file has a nonzero score, return it
    if sorted_by_score[0][1] > 0:
        for file, score in sorted_by_score:
            try:
                print(f"Attempting to parse {file} as the root file.")
                md_text = pypandoc.convert_file(
                    source_file=file,
                    to='markdown',
                    format='latex'
                )
                return md_text
            except Exception as e:
                print(f"Warning: {file} was not the root file.")
                print(f"Exception: {e}")
        print("No tex files could be parsed as the root file.")


def split_on_lines(
    text: str
) -> List[str]:
    paragraphs = re.split(r"\n\s*\n+", text.strip())
    paragraphs = [p.strip() for p in paragraphs if p.strip()]
    return paragraphs
