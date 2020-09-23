from google.cloud import storage
from google.oauth2 import service_account
import sys
import os
import re
from datetime import timedelta
import json

'''
1. cd ~/mindcontrol
2. Make sure you have a credentials.json file for Google Storage access.
   Run 'export GOOGLE_APPLICATION_CREDENTIALS=/path/to/credentials.json'
3. Set parameters below as needed.
4. From root of repo, run 'python3 generate_start_up_json.py'
5. You should see a files called start_up_json.json be created in the repo.
6. Host your start_up_json.json on a server and make sure it's public.
7. Copy/paste its url into the "startup_json" value on settings.dev.json
8. Run 'meteor reset' in terminal
9. Run 'meteor --settings settings.dev.json' in terminal
'''
''' 
SET PARAMETERS BELOW
'''
bucket_name="spi2_4_inputs" # name of google storage bucket
file_name = "mag_res.nii.gz" # name of image you want from bucket
max_results = 20 # max number of files to pull from bucket (before we filter for specific file_name
session_time = 3600 # how long the signed urls will give you access to the images in Google Storage (in seconds)
''' 
SET PARAMETERS ABOVE
'''


outputfilename = "./start_up_json.json"

def list_images_in_storage(bucket_name):
    storage_client = storage.Client()
    return storage_client.list_blobs(bucket_name, max_results=max_results)

def make_dict_for_json(images):
	# cursor for all image blobs
    images = list_images_in_storage(bucket_name)
    subjects = {}
    for i in images:
        name = i.name
        m = re.match(r"(?P<subj_id>\w+)/month(?P<month_num>\d+)/(?P<anat_level>.*?)/mag_res\.nii\.gz", name)
        if m:
            parsed_dict = m.groupdict()
            subj_id = parsed_dict["subj_id"]
            month = parsed_dict["month_num"]
            anat_level = parsed_dict["anat_level"]
            signed_url = i.generate_signed_url(timedelta(seconds=session_time))

            if subj_id in subjects:
                subj = subjects[subj_id]
                subj["check_masks"].append(signed_url)
            else:
                new_subj = {"check_masks":[signed_url], 
                    "entry_type": "SPI2",
                    "metrics": {
                        "Age": 6.728039999999999,
                        "EHQ_Total": 65.57,
                        "Sex": 1.0
                    },
                    "name": '{}_month{}_{}_{}'.format(subj_id, month, anat_level, file_name)}
                subjects[subj_id] = new_subj

    subjects_list = list(subjects.values())
    with open(outputfilename, 'w') as outfile:
        json.dump(subjects_list, outfile)


if __name__ == "__main__":
    # args = sys.argv
    # download_NIFTI_from_bucket(args[1], args[2], args[3])
    images = list_images_in_storage(bucket_name)
    make_dict_for_json(images)
    
