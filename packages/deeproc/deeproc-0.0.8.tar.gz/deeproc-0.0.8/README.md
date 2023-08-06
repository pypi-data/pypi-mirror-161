# deeproc

**deeproc** is a Python package written by André Carrington and Yusuf Sheikh, for in-depth analysis of ROC plots in multiple groups/regions or a single region of interest.  It provides measures and plots which measure in a group: AUC (concordant partial AUC), the C statistic (partial C statistic), average sensitivity (partial AUC), average specificity (horizontal partial AUC) and other pre-test and post-test measures including average precision and inverse precision, also called average positive and negative predictive value.  
  
Groups are contiguous regions of predicted risk or probability (e.g., ranges of FPR or TPR) or non-contiguous demographic groups or clinical groups/arms.  Groups may be overlapping and not cover the whole ROC curve, or they may be mutually exclusive and perfectly cover the ROC curve.  

## Features

- Classes:

  - SimpleROC
  - FullROC
  - DeepROC
  - ConcordanceMatrixPlot

## Installation

The package can be installed from PyPi:

```bash
pip install deeproc
```
