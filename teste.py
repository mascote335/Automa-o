import time
from datetime import datetime, timedelta

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException,
    StaleElementReferenceException,
)


# ============================================================
# CONFIGURAÇÕES
# ============================================================

URL_EGS = "https://app.egssistemas.com.br/monitor-dfe"

PASTA_PERFIL = (
    r"C:\Users\win10\Desktop\automacao\perfil_chrome"
)

NOME_EMITENTE = (
    "VOG TRANSPORTES RODOVIARIOS DE CARGAS LTDA"
)

TEMPO_ESPERA = 25


# ============================================================
# SELETORES DOS BOTÕES
# ============================================================

SEL_PROCESSAR_XML = (
    "button[data-original-title='Processa XML NF-e']"
)

SEL_OK_PROCESSAMENTO = (
    "body > div.modal.zindex.ng-scope.ng-isolate-scope.in "
    "> div > div > div.modal-footer.ng-scope > div > button"
)

SEL_REGISTRO_DOCUMENTO = (
    "body > div:nth-child(8) > div > div > div > ui-view "
    "> div > div > div.mb10 > ul.nav.pull-left."
    "box-btn-pattern.btn-box-overflow > li:nth-child(7) "
    "> egs-button-common > button"
)

SEL_INTEGRACAO_FINANCEIRA = (
    "#egs-tabpanel > ng-transclude > tab:nth-child(1) "
    "> div > div > div > button"
)

SEL_GERAR_PARCELAS = (
    "body > div.modal.fade.ng-scope.ng-isolate-scope.in "
    "> div > div > div.modal-body.ng-scope "
    "> ul > li:nth-child(1) > button"
)

SEL_SAIR_FINANCEIRO = (
    "body > div.modal.fade.ng-scope.ng-isolate-scope.in "
    "> div > div > div.modal-footer.ng-scope "
    "> div:nth-child(1) > egs-button-close-popup > button"
)

SEL_SALVAR_DOCUMENTO = (
    "body > div.modal.ng-scope.ng-isolate-scope.in "
    "> div > div > div.modal-footer.ng-scope "
    "> div > div:nth-child(2) > egs-button-save-popup > button"
)


# ============================================================
# FUNÇÕES AUXILIARES
# ============================================================

def esperar(driver, segundos=TEMPO_ESPERA):
    return WebDriverWait(driver, segundos)


def clicar(driver, elemento):
    """Rola até o elemento e realiza o clique."""

    driver.execute_script(
        "arguments[0].scrollIntoView({block: 'center'});",
        elemento
    )

    time.sleep(0.4)

    try:
        elemento.click()
    except Exception:
        driver.execute_script(
            "arguments[0].click();",
            elemento
        )


def clicar_seletor(
    driver,
    seletor,
    descricao,
    timeout=TEMPO_ESPERA
):
    """Espera o botão ficar clicável e clica."""

    print(f"Clicando: {descricao}")

    elemento = WebDriverWait(
        driver,
        timeout
    ).until(
        EC.element_to_be_clickable(
            (By.CSS_SELECTOR, seletor)
        )
    )

    clicar(driver, elemento)
    time.sleep(1)

    return elemento


def preencher_campo(driver, elemento, valor):
    clicar(driver, elemento)

    elemento.send_keys(Keys.CONTROL, "a")
    elemento.send_keys(str(valor))
    elemento.send_keys(Keys.ENTER)

    time.sleep(2)


def aguardar_carregamento(driver, segundos=20):
    WebDriverWait(driver, segundos).until(
        lambda d: d.execute_script(
            "return document.readyState"
        ) == "complete"
    )


# ============================================================
# FILTRO: NOME DO EMITENTE
# ============================================================

def filtrar_emitente(driver):
    print("\nFiltrando o nome do emitente...")

    esperar(driver).until(
        EC.presence_of_all_elements_located(
            (
                By.CSS_SELECTOR,
                "input[aria-label='Filtro de célula']"
            )
        )
    )

    filtros = driver.find_elements(
        By.CSS_SELECTOR,
        "input[aria-label='Filtro de célula']"
    )

    print(f"Filtros encontrados: {len(filtros)}")

    indice_emitente = 5

    if len(filtros) <= indice_emitente:
        raise Exception(
            "Não encontrei o campo de filtro do emitente."
        )

    preencher_campo(
        driver,
        filtros[indice_emitente],
        NOME_EMITENTE
    )

    print(f"Emitente pesquisado: {NOME_EMITENTE}")


