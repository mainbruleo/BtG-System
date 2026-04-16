import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk
import sqlite3
import os
import webbrowser
from pathlib import Path
import shutil
from typing import Optional
import datetime
import zipfile
import docx
import sys
import os

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# Personalização do Background.
ESTILO_BG = "black"      
ESTILO_ALT_BG = "black"  
COR_CARMIM = "#960018"   

#  Personalização de Fonte.
ESTILO_FONTE = ("Roboto", 12, "bold")
ESTILO_TITULO = ("Roboto", 15, "bold") 

# Personalização de Interação.
ESTILO_ENTRY = {
    "bg": "black",        
    "fg": COR_CARMIM,     
    "insertbackground": COR_CARMIM, 
    "bd": 0,
    "highlightthickness": 1,
    "highlightbackground": COR_CARMIM, 
    "font": ESTILO_FONTE
}

# Personalização Botões.
ESTILO_BOTAO = {
    "bg": COR_CARMIM,
    "fg": "black",
    "font": ESTILO_FONTE,
    "activebackground": "#7a0014", # Tom levemente mais escuro ao clicar
    "activeforeground": "black",
    "relief": "flat",
    "cursor": "hand2"
}

# Define o logo da marca no canto inferior direito.
def adicionar_logo(janela):
    try:
        img_aberta = Image.open(resource_path("btg.png"))
        img_aberta = img_aberta.resize((80, 80), Image.Resampling.LANCZOS)
        logo_img = ImageTk.PhotoImage(img_aberta)
        
        label_logo = tk.Label(janela, image=logo_img, bg=ESTILO_BG)
        label_logo.image = logo_img  
        label_logo.place(relx=1.0, rely=1.0, anchor="se", x=-10, y=-10)
        
    except Exception as e:
        print(f"Erro ao carregar logo: {e}")

