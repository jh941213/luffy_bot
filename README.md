
# 🏴‍☠️ 루피봇 (with HyperClova X)

루피봇에 오신 것을 환영합니다! 이 프로젝트는 취업 공고를 탐색하고 다음 커리어를 준비하는 데 도움을 주기 위해 설계된 취업 지원 봇입니다. 이 봇은 HyperClova X를 활용한 자연어 처리와 기타 고급 기능을 통해 매끄러운 사용자 경험을 제공합니다.

## 목차
- [기능](#기능)
- [설치](#설치)
- [사용법](##사용법)
- [구성](##구성)
- [기여](##기여)
- [라이센스](##라이센스)
- [감사의 말](##감사의-말)

## 기능

- **문서 업로드:** PDF, Excel, Markdown 파일을 업로드하여 취업 관련 정보를 추출하고 처리할 수 있습니다.
- **채용 정보:** 외부 소스에서 채용 공고를 가져오고 요약합니다.
- **인터랙티브 채팅:** AI 비서와의 상호 작용을 통해 취업 조언과 지원 팁을 제공합니다.
- **세션 관리:** 세션 상태를 관리하고, 문서 검색을 위한 리트리버를 초기화하거나 지울 수 있습니다.

## 설치

1. **저장소 클론:**
   ```bash
   git clone https://github.com/jh941213/luffy_bot.git
   cd your-repo-name
   ```
2. **가상 환경 생성 및 활성화:**
   ```bash
   python -m venv venv
   source venv/bin/activate # Windows의 경우 venv\Scripts\activate
   ```
3. **필요한 패키지 설치:**
  ```bash
  pip install -r requirements.txt
```
4. **API 키 및 환경 변수 설정:**

.env.example 파일을 .env로 복사합니다.
HyperClova X API 키 및 기타 필요한 설정을 추가합니다.

## 사용법