# ============================================================
# FILTRO: REGISTRADA = FALSO
# ============================================================

def filtrar_registrada_falso(driver):
    print("\nAbrindo o filtro Registrada...")

    cabecalho = esperar(driver).until(
        EC.presence_of_element_located(
            (
                By.CSS_SELECTOR,
                "td[aria-label='Coluna Registrada']"
            )
        )
    )

    botao_filtro = cabecalho.find_element(
        By.CSS_SELECTOR,
        ".dx-header-filter"
    )

    clicar(driver, botao_filtro)
    time.sleep(1)

    opcao_falso = esperar(driver, 15).until(
        EC.element_to_be_clickable(
            (
                By.XPATH,
                "//*[normalize-space(text())='falso']"
            )
        )
    )

    clicar(driver, opcao_falso)
    time.sleep(1)

    botoes_ok = driver.find_elements(
        By.XPATH,
        "//*[normalize-space(text())='OK']"
    )

    for botao in botoes_ok:
        if botao.is_displayed():
            clicar(driver, botao)
            break

    time.sleep(3)

    print("Filtro Registrada = falso aplicado.")


# ============================================================
# FILTRO: DATA DE EMISSÃO
# ============================================================

def filtrar_data(driver, data_escolhida=None):
    print("\nFiltrando a data de emissão...")

    if data_escolhida is None:
        data_escolhida = (
            datetime.now() - timedelta(days=1)
        ).strftime("%d/%m/%Y")

    print(f"Data escolhida: {data_escolhida}")

    filtros = driver.find_elements(
        By.CSS_SELECTOR,
        "input[aria-label='Filtro de célula']"
    )

    indice_data = 3

    if len(filtros) <= indice_data:
        raise Exception(
            "Não encontrei o campo de filtro da data."
        )

    preencher_campo(
        driver,
        filtros[indice_data],
        data_escolhida
    )

    print("Filtro de data aplicado.")


# ============================================================
# LER OS CT-es VISÍVEIS NA TABELA
# ============================================================

def obter_documentos_visiveis(driver):
    """
    Lê os CT-es autorizados que aparecem na tabela filtrada.
    Ignora as linhas do painel fixo dos checkboxes.
    """

    documentos = []

    linhas = driver.find_elements(
        By.CSS_SELECTOR,
        ".dx-datagrid-rowsview tr.dx-data-row"
    )

    for linha in linhas:
        try:
            # Ignora o painel fixo de seleção.
            if linha.find_elements(
                By.CSS_SELECTOR,
                "td[colspan='30']"
            ):
                continue

            celulas = linha.find_elements(
                By.TAG_NAME,
                "td"
            )

            if len(celulas) < 7:
                continue

            status = celulas[1].text.strip()
            numero = celulas[2].text.strip()
            emitente = celulas[6].text.strip()

            if not numero:
                continue

            if "CT-e Autorizada" not in status:
                continue

            if NOME_EMITENTE not in emitente:
                continue

            indice = linha.get_attribute(
                "aria-rowindex"
            )

            if not indice:
                continue

            documentos.append({
                "numero": numero,
                "indice": indice,
                "status": status,
                "emitente": emitente,
            })

        except StaleElementReferenceException:
            # A tabela atualizou durante a leitura.
            continue

    # Remove eventuais duplicações.
    unicos = {}

    for documento in documentos:
        unicos[documento["numero"]] = documento

    return list(unicos.values())


# ============================================================
# SELECIONAR UM CT-e
# ============================================================

def selecionar_documento(driver, documento):
    numero = documento["numero"]
    indice = documento["indice"]

    print(f"\nSelecionando CT-e {numero}...")

    linhas = driver.find_elements(
        By.CSS_SELECTOR,
        (
            ".dx-datagrid-rowsview "
            f"tr[aria-rowindex='{indice}']"
        )
    )

    checkbox = None

    for linha in linhas:
        encontrados = linha.find_elements(
            By.CSS_SELECTOR,
            ".dx-select-checkbox"
        )

        if encontrados:
            checkbox = encontrados[0]
            break

    if checkbox is None:
        raise Exception(
            f"Checkbox não encontrado para o CT-e {numero}."
        )

    estado = checkbox.get_attribute("aria-checked")

    if estado != "true":
        clicar(driver, checkbox)

    time.sleep(1)

    print(f"CT-e {numero} selecionado.")


