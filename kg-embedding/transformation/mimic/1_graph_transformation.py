import os
import argparse
from helper import save_json
from rdflib import Graph


class GraphModUndirected:
    def __init__(self, file_path, context_flag, graph_version):
        self.file_path = file_path
        self.context_flag = context_flag
        self.init_graph = self.get_graph()
        self.triplet_dict = self.get_triplet_dict()
        if graph_version == 1:
            self.transformed_graph = self.get_transformed_graph_1()
        elif graph_version == 2:
            self.transformed_graph = self.get_transformed_graph_2()
        elif graph_version == 3:
            self.transformed_graph = self.get_transformed_graph_3()
        elif graph_version == 4:
            self.transformed_graph = self.get_transformed_graph_4()
    

    def get_graph(self):
        g = Graph()
        g.parse(self.file_path)
        return g

    
    def get_triplet_dict(self):
        triplet_dict = {}
        for s, p, o in self.init_graph.triples((None, None, None)):
            k = s.toPython().split('/')[-2] + '_' + s.toPython().split('/')[-1]
            if k not in triplet_dict.keys():
                try:
                    relation = p.toPython().split('/')[-1]
                    object = o.toPython().split('/')[-1]
                    triplet_dict[k] = {'relations': [relation],
                                       'objects': [object]}
                except:
                    relation = p.toPython().split('/')[-1]
                    object = o.split('/')[-1]
                    triplet_dict[k] = {'relations': [relation],
                                       'objects': [object]}
            else:
                try:
                    relation = p.toPython().split('/')[-1]
                    object = o.toPython().split('/')[-1]
                    triplet_dict[k]['relations'].append(relation)
                    triplet_dict[k]['objects'].append(object)
                except:
                    relation = p.toPython().split('/')[-1]
                    object = o.split('/')[-1]
                    triplet_dict[k]['relations'].append(relation)
                    triplet_dict[k]['objects'].append(object)
        
        for k in triplet_dict.keys():
            t = k.split('_')[0]
            for o in triplet_dict[k]['objects']:
                if o == 'procedure_provisioning' or o == 'medication_provisioning':
                    t += '_'
                    t += o
            triplet_dict[k]['type'] = t
        
        return triplet_dict


    def get_transformed_graph_1(self):
        bag_of_triplets = []
        for k in self.triplet_dict.keys():
            if self.triplet_dict[k]['type'] == 'patient':
                if self.context_flag['demographics']:
                    # Add marital status
                    ms_status = self.triplet_dict[k]['objects'][
                        self.triplet_dict[k]['relations'].index('hasMaritalStatus')]
                    if ms_status != 'marital_state_unknown':
                        bag_of_triplets.append((('patient', 'patient', 'patient'), 'hasMaritalStatus',
                                                (ms_status.replace('_', ' '), 'marital_status', 'marital_status')))
                    else:
                        bag_of_triplets.append((('patient', 'patient', 'patient'), 'hasMaritalStatus',
                                                ('unknown', 'marital_status', 'marital_status')))
                    # Add religion
                    religion = self.triplet_dict[k]['objects'][
                        self.triplet_dict[k]['relations'].index('followsReligion')]
                    if religion not in ['religion_unknown', 'other_religion']:
                        bag_of_triplets.append((('patient', 'patient', 'patient'), 'followsReligion',
                                                (religion.replace('_', ' '), 'religion', 'religion')))
                    else:
                        bag_of_triplets.append(
                            (('patient', 'patient', 'patient'), 'followsReligion', ('unknown', 'religion', 'religion')))
                    # Add race/ethnicity
                    race = self.triplet_dict[k]['objects'][
                        self.triplet_dict[k]['relations'].index('hasRaceorEthnicity')]
                    if race not in ['race_not_stated', 'race_unknown']:
                        bag_of_triplets.append((('patient', 'patient', 'patient'), 'hasRaceorEthnicity',
                                                (race.replace('_', ' '), 'race', 'race')))
                    else:
                        bag_of_triplets.append(
                            (('patient', 'patient', 'patient'), 'hasRaceorEthnicity', ('unknown', 'race', 'race')))
                    # Add gender
                    gender = self.triplet_dict[k]['objects'][self.triplet_dict[k]['relations'].index('hasGender')]
                    bag_of_triplets.append((('patient', 'patient', 'patient'), 'hasGender',
                                            (gender.replace('_', ' '), 'gender', 'gender')))
            # Add age
            if self.triplet_dict[k]['type'] == 'age':
                if self.context_flag['demographics']:
                    age_group = self.triplet_dict[k]['objects'][
                        self.triplet_dict[k]['relations'].index('belongsToAgeGroup')]
                    bag_of_triplets.append((('patient', 'patient', 'patient'), 'belongsToAgeGroup',
                                            (age_group.replace('_', ' '), 'age_group', 'age_group')))
            if self.triplet_dict[k]['type'] == 'disease':
                if self.context_flag['diseases']:
                    disease_name = self.triplet_dict[k]['objects'][
                        self.triplet_dict[k]['relations'].index('disease_name')]
                    bag_of_triplets.append(
                        (('patient', 'patient', 'patient'), 'hasDisease', (disease_name, 'disease', 'disease')))
            if self.triplet_dict[k]['type'] == 'intervention_procedure_provisioning':
                for o in self.triplet_dict[k]['objects']:
                    if o == 'CPT':
                        if self.context_flag['interventions_procedure_CPT']:
                            inter_name = self.triplet_dict[k]['objects'][
                                self.triplet_dict[k]['relations'].index('intervention_name')]
                            bag_of_triplets.append((('patient', 'patient', 'patient'), 'hasIntervention',
                                                    (inter_name, 'procedure_' + o, 'procedure')))
                    elif o == 'ICD9':
                        if self.context_flag['interventions_procedure_ICD9']:
                            inter_name = self.triplet_dict[k]['objects'][
                                self.triplet_dict[k]['relations'].index('intervention_name')]
                            bag_of_triplets.append((('patient', 'patient', 'patient'), 'hasIntervention',
                                                    (inter_name, 'procedure_' + o, 'procedure')))
            if self.triplet_dict[k]['type'] == 'intervention_medication_provisioning':
                if self.context_flag['interventions_medication']:
                    inter_name = self.triplet_dict[k]['objects'][
                        self.triplet_dict[k]['relations'].index('intervention_name')]
                    bag_of_triplets.append((('patient', 'patient', 'patient'), 'hasIntervention',
                                            (inter_name, 'procedure_medication', 'procedure')))
            if self.triplet_dict[k]['type'] in ['employment', 'household', 'housing']:
                if self.context_flag['social_info']:
                    social_context = k.split('_')[-1]
                    bag_of_triplets.append((('patient', 'patient', 'patient'), 'hasSocialContext', (
                    social_context.replace('_', ' '), self.triplet_dict[k]['type'], 'social_context')))

        return bag_of_triplets


    def get_transformed_graph_2(self):
        bag_of_triplets = []
        for k in self.triplet_dict.keys():
            if self.triplet_dict[k]['type'] == 'patient':
                if self.context_flag['demographics']:
                    # Add marital status
                    ms_status = self.triplet_dict[k]['objects'][
                        self.triplet_dict[k]['relations'].index('hasMaritalStatus')]
                    if ms_status != 'marital_state_unknown':
                        bag_of_triplets.append((('patient', 'patient', 'patient'), 'hasDemographics',
                                                (ms_status.replace('_', ' '), 'marital_status', 'demographic_info')))
                    else:
                        bag_of_triplets.append((('patient', 'patient', 'patient'), 'hasDemographics',
                                                ('unknown', 'marital_status', 'demographic_info')))
                    # Add religion
                    religion = self.triplet_dict[k]['objects'][
                        self.triplet_dict[k]['relations'].index('followsReligion')]
                    if religion not in ['religion_unknown', 'other_religion']:
                        bag_of_triplets.append((('patient', 'patient', 'patient'), 'hasDemographics',
                                                (religion.replace('_', ' '), 'religion', 'demographic_info')))
                    else:
                        bag_of_triplets.append((('patient', 'patient', 'patient'), 'hasDemographics',
                                                ('unknown', 'religion', 'demographic_info')))
                    # Add race/ethnicity
                    race = self.triplet_dict[k]['objects'][
                        self.triplet_dict[k]['relations'].index('hasRaceorEthnicity')]
                    if race not in ['race_not_stated', 'race_unknown']:
                        bag_of_triplets.append((('patient', 'patient', 'patient'), 'hasDemographics',
                                                (race.replace('_', ' '), 'race', 'demographic_info')))
                    else:
                        bag_of_triplets.append((('patient', 'patient', 'patient'), 'hasDemographics',
                                                ('unknown', 'race', 'demographic_info')))
                    # Add gender
                    gender = self.triplet_dict[k]['objects'][self.triplet_dict[k]['relations'].index('hasGender')]
                    bag_of_triplets.append((('patient', 'patient', 'patient'), 'hasDemographics',
                                            (gender.replace('_', ' '), 'gender', 'demographic_info')))
            # Add age
            if self.triplet_dict[k]['type'] == 'age':
                if self.context_flag['demographics']:
                    age_group = self.triplet_dict[k]['objects'][
                        self.triplet_dict[k]['relations'].index('belongsToAgeGroup')]
                    bag_of_triplets.append((('patient', 'patient', 'patient'), 'hasDemographics',
                                            (age_group.replace('_', ' '), 'age_group', 'demographic_infop')))
            if self.triplet_dict[k]['type'] == 'disease':
                if self.context_flag['diseases']:
                    disease_name = self.triplet_dict[k]['objects'][
                        self.triplet_dict[k]['relations'].index('disease_name')]
                    bag_of_triplets.append(
                        (('patient', 'patient', 'patient'), 'hasDisease', (disease_name, 'disease', 'disease')))
            if self.triplet_dict[k]['type'] == 'intervention_procedure_provisioning':
                for o in self.triplet_dict[k]['objects']:
                    if o == 'CPT':
                        if self.context_flag['interventions_procedure_CPT']:
                            inter_name = self.triplet_dict[k]['objects'][
                                self.triplet_dict[k]['relations'].index('intervention_name')]
                            bag_of_triplets.append((('patient', 'patient', 'patient'), 'hasIntervention',
                                                    (inter_name, 'procedure_' + o, 'procedure')))
                    elif o == 'ICD9':
                        if self.context_flag['interventions_procedure_ICD9']:
                            inter_name = self.triplet_dict[k]['objects'][
                                self.triplet_dict[k]['relations'].index('intervention_name')]
                            bag_of_triplets.append((('patient', 'patient', 'patient'), 'hasIntervention',
                                                    (inter_name, 'procedure_' + o, 'procedure')))
            if self.triplet_dict[k]['type'] == 'intervention_medication_provisioning':
                if self.context_flag['interventions_medication']:
                    inter_name = self.triplet_dict[k]['objects'][
                        self.triplet_dict[k]['relations'].index('intervention_name')]
                    bag_of_triplets.append((('patient', 'patient', 'patient'), 'hasIntervention',
                                            (inter_name, 'procedure_medication', 'procedure')))
            if self.triplet_dict[k]['type'] in ['employment', 'household', 'housing']:
                if self.context_flag['social_info']:
                    social_context = k.split('_')[-1]
                    bag_of_triplets.append((('patient', 'patient', 'patient'), 'hasSocialContext', (
                    social_context.replace('_', ' '), self.triplet_dict[k]['type'], 'social_context')))

        return bag_of_triplets


    def get_transformed_graph_3(self):
        bag_of_triplets = []
        for k in self.triplet_dict.keys():
            if self.triplet_dict[k]['type'] == 'patient':
                if self.context_flag['demographics']:
                    # Add marital status
                    ms_status = self.triplet_dict[k]['objects'][
                        self.triplet_dict[k]['relations'].index('hasMaritalStatus')]
                    if ms_status != 'marital_state_unknown':
                        bag_of_triplets.append((('patient', 'patient', 'patient'), 'has',
                                                (ms_status.replace('_', ' '), 'marital_status', 'info')))
                    else:
                        bag_of_triplets.append(
                            (('patient', 'patient', 'patient'), 'has', ('unknown', 'marital_status', 'info')))
                    # Add religion
                    religion = self.triplet_dict[k]['objects'][
                        self.triplet_dict[k]['relations'].index('followsReligion')]
                    if religion not in ['religion_unknown', 'other_religion']:
                        bag_of_triplets.append((('patient', 'patient', 'patient'), 'has',
                                                (religion.replace('_', ' '), 'religion', 'info')))
                    else:
                        bag_of_triplets.append(
                            (('patient', 'patient', 'patient'), 'has', ('unknown', 'religion', 'info')))
                    # Add race/ethnicity
                    race = self.triplet_dict[k]['objects'][
                        self.triplet_dict[k]['relations'].index('hasRaceorEthnicity')]
                    if race not in ['race_not_stated', 'race_unknown']:
                        bag_of_triplets.append(
                            (('patient', 'patient', 'patient'), 'has', (race.replace('_', ' '), 'race', 'info')))
                    else:
                        bag_of_triplets.append((('patient', 'patient', 'patient'), 'has', ('unknown', 'race', 'info')))
                    # Add gender
                    gender = self.triplet_dict[k]['objects'][self.triplet_dict[k]['relations'].index('hasGender')]
                    bag_of_triplets.append(
                        (('patient', 'patient', 'patient'), 'has', (gender.replace('_', ' '), 'gender', 'info')))
            # Add age
            if self.triplet_dict[k]['type'] == 'age':
                if self.context_flag['demographics']:
                    age_group = self.triplet_dict[k]['objects'][
                        self.triplet_dict[k]['relations'].index('belongsToAgeGroup')]
                    bag_of_triplets.append(
                        (('patient', 'patient', 'patient'), 'has', (age_group.replace('_', ' '), 'age_group', 'info')))
            if self.triplet_dict[k]['type'] == 'disease':
                if self.context_flag['diseases']:
                    disease_name = self.triplet_dict[k]['objects'][
                        self.triplet_dict[k]['relations'].index('disease_name')]
                    bag_of_triplets.append(
                        (('patient', 'patient', 'patient'), 'has', (disease_name, 'disease', 'info')))
            if self.triplet_dict[k]['type'] == 'intervention_procedure_provisioning':
                for o in self.triplet_dict[k]['objects']:
                    if o == 'CPT':
                        if self.context_flag['interventions_procedure_CPT']:
                            inter_name = self.triplet_dict[k]['objects'][
                                self.triplet_dict[k]['relations'].index('intervention_name')]
                            bag_of_triplets.append(
                                (('patient', 'patient', 'patient'), 'has', (inter_name, 'procedure_' + o, 'info')))
                    elif o == 'ICD9':
                        if self.context_flag['interventions_procedure_ICD9']:
                            inter_name = self.triplet_dict[k]['objects'][
                                self.triplet_dict[k]['relations'].index('intervention_name')]
                            bag_of_triplets.append(
                                (('patient', 'patient', 'patient'), 'has', (inter_name, 'procedure_' + o, 'info')))
            if self.triplet_dict[k]['type'] == 'intervention_medication_provisioning':
                if self.context_flag['interventions_medication']:
                    inter_name = self.triplet_dict[k]['objects'][
                        self.triplet_dict[k]['relations'].index('intervention_name')]
                    bag_of_triplets.append(
                        (('patient', 'patient', 'patient'), 'has', (inter_name, 'procedure_medication', 'info')))
            if self.triplet_dict[k]['type'] in ['employment', 'household', 'housing']:
                if self.context_flag['social_info']:
                    social_context = k.split('_')[-1]
                    bag_of_triplets.append((('patient', 'patient', 'patient'), 'has',
                                            (social_context.replace('_', ' '), self.triplet_dict[k]['type'], 'info')))

        return bag_of_triplets


    def get_transformed_graph_4(self):
        bag_of_triplets = []
        if self.context_flag['demographics']:
            bag_of_triplets.append((('patient', 'patient', 'patient'), 'has', ('demographics', 'demographics', 'group_node')))
        if self.context_flag['diseases']:
            bag_of_triplets.append((('patient', 'patient', 'patient'), 'has', ('diseases', 'diseases', 'group_node')))
        if self.context_flag['interventions']:
            bag_of_triplets.append((('patient', 'patient', 'patient'), 'has', ('interventions', 'interventions', 'group_node')))
        if self.context_flag['social_info']:
            bag_of_triplets.append((('patient', 'patient', 'patient'), 'has', ('social context', 'social_context', 'group_node')))
        if self.context_flag['interventions_procedure_CPT']:
            bag_of_triplets.append((('interventions', 'interventions', 'group_node'), 'has', ('procedure provisioning CPT', 'procedure_provisioning_CPT', 'group_node')))
        if self.context_flag['interventions_procedure_ICD9']:
            bag_of_triplets.append((('interventions', 'interventions', 'group_node'), 'has', ('procedure provisioning ICD9', 'procedure_provisioning_ICD9', 'group_node')))
        if self.context_flag['interventions_medication']:
            bag_of_triplets.append((('interventions', 'interventions', 'group_node'), 'has', ('medication provisioning', 'medication_provisioning', 'group_node')))

        for k in self.triplet_dict.keys():
            if self.triplet_dict[k]['type'] == 'patient':
                if self.context_flag['demographics']:
                    # Add marital status
                    ms_status = self.triplet_dict[k]['objects'][
                        self.triplet_dict[k]['relations'].index('hasMaritalStatus')]
                    if ms_status != 'marital_state_unknown':
                        bag_of_triplets.append((('demographics', 'demographics', 'group_node'), 'hasMaritalStatus', (ms_status.replace('_', ' '), 'marital_status', 'marital_status')))
                    else:
                        bag_of_triplets.append((('demographics', 'demographics', 'group_node'), 'hasMaritalStatus', ('unknown', 'marital_status', 'marital_status')))
                    # Add religion
                    religion = self.triplet_dict[k]['objects'][
                        self.triplet_dict[k]['relations'].index('followsReligion')]
                    if religion not in ['religion_unknown', 'other_religion']:
                        bag_of_triplets.append((('demographics', 'demographics', 'group_node'), 'followsReligion', (religion.replace('_', ' '), 'religion', 'religion')))
                    else:
                        bag_of_triplets.append((('demographics', 'demographics', 'group_node'), 'followsReligion', ('unknown', 'religion', 'religion')))
                    # Add race/ethnicity
                    race = self.triplet_dict[k]['objects'][
                        self.triplet_dict[k]['relations'].index('hasRaceorEthnicity')]
                    if race not in ['race_not_stated', 'race_unknown']:
                        bag_of_triplets.append((('demographics', 'demographics', 'group_node'), 'hasRaceorEthnicity', (race.replace('_', ' '), 'race', 'race')))
                    else:
                        bag_of_triplets.append((('demographics', 'demographics', 'group_node'), 'hasRaceorEthnicity', ('unknown', 'race', 'race')))
                    # Add gender
                    gender = self.triplet_dict[k]['objects'][self.triplet_dict[k]['relations'].index('hasGender')]
                    bag_of_triplets.append((('demographics', 'demographics', 'group_node'), 'hasGender', (gender.replace('_', ' '), 'gender', 'gender')))
            # Add age
            if self.triplet_dict[k]['type'] == 'age':
                if self.context_flag['demographics']:
                    age_node = self.triplet_dict[k]['objects'][self.triplet_dict[k]['relations'].index('age_in_years')]
                    # Corner-case in Mimic: Patients, that are 89 years old or older, are masked. The masked age is over 300 years.
                    if int(age_node) >= 300:
                        age_node = '300'
                    bag_of_triplets.append((('demographics', 'demographics', 'group_node'), 'has', (age_node, 'age', 'group_node')))
                    stage_of_life = self.triplet_dict[k]['objects'][
                        self.triplet_dict[k]['relations'].index('hasStageOfLife')]
                    bag_of_triplets.append(((age_node, 'age', 'group_node'), 'hasStageOfLife', (stage_of_life.replace('_', ' '), 'stage_of_life', 'stage_of_life')))
                    age_group = self.triplet_dict[k]['objects'][
                        self.triplet_dict[k]['relations'].index('belongsToAgeGroup')]
                    bag_of_triplets.append(((age_node, 'age', 'group_node'), 'belongsToAgeGroup', (age_group.replace('_', ' '), 'age_group', 'age_group')))
            if self.triplet_dict[k]['type'] == 'disease':
                if self.context_flag['diseases']:
                    disease_name = self.triplet_dict[k]['objects'][self.triplet_dict[k]['relations'].index('disease_name')]
                    bag_of_triplets.append((('diseases', 'diseases', 'group_node'), 'hasDisease', (disease_name, 'disease', 'disease')))
            if self.triplet_dict[k]['type'] == 'intervention_procedure_provisioning':
                for o in self.triplet_dict[k]['objects']:
                    if o == 'CPT':
                        if self.context_flag['interventions_procedure_CPT']:
                            inter_name = self.triplet_dict[k]['objects'][self.triplet_dict[k]['relations'].index('intervention_name')]
                            bag_of_triplets.append((('procedure provisioning ' + o, 'procedure_provisioning_' + o, 'group_node'), 'hasIntervention', (inter_name, 'procedure_' + o, 'procedure_' + o)))
                    elif o == 'ICD9':
                        if self.context_flag['interventions_procedure_ICD9']:
                            inter_name = self.triplet_dict[k]['objects'][self.triplet_dict[k]['relations'].index('intervention_name')]
                            bag_of_triplets.append((('procedure provisioning ' + o, 'procedure_provisioning_' + o, 'group_node'), 'hasIntervention', (inter_name, 'procedure_' + o, 'procedure_' + o)))
            if self.triplet_dict[k]['type'] == 'intervention_medication_provisioning':
                if self.context_flag['interventions_medication']:
                    inter_name = self.triplet_dict[k]['objects'][
                        self.triplet_dict[k]['relations'].index('intervention_name')]
                    bag_of_triplets.append((('medication provisioning', 'medication_provisioning', 'group_node'), 'hasIntervention', (inter_name, 'procedure_medication', 'procedure_medication')))
            if self.triplet_dict[k]['type'] in ['employment', 'household', 'housing']:
                if self.context_flag['social_info']:
                    social_context = k.split('_')[-1]
                    bag_of_triplets.append((('social context', 'social_context', 'group_node'), 'hasSocialContext', (social_context.replace('_', ' '), self.triplet_dict[k]['type'], 'social_context')))

        return bag_of_triplets
    



