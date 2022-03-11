#!/usr/bin/env python3

import argparse
import json
import os
import sys

args = argparse.ArgumentParser()
args.add_argument("dir", action="store", help="specify json directory")
args_dict = vars(args.parse_args())


snd_exts = {
    ".ogg",
    ".wav",
    ".mp3",
    ".aac",
    ".opus",
    ".flac",
    ".midi",
    ".aax",
    ".m4a",
    ".bnk",
    ".wma",
    ".aiff",
    ".raw",
    ".fla",
    ".mpa",
    ".oga",
    ".m3a",
    ".aif",
    ".mpega"
}


def find_obj_ref(sndfile, jo) -> bool:
    if "type" in jo:
        if jo["type"] == "playlist" and "playlists" in jo:
            for pl in jo["playlists"]:
                if "files" in pl:
                    for file in pl["files"]:
                        if file["file"] == sndfile:
                            return True
        if jo["type"] == "sound_effect" and "files" in jo:
            for file in jo["files"]:
                if file == sndfile:
                    return True
    return False


def find_ref(sndfile, jsonfile) -> bool:
    with open(jsonfile, "r", encoding="utf-8") as json_file:
        jdata = json.load(json_file)
        for jo in jdata:
            if type(jo) is not dict:
                if find_obj_ref(sndfile, jdata):
                    return True
                break
            if find_obj_ref(sndfile, jo):
                return True
    return False


def match_file(path) -> bool:
    for root, dirs, filenames in os.walk(args_dict["dir"]):
        for filename in filenames:
            json_file = os.path.join(root, filename)
            if json_file.endswith(".json"):
                if find_ref(path, json_file):
                    print(" + Found reference in {}".format(json_file))
                    return True
    print(" - Error: No JSON reference for sound file {}".format(path),
          file=sys.stderr)
    return False


def check_credits(path) -> bool:
    fname = path.split("/").pop()
    for root, dirs, filenames in os.walk(args_dict["dir"]):
        for filename in filenames:
            if filename.lower() in { "credits.md", "credits.txt" }:
                cred_file = os.path.join(root, filename)
                with open(cred_file, "r", encoding="utf-8") as credata:
                    if fname in credata.read():
                        print(" + Found credit entry for \"{}\" in {}"
                              .format(fname, cred_file))
                        return True
    print(" - Error: No credits entry for \"{}\"".format(fname))
    return False


retval = 0
at_least_one = False

for root, dirs, filenames in os.walk(args_dict["dir"]):
    for filename in filenames:
        path = os.path.join(root, filename)
        ext = os.path.splitext(filename)
        if ext[1].lower() in snd_exts:
            at_least_one = True
            shortpath = path.split(args_dict["dir"]).pop()
            print("\nSearching for references to {} ...".format(shortpath))
            if not match_file(shortpath):
                retval = 1
            if not check_credits(shortpath):
                retval = 1

if at_least_one == False:
    print("Error: No sound files processed", file=sys.stderr)
    retval = 1

sys.exit(retval)
