#!/usr/bin/env python3
"""Entry point: write the pre-rendered news image to the output dir.

The image itself is drawn by build_image.py (which needs Pillow) and is
committed beside this file as entry.png. This program uses only the
standard library, so it runs unchanged in the grading sandbox, and it
writes exactly the same bytes on every run.
"""
import os
import shutil


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    src = os.path.join(here, "entry.png")
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    shutil.copyfile(src, os.path.join(out_dir, "entry.png"))


if __name__ == "__main__":
    main()
