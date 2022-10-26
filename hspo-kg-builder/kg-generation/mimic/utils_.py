from rdflib import Graph, Namespace
from rdflib.namespace import RDF, OWL
from rdflib.term import URIRef
import json


def read_json(path):
        with open(path) as json_file:
            return json.load(json_file)


def process_URIRef_terms(dict_):
    updated_dict_ = {}
    for k in dict_.keys():
        updated_dict_[k] = URIRef(dict_[k])
    return updated_dict_


def remove_special_character_and_spaces(text):
    proc_text = ''
    for word in text.split(' '):
        tmp_word = ''.join(c for c in word if c.isalnum())
        if len(tmp_word) > 0:
            proc_text += tmp_word.lower()
            proc_text += '_'
    # Remove the last _
    proc_text = proc_text[:-1]
    return proc_text


class Ontology:
    def __init__(self, input_path, ont_namespace):
        self.input_path = input_path
        self.ont = self.load_ontology()
        self.ont_namespace = Namespace(ont_namespace)
        self.ont_classes = self.get_ont_classes()
        self.ont_class_instances = self.get_ont_classes_instances()
    

    def load_ontology(self):
        ont = Graph()
        ont.parse(self.input_path)
        return ont
    

    def print_number_of_statements(self):
        print("Ontology has {} statements." .format(len(self.ont)))
    

    def get_ont_classes(self):
        classes = {'name': [],
                   'umlsCui': []}
        for s, _, _ in self.ont.triples((None,  RDF.type, OWL.Class)):
            classes['name'].append(s)
            tmp_umlsCui = []
            for _, _, o1 in self.ont.triples((s, self.ont_namespace.umlsCui, None)):
                tmp_umlsCui.append(o1)
            classes['umlsCui'].append(tmp_umlsCui)
        return classes
    

    def get_ont_classes_instances(self):
        classes_instances = {}
        for c in self.ont_classes['name']:
            classes_instances[c] = {'instances': [],
                                    'umlsCui': []}
            for s, _, _ in self.ont.triples((None,  RDF.type, c)):
                classes_instances[c]['instances'].append(s)
                for _, _, o1 in self.ont.triples((s, self.ont_namespace.umlsCui, None)):
                    classes_instances[c]['umlsCui'].append(o1)
        return classes_instances