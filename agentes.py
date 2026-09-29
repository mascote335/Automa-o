
import tkinter as tk
from tkinter import messagebox
from datetime import datetime, timedelta

from teste import executar_egs


def formatar_data(data):
    return data.strftime("%d/%m/%Y")


def preencher_data(data):
    campo_data.delete(0, tk.END)
    campo_data.insert(0, formatar_data(data))


def selecionar_hoje():
    preencher_data(datetime.now())


def selecionar_ontem():
    ontem = datetime.now() - timedelta(days=1)
    preencher_data(ontem)


def consultar_documentos():

    data_escolhida = campo_data.get().strip()

    # Validar a data digitada
    try:
        datetime.strptime(data_escolhida, "%d/%m/%Y")

    except ValueError:
        messagebox.showerror(
            "Data invalida",
            "Digite uma data valida no formato DD/MM/AAAA.\n"
            "Exemplo: 24/09/2026"
        )
        return

    # Confirmar a consulta
    confirmar = messagebox.askyesno(
        "Confirmar consulta",
        f"Consultar documentos com data de emissao "
        f"{data_escolhida}?"
    )

    if not confirmar:
        return

    botao_consultar.config(
        state="disabled",
        text="Consulta em andamento..."
    )

    status.config(
        text="Abrindo o EGS...",
        fg="blue"
    )

    janela.update_idletasks()

    try:
        # Envia a data escolhida para o Selenium
        executar_egs(data_escolhida)

        status.config(
            text="Consulta finalizada.",
            fg="green"
        )

    except Exception as erro:

        messagebox.showerror(
            "Erro",
            f"Ocorreu um erro:\n{erro}"
        )

        status.config(
            text="Ocorreu um erro.",
            fg="red"
        )

    finally:
        botao_consultar.config(
            state="normal",
            text="Consultar documentos"
        )


# ==========================================
# CRIAR JANELA
# ==========================================

janela = tk.Tk()

janela.title("EGS - Assistente DF-e")
janela.geometry("460x390")
janela.resizable(False, False)

# Titulo
titulo = tk.Label(
    janela,
    text="EGS - Assistente DF-e",
    font=("Segoe UI", 18, "bold")
)
titulo.pack(pady=(22, 5))

subtitulo = tk.Label(
    janela,
    text="Painel de consulta de documentos",
    font=("Segoe UI", 10)
)
subtitulo.pack(pady=(0, 22))

# Campo de data
label_data = tk.Label(
    janela,
    text="Data de emissao (DD/MM/AAAA):",
    font=("Segoe UI", 10)
)
label_data.pack()

campo_data = tk.Entry(
    janela,
    font=("Segoe UI", 14),
    justify="center",
    width=18
)
campo_data.pack(pady=8)

# Por padrao, iniciar com ontem
selecionar_ontem()

# Botoes Hoje e Ontem
frame_datas = tk.Frame(janela)
frame_datas.pack(pady=5)

botao_hoje = tk.Button(
    frame_datas,
    text="Hoje",
    width=12,
    command=selecionar_hoje
)
botao_hoje.pack(side="left", padx=5)

botao_ontem = tk.Button(
    frame_datas,
    text="Ontem",
    width=12,
    command=selecionar_ontem
)
botao_ontem.pack(side="left", padx=5)

# Informacoes dos filtros
info = tk.Label(
    janela,
    text="Emitente: vog  |  Registrada: falso",
    font=("Segoe UI", 9)
)
info.pack(pady=14)

# Botao de consulta
botao_consultar = tk.Button(
    janela,
    text="Consultar documentos",
    font=("Segoe UI", 11, "bold"),
    width=25,
    height=2,
    command=consultar_documentos
)
botao_consultar.pack(pady=5)

# Status
status = tk.Label(
    janela,
    text="Pronto para consultar.",
    font=("Segoe UI", 9),
    fg="gray"
)
status.pack(pady=12)

aviso = tk.Label(
    janela,
    text="Esta etapa consulta os documentos, sem processar.",
    font=("Segoe UI", 9),
    fg="gray"
)
aviso.pack()

janela.mainloop()