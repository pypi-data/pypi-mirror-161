from src.conexion import get_dataframe
import matplotlib.pyplot as plt
import numpy as np

df = get_dataframe()

#Informacion de vacunados por region
def vacunados_region(region):
	datos = df[df['region']==region][["primera_dosis","segunda_dosis","dosis_unica","dosis_refuerzo","dosis_total","created_at"]]
	return datos.groupby('created_at').agg(np.sum)

#Informacion de vacunados por provincia
def vacunados_provincia(provincia):
	datos = df[df['provincia']==provincia][["primera_dosis","segunda_dosis","dosis_unica","dosis_refuerzo","dosis_total","created_at"]]
	return datos.groupby('created_at').agg(np.sum)

#Informacion de vacunados por canton
def vacunados_canton(canton):
	datos = df[df['canton']==canton][["primera_dosis","segunda_dosis","dosis_unica","dosis_refuerzo","dosis_total","created_at"]]
	return datos.groupby('created_at').agg(np.sum)


