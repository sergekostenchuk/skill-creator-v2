# Skill Creator V2

Skill Creator V2는 AI skill과 skill group을 production 수준으로 만들기 위한 meta-skill입니다.

단순히 완성되어 보이는 prompt가 아니라, 문서화되고 테스트 가능하며 의존성을 명시하고 근거를 남기는 skill이 필요할 때 유용합니다.

사용 방법: npm 패키지를 설치하고 target runtime에 skill을 복사한 뒤 agent에게 skill 생성 또는 개선을 요청합니다. 이 skill은 요청을 분류하고 필요한 reference만 읽으며, tool/dependency를 검증하고 필요한 lint/eval을 실행한 뒤 readiness report를 만듭니다.

기대 결과: `SKILL.md`, references, scripts, evals, tests, 그리고 evidence-backed review가 포함된 구조화된 패키지입니다.

예시: UI Intelligence group은 얕은 reference 수집에서 live-site evidence, scroll-state screenshots, public code/font/effect metadata, originality checks, 그리고 실제 실패를 skill 개선으로 되돌리는 feedback loop로 발전했습니다.