class GraphModDirected:
    def __init__(self, file_path, context_flag, graph_version):
        self.file_path = file_path
        self.context_flag = context_flag
        self.init_graph = self.get_graph()
        self.triplet_dict = self.get_triplet_dict()
        if graph_version == 1:
            self.transformed_graph = self.get_transformed_graph_1()
        elif graph_version == 2:
            self.transformed_graph = self.get_transformed_graph_2()
        elif graph_version == 3:
            self.transformed_graph = self.get_transformed_graph_3()
        elif graph_version == 4:
            self.transformed_graph = self.get_transformed_graph_4()


    def get_graph(self):
        g = Graph()
        g.parse(self.file_path)
        return g

    
    def get_triplet_dict(self):
        triplet_dict = {}
        for s, p, o in self.init_graph.triples((None, None, None)):
            k = s.toPython().split('/')[-2] + '_' + s.toPython().split('/')[-1]
            if k not in triplet_dict.keys():
                try:
                    relation = p.toPython().split('/')[-1]
                    object = o.toPython().split('/')[-1]
                    triplet_dict[k] = {'relations': [relation],
                                       'objects': [object]}
                except:
                    relation = p.toPython().split('/')[-1]
                    object = o.split('/')[-1]
                    triplet_dict[k] = {'relations': [relation],
                                       'objects': [object]}
            else:
                try:
                    relation = p.toPython().split('/')[-1]
                    object = o.toPython().split('/')[-1]
                    triplet_dict[k]['relations'].append(relation)
                    triplet_dict[k]['objects'].append(object)
                except:
                    relation = p.toPython().split('/')[-1]
                    object = o.split('/')[-1]
                    triplet_dict[k]['relations'].append(relation)
                    triplet_dict[k]['objects'].append(object)
        
        for k in triplet_dict.keys():
            t = k.split('_')[0]
            for o in triplet_dict[k]['objects']:
                if o == 'procedure_provisioning' or o == 'medication_provisioning':
                    t += '_'
                    t += o
            triplet_dict[k]['type'] = t
        
        return triplet_dict



    def get_transformed_graph_1(self):
        bag_of_triplets = []
        for k in self.triplet_dict.keys():
            if self.triplet_dict[k]['type'] == 'patient':
                if self.context_flag['demographics']:
                    # Add marital status
                    ms_status = self.triplet_dict[k]['objects'][
                        self.triplet_dict[k]['relations'].index('hasMaritalStatus')]
                    if ms_status != 'marital_state_unknown':
                        bag_of_triplets.append(((ms_status.replace('_', ' '), 'marital_status', 'marital_status'),
                                                'hasMaritalStatus', ('patient', 'patient', 'patient')))
                    else:
                        bag_of_triplets.append((('unknown', 'marital_status', 'marital_status'), 'hasMaritalStatus',
                                                ('patient', 'patient', 'patient')))
                    # Add religion
                    religion = self.triplet_dict[k]['objects'][
                        self.triplet_dict[k]['relations'].index('followsReligion')]
                    if religion not in ['religion_unknown', 'other_religion']:
                        bag_of_triplets.append(((religion.replace('_', ' '), 'religion', 'religion'), 'followsReligion',
                                                ('patient', 'patient', 'patient')))
                    else:
                        bag_of_triplets.append(
                            (('unknown', 'religion', 'religion'), 'followsReligion', ('patient', 'patient', 'patient')))
                    # Add race/ethnicity
                    race = self.triplet_dict[k]['objects'][
                        self.triplet_dict[k]['relations'].index('hasRaceorEthnicity')]
                    if race not in ['race_not_stated', 'race_unknown']:
                        bag_of_triplets.append(((race.replace('_', ' '), 'race', 'race'), 'hasRaceorEthnicity',
                                                ('patient', 'patient', 'patient')))
                    else:
                        bag_of_triplets.append(
                            (('unknown', 'race', 'race'), 'hasRaceorEthnicity', ('patient', 'patient', 'patient')))
                    # Add gender
                    gender = self.triplet_dict[k]['objects'][self.triplet_dict[k]['relations'].index('hasGender')]
                    bag_of_triplets.append(((gender.replace('_', ' '), 'gender', 'gender'), 'hasGender',
                                            ('patient', 'patient', 'patient')))
            # Add age
            if self.triplet_dict[k]['type'] == 'age':
                if self.context_flag['demographics']:
                    age_group = self.triplet_dict[k]['objects'][
                        self.triplet_dict[k]['relations'].index('belongsToAgeGroup')]
                    bag_of_triplets.append((
                                           (age_group.replace('_', ' '), 'age_group', 'age_group'), 'belongsToAgeGroup',
                                           ('patient', 'patient', 'patient')))
            if self.triplet_dict[k]['type'] == 'disease':
                if self.context_flag['diseases']:
                    disease_name = self.triplet_dict[k]['objects'][
                        self.triplet_dict[k]['relations'].index('disease_name')]
                    bag_of_triplets.append(
                        ((disease_name, 'disease', 'disease'), 'hasDisease', ('patient', 'patient', 'patient')))
            if self.triplet_dict[k]['type'] == 'intervention_procedure_provisioning':
                for o in self.triplet_dict[k]['objects']:
                    if o == 'CPT':
                        if self.context_flag['interventions_procedure_CPT']:
                            inter_name = self.triplet_dict[k]['objects'][
                                self.triplet_dict[k]['relations'].index('intervention_name')]
                            bag_of_triplets.append(((inter_name, 'procedure_' + o, 'procedure'), 'hasIntervention',
                                                    ('patient', 'patient', 'patient')))
                    elif o == 'ICD9':
                        if self.context_flag['interventions_procedure_ICD9']:
                            inter_name = self.triplet_dict[k]['objects'][
                                self.triplet_dict[k]['relations'].index('intervention_name')]
                            bag_of_triplets.append(((inter_name, 'procedure_' + o, 'procedure'), 'hasIntervention',
                                                    ('patient', 'patient', 'patient')))
            if self.triplet_dict[k]['type'] == 'intervention_medication_provisioning':
                if self.context_flag['interventions_medication']:
                    inter_name = self.triplet_dict[k]['objects'][
                        self.triplet_dict[k]['relations'].index('intervention_name')]
                    bag_of_triplets.append(((inter_name, 'procedure_medication', 'procedure'), 'hasIntervention',
                                            ('patient', 'patient', 'patient')))
            if self.triplet_dict[k]['type'] in ['employment', 'household', 'housing']:
                if self.context_flag['social_info']:
                    social_context = k.split('_')[-1]
                    bag_of_triplets.append(((social_context.replace('_', ' '), self.triplet_dict[k]['type'],
                                             'social_context'), 'hasSocialContext', ('patient', 'patient', 'patient')))

        return bag_of_triplets


    def get_transformed_graph_2(self):
        bag_of_triplets = []
        for k in self.triplet_dict.keys():
            if self.triplet_dict[k]['type'] == 'patient':
                if self.context_flag['demographics']:
                    # Add marital status
                    ms_status = self.triplet_dict[k]['objects'][
                        self.triplet_dict[k]['relations'].index('hasMaritalStatus')]
                    if ms_status != 'marital_state_unknown':
                        bag_of_triplets.append(((ms_status.replace('_', ' '), 'marital_status', 'demographic_info'),
                                                'hasDemographics', ('patient', 'patient', 'patient')))
                    else:
                        bag_of_triplets.append((('unknown', 'marital_status', 'demographic_info'), 'hasDemographics',
                                                ('patient', 'patient', 'patient')))
                    # Add religion
                    religion = self.triplet_dict[k]['objects'][
                        self.triplet_dict[k]['relations'].index('followsReligion')]
                    if religion not in ['religion_unknown', 'other_religion']:
                        bag_of_triplets.append(((religion.replace('_', ' '), 'religion', 'demographic_info'),
                                                'hasDemographics', ('patient', 'patient', 'patient')))
                    else:
                        bag_of_triplets.append((('unknown', 'religion', 'demographic_info'), 'hasDemographics',
                                                ('patient', 'patient', 'patient')))
                    # Add race/ethnicity
                    race = self.triplet_dict[k]['objects'][
                        self.triplet_dict[k]['relations'].index('hasRaceorEthnicity')]
                    if race not in ['race_not_stated', 'race_unknown']:
                        bag_of_triplets.append(((race.replace('_', ' '), 'race', 'demographic_info'), 'hasDemographics',
                                                ('patient', 'patient', 'patient')))
                    else:
                        bag_of_triplets.append((('unknown', 'race', 'demographic_info'), 'hasDemographics',
                                                ('patient', 'patient', 'patient')))
                    # Add gender
                    gender = self.triplet_dict[k]['objects'][self.triplet_dict[k]['relations'].index('hasGender')]
                    bag_of_triplets.append(((gender.replace('_', ' '), 'gender', 'demographic_info'), 'hasDemographics',
                                            ('patient', 'patient', 'patient')))
            # Add age
            if self.triplet_dict[k]['type'] == 'age':
                if self.context_flag['demographics']:
                    age_group = self.triplet_dict[k]['objects'][
                        self.triplet_dict[k]['relations'].index('belongsToAgeGroup')]
                    bag_of_triplets.append(((age_group.replace('_', ' '), 'age_group', 'demographic_info'),
                                            'hasDemographics', ('patient', 'patient', 'patient')))
            if self.triplet_dict[k]['type'] == 'disease':
                if self.context_flag['diseases']:
                    disease_name = self.triplet_dict[k]['objects'][
                        self.triplet_dict[k]['relations'].index('disease_name')]
                    bag_of_triplets.append(
                        (('diseases', 'diseases', 'diseases'), 'hasDisease', (disease_name, 'disease', 'disease')))
            if self.triplet_dict[k]['type'] == 'intervention_procedure_provisioning':
                for o in self.triplet_dict[k]['objects']:
                    if o == 'CPT':
                        if self.context_flag['interventions_procedure_CPT']:
                            inter_name = self.triplet_dict[k]['objects'][
                                self.triplet_dict[k]['relations'].index('intervention_name')]
                            bag_of_triplets.append(((inter_name, 'procedure_' + o, 'procedure'), 'hasIntervention',
                                                    ('interventions', 'interventions', 'interventions')))
                    elif o == 'ICD9':
                        if self.context_flag['interventions_procedure_ICD9']:
                            inter_name = self.triplet_dict[k]['objects'][
                                self.triplet_dict[k]['relations'].index('intervention_name')]
                            bag_of_triplets.append(((inter_name, 'procedure_' + o, 'procedure'), 'hasIntervention',
                                                    ('interventions', 'interventions', 'interventions')))
            if self.triplet_dict[k]['type'] == 'intervention_medication_provisioning':
                if self.context_flag['interventions_medication']:
                    inter_name = self.triplet_dict[k]['objects'][
                        self.triplet_dict[k]['relations'].index('intervention_name')]
                    bag_of_triplets.append(((inter_name, 'procedure_medication', 'procedure'), 'hasIntervention',
                                            ('interventions', 'interventions', 'interventions')))
            if self.triplet_dict[k]['type'] in ['employment', 'household', 'housing']:
                if self.context_flag['social_info']:
                    social_context = k.split('_')[-1]
                    bag_of_triplets.append(((social_context.replace('_', ' '), self.triplet_dict[k]['type'],
                                             'social_context'), 'hasSocialContext', ('patient', 'patient', 'patient')))

        return bag_of_triplets


    def get_transformed_graph_3(self):
        bag_of_triplets = []
        for k in self.triplet_dict.keys():
            if self.triplet_dict[k]['type'] == 'patient':
                if self.context_flag['demographics']:
                    # Add marital status
                    ms_status = self.triplet_dict[k]['objects'][
                        self.triplet_dict[k]['relations'].index('hasMaritalStatus')]
                    if ms_status != 'marital_state_unknown':
                        bag_of_triplets.append(((ms_status.replace('_', ' '), 'marital_status', 'info'), 'has',
                                                ('patient', 'patient', 'patient')))
                    else:
                        bag_of_triplets.append(
                            (('unknown', 'marital_status', 'info'), 'has', ('patient', 'patient', 'patient')))
                    # Add religion
                    religion = self.triplet_dict[k]['objects'][
                        self.triplet_dict[k]['relations'].index('followsReligion')]
                    if religion not in ['religion_unknown', 'other_religion']:
                        bag_of_triplets.append(((religion.replace('_', ' '), 'religion', 'info'), 'has',
                                                ('patient', 'patient', 'patient')))
                    else:
                        bag_of_triplets.append(
                            (('unknown', 'religion', 'info'), 'has', ('patient', 'patient', 'patient')))
                    # Add race/ethnicity
                    race = self.triplet_dict[k]['objects'][
                        self.triplet_dict[k]['relations'].index('hasRaceorEthnicity')]
                    if race not in ['race_not_stated', 'race_unknown']:
                        bag_of_triplets.append(
                            ((race.replace('_', ' '), 'race', 'info'), 'has', ('patient', 'patient', 'patient')))
                    else:
                        bag_of_triplets.append((('unknown', 'race', 'info'), 'has', ('patient', 'patient', 'patient')))
                    # Add gender
                    gender = self.triplet_dict[k]['objects'][self.triplet_dict[k]['relations'].index('hasGender')]
                    bag_of_triplets.append(
                        ((gender.replace('_', ' '), 'gender', 'info'), 'has', ('patient', 'patient', 'patient')))
            # Add age
            if self.triplet_dict[k]['type'] == 'age':
                if self.context_flag['demographics']:
                    age_group = self.triplet_dict[k]['objects'][
                        self.triplet_dict[k]['relations'].index('belongsToAgeGroup')]
                    bag_of_triplets.append(
                        ((age_group.replace('_', ' '), 'age_group', 'info'), 'has', ('patient', 'patient', 'patient')))
            if self.triplet_dict[k]['type'] == 'disease':
                if self.context_flag['diseases']:
                    disease_name = self.triplet_dict[k]['objects'][
                        self.triplet_dict[k]['relations'].index('disease_name')]
                    bag_of_triplets.append(
                        ((disease_name, 'disease', 'info'), 'has', ('patient', 'patient', 'patient')))
            if self.triplet_dict[k]['type'] == 'intervention_procedure_provisioning':
                for o in self.triplet_dict[k]['objects']:
                    if o == 'CPT':
                        if self.context_flag['interventions_procedure_CPT']:
                            inter_name = self.triplet_dict[k]['objects'][
                                self.triplet_dict[k]['relations'].index('intervention_name')]
                            bag_of_triplets.append(
                                ((inter_name, 'procedure_' + o, 'info'), 'has', ('patient', 'patient', 'patient')))
                    elif o == 'ICD9':
                        if self.context_flag['interventions_procedure_ICD9']:
                            inter_name = self.triplet_dict[k]['objects'][
                                self.triplet_dict[k]['relations'].index('intervention_name')]
                            bag_of_triplets.append(
                                ((inter_name, 'procedure_' + o, 'info'), 'has', ('patient', 'patient', 'patient')))
            if self.triplet_dict[k]['type'] == 'intervention_medication_provisioning':
                if self.context_flag['interventions_medication']:
                    inter_name = self.triplet_dict[k]['objects'][
                        self.triplet_dict[k]['relations'].index('intervention_name')]
                    bag_of_triplets.append(
                        ((inter_name, 'procedure_medication', 'info'), 'has', ('patient', 'patient', 'patient')))
            if self.triplet_dict[k]['type'] in ['employment', 'household', 'housing']:
                if self.context_flag['social_info']:
                    social_context = k.split('_')[-1]
                    bag_of_triplets.append(((social_context.replace('_', ' '), self.triplet_dict[k]['type'], 'info'),
                                            'has', ('patient', 'patient', 'patient')))

        return bag_of_triplets


    def get_transformed_graph_4(self):
        bag_of_triplets = []
        if self.context_flag['demographics']:
            bag_of_triplets.append((('demographics', 'demographics', 'group_node'), 'has', ('patient', 'patient', 'patient')))
        if self.context_flag['diseases']:
            bag_of_triplets.append((('diseases', 'diseases', 'group_node'), 'has', ('patient', 'patient', 'patient')))
        if self.context_flag['interventions']:
            bag_of_triplets.append((('interventions', 'interventions', 'group_node'), 'has', ('patient', 'patient', 'patient')))
        if self.context_flag['social_info']:
            bag_of_triplets.append((('social context', 'social_context', 'group_node'), 'has', ('patient', 'patient', 'patient')))
        if self.context_flag['interventions_procedure_CPT']:
            bag_of_triplets.append((('procedure provisioning CPT', 'procedure_provisioning_CPT', 'group_node'), 'has', ('interventions', 'interventions', 'group_node')))
        if self.context_flag['interventions_procedure_ICD9']:
            bag_of_triplets.append((('procedure provisioning ICD9', 'procedure_provisioning_ICD9', 'group_node'), 'has', ('interventions', 'interventions', 'group_node')))
        if self.context_flag['interventions_medication']:
            bag_of_triplets.append((('medication provisioning', 'medication_provisioning', 'group_node'), 'has', ('interventions', 'interventions', 'group_node')))

        for k in self.triplet_dict.keys():
            if self.triplet_dict[k]['type'] == 'patient':
                if self.context_flag['demographics']:
                    # Add marital status
                    ms_status = self.triplet_dict[k]['objects'][self.triplet_dict[k]['relations'].index('hasMaritalStatus')]
                    if ms_status != 'marital_state_unknown':
                        bag_of_triplets.append((('demographics', 'demographics', 'group_node'), 'hasMaritalStatus', (ms_status.replace('_', ' '), 'marital_status', 'marital_status')))
                        bag_of_triplets.append(((ms_status.replace('_', ' '), 'marital_status', 'marital_status'), 'rev_hasMaritalStatus', ('demographics', 'demographics', 'group_node')))
                    else:
                        bag_of_triplets.append((('demographics', 'demographics', 'group_node'), 'hasMaritalStatus', ('unknown', 'marital_status', 'marital_status')))
                        bag_of_triplets.append((('unknown', 'marital_status', 'marital_status'), 'rev_hasMaritalStatus', ('demographics', 'demographics', 'group_node')))
                    # Add religion
                    religion = self.triplet_dict[k]['objects'][self.triplet_dict[k]['relations'].index('followsReligion')]
                    if religion not in ['religion_unknown', 'other_religion']:
                        bag_of_triplets.append((('demographics', 'demographics', 'group_node'), 'followsReligion', (religion.replace('_', ' '), 'religion', 'religion')))
                        bag_of_triplets.append(((religion.replace('_', ' '), 'religion', 'religion'), 'rev_followsReligion', ('demographics', 'demographics', 'group_node')))
                    else:
                        bag_of_triplets.append((('demographics', 'demographics', 'group_node'), 'followsReligion', ('unknown', 'religion', 'religion')))
                        bag_of_triplets.append((('unknown', 'religion', 'religion'), 'rev_followsReligion', ('demographics', 'demographics', 'group_node')))
                    # Add race/ethnicity
                    race = self.triplet_dict[k]['objects'][self.triplet_dict[k]['relations'].index('hasRaceorEthnicity')]
                    if race not in ['race_not_stated', 'race_unknown']:
                        bag_of_triplets.append((('demographics', 'demographics', 'group_node'), 'hasRaceorEthnicity', (race.replace('_', ' '), 'race', 'race')))
                        bag_of_triplets.append(((race.replace('_', ' '), 'race', 'race'), 'rev_hasRaceorEthnicity', ('demographics', 'demographics', 'group_node')))
                    else:
                        bag_of_triplets.append((('demographics', 'demographics', 'group_node'), 'hasRaceorEthnicity', ('unknown', 'race', 'race')))
                        bag_of_triplets.append((('unknown', 'race', 'race'), 'rev_hasRaceorEthnicity', ('demographics', 'demographics', 'group_node')))
                    # Add gender
                    gender = self.triplet_dict[k]['objects'][self.triplet_dict[k]['relations'].index('hasGender')]
                    bag_of_triplets.append((('demographics', 'demographics', 'group_node'), 'hasGender', (gender.replace('_', ' '), 'gender', 'gender')))
                    bag_of_triplets.append(((gender.replace('_', ' '), 'gender', 'gender'), 'rev_hasGender', ('demographics', 'demographics', 'group_node')))
            # Add age
            if self.triplet_dict[k]['type'] == 'age':
                if self.context_flag['demographics']:
                    age_node = self.triplet_dict[k]['objects'][self.triplet_dict[k]['relations'].index('age_in_years')]
                    # Corner-case in Mimic: Patients, that are 89 years old or older, are masked. The masked age is over 300 years.
                    if int(age_node) >= 300:
                        age_node = '300'
                    bag_of_triplets.append((('demographics', 'demographics', 'group_node'), 'has', (age_node, 'age', 'group_node')))
                    bag_of_triplets.append(((age_node, 'age', 'group_node'), 'rev_has', ('demographics', 'demographics', 'group_node')))
                    stage_of_life = self.triplet_dict[k]['objects'][self.triplet_dict[k]['relations'].index('hasStageOfLife')]
                    bag_of_triplets.append(((age_node, 'age', 'group_node'), 'hasStageOfLife', (stage_of_life.replace('_', ' '), 'stage_of_life', 'stage_of_life')))
                    bag_of_triplets.append(((stage_of_life.replace('_', ' '), 'stage_of_life', 'stage_of_life'), 'rev_hasStageOfLife', (age_node, 'age', 'group_node')))
                    age_group = self.triplet_dict[k]['objects'][self.triplet_dict[k]['relations'].index('belongsToAgeGroup')]
                    bag_of_triplets.append(((age_node, 'age', 'group_node'), 'belongsToAgeGroup', (age_group.replace('_', ' '), 'age_group', 'age_group')))
                    bag_of_triplets.append(((age_group.replace('_', ' '), 'age_group', 'age_group'), 'rev_belongsToAgeGroup', (age_node, 'age', 'group_node')))
            if self.triplet_dict[k]['type'] == 'disease':
                if self.context_flag['diseases']:
                    disease_name = self.triplet_dict[k]['objects'][self.triplet_dict[k]['relations'].index('disease_name')]
                    bag_of_triplets.append((('diseases', 'diseases', 'group_node'), 'hasDisease', (disease_name, 'disease', 'disease')))
                    bag_of_triplets.append(((disease_name, 'disease', 'disease'), 'rev_hasDisease', ('diseases', 'diseases', 'group_node')))
            if self.triplet_dict[k]['type'] == 'intervention_procedure_provisioning':
                for o in self.triplet_dict[k]['objects']:
                    if o == 'CPT':
                        if self.context_flag['interventions_procedure_CPT']:
                            inter_name = self.triplet_dict[k]['objects'][self.triplet_dict[k]['relations'].index('intervention_name')]
                            bag_of_triplets.append((('procedure provisioning ' + o, 'procedure_provisioning_' + o, 'group_node'), 'hasIntervention', (inter_name, 'procedure_' + o, 'procedure_' + o)))
                            bag_of_triplets.append(((inter_name, 'procedure_' + o, 'procedure_' + o), 'rev_hasIntervention', ('procedure provisioning ' + o, 'procedure_provisioning_' + o, 'group_node')))
                    elif o == 'ICD9':
                        if self.context_flag['interventions_procedure_ICD9']:
                            inter_name = self.triplet_dict[k]['objects'][self.triplet_dict[k]['relations'].index('intervention_name')]
                            bag_of_triplets.append((('procedure provisioning ' + o, 'procedure_provisioning_' + o, 'group_node'), 'hasIntervention', (inter_name, 'procedure_' + o, 'procedure_' + o)))
                            bag_of_triplets.append(((inter_name, 'procedure_' + o, 'procedure_' + o), 'rev_hasIntervention', ('procedure provisioning ' + o, 'procedure_provisioning_' + o, 'group_node')))
            if self.triplet_dict[k]['type'] == 'intervention_medication_provisioning':
                if self.context_flag['interventions_medication']:
                    inter_name = self.triplet_dict[k]['objects'][self.triplet_dict[k]['relations'].index('intervention_name')]
                    bag_of_triplets.append((('medication provisioning', 'medication_provisioning', 'group_node'), 'hasIntervention', (inter_name, 'procedure_medication', 'procedure_medication')))
                    bag_of_triplets.append(((inter_name, 'procedure_medication', 'procedure_medication'), 'rev_hasIntervention', ('medication provisioning', 'medication_provisioning', 'group_node')))
            if self.triplet_dict[k]['type'] in ['employment', 'household', 'housing']:
                if self.context_flag['social_info']:
                    social_context = k.split('_')[-1]
                    bag_of_triplets.append((('social context', 'social_context', 'group_node'), 'hasSocialContext', (
                        social_context.replace('_', ' '), self.triplet_dict[k]['type'], 'social_context')))
                    bag_of_triplets.append(((social_context.replace('_', ' '), self.triplet_dict[k]['type'], 'social_context'), 'hasSocialContext', ('social context', 'social_context', 'group_node')))

        return bag_of_triplets




