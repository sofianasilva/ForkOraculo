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

## Planejamento de Sprints

### Sprint 1: **Base da IA e Respostas Consistentes** (02/10/2025 -- 08/10/2025)
- **Issue:** Feature 6 - Padronização de Respostas da IA  

---

### Sprint 2: **Primeiros Recursos Inteligentes** (09/10/2025 -- 22/10/2025)
- **Issue:** Feature 3 - Memória Contextual com LangChain  
- **Issue:** Feature 4 - Geração de Gráficos e Visualização de Dados  

---

### Sprint 3: **Experiência do Usuário e Interface** (23/10/2025 -- 31/10/2025)
- **Issue:** Feature 5 - Design de Frontend e Usabilidade (UX)  

---

### Sprint 4: **Segurança e Integrações Críticas** (03/11/2025 -- 16/11/2025)
- **Issue:** Feature 1 - Autenticação de Usuário e Controle de Acesso  
- **Issue:** Feature 2 - Gerenciamento Dinâmico de Token  

---

### Sprint 5: **Estabilização e Revisão Final** (17/11/2025 -- 30/11/2025)
- **Issue:** Revisão e correção de problemas das issues realizadas anteriormente  

---

## Marcos de Grandes Entregas (Milestones)

| Data da Entrega | Sprints Inclusas | Features Entregues (Escopo) |
| :--- | :--- | :--- |
| **02/11/2025** | Sprint 1 + Sprint 2 | Funcionalidades de **Baixa e Média Complexidade** entregues: Padronização da IA (F6), Memória Contextual (F3) e Geração de Gráficos (F4). |
| **30/11/2025** | Sprint 3 + Sprint 4 + Sprint 5 | Funcionalidades de **Alta Complexidade** entregues: Design de Frontend e Usabilidade (F5), Autenticação/Controle de Acesso (F1) e Gerenciamento Dinâmico de Token (F2). Além disso, inclui o período de estabilização e revisão final (Sprint 5). |
