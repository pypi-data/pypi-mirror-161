#importacion de librerias
import os
from src.listados import get_regiones
from src.listados import get_provincias
from src.listados import get_cantones
from src.vacunados import vacunados_region
from src.vacunados import vacunados_provincia
from src.vacunados import vacunados_canton
from src.grafica import graficar_vacunados_region
from src.grafica import graficar_vacunados_provincia
from src.grafica import graficar_vacunados_canton


if __name__ == "__main__":

	os.system('clear')
	print("=========================================")
	print("Datos de vacunacion del Ecuador")
	print("=========================================")
	print("1. Numero de vacunados por region")
	print("2. Numero de vacunados por provincia")
	print("3. Numero de vacunados por canton")
	print("4. Salir ................")
	print("=========================================")
	print("")

	opcion = int(input("Escoja una opcion [1-4]: "))
	os.system("clear")

	if opcion == 1:
		print("=================================")
		print("Listado de regiones: ")
		print("=================================")

		regiones = get_regiones()

		aux = 1
		for region in regiones:
			print(str(aux)+". "+region)
			aux = aux + 1

		print("==================================")
		print("")	

		r = int(input("Escoja una region [1-"+str(aux-1)+"]: "))
			
		lista_vacunados = vacunados_region(regiones[r-1])

		os.system('clear')
		print("=========================================")
		print("Datos region "+regiones[r-1])
		print("=========================================")

		print(lista_vacunados)

		graficar_vacunados_region(lista_vacunados,regiones[r-1])


	if opcion == 2:
		print("=================================")
		print("Listado de provincias: ")
		print("=================================")

		provincias = get_provincias()

		aux = 1
		for provincia in provincias:
			print(str(aux)+". "+provincia)
			aux = aux + 1

		print("==================================")
		print("")	

		r = int(input("Escoja una provincia [1-"+str(aux-1)+"]: "))
			
		lista_vacunados = vacunados_provincia(provincias[r-1])

		os.system('clear')
		print("=========================================")
		print("Datos provincia "+provincias[r-1])
		print("=========================================")

		print(lista_vacunados)

		graficar_vacunados_provincia(lista_vacunados,provincias[r-1])


	if opcion == 3:
		print("=================================")
		print("Listado de cantones: ")
		print("=================================")

		cantones = get_cantones()

		aux = 1
		for canton in cantones:
			print(str(aux)+". "+canton)
			aux = aux + 1

		print("==================================")
		print("")	

		r = int(input("Escoja una canton [1-"+str(aux-1)+"]: "))
			
		lista_vacunados = vacunados_canton(cantones[r-1])

		os.system('clear')
		print("=========================================")
		print("Datos canton "+cantones[r-1])
		print("=========================================")

		print(lista_vacunados)

		graficar_vacunados_canton(lista_vacunados,cantones[r-1])

	if opcion == 4:
		exit()









	

