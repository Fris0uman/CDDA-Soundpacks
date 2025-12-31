import json
import sys
import os
from glob import glob

folder_path = sys.argv[1]


def has_sounds(ref_dict, list_of_sounds):
    for objc in ref_dict:
        if objc['files'] == list_of_sounds:
            return True
    return False


if __name__ == '__main__':
    if not os.path.isdir(folder_path):
        print('argument needs to be a path to a folder')
        sys.exit()

    for file in glob(folder_path + '/**/*.json', recursive=True):
        ref_list = []
        with open(file, 'r') as f:
            dict_list = json.load(f)
            if len(dict_list) > 1:
                ref_list = [dict_list[0]]
                temp_list = dict_list
                # Build the list of all unique sound selection
                for obj in dict_list[1:]:
                    if not has_sounds(ref_list, obj['files']):
                        ref_list.append(obj)
                        temp_list.remove(obj)
                # Now merge in one object each object using the same sounds
                for obj_ref in ref_list:
                    variant_list = [obj_ref['variant']]
                    for obj in temp_list[1:]:
                        if obj_ref['files'] == obj['files']:
                            variant_list.append(obj['variant'])
                    obj_ref['variant'] = variant_list

        with open(file, 'w') as f:
            json.dump(ref_list, f, indent=2)
