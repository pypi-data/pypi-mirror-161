import pandas as pd

#Obtenemos un dataframe
def get_dataframe():
	return pd.read_csv("data/vacunometro_cantones.csv" , sep=",").sort_index()