import asyncio
import nest_asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
from clova import LlmClovaStudio
import time
from get_jobs import get_job_postings
from typing import Any, List, Mapping, Optional
from langchain.callbacks.manager import CallbackManagerForLLMRun
from langchain_core.language_models.llms import LLM
import json
import requests

class ClovaBase(LLM):
    """
    Custom LLM class for using the ClovaStudio API.
    """
    host: str
    api_key: str
    api_key_primary_val: str
    request_id: str

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.host = kwargs.get('host')
        self.api_key = kwargs.get('api_key')
        self.api_key_primary_val = kwargs.get('api_key_primary_val')
        self.request_id = kwargs.get('request_id')

    @property
    def _llm_type(self) -> str:
        return "custom"

    def _call(self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None
    ) -> str:
        """
        Make an API call to the ClovaStudio endpoint using the specified 
        prompt and return the response.
        """
        if stop is not None:
            raise ValueError("stop kwargs are not permitted.")

        headers = {
            "X-NCP-CLOVASTUDIO-API-KEY": self.api_key,
            "X-NCP-APIGW-API-KEY": self.api_key_primary_val,
            "X-NCP-CLOVASTUDIO-REQUEST-ID": self.request_id,
            "Content-Type": "application/json; charset=utf-8",
            "Accept": "text/event-stream"
        }
        sys_prompt = '''

        # 지시사항 :
        - 당신은 취업공고를 읽고, 그 정보를 요약해야 합니다. \n
        - 결과는 다음과 같이 example 형식에 맞게 출력하세요. \n
        # example :
        회사명 :
        제목 :
        포지션 :
        위치 :
        마감일 :
        지원자격 :
        우대사항 :

        반드시 example 형식에 맞게 출력하세요.

        '''
        preset_text = [{"role": "system", "content": sys_prompt}, {"role": "user", "content": prompt}]

        request_data = {
            "messages": preset_text,
            "topP": 0.9,
            "topK": 0,
            "maxTokens": 4096,
            "temperature": 0.1,
            "repeatPenalty": 1.2,
            "stopBefore": [],
            "includeAiFilters": False
        }

        response = requests.post(
            self.host + '/testapp/v1/chat-completions/HCX-003',  # 본인 튜닝 API 경로 사용도 가능 test App 에서
            headers=headers,
            json=request_data,
            stream=True
        )

        # 스트림에서 마지막 'data:' 라인을 찾기 위한 로직
        last_data_content = ""

        for line in response.iter_lines():
            if line:
                decoded_line = line.decode("utf-8")
                if '"data":"[DONE]"' in decoded_line:
                    break
                if decoded_line.startswith("data:"):
                    last_data_content = json.loads(decoded_line[5:])["message"]["content"]

        return last_data_content 

def get_job_summary(data):
    clova_base_llm = ClovaBase(
    host='https://clovastudio.stream.ntruss.com',
        api_key='<api_key>',
        api_key_primary_val='<api_key>',
        request_id='<request_id>'
    )
    response_data = []
    for index, posting in enumerate(data[:5], start=1):  # 처음 5개의 포스팅만 처리
        try:
            formatted_posting = f'''- {posting['title']} | {posting['company']} | {posting['location']} | {posting['recruitment_period']}\n{posting['content']}
            \n 답변 :
            '''
            
            response = clova_base_llm._call(formatted_posting)
            response_data.append(f"{index}번째 회사: {response}")
            print(f"{index}번째  {response}")
            time.sleep(3)
        except Exception as e:
            print(f"Error processing {index}번째 회사: {str(e)}")
            print(f"Error details: {posting}")
    return response_data

