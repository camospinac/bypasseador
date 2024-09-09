from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import requests
from pydub import AudioSegment
import speech_recognition as sr
import time
import os

#Se importa el driver
driver = webdriver.Chrome()
driver.get("aca viene la URL el cúal quieren bypassear")
time.sleep(2)
#Este primer bloque lo que hace es ubicar el IFRAME del captcha y dar el primer
#clic al check.
WebDriverWait(driver, 10).until(EC.frame_to_be_available_and_switch_to_it((By.XPATH, "//iframe[@title='reCAPTCHA']")))
boton_1 = driver.find_element(By.XPATH, '//*[@id="recaptcha-anchor"]')
boton_1.click()
time.sleep(2)
#Acá en este siguiente bloque lo que hace es nuevamente salir del IFRAME para
#localizar la ventana que se abre de validación y da clic al boton de los cascos
driver.switch_to.default_content()
WebDriverWait(driver, 10).until(EC.frame_to_be_available_and_switch_to_it((By.XPATH, "//iframe[contains(@src, 'api2/bframe')]")))
time.sleep(2)
boton_2 = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "recaptcha-audio-button")))
boton_2.click()
time.sleep(2)
#Acá por ultimo, localiza el botón de descarga del audio para posteriormente
#procesarlo
driver.switch_to.default_content()
WebDriverWait(driver, 20).until(EC.frame_to_be_available_and_switch_to_it((By.XPATH, "//iframe[contains(@src, 'api2/bframe')]")))
time.sleep(2)
audio_element = driver.find_element(By.XPATH, '//a[@class="rc-audiochallenge-tdownload-link"]')
audio_url = audio_element.get_attribute("href")
response = requests.get(audio_url)

#En este bloque lo que se realiza es la conversionde formato mp3 a wav
#haciendo uso de la libreria pydub y del plugin de ffmpeg
mp3_filename = "audio.mp3"
with open(mp3_filename, "wb") as file:
    file.write(response.content)
if os.path.exists(mp3_filename):
    directorio_trabajo = os.getcwd()
    mp3_path = os.path.join(directorio_trabajo, mp3_filename)
    sonido = AudioSegment.from_mp3(mp3_path)
    wav_filename = "audio.wav"
    sonido.export(wav_filename, format="wav")
    print(f"Audio convertido a WAV en {wav_filename}")
else:
    print(f"No se pudo encontrar el archivo MP3 en {mp3_filename}")
#En este bloque lo que se realiza es el procesamiento para transcribir el audio
#a texto
recognizer = sr.Recognizer()
try:
    with sr.AudioFile(wav_filename) as source:
        audio_data = recognizer.record(source)
        texto = recognizer.recognize_google(audio_data, language="es-ES")
        print("Texto transcrito:", texto)
except sr.UnknownValueError:
    print("Google Speech Recognition no pudo entender el audio")
except sr.RequestError as e:
    print(f"Error al solicitar resultados desde Google Speech Recognition; {e}")
#Por ultimo se manda la variable texto al input del captcha con sy respectivo clic
#y cerramos la sesión del driver
respuesta = driver.find_element(By.ID, "audio-response")
respuesta.send_keys(texto)
botonfinal = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "recaptcha-verify-button")))
botonfinal.click()
time.sleep(20)
driver.quit()