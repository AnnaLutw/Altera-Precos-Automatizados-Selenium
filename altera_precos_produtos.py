from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.options import Options
from dotenv import load_dotenv

import os
import time

load_dotenv()

user = os.getenv("USER")
password = os.getenv("PASSWORD")
url_login = os.getenv("URL_LOGIN")
url_produtos = os.getenv("URL_PRODUTOS")

extensao_path = r"C:\Users\fid2\AppData\Local\Google\Chrome\User Data\Default\Extensions\bhghoamapcdpbohphigoooaddinpkbai\8.0.1_0"
perfil_path   = r"C:\Users\fid2\AppData\Local\Google\Chrome\User Data" 
options = Options()
options.add_argument(f'--load-extension={extensao_path}')
options.add_argument(f'--user-data-dir={perfil_path}')  # Diretório de dados do usuário
options.add_argument(f'--profile-directory=Default')  # Use o perfil "Default"


service = Service('./chromedriver.exe')
driver = webdriver.Chrome(service=service, options=options)

driver.maximize_window()

def _esperar_elemento(by, value, timeout=10):
    return WebDriverWait(driver, timeout).until(EC.presence_of_element_located((by, value)))


def _clicar(by, value, timeout=10):
    try:
        elemento = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable((by, value)))
        elemento.click()
    except Exception as e:
        print(f"Erro ao clicar no elemento {value}: {e}")


def _enviar_dados_elemento(by, value, texto, limpa=False, timeout=10):
    try:
        elemento = _esperar_elemento(by, value, timeout)
        if limpa:
            elemento.clear()
        elemento.send_keys(texto)
    except Exception as e:
        print(f"Erro ao enviar dados para o elemento {value}: {e}")


def scroll_ate_elemento(by, value):
    try:
        # Espera até o elemento estar visível
        elemento = _esperar_elemento(by, value)
        
        # Realiza o scroll até o elemento usando JavaScript
        driver.execute_script("arguments[0].scrollIntoView(true);", elemento)
        time.sleep(1)  # Aguarda o scroll ser completado
    except Exception as e:
        print(f"Erro ao fazer scroll até o elemento {value}: {e}")


def realizar_login(code):
    driver.get(url_login)

    # _enviar_dados_elemento(By.XPATH, '//input[contains(@name, "email")]', user)
    # _enviar_dados_elemento(By.XPATH, '//input[contains(@name, "senha")]', password)
    # _clicar(By.CLASS_NAME, 'form2018-radio')

    # _clicar(By.CLASS_NAME, 'form2018-botao')
    # time.sleep(1)

    _enviar_dados_elemento(By.XPATH, '//input[contains(@name, "codigo")]', code)
    time.sleep(1)
    _clicar(By.XPATH, '//button[contains(@class, "form2018-botao") and contains(text(), "Validar")]')


def pega_codigo_autenticacao_e_faz_login():
    # Acessa a página da extensão
    driver.get('chrome-extension://bhghoamapcdpbohphigoooaddinpkbai/view/popup.html')
    time.sleep(2)

    try:
        # Executa um script JavaScript para obter o código diretamente do DOM
        script = """
            var codigoElement = document.getElementsByClassName("code");
            if (codigoElement.length > 0) {
                return codigoElement[0].innerText;
            } else {
                return null;
            }
        """
        # Executa o script e obtém o código de autenticação
        code = driver.execute_script(script)
        
        if code:
            print("Código de autenticação: ", code)

            realizar_login(code)

            
        else:
            print("Não foi possível encontrar o código de autenticação.")
    
    except Exception as e:
        print(f"Erro ao pegar o código de autenticação: {e}")
    

def filtra():
    _clicar(By.XPATH, "//a[contains(., 'Filtros Avançados') and @href='javascript:void(0)']")
    select_element = _esperar_elemento(By.XPATH, '//select[contains(@name, "advFtr[0][tipoFiltro]")]')
    Select(select_element).select_by_value('esteja')

    select_element = _esperar_elemento(By.XPATH, '//select[contains(@name, "advFtr[0][esteja]")]')
    Select(select_element).select_by_value('status')

    select_element = _esperar_elemento(By.XPATH, '//select[contains(@name, "advFtr[0][valor]")]')
    Select(select_element).select_by_value('s')

    _clicar(By.CLASS_NAME, 'boxFiltrosAvancados-aplicarFiltros')

    time.sleep(1)

    select_element = _esperar_elemento(By.CLASS_NAME, 'selecionaIPP')
    Select(select_element).select_by_value('40')
    time.sleep(1)


