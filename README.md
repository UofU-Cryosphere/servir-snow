# Snow Remote Sensing
[![Build Status](https://travis-ci.org/UofU-Cryosphere/servir-snow.svg?branch=master)](https://travis-ci.org/UofU-Cryosphere/servir-snow)

Helper scripts to download and process remote sensing data for MODIS and AMSR 2 satellites.

## Setup

Steps for local setup:
* Clone repository
* Create conda environment using the supplied `environment.yml`:
```bash
conda create env -f environment.yml
```
* Install this repo to your conda environment:
```bash
conda activate servir_snow
cd <_path_to_cloned_repository_>/servir_snow
pip install -e .
```