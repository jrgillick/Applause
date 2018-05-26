# Applause

This repository contains code to run the experiments and to acquire and process the C-SPAN dataset presented in the following paper:
Jon Gillick and David Bamman, "Please Clap: Modeling Applause in Campaign Speeches", NAACL 2018

#### Accessing C-SPAN Data
To download the C-SPAN videos and transcripts, see src/cspan/scripts/download_cspan_data.py. To clean and process the data, see the rest of the files in the src/cspan/scripts/.

#### Detecting Applause in Audio
See src/Detection/Applause Detection.ipynb. Data to train this model can be found here: https://github.com/hipstas/applause-classifier.

#### Forced Alignment
We use the forced alignment code built on Kaldi: https://github.com/lowerquality/gentle.

#### Computing Features
See src/cspan/core.  Required libraries for audio features: http://librosa.github.io/librosa/, https://github.com/google/REAPER.

#### Training Models
See src/cspan/core/Run Models.ipynb and src/cspan/core/Run Neural.ipynb.

#### Enter Text and Get an Applause Prediction from a Trained Model
Coming soon.
