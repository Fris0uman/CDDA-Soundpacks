#!/usr/bin/env python3

codec_target = 'vorbis'
bit_rate_target = '128000'
sample_rate_target = '48000'
channels_target = '1'

import json
import os
import subprocess
import argparse
import sys

args = argparse.ArgumentParser()
args.add_argument("rootdir", action="store", help="specify sounds directory")
args_dict = vars(args.parse_args())

def probe_file(f):
  jsin = json.loads(subprocess.run(["ffprobe", "-hide_banner", "-v", "quiet", "-print_format", "json",\
                                    "-show_format", "-show_streams", f], \
                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True).stdout)
  streams = jsin.get('streams', [])
  if len(streams) != 1:
    raise Exception(f'Bad stream count {len(streams)} in {f}, expected 1')
  for stream in streams:
    res = dict()
    res['codec'] = str(stream.get('codec_name', 'unknown'))
    res['channels'] = str(stream.get('channels', 'unknown'))
    res['sample_rate'] = str(stream.get('sample_rate', 'unknown'))
    res['bit_rate'] = str(stream.get('bit_rate', 'unknown'))
  return res

def validate_field_and_mark(p, field, expected):
  if p[field] == expected:
    p[field] += "✔️"
  else:
    p[field] += f"❌(expect {expected})"
    p['valid'] = False

def validate_probe(p):
  p['valid'] = True
  validate_field_and_mark(p, 'codec', codec_target)
  validate_field_and_mark(p, 'sample_rate', sample_rate_target)
  validate_field_and_mark(p, 'bit_rate', bit_rate_target)
  validate_field_and_mark(p, 'channels', channels_target)

print("| file | codec | channels | sample rate | bit rate |")
print("| :--- | :--- | ---: | ---: | ---: |")
exclude = set([ '.git', '.github', '.gitignore', '.gitmodules' ])
all_valid = True
probes = []

for root, dirs, files in os.walk(args_dict["rootdir"]):
  dirs[:] = [d for d in dirs if d not in exclude]
  for file in files:
    if file in exclude or file.endswith( ( ".json", ".md", ".py", ".txt", '.sh' ) ):
      continue

    fullpath = os.path.join( root, file ).replace( "\\", "/" )

    p = probe_file(fullpath)
    p['file'] = file
    validate_probe(p)

    if not p['valid']:
      all_valid = False

    probes.append(p)

probes.sort(key = lambda x: x['valid'])

for p in probes:
  print(f"| {p['file']} | {p['codec']} | {p['channels']} | {p['sample_rate']} | {p['bit_rate']} |")

sys.exit(0 if all_valid else 1)
