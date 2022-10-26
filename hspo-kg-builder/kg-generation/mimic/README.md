# Person-Centric Knowledge Graph Extraction using MIMIC-III dataset: An ICU-readmission prediction study 

## Knowledge Graph Generation

## Setup
### Requirements
- Python 3.5+
- rdflib (tested with version 6.1.1)
- HSPO ontology (tested with version 0.0.17)


### Execution 
- Run the ```graph_creation_ontology_mapping.py --data_path --ontology_path --URIflag --output_path --text_URI --gender_mapping_path --ethnicity_mapping_path --marital_status_mapping_path --religion_mapping_path``` script to extract the person-centric Knowledge Graphs in RDF format using the final .json file that is extracted from the data-preprocessing pipeline (code under <it>hspo-kg-builder/data-lifting/mimic/</it> folder). Arguments:
    - data_path: The path of the final json file with the data.
    - ontology_path: The path of the ontology .ttl file.
    - URIflag: The flag to define the URI creation strategy. Possible values: 0, 1, 2
    - output_path: The output path where the RDF graphs are going to be stored.
    - text_URI: The flag to define if text (1) or ICD9 codes (0) are going to be used in the URI creation. Possible values: 0, 1
    - gender_mapping_path: The path of the gender ontology mapping file.
    - ethnicity_mapping_path: The path of the ethnicity ontology mapping file.
    - marital_status_mapping_path: The path of the marital status ontology mapping file.
    - religion_mapping_path: The path of the relation mapping file.

### Notes


## References
```

```