# Criar o SQLite com os dados inputados.
def criar_banco():
    conn = sqlite3.connect("fisio.db")
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS infoscomplementares (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            endereco TEXT NOT NULL,
            telefone TEXT,
            rg TEXT,
            cpf TEXT UNIQUE, 
            data DATE
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS infospacientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            idade INTEGER,
            peso REAL,
            sexo TEXT,
            profissao TEXT,
            foto TEXT,
            complemento_id INTEGER,
            FOREIGN KEY (complemento_id) REFERENCES infoscomplementares(id) ON DELETE CASCADE
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS exames (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            paciente_id INTEGER,
            caminho_img TEXT NOT NULL,
            FOREIGN KEY (paciente_id) REFERENCES infospacientes(id) ON DELETE CASCADE
        )
    ''')

    conn.commit()
    conn.close()
    print("Banco de dados criado com sucesso!")

# Limpeza dos backups antigos.
def limpar_backups_antigos(diretorio, limite):
    """Remove arquivos excedentes."""

    arquivos = sorted(list(diretorio.glob("*.*")), key=os.path.getmtime)
    
    while len(arquivos) > (limite * 2):
        try:
            arquivos[0].unlink()
            arquivos.pop(0)
        except Exception as e:
            print(f"Erro ao limpar backup antigo: {e}")

# Criar novos backups (5), excluindo sempre o mais antigo primeiro.
def realizar_backup_fisio():
    """Executa a cópia do banco e das pastas de pacientes para o OneDrive."""
    try:
        home = Path(os.path.expanduser("~"))
        diretorio_onedrive_docs = home / "OneDrive" / "Documentos"
        
        if not diretorio_onedrive_docs.exists():
            diretorio_onedrive_docs = home / "OneDrive" / "Documents"
        
        if not diretorio_onedrive_docs.exists():
            diretorio_onedrive_docs = home / "Documents"

        diretorio_backup = diretorio_onedrive_docs / "Backups_BtGSys"
        diretorio_backup.mkdir(parents=True, exist_ok=True)

        data_str = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

        if os.path.exists("fisio.db"):
            shutil.copy2("fisio.db", diretorio_backup / f"fisio_backup_{data_str}.db")

        pasta_origem_pacientes = Path("pacientes")
        if pasta_origem_pacientes.exists():
            arquivo_zip = diretorio_backup / f"arquivos_pacientes_{data_str}.zip"
            with zipfile.ZipFile(arquivo_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for raiz, dirs, arquivos in os.walk(pasta_origem_pacientes):
                    for arquivo in arquivos:
                        caminho_completo = Path(raiz) / arquivo
                        zipf.write(caminho_completo, caminho_completo.relative_to(pasta_origem_pacientes.parent))

        limpar_backups_antigos(diretorio_backup, limite=5)
        print(f"Backup sincronizado no OneDrive em: {diretorio_backup}")
        
    except Exception as e:
        print(f"Falha ao realizar backup no OneDrive: {e}")

# Cadastro de informações na tela "Cadastrar".
def abrir_tela_cadastro(root):
    root.destroy()
    cadastro = tk.Tk()
    cadastro.title("Cadastro")
    cadastro.geometry("1920x1032+0+0")
    cadastro.state("zoomed")
    adicionar_logo(cadastro)
    cadastro.configure(bg=ESTILO_BG)
    caminho_foto: Optional[str] = None
    caminhos_exames = []

    cadastro.iconbitmap(resource_path("iconapplication.ico"))
    
    frame_principal = tk.Frame(cadastro, bg=ESTILO_BG)
    frame_principal.place(relx=0.5, rely=0.4, anchor=tk.CENTER)

    tk.Label(frame_principal, text="Dados do Paciente:", font=ESTILO_TITULO, bg=ESTILO_BG, fg=COR_CARMIM).grid(row=0, column=0, columnspan=2, pady=(0, 20))

    frame_esquerda = tk.Frame(frame_principal, bg=ESTILO_BG)
    frame_esquerda.grid(row=1, column=0, padx=20, pady=0) # Reduzi o pady para não afastar muito do título

    campos_pacientes = ["Nome", "Idade", "Peso", "Sexo", "Profissão"]
    entries_pacientes = {}

    for campo in campos_pacientes:
        tk.Label(frame_esquerda, text=campo + ":", font=ESTILO_FONTE, bg=ESTILO_BG, fg=COR_CARMIM).pack(anchor="w")
        entry = tk.Entry(frame_esquerda, **ESTILO_ENTRY, width=30)
        entry.pack()
        entries_pacientes[campo] = entry

    frame_direita = tk.Frame(frame_principal, bg=ESTILO_BG)
    frame_direita.grid(row=1, column=1, padx=20, pady=0)

    campos_complementares = ["Endereço", "Telefone", "RG", "CPF", "Data da Avaliação"]
    entries_complementares = {}

    for campo in campos_complementares:
        tk.Label(frame_direita, text=campo + ":", font=ESTILO_FONTE, bg=ESTILO_BG, fg=COR_CARMIM).pack(anchor="w")
        entry = tk.Entry(frame_direita, **ESTILO_ENTRY, width=30)
        entry.pack()
        entries_complementares[campo] = entry

    frame_botoes = tk.Frame(frame_principal, bg=ESTILO_BG)
    frame_botoes.grid(row=2, column=0, columnspan=2, pady=20)

    # Anexar a foto do paciente.
    def anexar_foto():
        nonlocal caminho_foto
        arquivo = filedialog.askopenfilename()
        if arquivo:
            caminho_foto = arquivo
            messagebox.showinfo("Sucesso", "Foto anexada com sucesso!")

    # Anexar os exames do paciente.
    def anexar_exames():
        nonlocal caminhos_exames
        arquivos = filedialog.askopenfilenames(filetypes=[("Arquivos de Imagem", "*.png *.jpg *.jpeg *.bmp *.gif"),
        ("Todos os arquivos", "*.*")])
        if arquivos:
            caminhos_exames = arquivos
            messagebox.showinfo("Sucesso", "Exames anexados com sucesso!")

    tk.Button(frame_botoes, text="Anexar Foto", **ESTILO_BOTAO, command=anexar_foto).pack(pady=5, fill="x")
    tk.Button(frame_botoes, text="Anexar Exames", **ESTILO_BOTAO, command=anexar_exames).pack(pady=5, fill="x")

    # Salvar os dados do paciente no SQLite.
    def salvar_dados():
        nonlocal caminho_foto
        endereco = entries_complementares["Endereço"].get()
        telefone = entries_complementares["Telefone"].get()
        rg = entries_complementares["RG"].get()
        cpf = entries_complementares["CPF"].get()
        data = entries_complementares["Data da Avaliação"].get()

        nome_paciente = entries_pacientes["Nome"].get()
        idade = entries_pacientes["Idade"].get()
        peso = entries_pacientes["Peso"].get()
        sexo = entries_pacientes["Sexo"].get()
        profissao = entries_pacientes["Profissão"].get()

        try:
            idade = int(idade)
            peso = float(peso)
            rg = int(rg)
            cpf = int(cpf)
            telefone = int(telefone)
        except ValueError:
            messagebox.showerror("Erro", "Idade, Peso, Telefone, RG e CPF devem ser algarismos")
            return

        if not cpf or not nome_paciente:
            messagebox.showerror("Erro", "CPF e nome do paciente são obrigatórios.")
            return

        try:
            conn = sqlite3.connect("fisio.db")
            cursor = conn.cursor()

            cursor.execute('''
                INSERT INTO infoscomplementares (endereco, telefone, rg, cpf, data)
                VALUES (?, ?, ?, ?, ?)
            ''', (endereco, telefone, rg, cpf, data))
            complemento_id = cursor.lastrowid

            cursor.execute('''
                INSERT INTO infospacientes (nome, idade, peso, sexo, profissao, foto, complemento_id)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (nome_paciente, idade, peso, sexo, profissao, None, complemento_id))
            paciente_id = cursor.lastrowid

            pasta_paciente = Path("pacientes") / f"{nome_paciente}_{paciente_id}"
            pasta_paciente.mkdir(parents=True, exist_ok=True)

            if caminho_foto is not None:
                caminho_foto_path = Path(caminho_foto)
                destino_foto = pasta_paciente / Path(caminho_foto).name
                shutil.copy2(str(caminho_foto_path), str(destino_foto))
                caminho_foto = str(destino_foto)
                cursor.execute("UPDATE infospacientes SET foto = ? WHERE id = ?", (str(destino_foto), paciente_id))

            for caminho_img in caminhos_exames:
                destino_img = pasta_paciente / Path(caminho_img).name
                shutil.copy2(caminho_img, destino_img)
                cursor.execute("INSERT INTO exames (paciente_id, caminho_img) VALUES (?, ?)", (paciente_id, str(destino_img)))

            planilha_pagamento = Path("modelos/pagamentos.xlsx")
            destino_pagamento = pasta_paciente / "pagamentos.xlsx"

            if planilha_pagamento.exists():
                shutil.copy2(planilha_pagamento, destino_pagamento)

            modelo_avaliacao_fisica = Path("modelos/avaliacao_fisica.docx")
            destino_avaliacao_fisica = pasta_paciente / "avaliacao_fisica.docx"
            if modelo_avaliacao_fisica.exists():
                shutil.copy2(modelo_avaliacao_fisica, destino_avaliacao_fisica)

            try:
                conn.commit()
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao salvar dados: {e}")
            finally:
                conn.close()

            messagebox.showinfo("Sucesso", "Dados salvos com sucesso!")

            cadastro.destroy()
            iniciar_interface()

        except sqlite3.IntegrityError as e:

            if "UNIQUE constraint failed: infoscomplementares.cpf" in str(e):
                messagebox.showerror("Erro", "CPF já cadastrado.")
            else:
                messagebox.showerror("Erro", f"Erro ao salvar dados: {e}")

    tk.Button(frame_botoes, text="Salvar", **ESTILO_BOTAO, command=salvar_dados).pack(pady=10)
    frame_voltar = tk.Frame(cadastro, bg=ESTILO_BG)
    frame_voltar.pack(side=tk.BOTTOM, anchor="w", padx=20, pady=20)

    tk.Button(frame_voltar, text="Voltar", **ESTILO_BOTAO, command=lambda: [cadastro.destroy(), iniciar_interface()]).pack(anchor="w")

