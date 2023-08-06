from src.conexion import get_dataframe

df = get_dataframe()

#Listado de regiones
def get_regiones():
	return df['region'].sort_values().unique()

#Listado de provincias
def get_provincias():
	return df['provincia'].sort_values().unique()

#Listado de cantones
def get_cantones():
	return df['canton'].sort_values().unique()


