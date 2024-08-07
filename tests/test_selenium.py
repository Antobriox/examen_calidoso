from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import unittest

class TestSistemaEvaluacion(unittest.TestCase):

    def setUp(self):
        self.driver = webdriver.Chrome()  # Asegúrate de tener ChromeDriver en tu PATH
        self.driver.get("http://localhost:5000")

    def test_registro(self):
        driver = self.driver
        driver.find_element(By.LINK_TEXT, "Registro").click()
        driver.find_element(By.ID, "username").send_keys("testuser")
        driver.find_element(By.ID, "email").send_keys("test@example.com")
        driver.find_element(By.ID, "password").send_keys("password123")
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

        success_message = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".alert-success"))
        )
        self.assertIn("¡Registro exitoso!", success_message.text)

    def test_login(self):
        driver = self.driver
        driver.find_element(By.LINK_TEXT, "Login").click()
        driver.find_element(By.ID, "username").send_keys("testuser")
        driver.find_element(By.ID, "password").send_keys("password123")
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

        self.assertIn("home", driver.current_url)

    def test_agregar_tema(self):
        self.test_login()  # Iniciar sesión primero
        driver = self.driver
        driver.find_element(By.LINK_TEXT, "Agregar Nuevo Artículo").click()
        driver.find_element(By.ID, "titulo").send_keys("Test Tema")
        driver.find_element(By.ID, "descripcion").send_keys("Descripción del tema de prueba")
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

        success_message = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".alert-success"))
        )
        self.assertIn("Descripción del tema de prueba", driver.page_source)

    def test_agregar_respuesta(self):
        self.test_agregar_tema()  # Agregar un tema primero
        driver = self.driver
        driver.find_element(By.LINK_TEXT, "Test Tema").click()
        driver.find_element(By.ID, "contenido").send_keys("Respuesta de prueba")
        driver.find_element(By.ID, "calificacion").send_keys("5")
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

        success_message = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".alert-success"))
        )
        self.assertIn("Respuesta de prueba", driver.page_source)

    def tearDown(self):
        self.driver.quit()

if __name__ == "__main__":
    unittest.main()
