# 💧 Gestão Água - Backend

API de gestão de análises de água, construída em **Django + Ninja** e containerizada com **Docker**.

## Executar localmente

### 1. Clone o repositório

```bash
git clone https://github.com/pedro2168/gestao_agua_backend.git
cd gestao_agua_backend
```

### 2. Instale a máquina virtual

```bash
python -m venv venv
```

Ative o ambiente virtual:

**Linux / MacOS:**
```bash
source venv/bin/activate
```

**Windows:**
```bash
source venv/Scripts/activate
```

### 3. Baixe e monte o ambiente Docker

Faça o download e instale o Docker em:  
[https://www.docker.com/](https://www.docker.com/)

Depois, execute o ambiente:

```bash
docker-compose up --build
```

### 4. Acesse a API

Após a inicialização, a API estará disponível em:

```
http://localhost:8000/api/
```

E a documentação interativa (Swagger) pode ser acessada em:

```
http://localhost:8000/api/docs
```

### 5. Parar o ambiente Docker

Para encerrar os containers, execute:

```bash
docker-compose down
```

---

### Sempre que alterar o código-fonte, você pode reconstruir a imagem com:

```bash
docker-compose up --build
```

---

 **Tecnologias principais**
- Python 3.12+
- Django + Django Ninja
- PostgreSQL
- Docker + Docker Compose

---
