"""
Configurações para testes de qualidade da IA com BERT
Este arquivo centraliza as configurações dos testes de qualidade
"""

SIMILARITY_THRESHOLDS = {
    'HIGH_QUALITY': 0.8,      
    'MEDIUM_QUALITY': 0.6,    
    'LOW_QUALITY': 0.4,     
    'COHERENCE': 0.5          
}

# Configurações do modelo BERT
BERT_CONFIG = {
    'MODEL_NAME_PT': 'neuralmind/bert-base-portuguese-cased',  
    'MODEL_NAME_EN': 'bert-base-uncased',                      
    'MAX_LENGTH': 512,        
    'BATCH_SIZE': 1           
}


SAMPLE_QUESTIONS = {
    'ISSUES': [
        "Quantas issues estão abertas?",
        "Me mostre as issues pendentes",
        "Quais problemas não foram resolvidos?"
    ],
    'REPOSITORIES': [
        "Quais repositórios têm mais commits?",
        "Listar repositórios por atividade",
        "Repositórios mais ativos"
    ],
    'USERS': [
        "Quem são os usuários mais ativos?",
        "Desenvolvedores com mais contribuições",
        "Lista de colaboradores ativos"
    ]
}


SQL_PATTERNS = {
    'COUNT_ISSUES': "SELECT COUNT(*) FROM issues WHERE state = 'open'",
    'REPO_ACTIVITY': "SELECT repository, COUNT(*) FROM commits GROUP BY repository",
    'ACTIVE_USERS': "SELECT login FROM users ORDER BY activity DESC"
}


LOG_MESSAGES = {
    'BERT_LOADED': "Modelo BERT carregado com sucesso",
    'SIMILARITY_CALC': "Calculando similaridade semântica",
    'TEST_PASSED': "Teste de qualidade aprovado",
    'TEST_FAILED': "Teste de qualidade falhou"
}