from src.conexion import get_dataframe
import matplotlib.pyplot as plt
import numpy as np

df = get_dataframe()

#Grafica de vacunados por region
def graficar_vacunados_region(data,titulo):
	data.tail().plot(kind='bar',ylabel='Cantidad de vacunados',xlabel='Fecha de registro',title='Vacunacion en la Region ' +titulo)
	plt.xticks(rotation=360)	
	plt.savefig("./img/Vacunados_Region.png")
	plt.show()

#Grafica de vacunados por provincia
def graficar_vacunados_provincia(data,titulo):
	data.plot(kind='line',ylabel='Cantidad de vacunados',xlabel='Fecha de registro',title='Vacunacion en la Provincia de ' +titulo)
	plt.xticks(rotation=360)	
	plt.savefig("./img/Vacunados_Provincia.png")
	plt.show()

#Grafica de vacunados por canton
def graficar_vacunados_canton(data,titulo):
	data.plot(kind='line',ylabel='Cantidad de vacunados',xlabel='Fecha de registro',title='Vacunacion en el Canton ' +titulo)
	plt.xticks(rotation=360)	
	plt.savefig("./img/Vacunados_Canton.png")
	plt.show()





	