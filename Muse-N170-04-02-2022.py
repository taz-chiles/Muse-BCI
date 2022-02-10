
import os
from collections import OrderedDict
import warnings
warnings.filterwarnings('ignore')

from eegnb import generate_save_fn
from eegnb.devices.eeg import EEG
from eegnb.experiments.visual_n170 import n170
from eegnb.datasets import fetch_dataset
from eegnb.analysis.utils import load_data, plot_conditions

from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score

from mne.decoding import Vectorizer

from pylsl import StreamInlet, resolve_stream

import matplotlib, mne
import numpy as np
from mne import Epochs,find_events

# Define some variables
board_name = 'muse2016'
# board_name = 'cyton'
experiment = 'visual_n170'
session = 999
subject = 999 # a 'very British number'
record_duration=120

# Initiate EEG device
eeg_device = EEG(device=board_name)

# Create output filename
save_fn = generate_save_fn(board_name, experiment, subject, session)

# Run experiment
n170.present(duration=record_duration, eeg=eeg_device, save_fn=save_fn)

# Practice loading an example N170 dataset then try and load the dataset that I saved. 

eegnb_data_path = os.path.join('~/','.eegnb', 'data')
n170_data_path = os.path.join('visual_n170','local', 'muse2016','subject0999','session999','recording_2022-02-04-21.41.20.csv')
#n170_data_path = os.path.join('visual_n170','local', 'muse2016','subject0999','session999','recording_2022-02-04-21.41.20.csv')

fetch_dataset(data_dir=n170_data_path, experiment='visual-N170', site='eegnb_examples')

# Load data as a raw object into MNE

subject = 1
session = 1
raw = load_data(subject,session,
                experiment='visual-N170', site='eegnb_examples', device_name='muse2016',
                data_dir = n170_data_path)

# Plot PSD
raw.plot_psd()

# Apply bandpass filter and plot again 
raw.filter(1,30, method='iir')
raw.plot_psd(fmin=1, fmax=120);

#inline is not interactive, use matplotlib notebook for an interactive plot
%matplotlib inline 
raw.plot(n_channels=16, scalings=dict(eeg=.0001), duration=30, title='Raw EEG');

# Create an array containing the timestamps and type of each stimulus (i.e. face or house)
events = find_events(raw)
event_id = {'House': 1, 'Face': 2}

# Create an MNE Epochs object representing all the epochs around stimulus presentation
epochs = Epochs(raw, events=events, event_id=event_id,
                tmin=-0.1, tmax=0.8, baseline=None,
                reject={'eeg': 75e-6}, preload=True,
                verbose=False, picks=[0,1,2,3])
print('sample drop %: ', (1 - len(epochs.events)/len(events)) * 100)
epochs.plot_image(picks=['TP9'])

# Plot epoch averages
conditions = OrderedDict()
conditions['House'] = [1]
conditions['Face'] = [2]

fig, ax = plot_conditions(epochs, conditions=conditions,
                          ci=97.5, n_boot=1000, title='',
                          diff_waveform=(1, 2))


# Can also plot an average of all epochs for all channels in a nicer looking graph with matplotlib 
%matplotlib inline
epochs.average().plot(spatial_colors=True);

# EVENT PROCESSING 

%matplotlib inline
events = mne.find_events(raw, 'stim') 
fig = mne.viz.plot_events(events, raw.info['sfreq'], event_id=event_id);

# RUN ICA TO CORRECT EYE MOVEMENTS

n_components = .99

ica = mne.preprocessing.ICA(n_components=n_components, method='fastica', 
                            max_iter=500, random_state=42)

picks = mne.pick_types(epochs.info, meg=False, 
                       eeg=True, eog=False, stim=False, exclude='bads')

ica.fit(epochs, picks=picks, decim=3, reject=None)

# Plot scalp maps of independent components
ica.plot_components(picks=None, ch_type='eeg');

# Should then remove any artifacts manually however won't do that this time. But for future reference

# ESTIMATING EVOKED RESPONSES

# Take an average of the epochs, then plot the average of the different events on top of each other.
house_evokeds = epochs['House'].average()
face_evokeds = epochs['Face'].average()

house_evokeds.plot(spatial_colors=True);
face_evokeds.plot(spatial_colors=True);

mne.viz.plot_compare_evokeds(dict(house=house_evokeds, face=face_evokeds))

house_evokeds.plot_joint()
face_evokeds.plot_joint()

# APPLY SOME MACHINE LEARNING 

# Classify using Logistic Regression 

# start by specifying labels and by creating a new copy of the original, unfiltered epochs
labels = epochs.events[:, -1]
new_epochs = epochs

# Get the data into the right format - first need to downsample (maybe)

from sklearn.utils import resample

#produces a list of individual epochs
nontarget_downsampled = resample(new_epochs['House'], 
                                 replace=False,    # sample without replacement
                                 n_samples=104,     # to match minority class
                                 random_state=123) # reproducible results

#concatenate them into nontargets
nontarget_downsampled = mne.concatenate_epochs(nontarget_downsampled)

targets = new_epochs['Face']

#concatenate to downsized sample
epochs_downsampled = mne.concatenate_epochs([targets, nontarget_downsampled])

downsized_labels = epochs_downsampled.events[:, -1]

clf = make_pipeline(Vectorizer(),
                    MinMaxScaler(),
                    LogisticRegression(penalty='l1', solver='liblinear',
                                       multi_class='auto'))

#split into the n-folds for n-fold cross validation
cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42) 

preds = np.empty(len(downsized_labels))

for train, test in cv.split(epochs_downsampled, downsized_labels):
    clf.fit(epochs_downsampled[train], downsized_labels[train])
    preds[test] = clf.predict(epochs_downsampled[test])
    
report = classification_report(downsized_labels, preds)
acc = accuracy_score(downsized_labels, preds)
    
print('Logistic Regression Classification for EEG Set 1: ' + str(acc))
print(report) #use this for a detailed report including precision, recall and f-measure

