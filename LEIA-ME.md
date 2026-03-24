# 🏠 House Flipper

Aplicativo desktop para acompanhar seu progresso no House Flipper.

---

## ▶ Como rodar

### Opção 1: Executável (recomendado)
Dê **duplo clique** no arquivo `house flipper.exe` na pasta `dist/`.

### Opção 2: Código fonte (requer Python)
Se preferir rodar o código fonte:

#### 1. Instale o Python
Baixe em: https://www.python.org/downloads/  
**Marque a opção "Add Python to PATH"** durante a instalação.

#### 2. Instale a dependência

Abra o Terminal (ou Prompt de Comando) e execute:

```
pip install customtkinter
```

#### 3. Execute o app

```
python app.py
```

Ou dê **duplo clique** no arquivo `app.py` (se o Python estiver configurado).

---

## 💾 Onde ficam os dados salvos?

O arquivo `progresso.db` é criado automaticamente na mesma pasta do executável.  
Seus checklists e contador de vendas ficam salvos lá — feche e abra o app à vontade.

---

## 📦 Executável

O executável `house flipper.exe` já foi gerado na pasta `dist/`.  
Para gerar novamente ou personalizar:

```
pip install pyinstaller
pyinstaller --onefile --noconsole app.py
```

---

## 🧩 Funcionalidades

- ✅ Checklists por fase com progresso visual
- 🏆 Badges de troféu em cada tarefa
- 🎮 Guia completo do Chang Choi
- 📊 Contador de vendas com barra de progresso
- 💾 Tudo salvo automaticamente no SQLite
- 🔄 Botão de reset com confirmação