def acessa_tela_produtos():
    time.sleep(2)
    driver.get(url_produtos)

    filtra()

    _esperar_elemento(By.XPATH, '//table')

    while True:
        produtos = driver.find_elements(By.XPATH, '//table//tr')
        if not produtos:
            break

        for index, produto in enumerate(produtos, start=1):
            try:
                entra_em_produto(produto, index)
            except Exception as e:
                print(f"Erro ao processar o produto {index}, passando para o próximo: {e}")
                continue  


        _esperar_elemento(By.XPATH, '//table')

        # Verifica se a próxima página está desabilitada
        proxima_pagina_btn = _esperar_elemento(By.CLASS_NAME, 'proxima')

        if 'disabled' in proxima_pagina_btn.get_attribute('class'):
            print("Fim das páginas!")
            break

        # Clica na próxima página
        try:
            _clicar(By.CLASS_NAME, 'proxima')
            time.sleep(1)
        except Exception as e:
            print(f"Erro ao clicar na próxima página: {e}")
            break  # Se falhar ao clicar na próxima página, sai do loop.


def entra_em_produto(produto, index):
    try:
        # Utiliza o index para acessar o produto correto dentro da tabela
        _clicar(By.XPATH, f'//table//tr[{index}]//td[11]//a[contains(@title, "Editar produto")]')
        time.sleep(1)
        
        pega_preco_correto_e_edita()

        # Clica no botão "Voltar para lista"
        _clicar(By.XPATH, '//button/i[@class="icon-arrow-left"]')
        time.sleep(1)

    except Exception as e:
        print(f"Erro ao entrar no produto {index}: {e}")


def altera_valor_input(script, xpath):
    preco_por_element = _esperar_elemento(By.XPATH, xpath)
    driver.execute_script(script, preco_por_element)


def pega_preco_correto_e_edita():
    try:
        # Clicar na aba "Associados"
        xpath_associados = '//a[contains(text(), "Associados")]'
        _clicar(By.XPATH, xpath_associados)
        time.sleep(1)

        # Scroll até a tabela de atributos
        atributos = 'tabelaAtributosSimples'
        scroll_ate_elemento(By.CLASS_NAME, atributos)

        valor_elemento  = _esperar_elemento(By.CLASS_NAME, 'alterarPrecoPreviewRegrasAtributo')
        valor_bruto     = valor_elemento.get_attribute('value').strip()
        valor_formatado = formatar_valor(valor_bruto)

        # Buscar todos os campos 'precoDe' na aba "Associados"
        precos_de_associados = driver.find_elements(By.XPATH, '//input[contains(@name, "produtoAtributo") and contains(@name, "[precoDe]")]')

        # Atualizar todos os campos 'precoDe' com o valor formatado
        for index, preco_de_associado in enumerate(precos_de_associados, start=1):
            script_set_value = f"arguments[0].setAttribute('value', '{valor_formatado}');"
            driver.execute_script(script_set_value, preco_de_associado)
            print(f"Preço do campo {index} atualizado para: {valor_formatado}")

        # Salvar alterações
        _clicar(By.CLASS_NAME, 'botaoSave')
        print('Alterações salvas na aba "Associados".')

        # Clicar na aba "Preços"
        _clicar(By.XPATH, '//a[contains(text(), "Preços")]')
        time.sleep(1)

        # Atualizar os campos 'precoDe' e 'precoPor' na aba "Preços"
        script_set_value = f"arguments[0].setAttribute('value', '{valor_formatado}');"

        altera_valor_input(script_set_value,  '//input[contains(@name, "precoDe")]')
        altera_valor_input(script_set_value,  '//input[contains(@name, "precoPor")]')

        # Salvar alterações
        _clicar(By.CLASS_NAME, 'botaoSave')
        print('Alterações salvas na aba "Preços".')

    except Exception as e:
        print(f"Erro ao pegar e editar preço: {e}")



def formatar_valor(valor_bruto):
    if ',' in valor_bruto:
        valor_sem_ponto = valor_bruto.replace(',', '')
        valor_formatado = f"{int(valor_sem_ponto[:-2])}.{valor_sem_ponto[-2:]}"
    elif '.' in valor_bruto:
        valor_formatado = valor_bruto
    else:
        raise ValueError(f"Formato de valor desconhecido: {valor_bruto}")
    
    return valor_formatado


pega_codigo_autenticacao_e_faz_login()
acessa_tela_produtos()


time.sleep(5)

