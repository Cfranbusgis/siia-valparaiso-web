# Makefile de conveniencia (Linux/macOS). En Windows usa: python scripts/run_pipeline.py
.PHONY: help install pipeline site serve clean

help:
	@echo "Objetivos disponibles:"
	@echo "  make install   Instala dependencias Python (requirements.txt)"
	@echo "  make pipeline  Ejecuta el análisis completo y construye el sitio"
	@echo "  make site      Solo reconstruye public/ desde los datos existentes"
	@echo "  make serve     Sirve el sitio en http://localhost:3000"
	@echo "  make clean     Elimina caches de Python"

install:
	pip install -r requirements.txt

pipeline:
	python scripts/run_pipeline.py

site:
	python scripts/assemble_web.py

serve:
	npm start

clean:
	rm -rf scripts/__pycache__ __pycache__