# Histórico de informações na tela "Histórico do Paciente".
def abrir_tela_historico():
    historico = tk.Tk()
    historico.title("Histórico")
    historico.geometry("1920x1032+0+0")
    historico.state("zoomed")
    adicionar_logo(historico)
    historico.configure(bg=ESTILO_BG)

    historico.iconbitmap(resource_path("iconapplication.ico"))

    style = ttk.Style()
    style.theme_use("default") 
    
    style.configure("Treeview",
                    background="black",
                    foreground=COR_CARMIM,
                    fieldbackground="black",
                    rowheight=30,
                    borderwidth=0,
                    relief="flat",
                    font=("Roboto", 12, "bold"))

    style.layout("Treeview", [('Treeview.treearea', {'sticky': 'nswe'})]) 

    style.configure("Treeview.Heading",
                    background="black",
                    foreground=COR_CARMIM,
                    borderwidth=0,
                    relief="flat",
                    font=("Roboto", 12, "bold"))

    style.map("Treeview",
              background=[('selected', COR_CARMIM)], 
              foreground=[('selected', 'black')])

    frame_principal = tk.Frame(historico, bg=ESTILO_BG)
    frame_principal.pack(pady=20, padx=20, fill=tk.BOTH, expand=True)

    tk.Label(frame_principal, text="Histórico de Pacientes:", font=ESTILO_TITULO, bg=ESTILO_BG, fg=COR_CARMIM).pack(pady=10)

    frame_lista = tk.Frame(frame_principal, bg=ESTILO_BG)
    frame_lista.pack(fill=tk.BOTH, expand=True)

    tree = ttk.Treeview(frame_lista, columns=("Nome",), show="headings")
    tree.heading("Nome", text="Nome do Paciente")
    tree.column("Nome", width=300)
    tree.pack(fill=tk.BOTH, expand=True, pady=10)

    # Carrega as informações cadastradas do paciente no SQLite.
    def carregar_pacientes():
        conn = sqlite3.connect("fisio.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id, nome FROM infospacientes ORDER BY nome ASC")
        pacientes = cursor.fetchall()
        conn.close()

        for item in tree.get_children():
            tree.delete(item)

        for paciente_id, nome in pacientes:
            tree.insert("", tk.END, values=(nome,), iid=paciente_id)

    # Permite visualizar as informações cadastradas no SQLite do paciente selecionado.
    def ver_paciente():
        item = tree.focus()
        if item:
            paciente_id = item
            historico.destroy()
            abrir_tela_visualizacao_edicao(paciente_id)
        else:
            messagebox.showwarning("Aviso", "Selecione um paciente para visualizar.")

    # Permite excluir as informações cadastradas do paciente.
    def excluir_paciente():
        item = tree.focus()
        if item:
            paciente_id = item
            resposta = messagebox.askyesno("Confirmação", "Tem certeza que deseja excluir este paciente?")
            if resposta:
                conn = sqlite3.connect("fisio.db")
                cursor = conn.cursor()
                cursor.execute("SELECT nome FROM infospacientes WHERE id = ?", (paciente_id,))
                resultado = cursor.fetchone()
                if resultado:
                    nome = resultado[0]
                    nome_pasta = f"{nome}_{paciente_id}"
                    pasta = Path("pacientes") / nome_pasta
                    cursor.execute("DELETE FROM infospacientes WHERE id = ?", (paciente_id,))
                    conn.commit()
                    conn.close()
                    if pasta.exists():
                        try:
                            shutil.rmtree(pasta)
                        except Exception as e:
                            messagebox.showwarning("Aviso", f"Erro ao excluir pasta: {e}")
                            return
                    carregar_pacientes()
                    messagebox.showinfo("Sucesso", "Paciente excluído com sucesso.")
        else:
            messagebox.showwarning("Aviso", "Selecione um paciente para excluir.")

    frame_botoes = tk.Frame(frame_principal, bg=ESTILO_BG)
    frame_botoes.pack(pady=10)

    tk.Button(frame_botoes, text="Ver", **ESTILO_BOTAO, command=ver_paciente).pack(side=tk.LEFT, padx=10)
    tk.Button(frame_botoes, text="Excluir", **ESTILO_BOTAO, command=excluir_paciente).pack(side=tk.LEFT, padx=10)
    tk.Button(historico, text="Voltar", **ESTILO_BOTAO, command=lambda: [historico.destroy(), iniciar_interface()]).pack(side=tk.BOTTOM, anchor=tk.W, padx=20, pady=20)

    carregar_pacientes()
    historico.mainloop()

