-- Garante que o script pare se houver um erro
\set ON_ERROR_STOP on

-- Drop tables if they exist to allow for clean recreation
-- A ordem de drop é importante devido às dependências de chaves estrangeiras
---

DROP TABLE IF EXISTS parents_commits CASCADE;
DROP TABLE IF EXISTS commits CASCADE;
DROP TABLE IF EXISTS branch CASCADE;
DROP TABLE IF EXISTS pull_request_assignees CASCADE; -- Nova tabela
DROP TABLE IF EXISTS issue_assignees CASCADE;       -- Nova tabela
DROP TABLE IF EXISTS pull_requests CASCADE;
DROP TABLE IF EXISTS issue CASCADE;
DROP TABLE IF EXISTS milestone CASCADE;             -- Nova tabela
DROP TABLE IF EXISTS repository CASCADE;
DROP TABLE IF EXISTS "user" CASCADE;                -- "user" é uma palavra reservada, então aspas duplas são usadas

---

-- Table: user
-- Armazena informações sobre usuários
CREATE TABLE "user" (
    id BIGSERIAL PRIMARY KEY, -- ID auto-incrementável para a tabela de usuários
    login VARCHAR(255) UNIQUE NOT NULL, -- Login do usuário (e.g., username do GitHub), deve ser único
    html_url TEXT NOT NULL -- Link para o perfil do usuário (TEXT para URLs longas)
);

---

-- Table: repository
-- Armazena informações sobre repositórios
CREATE TABLE repository (
    id SERIAL PRIMARY KEY, -- ID auto-incrementável para a tabela de repositórios
    name VARCHAR(255) UNIQUE NOT NULL -- Nome do repositório, deve ser único
);

---

-- Table: milestone
-- Armazena informações sobre milestones
CREATE TABLE milestone (
    id BIGSERIAL PRIMARY KEY, -- ID auto-incrementável para a tabela de milestones
    repository_id INTEGER NOT NULL, -- Chave estrangeira para o repositório da milestone (INTEGER, não SERIAL)
    title TEXT NOT NULL,    -- Título da milestone
    description TEXT,       -- Corpo/descrição da milestone (pode ser nulo)
    number INTEGER NOT NULL, -- Número da milestone (único por repositório)
    state VARCHAR(50) NOT NULL, -- Estado da milestone (e.g., 'open', 'closed')
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP, -- Data e hora de criação com fuso horário
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP, -- Data e hora da última atualização com fuso horário
    creator BIGINT NOT NULL, -- ID do usuário que criou a milestone (INTEGER, não SERIAL)

    CONSTRAINT fk_milestone_creator
        FOREIGN KEY (creator) -- Referencia a coluna 'creator' que você definiu
        REFERENCES "user" (id)
        ON DELETE CASCADE,
    CONSTRAINT fk_milestone_repository
        FOREIGN KEY (repository_id)
        REFERENCES repository (id)
        ON DELETE CASCADE,
    CONSTRAINT unq_milestone_number_repo_id UNIQUE (number, repository_id) -- Garante que o número da milestone seja único por repositório
); -- REMOVIDA VÍRGULA EXTRA AQUI

---

