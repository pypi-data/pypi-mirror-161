#!/usr/bin/env python3

import os
import tensorboard
import shutil
import subprocess
import webbrowser


def show_results(fpath):
    fpath = fpath.replace("file://", "")
    print(fpath)
    for file in sorted(os.listdir(fpath)):
        if file.endswith("tfevents"):
            print(f"Found tf events file: {file}")

    os.system(f"tensorboard --logdir={fpath}")
    os.system(f"firefox http://localhost:6006/")
    # webbrowser.get("firefox").open_new_tab("http://localhost:6006/")
    # webbrowser.open("http://localhost:6006/")


if __name__ == '__main__':

    FDIR = "/media/findux/DATA/Documents/Malta_II/results/5763_2022-05-26_183938/"
    show_results(FDIR)

    # then open http://localhost:6006/ in browser.