# A False Sense of Security? Revisiting the State of Machine Learning-Based Industrial Intrusion Detection

This repository contains our evaluation artifacts to investigate the generalizability of machine learning-based industrial intrusion detection systems.

> Anomaly-based intrusion detection promises to detect novel or unknown attacks on industrial control systems by modeling expected system behavior and raising corresponding alarms for any deviations. As manually creating these behavioral models is tedious and error-prone, research focuses on machine learning to train them automatically, achieving detection rates upwards of 99 %. However, these approaches are typically trained not only on benign traffic but also on attacks and then evaluated against the same type of attack used for training. Hence, their actual, real-world performance on unknown (not trained on) attacks remains unclear. In turn, the reported near-perfect detection rates of machine learning-based intrusion detection might create a false sense of security. To assess this situation and clarify the _real_ potential of machine learning-based industrial intrusion detection, we develop an evaluation methodology and examine multiple approaches from literature for their performance on unknown attacks (excluded from training). Our results highlight an ineffectiveness in detecting unknown attacks, with detection rates dropping to between 3.2 % and 14.7 % for some types of attacks. Moving forward, we derive recommendations for further research on machine learning-based approaches to ensure clarity on their ability to detect unknown attacks.

## Publication

- Dominik Kus, Eric Wagner, Jan Pennekamp, Konrad Wolsing, Ina Berenice Fink, Markus Dahlmanns, Klaus Wehrle, and Martin Henze: _A False Sense of Security? Revisiting the State of Machine Learning-Based Industrial Intrusion Detection_. In Proceedings of the 8th ACM Cyber-Physical System Security Workshop (CPSS '22), ACM, 2022.

If you use any portion of our work, please cite our publication.

```
@inproceedings{kus2022generalizability,
    author = {Kus, Dominik and Wagner, Eric and Pennekamp, Jan and Wolsing, Konrad and Fink, Ina Berenice and Dahlmanns, Markus and Wehrle, Klaus and Henze, Martin},
    title = {{A False Sense of Security? Revisiting the State of Machine Learning-Based Industrial Intrusion Detection}},
    booktitle = {Proceedings of the 8th ACM Cyber-Physical System Security Workshop (CPSS '22)},
    year = {2022},
    month = {05},
    publisher = {ACM},
}
```

## Artifacts

###### Classifiers

We use the RF, SVM and BLSTM classifiers presented in the publication [Machine Learning for Reliable Network Attack Detection in SCADA Systems](https://doi.org/10.1109/TrustCom/BigDataSE.2018.00094).
In particular, we use an implementation of them on top of the Industrial Protocol Abstraction Layer IPAL which is available on [GitHub](https://github.com/fkie-cad/ipal_ids_framework).

###### Dataset

We use the MorrisDS4 dataset in Arff format ([Website](https://sites.google.com/a/uah.edu/tommy-morris-uah/ics-data-sets)).

Note, that RF and SVM operate on the system state which is obtained by the _keep last_ method while BLSTM operates directly on the data and handles empty fields using the _indicate-none_ preprocessor.

### Experimental Results

The generated artifacts are located in the experiment subfolders ([experiments/omit-attacks/results/](experiments/omit-attacks/results/) and [experiments/single-attacks/results/](experiments/single-attacks/results/)).
They are aggregated into a single JSON file [experiments/results.json](experiments/results.json) for easier handling.

Plots are generated using the scripts in the [plotting/](plotting/) subfolder.
A subset of the generated plots is presented in [PLOTS.md](PLOTS.md).

### Run Experiments

#### Python Environment

To run the experiments, a python environment with certain packages is needed.
With miniconda installed, it can be created and activated using:

```
conda env create
conda activate ml-and-ids
```

#### Preparation

The base dataset in Arff format can be downloaded on the project's [website](https://sites.google.com/a/uah.edu/tommy-morris-uah/ics-data-sets).

To run the required preprocessing on it, execute:

```
cd dataset
./prepare-dataset.sh -d <PATH_TO_ARFF_DATASET>
```

This will transcribe it to IPAL, add system state information and split it into 5 parts of equal size for cross-validation.

#### Run directly

The two experiments can be executed using the corresponding shell scripts in their respective subfolder ([experiments/omit-attacks/run-experiment.sh](experiments/omit-attacks/run-experiment.sh) and [experiments/single-attacks/run-experiment.sh](experiments/single-attacks/run-experiment.sh)).

Example to run the BLSTM baseline experiment (using a standard train/test split) and redirect its output to a file:

```
cd experiments/omit-attacks
./run-experiment.sh -c blstm 2>&1 | tee results/blstm/blstm-baseline.out
```

Example to run one single attacks experiment, training RF exclusively on attack type 3:

```
cd experiments/single-attacks
./run-experiment.sh -c rf -t 3 2>&1 | tee results/rf/rf-type-03.out
```

#### Slurm

For convenience, Slurm scripts are provided to run the experiments.
Note, that those scripts need to be run in the _experiment main folder_ and not in the respective `slurm/` subfolder.
Example:

```
cd experiments/omit-attacks
sbatch < slurm/rf-baseline.sh
```

#### Note for AMD CPUs

Performance of Tensorflow on AMD CPUs is severely degraded by Intel deliberately slowing down MKL.
To circumvent that, an older MKL version must be used (<= 2019) and `MKL_DEBUG_CPU_TYPE=5` must be set in the environment.
This speeds up BLSTM training from 120s per epoch to 2s per epoch.

## Acknowledgments

This work is funded by the Deutsche Forschungsgemeinschaft (DFG, German Research Foundation) under Germany's Excellence Strategy – EXC-2023 Internet of Production – 390621612.

## License

MIT License.
See [LICENSE](LICENSE) for details.
