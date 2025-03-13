import fitz  # PyMuPDF para leer el PDF

# 📌 Paso 1: Leer el PDF y extraer texto
def extraer_texto(pdf_path):
    doc = fitz.open(pdf_path)
    texto = ""
    for pagina in doc:
        texto += pagina.get_text("text")
    return texto

# 📌 Ejecutar el análisis
pdf_path = "Libros/Completo.pdf"
texto = extraer_texto(pdf_path)
with open("Libro.txt", "w", encoding="utf-8") as f:
    f.write(texto)