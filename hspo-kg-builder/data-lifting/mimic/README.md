# Person-Centric Knowledge Graph Extraction using MIMIC-III dataset: An ICU-readmission prediction study 

## EHR Data Preprocessing

## Setup
### Requirements


### Execution Steps
- Download the <a target="_blank" href="https://physionet.org/content/mimiciii/1.4/">MIMIC-III</a> dataset \[1\] and store the .csv files under the ```data``` folder. Move the dictionary files under the ```data/dictionaries/``` folder.
- Run the ```1_data_selection.py``` script to clean and select the data.
- Run the ```2_1_data_wrangling.py``` and ```2_2_data_wrangling_grouped_icd9.py``` scripts to extract a unified json information with the information that is needed for the next steps. In the second version (```2_2_data_wrangling_grouped_icd9.py```), the ICD9 codes of the diseases/diagnoses and procedures are grouped.
- Run the ```3_1_data_mapping_dictionaries.py``` and ```3_2_data_mapping_dictionaries_grouped_icd9.py``` scripts (order should be respected) to extract map the ICD9 codes, using dictionaries, and extract the corresponding textual description.
- Run the ```4_data_sampling.py [--threshold]``` script to sample the patient records that are valid for our task. The threshold argument defines the the day span for monitoring if the patient is going to be readmitted to the ICU or no (e.g. python 4_data_sampling.py --threshold 30).
- Extract the UMLS codes from notes using the following steps:
    - Run ```notes_cui_extraction/find_remaining_files_create_note_buckets.py [--bucket_size]``` script to find the notes that have not been processed yet and create buckets with them. The <it>bucket_size</it> parameter defines the the size of each bucket of notes. We divide the notes into buckets for smoother processing in the next steps.


### Notes
- The implementation can be adapted easily other predictive tasks (e.g. mortality prediction) with an appropriate implementation/modification of the ```4_data_sampling.py``` script.

## References
```
[1] Johnson, A., Pollard, T., & Mark, R. (2016). MIMIC-III Clinical Database (version 1.4). PhysioNet. https://doi.org/10.13026/C2XW26
```