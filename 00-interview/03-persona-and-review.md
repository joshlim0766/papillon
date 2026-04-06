# 03-전용 페르소나 및 내부 리뷰

**상태:** Settled

## 확인된 사항
- shackled 전용 페르소나 (wtth 페르소나와 별도):
  - 코드 산출물: shackled-CODE(작성자) + shackled-BE 또는 shackled-FE(크로스 체커)
  - 런북/절차 산출물: shackled-SRE(작성자) + shackled-SEC(크로스 체커)
  - 풀스택: shackled-CODE + shackled-BE + shackled-FE
- 크로스 체커 역할: 설계서를 펴놓고 "여기 빠졌는데?", "설계서랑 다른데?" 확인
- PM 불필요: 요구사항은 inquisition에서, 설계는 리뷰에서 이미 확정된 상태
- wtth 전문가 풀과 겹치지 않음:
  - shackled: 방향 점검 (설계서 대조)
  - wtth 코드 리뷰: CODE + TEST (품질, 버그, 보안, 테스트)
  - wtth 운영 절차 리뷰: SRE + SEC (실행 안전성, 보안)