# ============================================================
# PROCESSAR XML E CLICAR EM OK
# ============================================================

def processar_xml(driver, numero):
    print(f"\nProcessando XML do CT-e {numero}...")

    clicar_seletor(
        driver,
        SEL_PROCESSAR_XML,
        "Processa XML NF-e"
    )

    print("Aguardando a confirmação do processamento...")

    clicar_seletor(
        driver,
        SEL_OK_PROCESSAMENTO,
        "OK do processamento",
        timeout=30
    )

    time.sleep(2)

    print(f"Processamento do CT-e {numero} confirmado.")


# ============================================================
# REENCONTRAR E SELECIONAR O CT-e APÓS PROCESSAR
# ============================================================

def selecionar_novamente(driver, numero):
    print(
        f"\nLocalizando novamente o CT-e {numero}..."
    )

    documentos = obter_documentos_visiveis(driver)

    documento = next(
        (
            item for item in documentos
            if item["numero"] == numero
        ),
        None
    )

    if documento is None:
        raise Exception(
            f"O CT-e {numero} não foi encontrado novamente "
            "após o processamento. O script foi interrompido "
            "para evitar abrir ou salvar outro documento."
        )

    selecionar_documento(driver, documento)


# ============================================================
# ABRIR REGISTRO DO DOCUMENTO
# ============================================================

def abrir_registro_documento(driver):
    clicar_seletor(
        driver,
        SEL_REGISTRO_DOCUMENTO,
        "Registro do Documento"
    )

    time.sleep(2)


# ============================================================
# INTEGRAÇÃO FINANCEIRA
# ============================================================

def gerar_parcelas(driver):
    clicar_seletor(
        driver,
        SEL_INTEGRACAO_FINANCEIRA,
        "Integração Financeira"
    )

    time.sleep(2)

    clicar_seletor(
        driver,
        SEL_GERAR_PARCELAS,
        "Gerar Parcelas"
    )

    print("Aguardando a geração das parcelas...")
    time.sleep(3)

    clicar_seletor(
        driver,
        SEL_SAIR_FINANCEIRO,
        "Sair da Integração Financeira"
    )

    time.sleep(2)


# ============================================================
# SALVAR DOCUMENTO
# ============================================================

def salvar_documento(driver):
    clicar_seletor(
        driver,
        SEL_SALVAR_DOCUMENTO,
        "Salvar documento"
    )

    time.sleep(3)

    print("Botão Salvar acionado.")


# ============================================================
# PROCESSAR UM CT-e COMPLETO
# ============================================================

def processar_documento_completo(driver, documento):
    numero = documento["numero"]

    print("\n" + "=" * 60)
    print(f"INICIANDO CT-e {numero}")
    print("=" * 60)

    # 1. Selecionar documento
    selecionar_documento(driver, documento)

    # 2. Processar XML e confirmar OK
    processar_xml(driver, numero)

    # 3. Selecionar novamente o mesmo CT-e
    selecionar_novamente(driver, numero)

    # 4. Abrir Registro do Documento
    abrir_registro_documento(driver)

    # 5. Entrar no financeiro e gerar parcelas
    gerar_parcelas(driver)

    # 6. Salvar o documento
    salvar_documento(driver)

    print("\n" + "=" * 60)
    print(f"CT-e {numero} CONCLUÍDO")
    print("=" * 60)


# ============================================================
# LOOP: PROCESSAR TODOS OS CT-es PENDENTES
# ============================================================

