## Backlog de Features 

### Feature 1: Autenticação de Usuário e Controle de Acesso
- **Descrição (PT):** Desenvolvimento completo do subsistema de autenticação. Deve incluir **Registro** e **Login** seguro de usuários. Implementação de **Controle de Acesso (ACL)** para que cada usuário possa **apenas visualizar e gerenciar seus próprios repositórios e dados**. Este é o alicerce de segurança do sistema.
- **Prioridade:** Alta
- **Estimativa de Complexidade:** Alta
- **Status:** To Do

---

### Feature 2: Gerenciamento Dinâmico de Token
- **Descrição (PT):** Criação de uma funcionalidade direta na interface do usuário (UI) que permita ao usuário **inserir, visualizar (parcialmente) e atualizar o token de acesso** ao repositório (ex: GitHub Token). Essa gestão deve ser feita de forma segura e imediata, **eliminando a necessidade de configuração manual em arquivos** ou no backend.
- **Prioridade:** Média
- **Estimativa de Complexidade:** Alta
- **Status:** To Do

---

### Feature 3: Memória Contextual com LangChain
- **Descrição (PT):** Implementação de uma **camada de memória** nas interações com a IA, utilizando a biblioteca **LangChain**. O objetivo é que a IA consiga **lembrar e referenciar informações de interações anteriores** na mesma conversa, permitindo um fluxo de diálogo contínuo, coerente e com contexto mantido.
- **Prioridade:** Alta
- **Estimativa de Complexidade:** Média
- **Status:** To Do

---

### Feature 4: Geração de Gráficos e Visualização de Dados
- **Descrição (PT):** Capacidade de o sistema **responder a interações do usuário gerando gráficos (charts)**. Deve ser integrada a bibliotecas de visualização (ex: Matplotlib/Pandas) para renderizar e exibir dados estruturados de forma visual e analítica diretamente na interface do chat.
- **Prioridade:** Média
- **Estimativa de Complexidade:** Média
- **Status:** To Do

---

### Feature 5: Design de Frontend e Usabilidade (UX)
- **Descrição (PT):** Criação e implementação de uma **Interface de Usuário (UI) responsiva** e moderna, garantindo excelente experiência em desktop e dispositivos móveis. **Melhoria da UX** para que a aplicação (especialmente containers Docker) possa ser iniciada com **mínima ou nenhuma configuração manual**.
- **Prioridade:** Média
- **Estimativa de Complexidade:** Baixa
- **Status:** To Do

---

### Feature 6: Padronização de Respostas da IA
- **Descrição (PT):** Definição e implementação de um **sistema de controle de parâmetros** (como 'temperature', 'top_p' e 'estilo/formato de saída') para garantir que as respostas da IA sejam **consistentes, previsíveis e adequadas ao contexto técnico**. Isso garante a confiabilidade das respostas.
- **Prioridade:** Baixa
- **Estimativa de Complexidade:** Baixa
- **Status:** To Do

---

## Planejamento de Sprints (1 semana cada)

### Sprint 1: **Memória Inicial com LangChain** (02/10/2025 -- 08/10/2025)
- **Issue:** Feature 3 - Memória Contextual com LangChain  

---

### Sprint 2: **Visualização e Gráficos** (09/10/2025 -- 15/10/2025)
- **Issue:** Feature 4 - Geração de Gráficos e Visualização de Dados  

---

### Sprint 3: **Padronização da IA - Parte 1** (16/10/2025 -- 22/10/2025)
- **Issue:** Feature 6 - Padronização de Respostas da IA (início)  

---

### Sprint 4: **Interface e UX** (23/10/2025 -- 29/10/2025)
- **Issue:** Feature 5 - Design de Frontend e Usabilidade (UX)  

---

### Sprint 5: **Autenticação Segura** (30/10/2025 -- 05/11/2025)
- **Issue:** Feature 1 - Autenticação de Usuário e Controle de Acesso  

---

### Sprint 6: **Gerenciamento de Token - Parte 1** (06/11/2025 -- 12/11/2025)
- **Issue:** Feature 2 - Gerenciamento Dinâmico de Token (início)  

---

### Sprint 7: **Gerenciamento de Token - Parte 2** (13/11/2025 -- 19/11/2025)
- **Issue:** Feature 2 - Gerenciamento Dinâmico de Token (finalização)  

---

### Sprint 8: **Estabilização e Revisão Final** (20/11/2025 -- 30/11/2025)
- **Issue:** Revisão e correção de problemas das issues realizadas anteriormente  

---

## Marcos de Grandes Entregas (Milestones)

| Data da Entrega | Sprints Inclusas | Features Entregues (Escopo) |
| :--- | :--- | :--- |
| **02/11/2025** | Sprint 1 + Sprint 2 + Sprint 3 | Funcionalidades iniciais entregues: Memória Contextual (F3), Geração de Gráficos (F4) e Padronização da IA - Parte 1 (F6). |
| **30/11/2025** | Sprint 4 + Sprint 5 + Sprint 6 + Sprint 7 + Sprint 8 | Funcionalidades finais entregues: Design de Frontend e Usabilidade (F5), Autenticação/Controle de Acesso (F1), Gerenciamento Dinâmico de Token (F2), e Estabilização/Revisão Final. |
