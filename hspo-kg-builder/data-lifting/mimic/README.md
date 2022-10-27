# Person-Centric Knowledge Graph Extraction using MIMIC-III dataset: An ICU-readmission prediction study 

## EHR Data Preprocessing

## Setup
### Requirements
- Python 3.5+
- numpy (tested with version 1.23.1)
- pandas (tested with version 1.4.2)
- <a target="_blank" href="https://github.com/AnthonyMRios/pymetamap">pymetamap</a>


### Execution Steps
- Download the <a target="_blank" href="https://physionet.org/content/mimiciii/1.4/">MIMIC-III</a> dataset \[1\] and store the .csv files under the ```data/initial_data/``` folder. Move the dictionary files under the ```data/dictionaries/``` folder.
- Run the ```1_data_selection.py``` script to clean and select the data.
- Run the ```2_1_data_wrangling.py``` and ```2_2_data_wrangling_grouped_icd9.py``` scripts to extract a unified json information with the information that is needed for the next steps. In the second version (```2_2_data_wrangling_grouped_icd9.py```), the ICD9 codes of the diseases/diagnoses and procedures are grouped.
- Run the ```3_1_data_mapping_dictionaries.py``` and ```3_2_data_mapping_dictionaries_grouped_icd9.py``` scripts (order should be respected) to extract map the ICD9 codes, using dictionaries, and extract the corresponding textual description.
- Run the ```4_data_sampling.py [--threshold]``` script to sample the patient records that are valid for our task. The threshold argument defines the the day span for monitoring if the patient is going to be readmitted to the ICU or no (e.g. python 4_data_sampling.py --threshold 30).
- Extract the UMLS codes from notes using the following steps:
    - Install <a target="_blank" href="https://lhncbc.nlm.nih.gov/ii/tools/MetaMap/run-locally/MetaMapLite.html"> MetaMap Lite </a> \[2\]  (and <a target="_blank" href="https://lhncbc.nlm.nih.gov/ii/tools/MetaMap/documentation/Installation.html"> MetaMap </a> \[3\] optionally) locally. We recommend to store everything under the <i> notes_cui_extraction/MetaMap </i> folder.
    - Run the ```notes_cui_extraction/find_remaining_files_create_note_buckets.py --umls_codes_path [--bucket_size]``` script to find the notes that have not been processed yet and create buckets with them. We divide the notes into buckets for smoother processing in the next steps. Arguments:
        - umls_codes_path: The path where the extracted UMLS codes are stored.
        - bucket_size (optional):  The size of each bucket of notes.
    - Move the ```notes_cui_extraction/MetaMap/extract_umls_codes.py --bucket_path --bucket_id --metamap_path --output_path [--divide_and_merge]``` script under the base directory of MetaMap lite installment (e.g. (<i> notes_cui_extraction/MetaMap/public_mm_lite_3.6.2rc8 </i>).
    - Run the ```notes_cui_extraction/MetaMap/extract_umls_codes.py --bucket_path --bucket_id --metamap_path --output_path [--divide_and_merge]``` script to extract the UMLS codes of the notes. Arguments:
        - bucket_path: The relative path of the note buckets that were created by ```notes_cui_extraction/find_remaining_files_create_note_buckets.py --umls_codes_path [--bucket_size]``` script.
        - bucket_id: The bucket id/number to indicate the one that is going to be processed.
        - metamap_path: The full path of metamap base directory.
        - output_path: The path where the extracted umls codes are stored (e.g. <i> ../../data/processed_data/umls_codes_notes/ </i>).
        - divide_and_merge (optional): This is a flag to define if the notes are going to be divided into subnotes and then processed by metamap. The final UMLS sublists are merged. (Values: 0 or 1)
    - When the UMLS code extraction has been completed for all the notes, then run the ```notes_cui_extraction/map_extracted_umls_files.py --umls_codes_path --output_path``` to map the extracted umls files to the task-valid (readmission prediction) files. Arguments:
        - umls_codes_path: The path where the extracted umls codes are stored (e.g. <i> ../data/processed_data/umls_codes_notes/ </i>).
        - output_path: The path where the <b>mapped</b> extracted umls codes are going to be stored (e.g. <i> ../data/processed_data/umls_codes_notes_task_valid/ </i>).
- Run the ```5_notes_info_integration.py --grouped_ICD9 --umls_codes_path --employment_mapping_path --household_mapping_path --housing_mapping_path``` script to integrate the social info, related to employment, household and housing conditions, that exists in the extracted umls codes. The three mappings (employment, household and housing) should be provided by the user in csv files with two columns, one with the name <i>CUI</i> that contains the umls codes, and one with the name <i>Description</i> that shows the corresponding textual description of each code. The mapping can be created manually and/or using the ontology. Examples of mappings can be found under the <i>data</i> folder. Arguments:
    - grouped_ICD9: Flag to define the input data (grouped ICD9 version or non-grouped ICD9 version).
    - umls_codes_path: The path where the <b>mapped</b> extracted umls codes are stored (e.g. <i>../data/processed_data/umls_codes_notes/</i>)
    - employment_mapping_path: The path of the employment mapping csv file.
    - household_mapping_path: The path of the household mapping csv file.
    - housing_mapping_path: The path of the housing mapping csv file.
- Run the ```6_1_data_analysis_overall.py --data_path --output_path --diagnoses_dictionary_path --procedures_dictionary_path --procedures_dictionary_path --procedures_manual_dict_path --ethnicity_mapping_path --marital_status_mapping_path --religion_mapping_path``` script to extract the overall distributions of the data. The ontology-based mappings for the ethnicity, marital status and religion should be provided by the user. Example of mappings can be found under the <i>data</i> folder. Finally, the following distributions are extracted:
    - Distributions:
        - age
        - age group
        - co-morbidity
        - CPT events
        - diagnoses
        - employment status
        - gender
        - household composition
        - housing conditions
        - marital status
        - prescriptions 
        - procedures
        - race/ethnicity
        - readmissions
    - Arguments:
        - data_path: The path of the final json file with the data (e.g. <i>4_data_after_adding_notes_info_grouped_icd9.json</i>).
        - output_path: The output path where distributions are going to be stored.
        - diagnoses_dictionary_path: The path of the dignoses dictionary (<i>D_ICD_DIAGNOSES_updated.csv</i>). 
        - procedures_dictionary_path: The path of the procedure dictionary (<i>D_ICD_PROCEDURES.csv</i>).
        - diagnoses_manual_dict_path: The path of the diagnoses manual dictionary (<i>codes_diag_updated.json</i>). 
        - procedures_manual_dict_path: The path of the procedure manual dictionary (<i>codes_proc_updated.json</i>).
        - ethnicity_mapping_path: The path of the ethnicity mapping file. 
        - marital_status_mapping_path: The path of the marital_status mapping file. 
        - religion_mapping_path: The path of the religion mapping file.
- Run the ```6_2_data_analysis_per_group.py --data_path --output_path --diagnoses_dictionary_path --procedures_dictionary_path --procedures_dictionary_path --procedures_manual_dict_path --ethnicity_mapping_path --marital_status_mapping_path --religion_mapping_path``` script to extract the distributions of the data per group (readmission and no readmission cases).
- Run the ```6_3_data_analysis_specific_use_case.py --data_path --output_path --diagnoses_dictionary_path --procedures_dictionary_path --procedures_dictionary_path --procedures_manual_dict_path --ethnicity_mapping_path --marital_status_mapping_path --religion_mapping_path``` script to extract the distributions of a specific use case. For example, if only the patients that have heart failure (ICD9 code: 428) or cardiac_dysrhythmias (ICD9 code: 427) should be included, then the following command should be executed: ```6_3_data_analysis_specific_use_case.py --query_codes '428' '427' --query_code_descriptions 'diagnoses' 'icd9_code' --query_code_descriptions 'diagnoses' 'icd9_code'``` Additional arguments:
    - output_path_1: The output path where the overall distributions are going to be stored.
    - output_path_2: The output path where the distributions per group (readmission & no readmission cases) are going to be stored.
    - query_codes: The list of codes (ICD9) that are used to create the use case.
    - query_code_descriptions: The list of the description (keys) of the codes (ICD9) that are used to create the use case. It is used to properly parse the json file.
- Run the ```extract_explore_use_cases.py --data_path --query_codes --query_code_descriptions``` script to extract a use case and explore how many positive and negative readmission cases exist. 

### Notes
- The MIMIC dictionaries for mappings (ICD9 codes --> description) were not complete. So, we manually created complete mappings (files: ```codes_diag_updated.json```, ```codes_proc_updated.json``` under the <i>data/dictionaries/</i> folder).
- The implementation can be adapted easily other predictive tasks (e.g. mortality prediction) with an appropriate implementation/modification of the ```4_data_sampling.py``` script.
- If the ```notes_cui_extraction/MetaMap/extract_umls_codes.py --bucket_path --bucket_id --metamap_path --output_path [--divide_and_merge]``` script has not been completed for all the buckets that were extracted, then the ```notes_cui_extraction/find_remaining_files_create_note_buckets.py --umls_codes_path [--bucket_size]``` script should be executed again to find the remaining non-processed notes and create the new buckets.

## References
```
[1] Johnson, A., Pollard, T., & Mark, R. (2016). MIMIC-III Clinical Database (version 1.4). PhysioNet. https://doi.org/10.13026/C2XW26
[2] Demner-Fushman, Dina, Willie J. Rogers, and Alan R. Aronson. "MetaMap Lite: an evaluation of a new Java implementation of MetaMap." Journal of the American Medical Informatics Association 24.4 (2017): 841-844.
[3] Aronson, Alan R. "Effective mapping of biomedical text to the UMLS Metathesaurus: the MetaMap program." Proceedings of the AMIA Symposium. American Medical Informatics Association, 2001.
```