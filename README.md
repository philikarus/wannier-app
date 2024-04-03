# Wannier App

## About This App

This app allows you to interactively visualize projection bands of your VASP calculation and help you better decide dis_win and froz_win parameters in wannierization using Wannier90.

## Pre-requisites

The app is tested in python 3.10 and the required packages is listed in `requirements.txt`. You can install them by running the following command:

```bash
pip install -r requirements.txt
```

## Docker

A Docker image has been built for this app. You can start a container by running the following command:

```bash
docker run -p 8060:8060 -d --name wann-app wannier-app:0.9
`
