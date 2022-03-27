# Experimental Result Plots

## Omit Attacks Experiment

| Relative recall change |                              RF                               |                              SVM                               |                              BLSTM                               |
| :--------------------: | :-----------------------------------------------------------: | :------------------------------------------------------------: | :--------------------------------------------------------------: |
|      Omit attacks      |  ![](plotting/recall-heatmaps/omit-attacks_rf_relative.png)   |  ![](plotting/recall-heatmaps/omit-attacks_svm_relative.png)   |  ![](plotting/recall-heatmaps/omit-attacks_blstm_relative.png)   |
|    Omit categories     | ![](plotting/recall-heatmaps/omit-categories_rf_relative.png) | ![](plotting/recall-heatmaps/omit-categories_svm_relative.png) | ![](plotting/recall-heatmaps/omit-categories_blstm_relative.png) |

| Absolute recall |                              RF                               |                              SVM                               |                              BLSTM                               |
| :-------------: | :-----------------------------------------------------------: | :------------------------------------------------------------: | :--------------------------------------------------------------: |
|  Omit attacks   |  ![](plotting/recall-heatmaps/omit-attacks_rf_absolute.png)   |  ![](plotting/recall-heatmaps/omit-attacks_svm_absolute.png)   |  ![](plotting/recall-heatmaps/omit-attacks_blstm_absolute.png)   |
| Omit categories | ![](plotting/recall-heatmaps/omit-categories_rf_absolute.png) | ![](plotting/recall-heatmaps/omit-categories_svm_absolute.png) | ![](plotting/recall-heatmaps/omit-categories_blstm_absolute.png) |

The first heatmap shows changes in recall relative to the baseline (`(baseline - value) / baseline`).
The color scheme is logarithmic which means that small values already have very saturated colors.
The second heatmap shows absolut recall values and has a linear color scale.
This corresponds to the plot from our publication.

Both have the omitted attack class on the y-axis and the attack class for which the recall value is calculated on the x-axis.
Therefore, one row represents the results from one trained IDS.
The baseline corresponds to the IDS trained on a standard 80/20 train/test split.

| Global metrics |                                                     |
| :------------: | :-------------------------------------------------: |
|    Accuracy    | ![](plotting/aggregated-metrics/omit_accuracy.png)  |
|   Precision    | ![](plotting/aggregated-metrics/omit_precision.png) |
|     Recall     |  ![](plotting/aggregated-metrics/omit_recall.png)   |
|       F1       |    ![](plotting/aggregated-metrics/omit_f1.png)     |

The metrics plot shows global metrics as achieved by the IIDS on the whole test set (which contains packets from all types of attacks as well as non-malicious packets).

## Single Attack Experiment

|  Absolute recall  |                           RF                           |                           SVM                           |                           BLSTM                           |
| :---------------: | :----------------------------------------------------: | :-----------------------------------------------------: | :-------------------------------------------------------: |
|  Single attacks   |  ![](plotting/recall-heatmaps/single-attacks_rf.png)   |  ![](plotting/recall-heatmaps/single-attacks_svm.png)   |  ![](plotting/recall-heatmaps/single-attacks_blstm.png)   |
| Single categories | ![](plotting/recall-heatmaps/single-categories_rf.png) | ![](plotting/recall-heatmaps/single-categories_svm.png) | ![](plotting/recall-heatmaps/single-categories_blstm.png) |

The heatmap shows the absolute recall values achieved by the IDSs.
It has the attack class which the IDS was trained on on the y-axis and the attack class for which the recall value is achieved on the x-axis.
Therefore, one row represents the results from one trained IDS.

| Global metrics |                    Global Metrics                     |
| :------------: | :---------------------------------------------------: |
|    Accuracy    | ![](plotting/aggregated-metrics/single_accuracy.png)  |
|   Precision    | ![](plotting/aggregated-metrics/single_precision.png) |
|     Recall     |  ![](plotting/aggregated-metrics/single_recall.png)   |
|       F1       |    ![](plotting/aggregated-metrics/single_f1.png)     |

The metrics plot shows global metrics as achieved by the IDS on the whole test set (which contains packets from all types of attacks as well as non-malicious packets).
