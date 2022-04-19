# Alligator's Den

A News Recommender System, made as part of IDC410 (Machine Learning) course at IISERM.

## Setting up the environment

- Using `pip`:
```
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt
```

- Using `conda`:
```
conda env create --file=environments.yml
```


To run the web server for the application, go to the root directory and execute `./flask_api/run.py`. 

**Note:** Only ./flask_api contains the final code for the application. All other folders either contain corpus creation subroutines or sandbox notebooks that we used to experiment before implementation.