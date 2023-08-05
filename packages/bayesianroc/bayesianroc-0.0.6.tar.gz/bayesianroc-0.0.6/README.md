# bayesianroc

**bayesianroc** is a Python package written by Franz Mayr and André Carrington, for Bayesian analysis of ROC plots (including Binary Chance), over the whole plot or in a region of interest.

Please read 'Bayesian ROC Tookit Documentation.docx' from the Github page for details.  

## Features

- Classes:

  - BayesianROC: a subclass of DeepROC (from the Deep ROC Toolkit).  It computes measures related to the Chance and Bayesian iso performance baselines and produces associated plots.  
  
- Example of Classification and Analysis

  - Test_Binary_Chance.py: creates a BayesianROC object and performs classification and analysis.  Questions are asked as input: you may hit enter to accept defaults, except it is recommended that you change the costs to see the effect of Binary Chance.  

## Installation

The package can be installed from PyPi:

```bash
pip install bayesianroc
  
