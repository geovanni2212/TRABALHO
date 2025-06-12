import sqlite3
import tkinter as tk
from tkinter import messagebox, ttk
import json
import csv
import os

def criar_banco():
    conn = sqlite3.connect("estacio.db")
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS alunos (
        matricula INTEGER PRIMARY KEY,
        nome TEXT NOT NULL
    )""")
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS disciplinas (
        codigo TEXT PRIMARY KEY,
        nome TEXT NOT NULL
    )""")
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS notas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        matricula INTEGER,
        codigo TEXT,
        nota REAL,
        FOREIGN KEY (matricula) REFERENCES alunos(matricula),
        FOREIGN KEY (codigo) REFERENCES disciplinas(codigo)
    )""")
    conn.commit()
    conn.close()

def executar_query(query, params=()):
    conn = sqlite3.connect("estacio.db")
    cursor = conn.cursor()
    cursor.execute(query, params)
    conn.commit()
    conn.close()

def listar_query(query):
    conn = sqlite3.connect("estacio.db")
    cursor = conn.cursor()
    cursor.execute(query)
    dados = cursor.fetchall()
    conn.close()
    return dados

def exportar_dados(formato):
    conn = sqlite3.connect("estacio.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM alunos")
    alunos = cursor.fetchall()
    cursor.execute("SELECT * FROM disciplinas")
    disciplinas = cursor.fetchall()
    cursor.execute("SELECT * FROM notas")
    notas = cursor.fetchall()
    conn.close()

    if formato == "json":
        dados = {
            "alunos": alunos,
            "disciplinas": disciplinas,
            "notas": notas
        }
        with open("dados.json", "w", encoding="utf-8") as f:
            json.dump(dados, f, ensure_ascii=False, indent=4)
    elif formato == "csv":
        with open("alunos.csv", "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["matricula", "nome"])
            writer.writerows(alunos)
        with open("disciplinas.csv", "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["codigo", "nome"])
            writer.writerows(disciplinas)
        with open("notas.csv", "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["id", "matricula", "codigo", "nota"])
            writer.writerows(notas)
    elif formato == "txt":
        with open("dados.txt", "w", encoding="utf-8") as f:
            f.write("Alunos:\n")
            for a in alunos:
                f.write(str(a) + "\n")
            f.write("\nDisciplinas:\n")
            for d in disciplinas:
                f.write(str(d) + "\n")
            f.write("\nNotas:\n")
            for n in notas:
                f.write(str(n) + "\n")

    caminho = os.path.abspath(".")
    os.startfile(caminho)
    messagebox.showinfo("Exportação", f"Dados exportados como {formato.upper()} com sucesso.")

def incluir_dados(tabela, campos, valores):
    query = f"INSERT INTO {tabela} ({','.join(campos)}) VALUES ({','.join(['?' for _ in valores])})"
    try:
        executar_query(query, valores)
        messagebox.showinfo("Sucesso", f"Dados inseridos na tabela {tabela}.")
    except sqlite3.IntegrityError:
        messagebox.showerror("Erro", f"Chave já cadastrada na tabela {tabela}.")

def excluir_dado(tabela, chave, valor):
    query = f"DELETE FROM {tabela} WHERE {chave} = ?"
    executar_query(query, (valor,))
    messagebox.showinfo("Remoção", f"Registro removido da tabela {tabela}.")

def alterar_dado(tabela, campos, valores, chave, chave_valor):
    sets = ', '.join([f"{campo} = ?" for campo in campos])
    query = f"UPDATE {tabela} SET {sets} WHERE {chave} = ?"
    executar_query(query, (*valores, chave_valor))
    messagebox.showinfo("Atualização", f"Registro da tabela {tabela} atualizado.")

def listar_dados(tabela):
    dados = listar_query(f"SELECT * FROM {tabela}")
    return "\n".join(str(d) for d in dados)

def criar_interface():
    root = tk.Tk()
    root.title("Sistema Acadêmico")
    root.geometry("650x550")

    frame = tk.Frame(root, padx=10, pady=10)
    frame.pack(fill="both", expand=True)

    campos = {
        "alunos": ["matricula", "nome"],
        "disciplinas": ["codigo", "nome"],
        "notas": ["matricula", "codigo", "nota"]
    }

    def janela_acao(acao):
        janela = tk.Toplevel()
        janela.title(f"{acao.title()} Dados")
        janela.geometry("500x500")
        aba = ttk.Notebook(janela)
        aba.pack(expand=True, fill='both')

        for tabela, colunas in campos.items():
            tab = tk.Frame(aba)
            aba.add(tab, text=tabela.title())
            entradas = []
            for i, campo in enumerate(colunas):
                tk.Label(tab, text=campo).grid(row=i, column=0)
                e = tk.Entry(tab)
                e.grid(row=i, column=1)
                entradas.append(e)

            if acao == "alterar":
                novos = []
                for i, campo in enumerate(colunas):
                    tk.Label(tab, text=f"Novo {campo}").grid(row=i + len(colunas), column=0)
                    en = tk.Entry(tab)
                    en.grid(row=i + len(colunas), column=1)
                    novos.append(en)

            def acao_local(t=tabela, es=entradas, ns=novos if acao == "alterar" else []):
                if acao == "incluir":
                    incluir_dados(t, campos[t], [e.get() for e in es])
                elif acao == "excluir":
                    excluir_dado(t, campos[t][0], es[0].get())
                elif acao == "alterar":
                    alterar_dado(t, campos[t], [n.get() for n in ns], campos[t][0], es[0].get())
                elif acao == "listar":
                    dados = listar_dados(t)
                    messagebox.showinfo("Listagem", dados if dados else "Nada encontrado.")

            tk.Button(tab, text=acao.title(), command=acao_local).grid(row=30, column=0, columnspan=2, pady=10)

    tk.Button(frame, text="Incluir", command=lambda: janela_acao("incluir"), width=20).pack(pady=5)
    tk.Button(frame, text="Alterar", command=lambda: janela_acao("alterar"), width=20).pack(pady=5)
    tk.Button(frame, text="Excluir", command=lambda: janela_acao("excluir"), width=20).pack(pady=5)
    tk.Button(frame, text="Listar", command=lambda: janela_acao("listar"), width=20).pack(pady=5)

    tk.Label(frame, text="Exportar Dados").pack(pady=10)
    tk.Button(frame, text="Exportar JSON", command=lambda: exportar_dados("json"), width=20).pack(pady=2)
    tk.Button(frame, text="Exportar CSV", command=lambda: exportar_dados("csv"), width=20).pack(pady=2)
    tk.Button(frame, text="Exportar TXT", command=lambda: exportar_dados("txt"), width=20).pack(pady=2)

    root.mainloop()

if __name__ == "__main__":
    criar_banco()
    criar_interface()
