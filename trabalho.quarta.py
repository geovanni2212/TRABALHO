import sqlite3
import tkinter as tk
from tkinter import messagebox

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

def adicionar_aluno(matricula, nome):
    conn = sqlite3.connect("estacio.db")
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO alunos (matricula, nome) VALUES (?, ?)", (matricula, nome))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def adicionar_disciplina(codigo, nome):
    conn = sqlite3.connect("estacio.db")
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO disciplinas (codigo, nome) VALUES (?, ?)", (codigo, nome))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def adicionar_nota(matricula, codigo, nota):
    conn = sqlite3.connect("estacio.db")
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM alunos WHERE matricula = ?", (matricula,))
    if not cursor.fetchone():
        conn.close()
        return "Aluno não encontrado"
    cursor.execute("SELECT 1 FROM disciplinas WHERE codigo = ?", (codigo,))
    if not cursor.fetchone():
        conn.close()
        return "Disciplina não encontrada"
    cursor.execute("INSERT INTO notas (matricula, codigo, nota) VALUES (?, ?, ?)", (matricula, codigo, nota))
    conn.commit()
    conn.close()
    return "Sucesso"

def buscar_notas(matricula):
    conn = sqlite3.connect("estacio.db")
    cursor = conn.cursor()
    cursor.execute("""
    SELECT disciplinas.nome, notas.nota FROM notas
    JOIN disciplinas ON notas.codigo = disciplinas.codigo
    WHERE notas.matricula = ?
    """, (matricula,))
    resultados = cursor.fetchall()
    conn.close()
    return resultados

class Aplicacao:
    def __init__(self, root):
        self.root = root
        root.title("Estácio")
        root.geometry("400x500")
        self.frame = tk.Frame(root, padx=20, pady=20)
        self.frame.pack()
        tk.Label(self.frame, text="Cadastro de Aluno").grid(row=0, column=0, columnspan=2, pady=5)
        tk.Label(self.frame, text="Matrícula:").grid(row=1, column=0, sticky="e")
        self.matricula_aluno = tk.Entry(self.frame)
        self.matricula_aluno.grid(row=1, column=1)
        tk.Label(self.frame, text="Nome:").grid(row=2, column=0, sticky="e")
        self.nome_aluno = tk.Entry(self.frame)
        self.nome_aluno.grid(row=2, column=1)
        tk.Button(self.frame, text="Adicionar Aluno", command=self.adicionar_aluno).grid(row=3, column=0, columnspan=2, pady=5)
        tk.Label(self.frame, text="Cadastro de Disciplina").grid(row=4, column=0, columnspan=2, pady=5)
        tk.Label(self.frame, text="Código:").grid(row=5, column=0, sticky="e")
        self.codigo_disciplina = tk.Entry(self.frame)
        self.codigo_disciplina.grid(row=5, column=1)
        tk.Label(self.frame, text="Nome:").grid(row=6, column=0, sticky="e")
        self.nome_disciplina = tk.Entry(self.frame)
        self.nome_disciplina.grid(row=6, column=1)
        tk.Button(self.frame, text="Adicionar Disciplina", command=self.adicionar_disciplina).grid(row=7, column=0, columnspan=2, pady=5)
        tk.Label(self.frame, text="Adicionar Nota").grid(row=8, column=0, columnspan=2, pady=5)
        tk.Label(self.frame, text="Matrícula:").grid(row=9, column=0, sticky="e")
        self.matricula_nota = tk.Entry(self.frame)
        self.matricula_nota.grid(row=9, column=1)
        tk.Label(self.frame, text="Código Disciplina:").grid(row=10, column=0, sticky="e")
        self.codigo_nota = tk.Entry(self.frame)
        self.codigo_nota.grid(row=10, column=1)
        tk.Label(self.frame, text="Nota (0-10):").grid(row=11, column=0, sticky="e")
        self.valor_nota = tk.Entry(self.frame)
        self.valor_nota.grid(row=11, column=1)
        tk.Button(self.frame, text="Adicionar Nota", command=self.adicionar_nota).grid(row=12, column=0, columnspan=2, pady=5)
        tk.Label(self.frame, text="Mostrar Notas do Aluno").grid(row=13, column=0, columnspan=2, pady=5)
        tk.Label(self.frame, text="Matrícula:").grid(row=14, column=0, sticky="e")
        self.matricula_busca = tk.Entry(self.frame)
        self.matricula_busca.grid(row=14, column=1)
        tk.Button(self.frame, text="Mostrar Notas", command=self.mostrar_notas).grid(row=15, column=0, columnspan=2, pady=5)

    def adicionar_aluno(self):
        try:
            matricula = int(self.matricula_aluno.get())
            nome = self.nome_aluno.get().strip()
            if not nome:
                raise ValueError
            sucesso = adicionar_aluno(matricula, nome)
            if sucesso:
                messagebox.showinfo("Sucesso", "Aluno cadastrado!")
            else:
                messagebox.showerror("Erro", "Matrícula já cadastrada.")
        except ValueError:
            messagebox.showerror("Erro", "Dados inválidos.")

    def adicionar_disciplina(self):
        codigo = self.codigo_disciplina.get().strip()
        nome = self.nome_disciplina.get().strip()
        if not codigo or not nome:
            messagebox.showerror("Erro", "Dados inválidos.")
            return
        sucesso = adicionar_disciplina(codigo, nome)
        if sucesso:
            messagebox.showinfo("Sucesso", "Disciplina cadastrada!")
        else:
            messagebox.showerror("Erro", "Código já cadastrado.")

    def adicionar_nota(self):
        try:
            matricula = int(self.matricula_nota.get())
            codigo = self.codigo_nota.get().strip()
            nota = float(self.valor_nota.get())
            if nota < 0 or nota > 10:
                raise ValueError
            resultado = adicionar_nota(matricula, codigo, nota)
            if resultado == "Sucesso":
                messagebox.showinfo("Sucesso", "Nota adicionada!")
            else:
                messagebox.showerror("Erro", resultado)
        except ValueError:
            messagebox.showerror("Erro", "Dados inválidos.")

    def mostrar_notas(self):
        try:
            matricula = int(self.matricula_busca.get())
            notas = buscar_notas(matricula)
            if notas:
                texto = "\n".join(f"{disc}: {nota}" for disc, nota in notas)
                messagebox.showinfo("Notas do Aluno", texto)
            else:
                messagebox.showinfo("Notas do Aluno", "Nenhuma nota cadastrada.")
        except ValueError:
            messagebox.showerror("Erro", "Matrícula inválida.")

if __name__ == "__main__":
    criar_banco()
    root = tk.Tk()
    app = Aplicacao(root)
    root.mainloop()
