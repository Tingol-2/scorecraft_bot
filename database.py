import os
import ydb

YDB_ENDPOINT = os.getenv("YDB_ENDPOINT")
YDB_DATABASE = os.getenv("YDB_DATABASE")

def get_ydb_pool(ydb_endpoint, ydb_database, timeout=30):
    ydb_driver_config = ydb.DriverConfig(
        ydb_endpoint,
        ydb_database,
        credentials=ydb.credentials_from_env_variables(),
        root_certificates=ydb.load_ydb_root_certificate(),
    )

    ydb_driver = ydb.Driver(ydb_driver_config)
    ydb_driver.wait(fail_fast=True, timeout=timeout)
    return ydb.SessionPool(ydb_driver)


def _format_kwargs(kwargs):
    return {"${}".format(key): value for key, value in kwargs.items()}


# Заготовки из документации
# https://ydb.tech/en/docs/reference/ydb-sdk/example/python/#param-prepared-queries
def execute_update_query(pool, query, **kwargs):
    def callee(session):
        prepared_query = session.prepare(query)
        session.transaction(ydb.SerializableReadWrite()).execute(
            prepared_query, _format_kwargs(kwargs), commit_tx=True
        )

    return pool.retry_operation_sync(callee)


# Заготовки из документации
# https://ydb.tech/en/docs/reference/ydb-sdk/example/python/#param-prepared-queries
def execute_select_query(pool, query, **kwargs):
    def callee(session):
        prepared_query = session.prepare(query)
        result_sets = session.transaction(ydb.SerializableReadWrite()).execute(
            prepared_query, _format_kwargs(kwargs), commit_tx=True
        )
        return result_sets[0].rows

    return pool.retry_operation_sync(callee)    

# Зададим настройки базы данных 
pool = get_ydb_pool(YDB_ENDPOINT, YDB_DATABASE)


# Структура квиза

questions = {
    '1' : ('Что тебе интересно?',['1a','1b','1c','1d']),
    '2' : ('куда поступаешь?', ['2a','2b','2c','2d','2e']),
    '3' : ('какое направление?', ['3a','3b','3c','3d']),
    '4' : ('получал ли образование на англ языке?', ['4a','4b']),
    '5' : ('получал ли образование на англ?', ['5a','5b']),
    '6' : ('в какой стране?',['6a','6b','6c']),
    '7' : ('тебе нужно сдать GRE и языковые тесты', ['7a','7b','7c']),
    '8' : ('Что хочешь узнать?', ['8a','8b','8c']),
    '100': ('Выбери тест', ['100a','100b']),
    '100m': ('math', []),
    '100v': ('verbal', []),
     }

answers = {
    '1a' : 'учеба',
    '1b' : 'работа',
    '1c' : 'переезд',
    '1d' : 'саморазвитие',
    '2a' : 'магистратура',
    '2b' : 'phd',
    '2c' : 'mba',
    '2d' : 'EMBA',
    '2e' : 'бакалавриат',   
    '3a' : 'финансы/экономика',
    '3b': 'естественные науки/STEM',
    '3c': 'гуманитарные науки',
    '3d': 'art/design',
    '4a' : 'да',
    '4b' : 'нет',
    '5a' : 'да',
    '5b' : 'нет',
    '6a' : 'США',
    '6b' : 'UK',
    '6c' : 'другое',
    '7a' : 'Узнать какой языковой тест выбрать',
    '7b' : 'Узнать  больше про GRE',
    '7c' : 'узнать про документы для поступления',
    '8a' : 'пройти диагностику',
    '8b' : 'узнать про формат',
    '8c' : 'узнать про подготовку',  
    '100a' : 'math',
    '100b' : 'verbal' 
    
}

tree = {k:'-1' for k in answers.keys()}
tree['1a'] = '2'
tree['2a'] = '3'
tree['2c'] = '4'
tree['2d'] = '5'
tree['2e'] = '6'
tree['3b'] = '7'
tree['7b'] = '8'
tree['8a'] = '100'
tree['100a'] = '100m'
tree['100b'] = '100v'

quiz_math = [
    {
        'question': '7+7',
        'options': ['49', '65', '33', '76'],
        'correct_option': 0
    },
    {
        'question': '5!',
        'options': ['44', '120', '55', '-1'],
        'correct_option': 1
    },
    {
        'question': '7+7',
        'options': ['49', '65', '33', '76'],
        'correct_option': 0
    },
    {
        'question': '5!',
        'options': ['44', '120', '55', '-1'],
        'correct_option': 1
    },
    {
        'question': '7+7',
        'options': ['49', '65', '33', '76'],
        'correct_option': 0
    },
    {
        'question': '5!',
        'options': ['44', '120', '55', '-1'],
        'correct_option': 1
    },
    {
        'question': '7+7',
        'options': ['49', '65', '33', '76'],
        'correct_option': 0
    },
    {
        'question': '5!',
        'options': ['44', '120', '55', '-1'],
        'correct_option': 1
    },
    # Добавьте другие вопросы
]

quiz_verbal = [
    {
        'question': 'Hell_?',
        'options': ['o', 'w', 'ow', 'e'],
        'correct_option': 0
    },
    {
        'question': 'He ha_?',
        'options': ['ve', 's', 't', 'ds'],
        'correct_option': 1
    },
     {
        'question': 'Hell_?',
        'options': ['o', 'w', 'ow', 'e'],
        'correct_option': 0
    },
    {
        'question': 'He ha_?',
        'options': ['ve', 's', 't', 'ds'],
        'correct_option': 1
    },
     {
        'question': 'Hell_?',
        'options': ['o', 'w', 'ow', 'e'],
        'correct_option': 0
    },
    {
        'question': 'He ha_?',
        'options': ['ve', 's', 't', 'ds'],
        'correct_option': 1
    },
     {
        'question': 'Hell_?',
        'options': ['o', 'w', 'ow', 'e'],
        'correct_option': 0
    },
    {
        'question': 'He ha_?',
        'options': ['ve', 's', 't', 'ds'],
        'correct_option': 1
    }
    # Добавьте другие вопросы
]

quizes = {'math':quiz_math, 'verbal' : quiz_verbal}

quizes_indexes = ['100m', '100v']