class GraphTransformation:
    def __init__(self, input_path, context_flag, output_path, directed, graph_version):
        self.input_path = input_path
        self.context_flag = context_flag
        self.output_path = output_path
        if not os.path.exists(self.output_path):
            os.makedirs(self.output_path)
        self.directed = directed
        self.graph_version = graph_version
        self.graph_file_paths = self.find_ttl_files()
    

    def find_ttl_files(self):
        files = []
        for file in os.listdir(self.input_path):
            if file.endswith(".ttl"):
                files.append(os.path.join(self.input_path, file))
        return files

    
    def extraction(self):
        c = 0
        for f in self.graph_file_paths:
            if self.directed:
                save_json(GraphModDirected(f, self.context_flag, self.graph_version).transformed_graph, self.output_path + f.split('/')[-1].split('.')[0] + '.json')
            else:
                save_json(GraphModUndirected(f, self.context_flag, self.graph_version).transformed_graph, self.output_path + f.split('/')[-1].split('.')[0] + '.json')
            c += 1
            if c % 5000 == 0:
                print('{} graphs were processed' .format(c))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_path", default='../../../hspo-kg-builder/kg-generation/mimic/PKG/grouped_icd9/nodes_with_textual_description/with_new_URI/', type=str, required=True,
                        help = "The input path with the ontology-mapped graphs.")
    parser.add_argument("--output_path", default='data/triplet_format_graphs/', type=str, required=False, 
                        help = "The path for storing the transformed graphs.")
    parser.add_argument("--directed", default=None, type=int, required=True,
                        help = "Int value to define if the graph is going to be directed (1) or no. (0)")
    parser.add_argument("--graph_version", default=None, type=int, required=True,
                        help = "An id to define the graph version that is going to be used.")

    args = parser.parse_args()
    

    context_flag = {'demographics': 1,
                    'diseases': 1,
                    'interventions': 1,
                    'interventions_procedure_CPT': 0,
                    'interventions_procedure_ICD9': 1,
                    'interventions_medication': 1,
                    'social_info': 1}

    if args.directed:
        full_output_path_0 = args.output_path + 'directed/0/' + 'v' + str(args.graph_version) + '/' 
        full_output_path_1 = args.output_path + 'directed/1/' + 'v' + str(args.graph_version) + '/' 
    else:
        full_output_path_0 = args.output_path + 'undirected/0/' + 'v' + str(args.graph_version) + '/' 
        full_output_path_1 = args.output_path + 'undirected/1/' + 'v' + str(args.graph_version) + '/' 

    graph_0 = GraphTransformation(input_path = args.input_path + '0/', 
                                  context_flag = context_flag, 
                                  output_path = full_output_path_0, 
                                  directed = args.directed, 
                                  graph_version = args.graph_version)
    graph_0.extraction()

    graph_1 = GraphTransformation(input_path = args.input_path + '1/', 
                                  context_flag = context_flag, 
                                  output_path = full_output_path_1, 
                                  directed = args.directed, 
                                  graph_version = args.graph_version)
    graph_1.extraction()