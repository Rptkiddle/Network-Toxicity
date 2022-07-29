# Network Toxicity

This repo contains replication materials for the work: 

*'Network Toxicity Analysis: an information-theoretic approach to studying the dynamic structure of toxicity on social media'*

Submitted as a final thesis project for the Research Masters Social Sciences (RMSS) programme at the Graduate School of Social Sciences (University of Amsterdam)

Author: Rupert Kiddle, 2022.

- This paper works with the dataset collected by Simon et. al. 2022: *LINK TO BE ADDED*

- This workflow uses the IDTxl mTE estimator that can be found here: https://github.com/pwollstadt/IDTxl


**WORKFLOW:**

- 1_prep.ipynb: takes messaging data and removes duplicates, returning unique messages in a .csv file. 

- 2_classify.py: takes a series of messages (in .csv or new line delimited text file) and queries the Perspective API (key required) in order to classify the toxicity of each; returns a JSON file of results. 

- 3_describe.ipynb: takes the JSON file returned above and produces several statistics and visualizations describing trends and distributions in the toxicity classification data; returns a .csv file with messaging data and toxicity scores combined. 

- 4_resample.py: takes the combined data from above and applies a chat/channel-level resampling strategy (suitable for Telegram, see paper for full details) to achieve a 5-minute equal sampling rate; returns resampled data.

- 5_estimate.py: takes the resampled toxicity data (see above) and iteratively calculates transfer entropy for multiple time periods using a sliding window technique; returns three .pkl files containing all results (indexed by time period) as well as data to reconcile edges with channels in the next step. 

- 6_results.ipynb: takes several files produced by this workflow (see workbook for further detail) as well as a manually specified .csv file with chat/channel information (taken from Simon et. al. 2022), restructures data into arrays and produces several network visualizations and statistics describing network toxicity relationships.
 
 
