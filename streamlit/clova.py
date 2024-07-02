from typing import Any, List, Mapping, Optional
from langchain.callbacks.manager import CallbackManagerForLLMRun
from langchain_core.language_models.llms import LLM
import json
import requests

class LlmClovaStudio(LLM):
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
        # 지시사항 
        - 당신은 취업지원을 도와주는 비서 해적왕 루피입니다. 도전적이고 희망찬 말들로 사용자에게 도움을 주세요.
        - #정보에는 사용자에 대한 정보가 포함되어있고, #채용공고 에는 채용공고에 대한 정보가 포함되어 있습니다 이를 토대로 질문에 답변하세요.
        - 이력에 관한 질문이 아니라면, 정보를 무시하고 답변하세요.
        '''

        preset_text = [{"role": "system", "content": sys_prompt}, {"role": "user", "content": prompt}]

        request_data = {
            "messages": preset_text,
            "topP": 0.9,
            "topK": 0,
            "maxTokens": 1024,
            "temperature": 0.1,
            "repeatPenalty": 1.2,
            "stopBefore": [],
            "includeAiFilters": False
        }

        response = requests.post(
            self.host + "your host link",  # 본인 튜닝 API 경로 사용도 가능 test App 에서
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
