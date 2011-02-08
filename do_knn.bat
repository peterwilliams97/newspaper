python parse_weka_results.py -r 100 -o f:\kaggle\unimelb f:\kaggle\unimelb\jrip6a3.txt f:\kaggle\unimelb\unimelb_test.subset6a.csv
python parse_weka_results.py -c -r 100 -o f:\kaggle\unimelb f:\kaggle\unimelb\jrip6a3.txt f:\kaggle\unimelb\unimelb_training.subset6a.csv

REM creates unimelb_training_subset6a.jrip6a3.knn.csv, unimelb_test_subset6a.jrip6a3.knn.csv

python pca.py -c 0 -o f:\kaggle\unimelb f:\kaggle\unimelb\unimelb_training_subset6a.jrip6a3.knn.csv -t jrip6a
python pca.py -o f:\kaggle\unimelb f:\kaggle\unimelb\unimelb_test_subset6a.jrip6a3.knn.csv -p jrip6a

REM creates unimelb_training_subset6a.jrip6a3.knn.90.csv and unimelb_test_subset6a.jrip6a3.knn.90.csv

python knn.py f:\kaggle\unimelb\unimelb_training_subset6a.jrip6a3.knn.90.csv f:\kaggle\unimelb\unimelb_test_subset6a.jrip6a3.knn.90.csv

