
# Table of Contents

1.  [Introduction](#org040c96a)
2.  [Installation](#orgc82ad3f)
    1.  [Requirements](#orga203bd9)
    2.  [Install](#orgf0ba1eb)
3.  [Example](#org0c39f09)
    1.  [Running PreservedFS example](#orgb8e82b0)
    2.  [Using PreservedFS example](#org58fe6de)



# Introduction

**PreservedFS** is a Filesystem in Userspace that aims at mounting a folder, doing modifications inside the mounted folder while preserving the original files.

To achieve this, **PreservedFS** uses three folders :

-   `target` or `root`: the folder to be mounted
-   `local`: the folder that will keep only the modifications from `target`
-   `mnt`: the folder you will browse that is an union of `target` and `local` that reflect the original files with the changes from `local`.


<a id="orgc82ad3f"></a>

# Installation


## Requirements

You need `Python 2.3` or newer to be installed. You also need the `libfuse` library on your system (shipped by all major Linux distributions).


## Install

1.  Clone this repository
2.  Install `fuse-python` package:
    
        pip install fuse-python


# Example


## Running PreservedFS example

Go to the root directory of the cloned git repository and run:

    python preservedfs/preservedfs.py


## Using PreservedFS example

You can then browse to the `example/mnt` folder which is the folder mounted by **PreservedFS**.

You will see a union of the content of the folders `example/target` and `example/local`.

If you modify a file within the `example/mnt` folder (such as this one `EXAMPLE.org`), the changes will be written in `example/local` and reflected in `example/mnt` but the original file will be preserved!

You can play around by creating / deleting files in `example/mnt` and see how it affects the folders `example/local` and `example/target`.

