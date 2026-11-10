from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import google.generativeai as genai
import os

app = FastAPI()

# CORS 설정 (어떤 도메인에서도 챗봇이 요청할 수 있도록 허용)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Google Gemini API 설정 (본인의 API 키 입력 또는 환경변수 연동)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyD6XS_vxBFq8y-M_fx24VNjNHNaKJcILa0")
genai.configure(api_key=GEMINI_API_KEY)

# 안정적인 모델 지정
model = genai.GenerativeModel("gemini-1.5-flash")

@app.post("/api/chat")
async def chat_proxy(request: Request):
    try:
        body = await request.json()
        prompt = body.get("prompt", "").strip()
        mode = body.get("mode", "sales")
        tel = body.get("tel", "010-2585-7349")
        
        if not prompt:
            return {"text": "궁금하신 내용을 입력해 주세요."}

        # 업종별 맞춤 페르소나 정의
        sector_names = {
            "sales": "종합 세일즈 컨설턴트",
            "hospital": "병원·의원 전문 상담 실장",
            "pension": "펜션·숙박 전문 매니저",
            "food": "음식점·카페 단체예약 캡틴",
            "academy": "학원·교육기관 수석 컨설턴트",
            "estate": "부동산 전문 공인중개 컨설턴트",
            "business": "기업 경영전략 수석 파트너",
            "partner": "전국 비즈니스 파트너십 총괄"
        }
        
        role_name = sector_names.get(mode, "수석 컨설턴트")

        # Gemini AI에게 전달할 프롬프트 구성
        system_prompt = f"""
        당신은 미라지 AI(지속가능경영연구원)의 '{role_name}'입니다. (공식 직통전화: {tel})
        고객의 질문: "{prompt}"
        
        [지침]:
        1. 질문의 핵심 의도를 정확히 파악하여 2~3문장으로 친절하고 전문적인 답변을 작성하십시오.
        2. 환각(거짓 정보)을 만들지 말고, 신뢰도 높은 비즈니스/매장 안내 톤을 유지하십시오.
        3. 답변 마지막에는 반드시 공식 직통전화({tel}) 또는 [실시간 예약]으로 상담을 유도하십시오.
        """

        # Gemini AI 호출 (파이썬 환경이므로 타임아웃 없이 안전하게 작동)
        response = model.generate_content(
            system_prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.2,
                max_output_tokens=400
            )
        )
        
        answer = response.text.strip()
        return {"text": answer}

    except Exception as e:
        # 장애 발생 시 안전한 Fallback 텍스트 반환
        fallback_msg = f"문의하신 내용에 대해 1:1 맞춤 안내를 도와드립니다. 상세 일정 및 상담 문의는 직통전화({tel})로 연락 주시기 바랍니다."
        return {"text": fallback_msg}

@app.get("/")
async def root():
    return {"status": "Mirage AI Backend is running successfully."}
@app.get("/")
async def root():
    return {"status": "Mirage AI Backend is running successfully."}

# 이 부분을 코드 맨 아래에 추가하세요!
if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)