-- Table: issue
-- Armazena informações sobre issues (problemas/tarefas)
CREATE TABLE issue (
    id BIGSERIAL PRIMARY KEY, -- ID auto-incrementável para a tabela de issues
    title TEXT NOT NULL,    -- Título da issue
    body TEXT,              -- Corpo/descrição da issue (pode ser nulo)
    number INTEGER NOT NULL, -- Número da issue (único por repositório)
    html_url TEXT,               -- URL da issue (TEXT para URLs longas)
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP, -- Data e hora de criação com fuso horário
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP, -- Data e hora da última atualização com fuso horário
    -- REMOVIDA: assignees SERIAL -- Esta coluna não é necessária se você tem issue_assignees
    created_by BIGINT NOT NULL, -- Chave estrangeira de quem criou a issue (INTEGER, não SERIAL)
    repository_id BIGINT NOT NULL, -- Chave estrangeira para o repositório ao qual a issue pertence (INTEGER, não SERIAL)
    milestone_id BIGINT, -- Chave estrangeira para a milestone a qual a issue pertence (INTEGER, não SERIAL, pode ser nulo)

    CONSTRAINT fk_issue_created_by_user -- Nome mais específico para a FK do criador
        FOREIGN KEY (created_by)
        REFERENCES "user" (id)
        ON DELETE CASCADE,
    CONSTRAINT fk_issue_repository
        FOREIGN KEY (repository_id)
        REFERENCES repository (id)
        ON DELETE CASCADE,
    CONSTRAINT fk_issue_milestone
        FOREIGN KEY (milestone_id)
        REFERENCES milestone (id) -- Referencia a nova tabela milestone
        ON DELETE SET NULL, -- Se a milestone for excluída, a issue permanece, mas o link é removido
    CONSTRAINT unq_issue_number_repo_id UNIQUE (number, repository_id) -- Garante que o número da issue seja único por repositório
);

---

-- Table: pull_requests
-- Armazena informações sobre pull requests
CREATE TABLE pull_requests (
    id BIGSERIAL PRIMARY KEY, -- ID auto-incrementável para a tabela de pull requests
    created_by BIGINT NOT NULL,    -- Chave estrangeira para o usuário que criou o PR (INTEGER, não SERIAL)
    repository_id INTEGER NOT NULL, -- Chave estrangeira para o repositório ao qual o PR pertence (INTEGER, não SERIAL)
    number INTEGER NOT NULL,        -- Número do pull request (único por repositório)
    state VARCHAR(50) NOT NULL,     -- Estado do PR (e.g., 'open', 'closed', 'merged')
    title TEXT NOT NULL,            -- Título do pull request
    body TEXT,                      -- Corpo/descrição do pull request (pode ser nulo)
    html_url TEXT NOT NULL,         -- URL do pull request (TEXT para URLs longas)
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP, -- Data e hora de criação com fuso horário
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP, -- Data e hora da última atualização com fuso horário
    milestone_id BIGINT, -- Chave estrangeira para a milestone a qual a issue pertence (INTEGER, não SERIAL, pode ser nulo)

    CONSTRAINT fk_pr_created_by_user -- Nome mais específico para a FK do criador
        FOREIGN KEY (created_by)
        REFERENCES "user" (id)
        ON DELETE CASCADE,
    CONSTRAINT fk_pr_repository
        FOREIGN KEY (repository_id)
        REFERENCES repository (id)
        ON DELETE CASCADE,
    CONSTRAINT fk_pr_milestone
        FOREIGN KEY (milestone_id)
        REFERENCES milestone (id) -- Referencia a nova tabela milestone
        ON DELETE SET NULL, -- Se a milestone for excluída, a issue permanece, mas o link é removido
    CONSTRAINT unq_pr_number_repo_id UNIQUE (number, repository_id) -- Garante que o número do PR seja único por repositório
);

---

-- Table: branch
-- Armazena informações sobre branches de repositórios
CREATE TABLE branch (
    id BIGSERIAL PRIMARY KEY, -- ID auto-incrementável para a tabela de branches
    name VARCHAR(255) NOT NULL,     -- Nome da branch (e.g., 'main', 'dev')
    repository_id INTEGER NOT NULL, -- Chave estrangeira para o repositório ao qual a branch pertence

    CONSTRAINT fk_branch_repository
        FOREIGN KEY (repository_id)
        REFERENCES repository (id)
        ON DELETE CASCADE,
    CONSTRAINT unq_branch_name_repo_id UNIQUE (name, repository_id) -- Garante que o nome da branch seja único por repositório
);

---

