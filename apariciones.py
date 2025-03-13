# Cargar el archivo CSV en un DataFrame de pandas
import pandas as pd
import re
import csv

# Ruta del archivo CSV (reemplázala con tu ruta real)
csv_path = "Personajes/personajes.csv"

# Cargar el archivo CSV en un DataFrame
df = pd.read_csv(csv_path, sep=",")

nombres = df["Nombre"].unique()
etiquetas = df["Etiqueta"].unique()
razas = df["Raza"].unique()
nombre_a_etiqueta = df.set_index("Nombre")["Etiqueta"].to_dict()

def leer_texto(txt_path):
    with open(txt_path, "r", encoding="utf-8") as file:
        texto = file.read()
    return texto


def contar_apariciones(texto, nombres):
    palabras = re.findall(r"\b[\w'-]+\b", texto)
    apariciones = {nombre: 0 for nombre in nombres}
    for palabra in palabras:
        if palabra in nombres:
            apariciones[palabra] += 1
    return apariciones


def contar_interacciones(texto, personajes, ventana=20):
    palabras = re.findall(r"\b[\w'-]+\b", texto)  # Tokenizar el texto en palabras
    interacciones = {}

    for i, palabra in enumerate(palabras):
        if palabra in personajes:
            # 📌 Definir la ventana de búsqueda
            inicio = max(0, i - ventana)
            fin = min(len(palabras), i + ventana)

            # 📌 Buscar otros personajes en la ventana
            personajes_encontrados = [p for p in palabras[inicio:fin] if p in personajes and p != palabra]

            # 📌 Registrar interacciones
            for p in personajes_encontrados:
                if (palabra, p) in interacciones:
                    interacciones[(palabra, p)] += 1
                elif (p, palabra) in interacciones:
                    interacciones[(p, palabra)] += 1
                else:
                    interacciones[(palabra, p)] = 1

    # Las interacciones se cuentan dos veces, por lo que se divide el peso entre 2
    for (p1, p2), peso in interacciones.items(): 
        interacciones[(p1, p2)] = int(peso // 2)  # Dividir el peso entre 2 para evitar duplicados

    return interacciones


# Función para guardar las interacciones en un CSV compatible con Gephi
def guardar_interacciones(interacciones, output_file):
    with open(output_file, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["Source", "Target", "Weight", "Type"])  # Encabezado para Gephi

        sorted_interacciones = sorted(interacciones.items(), key=lambda x: (x[0][0], x[0][1]))  # Orden alfabético

        for (p1, p2), peso in sorted_interacciones:
            if peso == 0:
                peso = 1  # Peso mínimo para evitar errores en Gephi
            writer.writerow([p1, p2, int(peso), "Undirected"])



txt_path = "Libro.txt"
texto = leer_texto(txt_path)
apariciones = contar_apariciones(texto, nombres)

# Interacciones en la comunidad del anillo
interacciones = contar_interacciones(texto, nombres)

# Crear un nuevo diccionario de interacciones agrupadas por etiquetas
interacciones_agrupadas = {}

for (p1, p2), peso in interacciones.items():
    etiqueta1 = nombre_a_etiqueta.get(p1, p1)  # Obtener la etiqueta o dejar el nombre si no tiene
    etiqueta2 = nombre_a_etiqueta.get(p2, p2)

    # Evitar duplicar interacciones al agrupar por etiquetas
    if etiqueta1 != etiqueta2:
        if (etiqueta1, etiqueta2) in interacciones_agrupadas:
            interacciones_agrupadas[(etiqueta1, etiqueta2)] += peso
        elif (etiqueta2, etiqueta1) in interacciones_agrupadas:
            interacciones_agrupadas[(etiqueta2, etiqueta1)] += peso
        else:
            interacciones_agrupadas[(etiqueta1, etiqueta2)] = peso


# Crear un diccionario para almacenar la suma de interacciones por etiqueta
suma_interacciones_por_etiqueta = {}

for (et1, et2), peso in interacciones_agrupadas.items():
    suma_interacciones_por_etiqueta[et1] = suma_interacciones_por_etiqueta.get(et1, 0) + peso
    suma_interacciones_por_etiqueta[et2] = suma_interacciones_por_etiqueta.get(et2, 0) + peso

# Filtrar solo los personajes que aparecen en la comunidad del anillo
df["Apariciones"] = df["Nombre"].map(apariciones).fillna(0)  # Agregar la columna de apariciones

# Combinar nombres con la misma etiqueta sumando las apariciones
df_combinado = df.groupby("Etiqueta", as_index=False).agg({
    "Nombre": "first",
    "Raza": "first",
    "Subraza": "first",
    "Género": "first",
    "Apariciones": "sum", # Sumar las apariciones de los nombres con la misma etiqueta
})

df_combinado = df_combinado[df_combinado["Apariciones"] > 0]  # Filtrar personajes con apariciones
df_combinado = df_combinado.sort_values("Apariciones", ascending=False)  # Ordenar por apariciones
df_combinado = df_combinado.drop(columns=["Nombre"]) # Eliminar columna etiqueta
df_combinado["Interacciones"] = df_combinado["Etiqueta"].map(suma_interacciones_por_etiqueta).fillna(0)
df_combinado = df_combinado.rename(columns={"Etiqueta": "Label"})
df_combinado["Id"] = df_combinado["Label"]
df_combinado["Interacciones"] = df_combinado["Interacciones"].astype(int)

# Guardar el nuevo archivo CSV con los personajes de la comunidad del anillo
csv_output_path = "Personajes/personajes_final_20.csv"
df_combinado.to_csv(csv_output_path, index=False)

# Guardar las interacciones en un archivo CSV compatible con Gephi
output_file = "Interacciones/interacciones_final_20.csv"
guardar_interacciones(interacciones_agrupadas, output_file)