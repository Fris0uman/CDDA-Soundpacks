"""
You need ffmpeg and ffprobe added to PATH to run this script
"""

#!python3

import json
import os
import subprocess
import shutil

class dotdict(dict):
    """dot.notation access to dictionary attributes"""
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__

tool_dir = os.path.dirname(__file__)

root_dir = os.path.join(tool_dir,'../sound/CC-Sounds')
exclude = set([ '.git', '.github', '.gitignore', '.gitmodules' ])
music_dirs = [os.path.join(tool_dir,'sound/CC-Sounds/music')]
ffprobe = shutil.which('ffprobe')
ffmpeg = shutil.which('ffmpeg')

bit_rate_target = 128000
sample_rate_target = 48000

ack_files = 0
nak_files = 0

def probe_file(file):
  jsin = json.loads(subprocess.run([ffprobe, "-hide_banner", "-v", "quiet", "-print_format", "json", "-show_format", "-show_streams", fullpath], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True).stdout)
  streams = jsin.get('streams', [])
  if len(streams) != 1:
    raise Exception(f'Streams count is {len(streams)}, expected 1')
  for stream in streams:
    res = dotdict()
    res['codec'] = stream.get('codec_name', 'unknown')
    res['channels'] = stream.get('channels', '0')
    res['sample_rate'] = stream.get('sample_rate', 'unknown')
    res['bit_rate'] = stream.get('bit_rate', 'unknown')
  return res

def run_ffmpeg(inputfile, params):
  # -q 3        VBR quality 3 (3 is default for libvorbis encoder)
  # -b:a XXXXX  target bitrate
  # -ar XXXXX   sampling rate
  subprocess.run([ffmpeg, '-i', inputfile, '-hide_banner', '-y', '-acodec', 'libvorbis', '-q', '3', \
                          '-b:a', str(bit_rate_target), '-ar', str(sample_rate_target)] + params, universal_newlines=True)

# https://stackoverflow.com/a/37487898
def append_suffix(fullpath, suffix):
  return "{0}{2}{1}".format(*os.path.splitext(fullpath) + (suffix,))

def convert_music(file):
  tempfile = append_suffix(fullpath, 'temp')
  # -ac 2 downmix to stereo
  run_ffmpeg(fullpath, ['-ac', '2', tempfile])
  os.replace(tempfile, file)

def convert_sound(file):
  tempfile = append_suffix(fullpath, 'temp')
  # -ac 1 downmix to mono
  run_ffmpeg(fullpath, ['-ac', '1', tempfile])
  os.replace(tempfile, file)

def validate_common(p):
  if str(p.codec) != 'vorbis':
    return f'codec is {p.codec}, expected vorbis'
  if int(p.sample_rate) != sample_rate_target:
    return f'sample rate is {p.sample_rate}, expected {sample_rate_target}'
  if int(p.bit_rate) > bit_rate_target:
    return f'bit rate is {p.bit_rate}, expected less than {bit_rate_target}'
  return None

def validate_music(fullpath):
  p = probe_file(fullpath)
  if int(p.channels) != 2:
    return f'channels is {p.channels}, expected 2'
  return validate_common(p)

def validate_sound(fullpath):
  p = probe_file(fullpath)
  if int(p.channels) != 1:
    return f'channels is {p.channels}, expected 1'
  return validate_common(p)

for root, dirs, files in os.walk(root_dir):
  dirs[:] = [d for d in dirs if d not in exclude]
  for file in files:
    if file in exclude:
      continue
    if file.endswith( ( ".json", ".md", ".py", ".txt", '.sh' ) ):
      continue

    fullpath = os.path.join( root, file ).replace( "\\", "/" )
    disppath = file.ljust(70)
    is_music = any([x in fullpath for x in music_dirs])

    if is_music:
      validation = validate_music(fullpath)
      if validation is None:
        print(f'{disppath} OK')
        ack_files = ack_files + 1
      else:
        print(f'{disppath} {validation}')
        nak_files = nak_files + 1
        convert_music(fullpath)
    else:
      validation = validate_sound(fullpath)
      if validation is None:
        print(f'{disppath} OK')
        ack_files = ack_files + 1
      else:
        print(f'{disppath} {validation}')
        nak_files = nak_files + 1
        convert_sound(fullpath)

print(f"OK: {ack_files}, invalid: {nak_files}")