-- Table: commits
-- Armazena informações sobre commits
CREATE TABLE commits (
    id BIGSERIAL PRIMARY KEY, -- ID auto-incrementável para a tabela de commits
    user_id BIGINT NOT NULL,      -- Chave estrangeira para o usuário que fez o commit
    branch_id INTEGER,             -- Chave estrangeira para a branch à qual o commit pertence (pode ser nulo se o commit não estiver associado a uma branch específica ou for órfão)
    pull_request_id BIGINT, -- Chave estrangeira para o repositório ao qual o commit pertence
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP, -- Data e hora de criação do commit
    message TEXT NOT NULL,          -- Mensagem do commit
    sha VARCHAR(40) UNIQUE NOT NULL, -- SHA do commit (hash, geralmente 40 caracteres para Git), deve ser único
    html_url TEXT,                       -- URL do commit (TEXT para URLs longas)

    CONSTRAINT fk_commit_user
        FOREIGN KEY (user_id)
        REFERENCES "user" (id)
        ON DELETE CASCADE,
    CONSTRAINT fk_commit_branch
        FOREIGN KEY (branch_id)
        REFERENCES branch (id)
        ON DELETE SET NULL, -- Se a branch for excluída, o commit não é excluído, mas branch_id se torna NULL
    CONSTRAINT fk_commit_pull_request
        FOREIGN KEY (pull_request_id)
        REFERENCES pull_requests (id)
        ON DELETE CASCADE,
    CONSTRAINT unq_commit_sha_pull_request_id UNIQUE (sha, pull_request_id) -- Garante que o SHA do commit seja único por pr
);

---

-- Table: parents_commits
-- Tabela de junção para armazenar as relações pai-filho entre commits (um commit pode ter múltiplos pais)
CREATE TABLE parents_commits (
    id SERIAL PRIMARY KEY,    -- ID auto-incrementável para a tabela de junção
    parent_sha VARCHAR(40) NOT NULL, -- SHA do commit pai
    commit_id INTEGER NOT NULL,      -- Chave estrangeira para o commit filho

    -- Não estamos usando parent_sha como FK para a tabela commits diretamente,
    -- pois isso implicaria que todo parent_sha precisa ser um commit existente no DB.
    -- Em alguns casos, pode-se querer armazenar parent_sha que ainda não foram inseridos como commits completos.
    -- Se você quiser garantir que parent_sha SEMPRE exista na tabela commits, adicione:
    -- CONSTRAINT fk_parent_commit_sha FOREIGN KEY (parent_sha) REFERENCES commits (sha) ON DELETE CASCADE,

    CONSTRAINT fk_pc_commit_id
        FOREIGN KEY (commit_id)
        REFERENCES commits (id)
        ON DELETE CASCADE, -- Se o commit filho for excluído, suas relações de pais também são
    CONSTRAINT unq_pc_parent_commit UNIQUE (parent_sha, commit_id) -- Garante que a relação pai-filho é única
);

---

-- Table: issue_assignees
-- Armazena usuários vinculados às issues (tabela de junção)
CREATE TABLE issue_assignees (
    issue_id BIGINT NOT NULL, -- INTEGER, não SERIAL para FKs
    user_id BIGINT NOT NULL,  -- INTEGER, não SERIAL para FKs
    PRIMARY KEY (issue_id, user_id), -- Chave primária composta para garantir unicidade da atribuição

    CONSTRAINT fk_ia_issue
        FOREIGN KEY (issue_id)
        REFERENCES issue (id)
        ON DELETE CASCADE, -- Se a issue for excluída, suas atribuições também são
    CONSTRAINT fk_ia_user
        FOREIGN KEY (user_id)
        REFERENCES "user" (id)
        ON DELETE CASCADE  -- Se o usuário for excluído, suas atribuições a issues também são
);

---

-- Table: pull_request_assignees
-- Armazena informações sobre usuários vinculados a pull requests (tabela de junção)
CREATE TABLE pull_request_assignees (
    pull_request_id BIGINT NOT NULL,
    user_id BIGINT NOT NULL,

    PRIMARY KEY (pull_request_id, user_id),
    CONSTRAINT fk_pra_pull_request
        FOREIGN KEY (pull_request_id)
        REFERENCES pull_requests (id)
        ON DELETE CASCADE,
    CONSTRAINT fk_pra_user
        FOREIGN KEY (user_id)
        REFERENCES "user" (id)
        ON DELETE CASCADE
);