from flask import Flask, request, jsonify
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
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

def scrape():
    start_time = time.time()
    number_to_input = 1152217759

    if not number_to_input:
        print({'error': 'Se necesita un número para hacer web scraping.'})
        return

    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    try:
        driver.get(url)
        #WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, id_input_nit)))

        input_box = driver.find_element(By.ID, id_input_nit)
        input_box.clear()
        input_box.send_keys(str(number_to_input))

        submit_button = driver.find_element(By.ID, id_boton_buscar)
        submit_button.click()

        #WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, id_razon_social)))

        razon_social = driver.find_element(By.ID, id_razon_social).text if driver.find_elements(By.ID, id_razon_social) else None

        if razon_social:
            print({'tipo': 'empresa', 'razon_social': razon_social})
        else:
            primer_apellido = driver.find_element(By.ID, id_primer_apellido).text if driver.find_elements(By.ID, id_primer_apellido) else ''
            segundo_apellido = driver.find_element(By.ID, id_segundo_apellido).text if driver.find_elements(By.ID, id_segundo_apellido) else ''
            primer_nombre = driver.find_element(By.ID, id_primer_nombre).text if driver.find_elements(By.ID, id_primer_nombre) else ''
            segundo_nombre = driver.find_element(By.ID, id_segundo_nombre).text if driver.find_elements(By.ID, id_segundo_nombre) else ''

            if not primer_nombre and not primer_apellido:
                print({'error': 'NIT no encontrado'})
            else:
                print({
                    'tipo': 'persona',
                    'primer_nombre': primer_nombre,
                    'segundo_nombre': segundo_nombre,
                    'primer_apellido': primer_apellido,
                    'segundo_apellido': segundo_apellido
                })

    except Exception as e:
        print({'error': str(e)})

    finally:
        driver.quit()

    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"Tiempo de ejecución: {elapsed_time:.2f} segundos")



scrape()