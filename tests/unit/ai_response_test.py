import pytest
from unittest.mock import patch, MagicMock
from transformers import BertTokenizer, BertModel
import torch
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import logging
import warnings
import sys
from src.assets.aux.env import env

GEMINI_API_KEY = env["GEMINI_API_KEY"]
GEMINI_MODEL_NAME = env["GEMINI_MODEL_NAME"]


from tests.config_bert_tests import (
    SIMILARITY_THRESHOLDS, 
    BERT_CONFIG, 
    SAMPLE_QUESTIONS, 
    SQL_PATTERNS,
    LOG_MESSAGES
)

# Configurações de logging, elimina logs desnecessários
logging.basicConfig(
    level=logging.INFO,
    format='🤖 %(message)s',  
    stream=sys.stdout,       
    force=True               
)

loggers_to_silence = [
    'chromadb', 'chromadb.telemetry', 'chromadb.telemetry.product',
    'chromadb.telemetry.product.posthog', 'posthog', 'transformers',
    'urllib3', 'requests', 'httpx', 'httpcore', 'asyncio',
    'google', 'google.genai', 'vanna', 'psycopg2', 'sqlalchemy',
    'torch', 'numpy', 'sklearn', 'tensorflow', 'jax'
]

for logger_name in loggers_to_silence:
    logging.getLogger(logger_name).setLevel(logging.ERROR)
    logging.getLogger(logger_name).propagate = False

logger = logging.getLogger(__name__)

@pytest.fixture(scope="module")
def vanna_instance():
    from src.api.database.MyVanna import MyVanna
    
    vn = MyVanna(config={
        'print_prompt': False, 
        'print_sql': False,
        'api_key': GEMINI_API_KEY,
        'model_name': GEMINI_MODEL_NAME
    })
    
    vn.prepare()
    logger.info("MyVanna instância criada e preparada para todos os testes")
    return vn

@pytest.fixture(scope="module")  
def gemini_client():
    from google import genai
    client = genai.Client(api_key=GEMINI_API_KEY)
    logger.info("Cliente Gemini criado para todos os testes")
    return client


class BERTResponseEvaluator:
    def __init__(self):
        try:
            self.tokenizer = BertTokenizer.from_pretrained(BERT_CONFIG['MODEL_NAME_PT'])
            self.model = BertModel.from_pretrained(BERT_CONFIG['MODEL_NAME_PT'])
            logger.info(LOG_MESSAGES['BERT_LOADED'])
        except Exception as e:
            logger.warning(f"Erro ao carregar BERT português, usando modelo inglês: {e}")
            self.tokenizer = BertTokenizer.from_pretrained(BERT_CONFIG['MODEL_NAME_EN'])
            self.model = BertModel.from_pretrained(BERT_CONFIG['MODEL_NAME_EN'])
    
    def get_embeddings(self, text):
        inputs = self.tokenizer(text, return_tensors='pt', truncate=True, 
                               padding=True, max_length=BERT_CONFIG['MAX_LENGTH'])
        
        with torch.no_grad():
            outputs = self.model(**inputs)
        
        embeddings = outputs.last_hidden_state[:, 0, :].numpy()
        return embeddings
    
    def calculate_similarity(self, text1, text2):
        logger.info(LOG_MESSAGES['SIMILARITY_CALC'])
        emb1 = self.get_embeddings(text1)
        emb2 = self.get_embeddings(text2)
        
        similarity = cosine_similarity(emb1, emb2)[0][0]
        return float(similarity)

@pytest.fixture
def bert_evaluator():
    return BERTResponseEvaluator()


@pytest.fixture
def sample_questions_and_expected():
    return [
        {
            "question": SAMPLE_QUESTIONS['ISSUES'][0],
            "sql_pattern": SQL_PATTERNS['COUNT_ISSUES'],
        },
        {
            "question": SAMPLE_QUESTIONS['REPOSITORIES'][0],
            "sql_pattern": SQL_PATTERNS['REPO_ACTIVITY'],
        },
        {
            "question": SAMPLE_QUESTIONS['USERS'][0],
            "sql_pattern": SQL_PATTERNS['ACTIVE_USERS'],
        }
    ]


class TestAIResponseQuality:    
    def test_acuracia_sql_gerado(self,vanna_instance, bert_evaluator, sample_questions_and_expected):
        from src.api.database.MyVanna import MyVanna # Importa a classe MyVanna
        
        
        for test_case in sample_questions_and_expected:
            question = test_case["question"]
            expected_sql_pattern = test_case["sql_pattern"]
            
            with patch('builtins.print'):
                generated_sql = vanna_instance.generate_sql(question)

            similarity = bert_evaluator.calculate_similarity(expected_sql_pattern, generated_sql)
            
            logger.info(f"Pergunta: {question}")
            logger.info(f"SQL gerado: {generated_sql}")
            logger.info(f"Similaridade: {similarity:.3f}")
            
            assert similarity >= SIMILARITY_THRESHOLDS['MEDIUM_QUALITY'], \
                f"SQL gerado tem baixa similaridade ({similarity:.3f}) para: {question}"
    
    def test_acuraica_resposta_gerada(self, bert_evaluator):
    
        from src.api.controller.AskController import AskController
        from src.api.models import Question
        
        test_cases = [
            {
                "question": SAMPLE_QUESTIONS['ISSUES'][0],
                "expected_response": "Existem 9 issues abertas",
            },
            {
                "question": SAMPLE_QUESTIONS['REPOSITORIES'][0],
                "expected_response": "Os repositórios com mais commits são 'nome_do_repositorio', com 84 commits, e 'nome_do_repositorio', com 21 commits",
            }
        ]
        
        with patch('builtins.print'):
            ask_controller = AskController()
        
        for test_case in test_cases:
            question_text = test_case["question"]
            expected_response = test_case["expected_response"]
            
            question = Question(question=question_text)
            
            with patch('builtins.print'):
                result = ask_controller.ask(question)
            gemini_response = result.get("output", "")
            
            similarity = bert_evaluator.calculate_similarity(
                expected_response, gemini_response
            )
            
            logger.info(f"Pergunta: {question_text}")
            logger.info(f"Resposta do AskController: {gemini_response}")
            logger.info(f"Coerência: {similarity:.3f}")
            
            assert similarity >= SIMILARITY_THRESHOLDS['COHERENCE'], \
                f"Resposta não coerente com contexto para: {question_text}"
    

if __name__ == "__main__":
    pytest.main(['-xvs', __file__])