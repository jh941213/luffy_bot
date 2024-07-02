from clova import LlmClovaStudio

from sliding_window_executor import SlidingWindowExecutor

clova_studio_llm = LlmClovaStudio(
    host='https://clovastudio.stream.ntruss.com/',
    api_key='<api_key>',
    api_key_primary_val='<api_key>',
    request_id='<reques'
)

sliding_window_executor = SlidingWindowExecutor(
    host='https://clovastudio.stream.ntruss.com/',
    api_key='<api_key>',
    api_key_primary_val='<api_key>',
    request_id='<request_id>'
)
