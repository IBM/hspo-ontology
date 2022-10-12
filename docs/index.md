
<img width="173" alt="image" src="img/hspo-logo.png">

# Documentation & User Guide
[![format](https://img.shields.io/badge/Ontology_Format-TTL-blue)](https://pages.github.ibm.com/Dublin-Research-Lab/hspo-ontology/ontology.ttl)
[![specification](https://img.shields.io/badge/Ontology_Specification-Docs-yellow)](ontology-specification/)
[![visualize](https://img.shields.io/badge/Visualize-WebVOWL-blue)](https://pages.github.ibm.com/Dublin-Research-Lab/hspo-ontology/ontology-specification/webvowl/index.html#)
[![license](https://img.shields.io/badge/License-Apache_2.0-green.svg)](LICENSE)
[![user guide](https://img.shields.io/badge/User_Guide-Docs-yellow)](https://pages.github.ibm.com/Dublin-Research-Lab/hspo-ontology/)

:construction:  Documentation under construction.
<br/>Please see the [Ontology Specification](ontology-specification/) for further technical details. 

# Overview

HSPO is an ontology that aims to build a holistic view centered around the individual and spans across their multiple facets (e.g. clinical, social, behavior). This ontology allows users to:

- Create star-shaped person-centered knowledge graphs which can then be, for example, translated into graph embeddings and used for downstream prediction or inference tasks
- Lift data from transactional records (e.g. Electronic Health Records) into a graph representation (e.g. represent a patient's hospital admission)
- Create a cohort of interest (e.g. group of patients in a clinical trial sharing similar characteristics)
- Mapping between existing terminologies and standards (e.g. UMLS, ICD)
- Annotation of unstructured data written in natural language

The ontology also defines the notion of evidence (e.g. information or knowledge extracted from research publications, statistical models, etc) which, in turn, enables graph completion. For example, the graph of an individual patient may be completed with information extracted from external sources of evidence (e.g. a research paper) and accompanied by a confidence score.

In the next chapter we will cover the available [Ontology classes](classes.md).
