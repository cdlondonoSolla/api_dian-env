from flask import Flask, request, jsonify
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

# URL y selectores de los campos
url = "https://muisca.dian.gov.co/WebRutMuisca/DefConsultaEstadoRUT.faces"
id_input_nit = "vistaConsultaEstadoRUT:formConsultaEstadoRUT:numNit"
id_boton_buscar = "vistaConsultaEstadoRUT:formConsultaEstadoRUT:btnBuscar"
id_razon_social = "vistaConsultaEstadoRUT:formConsultaEstadoRUT:razonSocial"
id_primer_apellido = "vistaConsultaEstadoRUT:formConsultaEstadoRUT:primerApellido"
id_segundo_apellido = "vistaConsultaEstadoRUT:formConsultaEstadoRUT:segundoApellido"
id_primer_nombre = "vistaConsultaEstadoRUT:formConsultaEstadoRUT:primerNombre"
id_segundo_nombre = "vistaConsultaEstadoRUT:formConsultaEstadoRUT:otrosNombres"

app = Flask(__name__)

@app.route('/scrape', methods=['POST'])
def scrape():
    # Obtener el número del parámetro recibido en la API
    data = request.get_json()
    number_to_input = data.get('number')

    if not number_to_input:
        return jsonify({'error': 'Se necesita un número para hacer web scraping.'}), 400

    # Configurar Selenium (usamos Chrome en este ejemplo)
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # Ejecuta el navegador en modo headless (sin interfaz gráfica)
    options.add_argument('--disable-gpu')
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    try:
        # Abrir la página web
        driver.get(url)

        # Esperar a que la página cargue completamente (puedes ajustar el tiempo según sea necesario)
        #time.sleep(1)

        # Localizar la caja de texto y enviar el número
        input_box = driver.find_element(By.ID, id_input_nit)
        input_box.clear()
        input_box.send_keys(str(number_to_input))

        # Localizar y hacer click en el botón de búsqueda
        submit_button = driver.find_element(By.ID, id_boton_buscar)
        submit_button.click()

        # Esperar un momento para que los resultados carguen (puedes ajustar el tiempo según sea necesario)
        #time.sleep(1)

        # Verificar si es una empresa (razón social está presente)
        razon_social = driver.find_element(By.ID, id_razon_social).text if driver.find_elements(By.ID, id_razon_social) else None

        if razon_social:
            return jsonify({'tipo': 'empresa', 'razon_social': razon_social})

        if not razon_social:
            # Verificar si es una persona (apellidos y nombres)
            primer_apellido = driver.find_element(By.ID, id_primer_apellido).text if driver.find_elements(By.ID, id_primer_apellido) else ''
            segundo_apellido = driver.find_element(By.ID, id_segundo_apellido).text if driver.find_elements(By.ID, id_segundo_apellido) else ''
            primer_nombre = driver.find_element(By.ID, id_primer_nombre).text if driver.find_elements(By.ID, id_primer_nombre) else ''
            segundo_nombre = driver.find_element(By.ID, id_segundo_nombre).text if driver.find_elements(By.ID, id_segundo_nombre) else ''

            # Si no se encuentra información de nombres o apellidos, devolver error
            if not primer_nombre and not primer_apellido:
                return jsonify({'error': 'NIT no encontrado'}), 404
            else:
            # Devolver la información de la persona
                return jsonify({
                    'tipo': 'persona',
                    'primer_nombre': primer_nombre,
                    'segundo_nombre': segundo_nombre,
                    'primer_apellido': primer_apellido,
                    'segundo_apellido': segundo_apellido
                })
    

    except Exception as e:
        return jsonify({'error': str(e)}), 500

    finally:
        # Cerrar el navegador
        driver.quit()

if __name__ == '__main__':
    app.run(debug=True)
