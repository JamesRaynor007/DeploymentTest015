import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import os

# Definir la ruta del archivo CSV
resultado_crew_path = os.path.join(os.path.dirname(__file__), 'resultado_crew.csv')
funcion_director_path = os.path.join(os.path.dirname(__file__), 'FuncionDirector.csv')

app = FastAPI()

# Cargar los datasets
try:
    resultado_crew = pd.read_csv(resultado_crew_path)
    funcion_director = pd.read_csv(funcion_director_path)
except FileNotFoundError as e:
    raise HTTPException(status_code=500, detail=f"Error al cargar los archivos: {str(e)}")
app = FastAPI()

class MovieInfo(BaseModel):
    title: str
    release_date: str
    return_: str  # Cambiado a str para formatear la salida
    budget: str   # Cambiado a str para formatear la salida
    revenue: str  # Cambiado a str para formatear la salida

class DirectorResponse(BaseModel):
    director_name: str
    total_revenue: str  # Cambiado a str para formatear la salida
    movies: List[MovieInfo]

@app.get("/director/{director_name}", response_model=DirectorResponse)
def get_director_info(director_name: str):
    # Normalizar el nombre del director a minúsculas
    director_name_lower = director_name.lower()
    
    # Filtrar las películas del director sin discriminar mayúsculas
    director_movies = resultado_crew[resultado_crew['name'].str.lower() == director_name_lower]
    
    if director_movies.empty:
        raise HTTPException(status_code=404, detail="Director no encontrado")

    # Unir con el DataFrame de función del director para obtener más detalles
    director_movies = director_movies.merge(funcion_director, left_on='movie_id', right_on='id', how='inner')

    # Calcular ganancias totales
    total_revenue = director_movies['revenue'].sum()

    # Crear la lista de películas
    movies_info = [
        MovieInfo(
            title=row['title'],
            release_date=row['release_date'],
            return_=f"{row['return'] :.2f}%",  # Formato de porcentaje
            budget=f"${row['budget']:,.2f}",   # Formato de moneda con separador de miles
            revenue=f"${row['revenue']:,.2f}"  # Formato de moneda con separador de miles
        ) for index, row in director_movies.iterrows()
    ]

    return DirectorResponse(
        director_name=director_name,
        total_revenue=f"${total_revenue:,.2f}",  # Formato de moneda con separador de miles
        movies=movies_info
    )

@app.get("/directores")
def obtener_directores():
    return resultado_crew['name'].unique().tolist()
