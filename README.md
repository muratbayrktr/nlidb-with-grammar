## Natural Language Interface to Databases (NLIDB) with Grammar

### Project Summary

This project implements a Natural Language Interface to Databases (NLIDB), designed to process natural language queries and generate corresponding SQL statements. By utilizing grammar-based parsing techniques, enriched input features, and machine learning models, the system effectively bridges the gap between user-friendly queries and database operations.

#### Key Features:
	•	Grammar-Based Parsing: Uses predefined grammatical structures for query processing.
	•	Machine Learning Integration: Predicts db names and table names using classifiers.
	•	Augmented Features: Enhances natural language input with database schema information.
---
#### Authors
	•	Murat Bayraktar
	•	Denizcan Yılmaz 
---
#### Using Poetry

This project uses Poetry to manage dependencies and environments. Follow these steps to set up and run the project:

Prerequisites
	•	Ensure you have Python 3.13 installed.
	•	Install Poetry if you haven’t already:

curl -sSL https://install.python-poetry.org | python3 -



Installation Steps
	1.	Clone the repository:

git clone https://github.com/muratbayrktr/nlidb-with-grammar.git
cd nlidb-with-grammar


	2.	Install project dependencies using Poetry:

poetry install


	3.	Activate the virtual environment:

poetry shell


	4.	Run the preprocessing or training scripts (e.g., preprocess.ipynb or xgboost_train.ipynb) within the Poetry environment.

Adding New Dependencies

If you need to add new dependencies, use:

poetry add <package-name>

To add a development dependency:

poetry add --dev <package-name>

Running Scripts with Poetry

To run Python scripts or notebooks, ensure the Poetry shell is active, then execute:

python <script_name>.py