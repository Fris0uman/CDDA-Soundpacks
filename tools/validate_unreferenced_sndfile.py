#!/usr/bin/env python3

import argparse
import json
import os
import sys

args = argparse.ArgumentParser()
args.add_argument("dir", action="store", help="specify json directory")
args.add_argument("fmt", action="store", help="escapes output if set to GHA")
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


def gha_escape(msg: str) -> str:
    msg = msg.replace("%", "%25")
    msg = msg.replace("\r", "%0D")
    msg = msg.replace("\n", "%0A")
    return msg


def printout(msg: str, err_lvl: int):
    if args_dict["fmt"] == "GHA":
        errmsg = " + "
        if err_lvl == 1:
            errmsg = "::Warning::"
        elif err_lvl == 2:
            errmsg = "::Error::"
        print("{}{}".format(errmsg, gha_escape(msg)))
    else:
        errmsg = " + "
        if err_lvl == 1:
            errmsg = " - Warning: "
        elif err_lvl == 2:
            errmsg = " - Error: "
        print("{}{}".format(errmsg, msg))


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
                    printout("Found reference in {}".format(json_file), 0)
                    return True
    printout("No JSON reference for sound file {}".format(path), 2)
    return False


def check_credits(path) -> bool:
    fname = path.split("/").pop()
    for root, dirs, filenames in os.walk(args_dict["dir"]):
        for filename in filenames:
            if filename.lower() in { "credits.md", "credits.txt" }:
                cred_file = os.path.join(root, filename)
                with open(cred_file, "r", encoding="utf-8") as credata:
                    if fname in credata.read():
                        printout("Found credit entry for \"{}\" in {}"
                                 .format(fname, cred_file), 0)
                        return True
    printout("No credits entry for \"{}\"".format(fname), 2)
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
    printout("No sound files processed", 2)
    retval = 1

sys.exit(retval)
