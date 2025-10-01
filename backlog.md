## Backlog de Features 

### Feature 1: Autenticação de Usuário e Controle de Acesso

- **Descrição (PT):** Desenvolvimento completo do subsistema de autenticação. Deve incluir **Registro** e **Login** seguro de usuários. Implementação de **Controle de Acesso (ACL)** para que cada usuário possa **apenas visualizar e gerenciar seus próprios repositórios e dados**. Este é o alicerce de segurança do sistema.
- **Prioridade:** Alta (Essencial para segurança e personalização)
- **Estimativa de Complexidade:** Alta
- **Status:** To Do

---

### Feature 2: Gerenciamento Dinâmico de Token

- **Descrição (PT):** Criação de uma funcionalidade direta na interface do usuário (UI) que permita ao usuário **inserir, visualizar (parcialmente) e atualizar o token de acesso** ao repositório (ex: GitHub Token). Essa gestão deve ser feita de forma segura e imediata, **eliminando a necessidade de configuração manual em arquivos** ou no backend.
- **Prioridade:** Média
- **Estimativa de Complexidade:** Baixa
- **Status:** To Do

---

### Feature 3: Memória Contextual com LangChain

- **Descrição (PT):** Implementação de uma **camada de memória** nas interações com a IA, utilizando a biblioteca **LangChain**. O objetivo é que a IA consiga **lembrar e referenciar informações de interações anteriores** na mesma conversa, permitindo um fluxo de diálogo contínuo, coerente e com contexto mantido.
- **Prioridade:** Alta (Core do valor da IA)
- **Estimativa de Complexidade:** Alta
- **Status:** To Do

---

### Feature 5: Geração de Gráficos e Visualização de Dados

- **Descrição (PT):** Capacidade de o sistema **responder a interações do usuário gerando gráficos (charts)**. Deve ser integrada a bibliotecas de visualização (ex: Matplotlib/Pandas) para renderizar e exibir dados estruturados de forma visual e analítica diretamente na interface do chat.
- **Prioridade:** Média
- **Estimativa de Complexidade:** Média
- **Status:** To Do

---

### Feature 6: Design de Frontend e Usabilidade (UX)

- **Descrição (PT):** Criação e implementação de uma **Interface de Usuário (UI) responsiva** e moderna, garantindo excelente experiência em desktop e dispositivos móveis. **Melhoria da UX** para que a aplicação (especialmente containers Docker) possa ser iniciada com **mínima ou nenhuma configuração manual**.
- **Prioridade:** Média
- **Estimativa de Complexidade:** Média
- **Status:** To Do

---

### Feature 7: Padronização de Respostas da IA

- **Descrição (PT):** Definição e implementação de um **sistema de controle de parâmetros** (como 'temperature', 'top\_p' e 'estilo/formato de saída') para garantir que as respostas da IA sejam **consistentes, previsíveis e adequadas ao contexto técnico**. Isso garante a confiabilidade das respostas.
- **Prioridade:** Baixa
- **Estimativa de Complexidade:** Baixa
- **Status:** To Do

---

## Planejamento de Sprints

### Sprint 1: Kickoff e Entregas Rápidas (01/10/2025 -- 07/10/2025)

*Foco na configuração inicial e entrega das funcionalidades mais simples (Baixa Complexidade).*

- **Issue:** Feature 7 - Padronização de Respostas da IA
- **Issue:** Feature 2 - Gerenciamento Dinâmico de Token

---

### Sprint 2: Interface Inicial e Usabilidade (08/10/2025 -- 21/10/2025)

*Foco na primeira parte do Frontend e na melhoria da experiência de uso inicial.*

- **Issue:** Feature 6 (Parte 1) - Implementação da UI Responsiva e Estrutura Básica do Frontend

---

### Sprint 3: Fechamento da Entrega 1 (22/10/2025 -- 31/10/2025)

*Foco na entrega de valor analítico e na conclusão da UX. **Garante a conclusão antes de 02/11/2025.***

- **Issue:** Feature 5 - Geração de Gráficos e Visualização de Dados
- **Issue:** Feature 6 (Parte 2) - Configuração de Containers Prontos para Uso

---

### Sprint 4: O Core da IA - Memória (03/11/2025 -- 16/11/2025)

*Foco na feature mais importante para a qualidade das conversas da IA (Alta Complexidade).*

- **Issue:** Feature 3 - Memória Contextual com LangChain

---

### Sprint 5: Segurança e Personalização (17/11/2025 -- 30/11/2025)

*Foco na conclusão do projeto com a entrega da funcionalidade de segurança e personalização. **Garante a conclusão na data de 30/11/2025.***

- **Issue:** Feature 1 - Autenticação de Usuário e Controle de Acesso

---

## Marcos de Grandes Entregas (Milestones)

Esta seção resume o que será entregue em cada um dos marcos cruciais do projeto:

| Data da Entrega | Sprint de Conclusão | Features Entregues (Escopo) |
| :--- | :--- | :--- |
| **02/11/2025** | Sprint 3 | Todas as funcionalidades de **Baixa e Média Complexidade** e a **Estrutura Básica do Produto** estarão prontas. Isso inclui: Padronização da IA (F7), Gerenciamento de Token (F2), UI Responsiva (F6-p1), Geração de Gráficos (F5) e Containers Prontos (F6-p2). |
| **30/11/2025** | Sprint 5 | O **Produto Completo** será entregue. As funcionalidades de **Alta Complexidade** estarão finalizadas, incluindo: Memória Contextual (F3) e Autenticação/Controle de Acesso (F1). |
