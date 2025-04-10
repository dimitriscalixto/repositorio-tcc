# Configurar o WebDriver com WebDriver Manager
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
from webdriver_manager.chrome import ChromeDriverManager

# Configurar o WebDriver
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)

# URL do site
url = "https://www.cartolafcbrasil.com.br/scouts/cartola-fc-2024/rodada-3"
driver.get(url)

# Aguarde a tabela carregar
wait = WebDriverWait(driver, 10)

# Função para extrair dados da tabela
def extract_table_data():
    table = wait.until(EC.presence_of_element_located((By.XPATH, "//table[not(contains(@class, 'tbpaging'))]")))
    headers = [th.text for th in table.find_elements(By.TAG_NAME, "th")]
    rows = table.find_elements(By.TAG_NAME, "tr")[1:]  # Ignorar o cabeçalho
    data = []

    for row in rows:
        cells = row.find_elements(By.TAG_NAME, "td")
        row_data = []
        for i, cell in enumerate(cells):
            if i == 1:  # Segunda coluna (Clube)
                try:
                    img = cell.find_element(By.TAG_NAME, "img")
                    club_name = img.get_attribute("alt")  # Captura o nome do clube pelo atributo "alt"
                    row_data.append(club_name)
                except Exception as e:
                    print(f"Erro ao buscar a imagem na segunda coluna: {e}")
                    row_data.append("N/A")  # Caso não encontre o nome do clube
            else:
                row_data.append(cell.text)
        data.append(row_data)

    return headers, data

# Extraia os dados de todas as páginas
all_data = []
page = 1

while True:
    print(f"Extraindo dados da página {page}...")
    headers, data = extract_table_data()
    all_data.extend(data)

    try:
        # Localizar o link da próxima página pelo índice
        next_page = driver.find_element(By.XPATH, f"//tr[@class='tbpaging']//a[text()='{page + 1}']")
        driver.execute_script("arguments[0].click();", next_page)  # Simula o clique usando JavaScript
        page += 1
        WebDriverWait(driver, 5).until(EC.staleness_of(next_page))  # Aguarde a próxima página carregar
    except Exception:
        print("Não há mais páginas.")
        break

# Feche o navegador
driver.quit()

# Converter para DataFrame
df = pd.DataFrame(all_data, columns=headers)

# Salvar em arquivo CSV
df.to_csv("scouts_todas_paginas-rodada-3.csv", index=False)
print("Dados salvos em 'scouts_todas_paginas-teste.csv'")