# Visualização e Edição de informações na tela "Visualização e Edição".
def abrir_tela_visualizacao_edicao(paciente_id):
    visualizacao = tk.Tk()
    visualizacao.title("Visualização e Edição")
    visualizacao.geometry("1920x1032+0+0")
    visualizacao.state("zoomed")
    adicionar_logo(visualizacao)
    visualizacao.configure(bg=ESTILO_BG)
    visualizacao.iconbitmap(resource_path("iconapplication.ico"))

    conn = sqlite3.connect("fisio.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT p.nome, p.idade, p.peso, p.sexo, p.profissao, p.foto,
               c.endereco, c.telefone, c.rg, c.cpf, c.data,
               p.id, c.id
        FROM infospacientes p
        JOIN infoscomplementares c ON p.complemento_id = c.id
        WHERE p.id = ?
    """, (paciente_id,))
    dados = cursor.fetchone()

    if not dados:
        messagebox.showerror("Erro", "Paciente não encontrado.")
        visualizacao.destroy()
        return

    (nome_paciente, idade, peso, sexo, profissao, foto,
     endereco, telefone, rg, cpf, data,
     id_paciente, id_complemento) = dados
    rg_original = str(rg)
    cpf_original = str(cpf)

    caminhos_novos_exames = []
    nova_foto_path = foto

    frame = tk.Frame(visualizacao, bg=ESTILO_BG)
    frame.place(relx=0.5, rely=0.3, anchor="center")

    tk.Label(frame, text="Dados do Paciente:", font=ESTILO_TITULO, bg=ESTILO_BG, fg=COR_CARMIM).grid(row=0, column=0, columnspan=2, pady=(0, 20))

    # Abre a possibilidade de editar os dados do SQLite previamente cadastrados para o paciente selecionado.
    def criar_entry(parent, texto, valor):
        tk.Label(parent, text=texto + ":", font=ESTILO_FONTE, bg=ESTILO_BG, fg=COR_CARMIM).pack(anchor="w")
        entry = tk.Entry(parent, **ESTILO_ENTRY, width=30)
        entry.insert(0, valor)
        entry.pack()
        return entry

    frame_paciente = tk.Frame(frame, bg=ESTILO_BG)
    frame_paciente.grid(row=1, column=0, padx=10, pady=10, sticky="n")
    
    entry_nome = criar_entry(frame_paciente, "Nome", nome_paciente)
    entry_idade = criar_entry(frame_paciente, "Idade", idade)
    entry_peso = criar_entry(frame_paciente, "Peso", peso)
    entry_sexo = criar_entry(frame_paciente, "Sexo", sexo)
    entry_profissao = criar_entry(frame_paciente, "Profissão", profissao)

    frame_foto = tk.Frame(visualizacao, bg=ESTILO_BG)
    frame_foto.place(relx=0.15, rely=0.35, anchor="center")

    label_foto = tk.Label(frame_foto, bg=ESTILO_BG)
    label_foto.pack()

    # Permite visualizar a foto do paciente.
    def exibir_foto(caminho):
        if caminho and os.path.exists(caminho):
            img = Image.open(caminho)
            img.thumbnail((150, 150))
            foto_tk = ImageTk.PhotoImage(img)
            label_foto.image = foto_tk
            label_foto.configure(image=foto_tk)

    # Permite substituir a foto do paciente.   
    def trocar_foto():
        nonlocal nova_foto_path
        arquivo = filedialog.askopenfilename()
        if arquivo:
            nova_foto_path = arquivo
            exibir_foto(nova_foto_path)

    exibir_foto(foto)

    btn_trocar_foto = tk.Button(frame_foto, text="Trocar Foto", **ESTILO_BOTAO, command=trocar_foto)
    btn_trocar_foto.pack(pady=5)
    
    frame_complementar = tk.Frame(frame, bg=ESTILO_BG)
    frame_complementar.grid(row=1, column=1, padx=10, pady=10, sticky="n")

    entry_complementar = {
        "endereço": criar_entry(frame_complementar, "Endereço", endereco),
        "telefone": criar_entry(frame_complementar, "Telefone", telefone),
        "rg": criar_entry(frame_complementar, "RG", rg),
        "cpf": criar_entry(frame_complementar, "CPF", cpf),
        "data": criar_entry(frame_complementar, "Data da Avaliação", data)
    }

    # Permite visualizar os exames do paciente.
    def abrir_exames():
        cursor.execute("SELECT caminho_img FROM exames WHERE paciente_id = ?", (paciente_id,))
        exames = cursor.fetchall()

        for (caminho,) in exames:
            if os.path.exists(caminho):
                webbrowser.open(caminho)
            else:
                messagebox.showwarning("Aviso", f"Arquivo {caminho} não encontrado.")

    # Permite anexar novos exames na página do paciente.
    def anexar_novos_exames():
        arquivos = filedialog.askopenfilenames(filetypes=[("Arquivos de Imagem", "*.png *.jpg *.jpeg *.bmp *.gif"),
        ("Todos os arquivos", "*.*")])

        if arquivos:
            caminhos_novos_exames.extend(arquivos)
            messagebox.showinfo("Sucesso", "Novos exames anexados!")

    # Abre a planilha de controle de pagamentos.
    def abrir_pagamento():
        pasta = Path(f"pacientes/{nome_paciente}_{id_paciente}")
        planilha_pagamento = pasta / "pagamentos.xlsx"

        if planilha_pagamento.exists():
            webbrowser.open(str(planilha_pagamento))
        else:
            messagebox.showerror("Erro", "Planilha não encontrada.")

    # Abre a ficha de avaliação física.
    def abrir_avaliacao_fisica():
        pasta = Path(f"pacientes/{nome_paciente}_{id_paciente}")
        modelo_avaliacao_fisica = pasta / "avaliacao_fisica.docx"

        if modelo_avaliacao_fisica.exists():
            webbrowser.open(str(modelo_avaliacao_fisica))
        else:
            messagebox.showerror("Erro", "Avaliação Física não encontrada.")

    # Salva as novas informações substituídas ou cadastradas do paciente.
    def salvar_alteracoes():
        novo_nome = entry_nome.get().strip()
        rg_input = entry_complementar["rg"].get().strip()
        cpf_input = entry_complementar["cpf"].get().strip()

        if cpf_input != cpf_original or rg_input != rg_original:
            messagebox.showerror("Erro", "Não é permitido alterar o CPF ou RG.")
            return

        try:
            idade = int(entry_idade.get().strip())
            peso = float(entry_peso.get().strip())
        except ValueError:
            messagebox.showerror("Erro", "Idade deve ser número inteiro e peso deve ser número decimal.")
            return

        try:
            pasta_base = Path("pacientes")
            nome_pasta_antiga = f"{nome_paciente}_{id_paciente}"
            nome_pasta_nova = f"{novo_nome}_{id_paciente}"
            
            caminho_antigo = pasta_base / nome_pasta_antiga
            caminho_novo = pasta_base / nome_pasta_nova

            if novo_nome != nome_paciente:
                if caminho_antigo.exists():
                    try:
                        os.rename(str(caminho_antigo), str(caminho_novo))
                        
                        cursor.execute("""
                            UPDATE exames 
                            SET caminho_img = REPLACE(caminho_img, ?, ?)
                            WHERE paciente_id = ?
                        """, (nome_pasta_antiga, nome_pasta_nova, paciente_id))
                        
                    except Exception as e:
                        messagebox.showerror("Erro", f"Erro ao renomear pasta/caminhos: {e}")
                        return

            caminho_foto_final = nova_foto_path
            if nova_foto_path:

                if nome_pasta_antiga in nova_foto_path:
                    caminho_foto_final = nova_foto_path.replace(nome_pasta_antiga, nome_pasta_nova)
  
                elif Path(nova_foto_path).exists() and str(pasta_base) not in nova_foto_path:
                    destino_foto = caminho_novo / Path(nova_foto_path).name
                    shutil.copy2(nova_foto_path, str(destino_foto))
                    caminho_foto_final = str(destino_foto)

            cursor.execute("""
                UPDATE infospacientes SET nome=?, idade=?, peso=?, sexo=?, profissao=?, foto=? WHERE id=?
            """, (novo_nome, idade, peso, entry_sexo.get(), entry_profissao.get(), caminho_foto_final, paciente_id))

            cursor.execute("""
                UPDATE infoscomplementares SET endereco=?, telefone=?, rg=?, cpf=?, data=? WHERE id=?
            """, (entry_complementar["endereço"].get(), entry_complementar["telefone"].get(),
                  rg_input, cpf_input, entry_complementar["data"].get() , id_complemento))

            for exame in caminhos_novos_exames:
                nome_arquivo = Path(exame).name
                destino_img = caminho_novo / nome_arquivo
                if not destino_img.exists():
                    shutil.copy2(exame, destino_img)
                cursor.execute("INSERT INTO exames (paciente_id, caminho_img) VALUES (?, ?)",
                               (paciente_id, str(destino_img)))

            conn.commit()
            messagebox.showinfo("Sucesso", "Alterações salvas com sucesso!")
            
            visualizacao.destroy()
            abrir_tela_historico()

        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar alterações: {e}")

    frame_botoes = tk.Frame(visualizacao, bg=ESTILO_BG)
    frame_botoes.place(relx=0.5, rely=0.7, anchor="center")

    tk.Button(frame_botoes, text="Abrir Exames", **ESTILO_BOTAO, width=25, command=abrir_exames).pack(pady=5)
    tk.Button(frame_botoes, text="Anexar Novos Exames", **ESTILO_BOTAO, width=25, command=anexar_novos_exames).pack(pady=5)
    tk.Button(frame_botoes, text="Abrir Controle de Pagamento", **ESTILO_BOTAO, width=25, command=abrir_pagamento).pack(pady=5)
    tk.Button(frame_botoes, text="Abrir Avaliação Física", **ESTILO_BOTAO, width=25, command=abrir_avaliacao_fisica).pack(pady=5)
    tk.Button(frame_botoes, text="Salvar Alterações", **ESTILO_BOTAO, width=25, command=salvar_alteracoes).pack(pady=10)

    frame_voltar = tk.Frame(visualizacao, bg=ESTILO_BG)
    frame_voltar.pack(side=tk.BOTTOM, anchor="w", padx=20, pady=20)

    tk.Button(frame_voltar, text="Voltar", **ESTILO_BOTAO, command=lambda: [visualizacao.destroy(), abrir_tela_historico()]).pack(anchor="w")

    visualizacao.mainloop()

# Inicia a interface de usuário.
def iniciar_interface():
    root = tk.Tk()
    root.title("BtG System")
    root.geometry("1920x1032+0+0")
    root.state("zoomed")
    root.configure(bg=ESTILO_BG)
    root.iconbitmap(resource_path("iconapplication.ico"))

    frame = tk.Frame(root, bg=ESTILO_BG)
    frame.pack(expand=True)

    btn_cadastrar = tk.Button(frame, text="CADASTRAR", width=20, pady=10, **ESTILO_BOTAO, command=lambda: abrir_tela_cadastro(root))
    btn_cadastrar.pack(pady=20)

    btn_historico = tk.Button(frame, text="HISTÓRICO", width=20, pady=10, **ESTILO_BOTAO, command=lambda: [root.destroy(), abrir_tela_historico()])
    btn_historico.pack(pady=20)

    adicionar_logo(root)
    root.mainloop()

if __name__ == "__main__":
    criar_banco()
    realizar_backup_fisio()
    iniciar_interface()