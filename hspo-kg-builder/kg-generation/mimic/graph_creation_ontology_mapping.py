from rdflib import Graph, Literal, BNode
from rdflib.term import URIRef
from rdflib.namespace import RDF
import json
import os
import argparse

from utils_ import remove_special_character_and_spaces, read_json, process_URIRef_terms
from utils_ import Ontology


class GraphMapping:
    def __init__(self, input_data_path, input_ont_path, ont_namespace, 
                 URIflag, output_path, text_URI, gender_mapping, ethnicity_mapping, 
                 marital_status_mapping, religion_mapping):
        self.input_data_path = input_data_path
        self.data = self.read_json()
        self.ont_namespace = ont_namespace
        self.ont_obj = Ontology(input_ont_path, ont_namespace)
        self.gender_mapping = gender_mapping
        self.ethnicity_mapping = ethnicity_mapping 
        self.marital_status_mapping = marital_status_mapping
        self.religion_mapping = religion_mapping
        self.URIflag = URIflag
        self.output_path = output_path
        self.text_URI = text_URI
        self.create_output_dirs()
    

    def create_output_dirs(self):
        if self.URIflag == 0:
            if not(os.path.exists(self.output_path + 'withoutURI/1/')):
                os.makedirs(self.output_path + 'withoutURI/1/')
            if not(os.path.exists(self.output_path + 'withoutURI/0/')):
                os.makedirs(self.output_path + 'withoutURI/0/')
        elif self.URIflag == 1:
            if not(os.path.exists(self.output_path + 'withURI_mixed/1/')):
                os.makedirs(self.output_path + 'withURI_mixed/1/')
            if not(os.path.exists(self.output_path + 'withURI_mixed/0/')):
                os.makedirs(self.output_path + 'withURI_mixed/0/')
        elif self.URIflag == 2:
            if not(os.path.exists(self.output_path + 'with_new_URI/1/')):
                os.makedirs(self.output_path + 'with_new_URI/1/')
            if not(os.path.exists(self.output_path + 'with_new_URI/0/')):
                os.makedirs(self.output_path + 'with_new_URI/0/')
        else:
            print('Wrong URIflag was given.')
            
    
    def exec(self):
        for k1 in self.data.keys():
            for k2 in self.data[k1].keys():
                patient_adm_id = k1 + '_' + k2
                # Initialize the graph
                g = Graph()
                g.bind('hspo', self.ont_obj.ont_namespace)
                # Initialize the central patient node
                if self.URIflag == 0:
                    patient = BNode()
                elif self.URIflag == 1:
                    patient = URIRef(self.ont_namespace + 'Person')
                elif self.URIflag == 2:
                    #patient = URIRef(self.ont_namespace + patient_adm_id)
                    patient = URIRef(self.ont_namespace + 'patient/' + patient_adm_id)

                if self.URIflag in [0, 2]:
                    g.add((patient, RDF.type, self.ont_obj.ont_namespace.Person))

                g.add((patient, self.ont_obj.ont_namespace.person_id, Literal(patient_adm_id)))
                #g.add((patient, RDF.type, FOAF.Person))
                #g.add((patient, FOAF.name, Literal(patient_adm_id)))
                # Adding demographics information
                g.add((patient, self.ont_obj.ont_namespace.hasGender, self.gender_mapping[self.data[k1][k2]['gender'].lower()]))
                g.add((patient, self.ont_obj.ont_namespace.hasRaceorEthnicity, self.ethnicity_mapping[self.data[k1][k2]['ethnicity'].lower()]))
                g.add((patient, self.ont_obj.ont_namespace.hasMaritalStatus, self.marital_status_mapping[self.data[k1][k2]['marital_status'].lower()]))
                g.add((patient, self.ont_obj.ont_namespace.followsReligion, self.religion_mapping[self.data[k1][k2]['religion'].lower()]))
                # Adding age information
                if self.URIflag == 0:
                    age = BNode()
                elif self.URIflag == 1:
                    age = URIRef(self.ont_namespace + 'Age')
                elif self.URIflag == 2:
                    age = URIRef(self.ont_namespace + 'age/' + self.data[k1][k2]['age'])

                if self.URIflag in [0, 2]:
                    g.add((age, RDF.type, self.ont_obj.ont_namespace.Age))

                g.add((patient, self.ont_obj.ont_namespace.hasAge, age))
                g.add((age, self.ont_obj.ont_namespace.age_in_years, Literal(int(self.data[k1][k2]['age']))))
                g.add((age, self.ont_obj.ont_namespace.hasStageOfLife, self.define_stage_of_life(int(self.data[k1][k2]['age']))))
                g.add((age, self.ont_obj.ont_namespace.belongsToAgeGroup, self.get_age_group(int(self.data[k1][k2]['age']))))
                # Adding diagnoses/diseases
                tmp_diseases = []
                for j, d_icd9 in enumerate(self.data[k1][k2]['diagnoses']['icd9_code']):
                    if d_icd9 not in tmp_diseases:
                        tmp_diseases.append(d_icd9)
                        if self.URIflag == 0:
                            disease = BNode()
                        elif self.URIflag in [1, 2]:
                            ####################### TO BE DONE: Use the EFO ontology to create the URIs for the diseases. ######################
                            # Implement the method: get_EFO_mapping
                            # Strategy:
                            #   - Load the EFO ontology.
                            #   - Manipulate and process it in a similar to HSPO ontology processing.
                            #   - Map the ICD9 code to the provided URI by the EFO ontology.
                            #   - Use the URI for the created node. 
                            ####################################################################################################################
                            if self.text_URI:
                                diseases_URIRef_ready = remove_special_character_and_spaces(self.data[k1][k2]['diagnoses']['textual_description'][j])
                                #disease = URIRef(self.ont_namespace + diseases_URIRef_ready)
                                disease = URIRef(self.ont_namespace + 'disease/' + diseases_URIRef_ready)
                            else:
                                #disease = URIRef(self.ont_namespace + 'icd9_' + d_icd9)
                                disease = URIRef(self.ont_namespace + 'disease/icd9_' + d_icd9)

                        g.add((disease, RDF.type, self.ont_obj.ont_namespace.Disease))
                        g.add((patient, self.ont_obj.ont_namespace.hasDisease, disease))
                        g.add((disease, self.ont_obj.ont_namespace.icd9Code, Literal(d_icd9)))
                        # disease_name is going to be removed when the EFO ontology is going to be used for mapping. 
                        g.add((disease, self.ont_obj.ont_namespace.disease_name, Literal(self.data[k1][k2]['diagnoses']['textual_description'][j])))
                    else:
                        continue
                # Adding prescriptions as intervations
                tmp_drugs = []
                for j, prescription in enumerate(self.data[k1][k2]['prescriptions']['drug']):
                    # Avoid adding the drug more than ones.
                    if prescription not in tmp_drugs:
                        tmp_drugs.append(prescription)
                        if self.URIflag == 0:
                            intervention = BNode()
                        elif self.URIflag in [1, 2]:
                            prescription_URIRef_ready = remove_special_character_and_spaces(prescription.lower())
                            #intervention = URIRef(self.ont_namespace + prescription_URIRef_ready)
                            intervention = URIRef(self.ont_namespace + 'intervention/' + prescription_URIRef_ready)

                        g.add((intervention, RDF.type, self.ont_obj.ont_namespace.Intervation))
                        g.add((patient, self.ont_obj.ont_namespace.hasIntervention, intervention))
                        g.add((intervention, self.ont_obj.ont_namespace.intervention_name, Literal(prescription.lower())))
                        g.add((intervention, self.ont_obj.ont_namespace.intervention_code_system, Literal("NDC")))
                        #g.add((intervention, self.ont_obj.ont_namespace.intervention_code_system, Literal("GSN")))
                        g.add((intervention, self.ont_obj.ont_namespace.intervention_code, Literal(self.data[k1][k2]['prescriptions']['ndc'][j])))
                        #g.add((intervention, self.ont_obj.ont_namespace.intervention_code, Literal(self.data[k1][k2]['prescriptions']['gsn'][j])))
                        g.add((intervention, self.ont_obj.ont_namespace.hasInterventionType, URIRef(self.ont_namespace + 'medication_provisioning')))
                    else:
                        continue
                # Adding CPT events
                tmp_cpt_events = []
                for j, cpt_event in enumerate(self.data[k1][k2]['cpt_events']['subsection_header']):
                    # Avoid adding the CPT event more than ones.
                    if cpt_event not in tmp_cpt_events:
                        tmp_cpt_events.append(cpt_event)
                        if self.URIflag == 0:
                            intervention = BNode()
                        elif self.URIflag in [1, 2]:
                            #intervention = URIRef(self.ont_namespace + remove_special_character_and_spaces(cpt_event.lower()))
                            intervention = URIRef(self.ont_namespace + 'intervention/' + remove_special_character_and_spaces(cpt_event.lower()))

                        g.add((intervention, RDF.type, self.ont_obj.ont_namespace.Intervation))
                        g.add((patient, self.ont_obj.ont_namespace.hasIntervention, intervention))
                        g.add((intervention, self.ont_obj.ont_namespace.intervention_name, Literal(cpt_event.lower())))
                        g.add((intervention, self.ont_obj.ont_namespace.intervention_code_system, Literal("CPT")))
                        g.add((intervention, self.ont_obj.ont_namespace.intervention_code, Literal(self.data[k1][k2]['cpt_events']['cpt_code'][j])))
                        g.add((intervention, self.ont_obj.ont_namespace.hasInterventionType, URIRef(self.ont_namespace + 'procedure_provisioning')))
                
                # Adding procedures
                for j, proc_icd9 in enumerate(self.data[k1][k2]['procedures']['icd9_code']):
                    if self.URIflag == 0:
                        intervention = BNode()
                    elif self.URIflag in [1, 2]:
                        if self.text_URI:
                            intervention_URIRef_ready = remove_special_character_and_spaces(self.data[k1][k2]['procedures']['textual_description'][j])
                            #intervention = URIRef(self.ont_namespace + intervention_URIRef_ready)
                            intervention = URIRef(self.ont_namespace + 'intervention/' + intervention_URIRef_ready)
                        else:
                            #intervention = URIRef(self.ont_namespace + 'icd9_' + proc_icd9)
                            intervention = URIRef(self.ont_namespace + 'intervention/icd9_' + proc_icd9)
                     
                    g.add((intervention, RDF.type, self.ont_obj.ont_namespace.Intervation))
                    g.add((patient, self.ont_obj.ont_namespace.hasIntervention, intervention))
                    g.add((intervention, self.ont_obj.ont_namespace.icd9Code, Literal(proc_icd9)))
                    g.add((intervention, self.ont_obj.ont_namespace.intervention_name, Literal(self.data[k1][k2]['procedures']['textual_description'][j])))
                    g.add((intervention, self.ont_obj.ont_namespace.intervention_code_system, Literal("ICD9")))
                    g.add((intervention, self.ont_obj.ont_namespace.intervention_code, Literal(proc_icd9)))
                    g.add((intervention, self.ont_obj.ont_namespace.hasInterventionType, URIRef(self.ont_namespace + 'procedure_provisioning')))
                
                # Adding social context
                # Add employment
                try:
                    for empl in self.data[k1][k2]['social_info']['employment']['textual_description']:
                        employment_URIRef_ready = remove_special_character_and_spaces(empl)
                        #employment = URIRef(self.ont_namespace + employment_URIRef_ready)
                        employment = URIRef(self.ont_namespace + 'employment/' + employment_URIRef_ready)
                        g.add((employment, RDF.type, self.ont_obj.ont_namespace.Employment))
                        g.add((patient, self.ont_obj.ont_namespace.hasSocialContext, employment))
                except:
                    pass
                
                # Add household 
                try:
                    for h_cui in self.data[k1][k2]['social_info']['household_composition']['umls_codes']:
                        index = self.ont_obj.get_ont_classes_instances()[URIRef(self.ont_namespace + 'Household')]['umlsCui'].index(Literal(h_cui))
                        household = self.ont_obj.get_ont_classes_instances()[URIRef(self.ont_namespace + 'Household')]['instances'][index]
                        # Add the "household/" in the URI, it is useful for the next step where the RDF graphs are transformed into triplets for GNN training.
                        household_edited = '/'.join(household.split('/')[:-1] + ['household'] + [household.split('/')[-1]])
                        g.add((household_edited, RDF.type, self.ont_obj.ont_namespace.Household))
                        g.add((patient, self.ont_obj.ont_namespace.hasSocialContext, household_edited))
                except:
                    pass
                
                # Add housing
                try:
                    for h in self.data[k1][k2]['social_info']['housing']['textual_description']:
                        housing_URIRef_ready = remove_special_character_and_spaces(h)
                        #housing = URIRef(self.ont_namespace + housing_URIRef_ready)
                        housing = URIRef(self.ont_namespace + 'housing/' + housing_URIRef_ready)
                        g.add((housing, RDF.type, self.ont_obj.ont_namespace.Housing))
                        g.add((patient, self.ont_obj.ont_namespace.hasSocialContext, housing))
                except:
                    pass
                
                # Save the graph
                readmission_label = self.data[k1][k2]['readmission']
                if self.URIflag == 0:
                    g.serialize(destination = self.output_path + 'withoutURI/' + readmission_label + '/' + patient_adm_id + '.ttl')
                elif self.URIflag == 1:
                    g.serialize(destination = self.output_path + 'withURI_mixed/' + readmission_label + '/' + patient_adm_id + '.ttl')
                elif self.URIflag == 2:
                    g.serialize(destination = self.output_path + 'with_new_URI/' + readmission_label + '/' + patient_adm_id + '.ttl')
                    

    def define_stage_of_life(self, age):
        if age <= 1:
            return URIRef(self.ont_namespace + 'infant')
        elif age <= 4:
            return URIRef(self.ont_namespace + 'toddler')
        elif age <= 12:
            return URIRef(self.ont_namespace + 'child')
        elif age <= 19:
            return URIRef(self.ont_namespace + 'teen')
        elif age <= 39:
            return URIRef(self.ont_namespace + 'adult')
        elif age <= 59:
            return URIRef(self.ont_namespace + 'middle_age_adult')
        else:
            return URIRef(self.ont_namespace + 'senior_adult')
    

    def get_age_group(self, age):
        if age < 5:
            return URIRef(self.ont_namespace + 'under_five')
        elif age < 10:
            return URIRef(self.ont_namespace + 'five_to_nine')
        elif age < 15:
            return URIRef(self.ont_namespace + 'ten_to_fourteen')
        elif age < 20:
            return URIRef(self.ont_namespace + 'fifteen_to_nineteen')
        elif age < 25:
            return URIRef(self.ont_namespace + 'twenty_to_twentyfour')
        elif age < 30:
            return URIRef(self.ont_namespace + 'twentyfive_to_twentynine')
        elif age < 35:
            return URIRef(self.ont_namespace + 'thirty_to_thirtyfour')
        elif age < 40:
            return URIRef(self.ont_namespace + 'thirtyfive_to_thirtynine')
        elif age < 45:
            return URIRef(self.ont_namespace + 'forty_to_fortyfour')
        elif age < 50:
            return URIRef(self.ont_namespace + 'fortyfive_to_fortynine')
        elif age < 55:
            return URIRef(self.ont_namespace + 'fifty_to_fiftyfour')
        elif age < 60:
            return URIRef(self.ont_namespace + 'fiftyfive_to_fiftynine')
        elif age < 65:
            return URIRef(self.ont_namespace + 'sixty_to_sixtyfour')
        elif age < 70:
            return URIRef(self.ont_namespace + 'sixtyfive_to_sixtynine')
        elif age < 75:
            return URIRef(self.ont_namespace + 'seventy_to_seventyfour')
        elif age < 80:
            return URIRef(self.ont_namespace + 'seventyfive_to_seventynine')
        elif age < 85:
            return URIRef(self.ont_namespace + 'eighty_to_eightyfour')
        else:
            return URIRef(self.ont_namespace + 'over_eightyfive')
        

    def get_EFO_mapping(self):
        pass


    def read_json(self):
        with open(self.input_data_path) as json_file:
            return json.load(json_file)



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--data_path", default='../../data-lifting/mimic/data/processed_data/4_data_after_adding_notes_info_grouped_icd9.json', type=str, required=False,
                        help = "The path of the final json file with the data.")
    parser.add_argument("--ontology_path", default='../../../ontology/hspo.ttl', type=str, required=False,
                        help = "The path of the ontology .ttl file.")
    parser.add_argument("--URIflag", default=None, type=int, required=True,
                        help = "The flag to define the URI creation strategy. Possible values: 0, 1, 2")
    parser.add_argument("--output_path", default='PKG/grouped_icd9/nodes_with_textual_description/', type=str, required=True,
                        help = "The output path where the RDF graphs are going to be stored.")
    parser.add_argument("--text_URI", default=None, type=int, required=True,
                        help = "The flag to define if text (1) or ICD9 codes (0) are going to be used in the URI creation. Possible values: 0, 1")
    parser.add_argument("--gender_mapping_path", default='data/gender_mappings.json', type=str, required=False,
                        help = "The path of the gender mapping file.")
    parser.add_argument("--ethnicity_mapping_path", default='data/ethnicity_mappings.json', type=str, required=False,
                        help = "The path of the ethnicity mapping file.")
    parser.add_argument("--marital_status_mapping_path", default='data/marital_status_mappings.json', type=str, required=False,
                        help = "The path of the marital status mapping file.")
    parser.add_argument("--religion_mapping_path", default='data/religion_mappings.json', type=str, required=False,
                        help = "The path of the relation mapping file.")

    args = parser.parse_args()

    gender_mapping = process_URIRef_terms(read_json(args.gender_mapping_path))
    ethnicity_mapping = process_URIRef_terms(read_json(args.ethnicity_mapping_path))
    marital_status_mapping = process_URIRef_terms(read_json(args.marital_status_mapping_path))
    religion_mapping = process_URIRef_terms(read_json(args.religion_mapping_path))


    # Without URI
    g_obj = GraphMapping(args.data_path,
                           args.ontology_path,
                           'http://research.ibm.com/ontologies/hspo/',
                           args.URIflag,
                           args.output_path,
                           args.text_URI,
                           gender_mapping, 
                           ethnicity_mapping, 
                           marital_status_mapping, 
                           religion_mapping)
    
    g_obj.exec()