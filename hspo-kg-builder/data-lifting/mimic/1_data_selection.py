import pandas as pd
import os
from utils_ import read_csv


def data_selection(input_path, filename, columns_to_remove, output_path):
    d = read_csv(input_path + filename)
    d.columns= d.columns.str.lower()
    d.drop(columns_to_remove, axis=1, inplace=True)
    d.to_csv(output_path + filename.lower(), index=False)
    del d


if __name__ == '__main__':
    input_path = 'data/initial_data/'
    output_path = 'data/selected_data/'
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    
    # PATIENTS file
    data_selection(input_path, 
                   "PATIENTS.csv", 
                   ["row_id", "dod_hosp", "dod_ssn"], 
                   output_path)

    # ADMISSIONS file
    data_selection(input_path, 
                   "ADMISSIONS.csv", 
                   ["row_id", "admission_type", "admission_location", "discharge_location", 
                    "insurance", "language", "has_chartevents_data"], 
                   output_path)

    # ICUSTAYS file
    data_selection(input_path, 
                   "ICUSTAYS.csv", 
                   ["row_id", "first_careunit", "last_careunit", "first_wardid", "last_wardid"], 
                   output_path)

    # CHARTEVENTS file
    data_selection(input_path, 
                   "CHARTEVENTS.csv", 
                   ["row_id", "storetime", "cgid"], 
                   output_path)
    
    # DATETIMEEVENTS file
    data_selection(input_path, 
                   "DATETIMEEVENTS.csv", 
                   ["row_id", "storetime", "cgid"], 
                   output_path)
    
    # INPUTEVENTS_CV file
    data_selection(input_path, 
                   "INPUTEVENTS_CV.csv", 
                   ["row_id", "rate", "rateuom","storetime", "cgid", "orderid", 
                    "linkorderid", "originalamount", "originalamountuom", "originalroute",
                    "originalrate", "originalrateuom", "originalsite"], 
                   output_path)
    
    # INPUTEVENTS_MV file
    data_selection(input_path, 
                   "INPUTEVENTS_MV.csv", 
                   ["row_id", "rate", "rateuom","storetime", "cgid", "orderid", 
                     "linkorderid", "ordercategoryname", "secondaryordercategoryname", 
                     "ordercomponenttypedescription", "ordercategorydescription", "totalamount",
                     "totalamountuom", "isopenbag", "continueinnextdept", "cancelreason", 
                     "comments_editedby", "comments_canceledby", "comments_date", 
                     "originalamount", "originalrate"], 
                   output_path)

    # OUTPUTEVENTS file
    data_selection(input_path, 
                   "OUTPUTEVENTS.csv", 
                   ["row_id", "cgid"], 
                   output_path)
    
    # PROCEDUREEVENTS_MV file
    data_selection(input_path, 
                   "PROCEDUREEVENTS_MV.csv", 
                   ["row_id", "location", "locationcategory",
                    "storetime", "cgid", "orderid", "linkorderid", "ordercategoryname",
                    "secondaryordercategoryname", "ordercategorydescription", "isopenbag", 
                    "continueinnextdept", "cancelreason", "comments_editedby", 
                    "comments_canceledby", "comments_date"], 
                   output_path)
    
    # CPTEVENTS file
    data_selection(input_path, 
                   "CPTEVENTS.csv", 
                   ["row_id", "costcenter", "ticket_id_seq", "description"], 
                   output_path)
    
    # DIAGNOSES_ICD file
    data_selection(input_path, 
                   "DIAGNOSES_ICD.csv", 
                   ["row_id"], 
                   output_path)

    # PRESCRIPTIONS file
    data_selection(input_path, 
                   "PRESCRIPTIONS.csv", 
                   ["row_id", "icustay_id", "drug_type", "drug_name_poe", 
                    "drug_name_generic", "prod_strength", "dose_val_rx",
                    "dose_unit_rx", "form_val_disp", "form_unit_disp",
                    "route"], 
                   output_path)
    
    # PROCEDURES_ICD file
    data_selection(input_path, 
                   "PROCEDURES_ICD.csv", 
                   ["row_id", "seq_num"], 
                   output_path)
    
    # NOTEEVENTS file
    data_selection(input_path, 
                   "NOTEEVENTS.csv", 
                   ["row_id", "chartdate", "charttime", "storetime", "cgid", "iserror"], 
                   output_path)