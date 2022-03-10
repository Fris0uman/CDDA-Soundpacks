#!/usr/bin/env python3

import argparse
import json
import os
import sys

args = argparse.ArgumentParser()
args.add_argument("dir", action="store", help="specify json directory")
args_dict = vars(args.parse_args())


fields = {
    "sound_effect": {
        "type",
        "id",
        "variant",
        "season",
        "is_indoors",
        "is_night",
        "volume",
        "files"
    },
    "sound_effect_preload": {
        "type",
        "preload"
    },
    "preload": {
        "id",
        "variant",
        "season",
        "is_indoors",
        "is_night"
    },
    "playlist": {
        "type",
        "playlists"
    },
    "playlists": {
        "id",
        "shuffle",
        "files"
    }
}


def parse_sound_effect(jo):
    if "id" not in jo:
        raise Exception("Missing field \"id\" in sound_effect")
    if "files" not in jo:
        raise Exception("Missing field \"files\" in sound_effect \"{}\""
                        .format(jo["id"]))
    for file in jo["files"]:
        path = os.path.join(args_dict["dir"], file)
        if not os.path.exists(path):
            raise Exception("File \"{}\" not found, required by sound_effect "
                            "\"{}\"".format(path, jo["id"]))
    for field in jo:
        if field not in fields["sound_effect"] and not field.startswith("//"):
            raise Exception("Unrecognized field \"{}\" in sound_effect \"{}\""
                            .format(field, jo["id"]))


def parse_sound_effect_preload(jo):
    if "preload" not in jo:
        raise Exception("Missing field \"preload\" in sound_effect_preload")
    for pl in jo["preload"]:
        if "id" not in pl:
            raise Exception("Missing field \"id\" in preload")
        for field in pl:
            if field not in fields["preload"]:
                raise Exception("Unrecognized field \"{}\" in preload \"{}\""
                                .format(field, pl["id"]))
    for field in jo:
        if field not in fields["sound_effect_preload"] and not field.startswith("//"):
            raise Exception("Unrecognized field \"{}\" in "
                            "sound_effect_preload".format(field))


def parse_playlist(jo):
    if "playlists" not in jo:
        raise Exception("Missing field \"playlists\" in playlist")
    for pl in jo["playlists"]:
        if "id" not in pl:
            raise Exception("Missing field \"id\" in playlist object")
        if "files" not in pl:
            raise Exception("Missing field \"files\" in playlist object "
                            "\"{}\"".format(pl["id"]))
        for file in pl["files"]:
            if "file" not in file:
                raise Exception("Missing field \"file\" in playlist file "
                                "\"{}\"".format(pl["id"]))
            if "volume" not in file:
                raise Exception("Missing field \"volume\" in playlist file "
                                "\"{}\"".format(pl["id"]))
        for field in pl:
            if field not in fields["playlists"] and not field.startswith("//"):
                raise Exception("Unrecognized field \"{}\" in playlist object "
                                "\"{}\"".format(field, pl["id"]))
    for field in jo:
        if field not in fields["playlist"] and not field.startswith("//"):
            raise Exception("Unrecognized field \"{}\" in playlist"
                            .format(field))


parsers = {
    "sound_effect": parse_sound_effect,
    "sound_effect_preload": parse_sound_effect_preload,
    "playlist": parse_playlist
}


def parse_json(path):
    print("Validating {} ...".format(path))
    with open(path, "r", encoding="utf-8") as json_file:
        jdata = json.load(json_file)
        for jo in jdata:
            if "type" in jo:
                jtype = ""
                try:
                    jtype = jo["type"].lower()
                except Exception as E:
                    print("Error: JSON content in file {} not wrapped in "
                          "'[]' brackets or object is malformed".format(path))
                    print("Exception: {}".format(E))
                    return True
                if jtype in parsers:
                    try:
                        parsers[jtype](jo)
                    except Exception as E:
                        print("Exception when parsing JSON data type "
                              "\"{}\" in file {}".format(jtype, path))
                        print(E)
                        return True
                else:
                    print("Unrecognized JSON data type \"{}\" in file {}"
                          .format(jtype, path))
                    return True
            else:
                print("Found JSON object with no \"type\" field in file {}"
                      .format(path))
                return True

    return False


for root, dirs, filenames in os.walk(args_dict["dir"]):
    for filename in filenames:
        path = os.path.join(root, filename)
        if path.endswith(".json"):
            if parse_json(path):
                sys.exit(1)

sys.exit(0)

