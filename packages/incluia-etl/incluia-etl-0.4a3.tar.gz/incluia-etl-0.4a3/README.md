# Incluia-ETL
This repository contains general tools for Extracting, Transforming and Loading data in Incluia projects.

## 1. Setting the Repo <a name="settings"></a>
### 1.1 Github Repo <a name="github"></a>

This repo contains the functions that are repeatedly used in all Incluia Projects. To start a new country's project start by creating a github repo, apply `git clone` locally, and then copy-paste `src` and `notebooks` from the lastest Incluia's project.

### 1.2. Virtual Environment <a name="anaconda"></a>

Then, we updated Anaconda to its last version and afer we generated a virtual environment called *incluia-<country>* with the following command:

	> conda env create --file environment.yml

This command uses the following files: *environment.yml*, *setup.py*, and *requirements.txt*. To activate the environment do

	> conda activate incluia-<country>

## 2. Workflow of the project  <a name="workflow"></a>

	Workflow can be accessed and modified [Here](https://miro.com/app/board/o9J_lUVWc1c=/)

![Flowchart](https://user-images.githubusercontent.com/22568654/139956069-ffebe91c-45a9-42ac-9683-68346ac88c6a.jpg)
