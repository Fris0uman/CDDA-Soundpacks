import json
import sys
import os
from glob import glob

folder_path = sys.argv[1]


# Check if ref_dict already has an object with the combination of files, is_indoors, is_night and season of new_dict
def has_sounds(ref_dict, new_dict):
    for objc in ref_dict:
        if objc['files'] == new_dict['files']:
            if 'is_indoors' in new_dict and 'is_indoor' in objc:
                if objc['is_indoors'] != new_dict['is_indoors']:
                    continue
            if 'is_night' in new_dict and 'is_night' in objc:
                if objc['is_night'] != new_dict['is_night']:
                    continue
            if 'season' in new_dict and 'season' in objc:
                if objc['season'] != new_dict['season']:
                    continue
            return True
    return False


if __name__ == '__main__':
    if not os.path.isdir(folder_path):
        print('argument needs to be a path to a folder')
        sys.exit()

    for file in glob(folder_path + '/**/*.json', recursive=True):
        ref_list = []
        write_new_dict = False
        with open(file, 'r') as f:
            dict_list = json.load(f)
            if len(dict_list) > 1:
                ref_list = [dict_list[0]]
                temp_list = dict_list
                # Build the list of all unique sound selection
                for obj in dict_list[1:]:
                    if not has_sounds(ref_list, obj):
                        ref_list.append(obj)
                        temp_list.remove(obj)
                # Now merge in one object each object using the same sounds
                for obj_ref in ref_list:
                    variant_list = [obj_ref['variant']]
                    for obj in temp_list[1:]:
                        if obj_ref['files'] == obj['files']:
                            variant_list.append(obj['variant'])
                    obj_ref['variant'] = variant_list
                write_new_dict = True

        if write_new_dict:
            with open(file, 'w') as f:
                json.dump(ref_list, f, indent=2)