def processar_todos(driver):
    processados = set()
    quantidade_concluida = 0

    print("\nIniciando o loop de processamento...")
    print("O loop terminará quando não houver CT-es")
    print("pendentes visíveis na tabela filtrada.")

    while True:
        # Atualiza a leitura da tabela a cada volta.
        documentos = obter_documentos_visiveis(driver)

        # Mantém somente os que ainda não foram concluídos
        # nesta execução.
        pendentes = [
            documento
            for documento in documentos
            if documento["numero"] not in processados
        ]

        if not pendentes:
            print("\nNão há mais CT-es pendentes na tabela.")
            break

        # Sempre começa pelo primeiro CT-e ainda pendente.
        documento = pendentes[0]
        numero = documento["numero"]

        print(
            f"\nPróximo CT-e: {numero} "
            f"| Já concluídos: {quantidade_concluida}"
        )

        # Se alguma etapa falhar, a exceção interrompe
        # o loop e evita seguir para outro documento.
        processar_documento_completo(
            driver,
            documento
        )

        # Só marca como concluído depois de passar por
        # todas as etapas, incluindo o clique em Salvar.
        processados.add(numero)
        quantidade_concluida += 1

        print(
            f"\nPROGRESSO: {quantidade_concluida} CT-e(s) "
            "concluído(s) nesta execução."
        )

        time.sleep(2)

    print("\n" + "=" * 60)
    print("LOOP FINALIZADO")
    print(f"Total concluído: {quantidade_concluida}")
    print("=" * 60)


# ============================================================
# EXECUÇÃO PRINCIPAL
# ============================================================

def executar_egs(data_escolhida=None):
    opcoes = Options()

    opcoes.add_argument(
        f"--user-data-dir={PASTA_PERFIL}"
    )

    driver = webdriver.Chrome(options=opcoes)

    try:
        print("Abrindo o EGS Sistemas...")

        driver.get(URL_EGS)
        aguardar_carregamento(driver)

        print("\nFaça o login no sistema, se necessário.")

        input(
            "Quando estiver logado e com o EGS aberto, "
            "pressione ENTER aqui no terminal..."
        )

        if "monitor-dfe" not in driver.current_url:
            driver.get(URL_EGS)
            aguardar_carregamento(driver)

        time.sleep(5)

        print("\nPágina atual:", driver.current_url)
        print("Título:", driver.title)

        # 1. Filtrar emitente
        filtrar_emitente(driver)

        # 2. Deslocar a tabela para a direita
        print("\nDeslocando a tabela para a direita...")

        driver.execute_script("""
            document.querySelectorAll(
                '.dx-datagrid-content'
            ).forEach(function(elemento) {
                elemento.scrollLeft += 200;
            });
        """)

        time.sleep(2)

        # 3. Filtrar Registrada = falso
        filtrar_registrada_falso(driver)

        # 4. Voltar a tabela para a esquerda
        print("\nVoltando a tabela para a esquerda...")

        driver.execute_script("""
            document.querySelectorAll(
                '.dx-datagrid-content'
            ).forEach(function(elemento) {
                elemento.scrollLeft = 0;
            });
        """)

        time.sleep(2)

        # 5. Filtrar pela data
        filtrar_data(driver, data_escolhida)

        time.sleep(3)

        # 6. Mostrar quantos documentos estão visíveis
        documentos = obter_documentos_visiveis(driver)

        print("\nCT-es encontrados na tabela filtrada:")

        for documento in documentos:
            print(
                f" - CT-e {documento['numero']} "
                f"| {documento['status']}"
            )

        if not documentos:
            print(
                "\nNenhum CT-e autorizado da VOG "
                "foi encontrado com os filtros atuais."
            )

            input("Pressione ENTER para encerrar...")
            return

        print(
            f"\nTotal inicial encontrado: {len(documentos)}"
        )

        # 7. Processar em loop até não restarem pendentes
        processar_todos(driver)

        input(
            "\nConfira o resultado no EGS. "
            "Pressione ENTER para encerrar..."
        )

    except TimeoutException:
        print(
            "\nTEMPO DE ESPERA ESGOTADO.\n"
            "O script foi interrompido porque não encontrou "
            "um elemento esperado. Confira a tela do EGS."
        )

        input("Pressione ENTER para encerrar...")

    except Exception as erro:
        print(f"\nERRO: {erro}")

        print(
            "\nA automação foi interrompida. "
            "Confira o último CT-e no EGS antes de executar "
            "novamente, para evitar duplicidade de parcelas."
        )

        input("Pressione ENTER para encerrar...")

    finally:
        driver.quit()


# ============================================================
# EXECUTAR DIRETAMENTE PELO ARQUIVO
# ============================================================

if __name__ == "__main__":
    executar_egs()