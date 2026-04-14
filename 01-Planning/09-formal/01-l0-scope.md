# 01-l0-scope: 단일 LLM 호출의 수학적 정의 — 스코프 선언

## Context
- **Parent:** [00-index.md](./00-index.md)
- **Related:** ASEWS `docs/modeling/00-index.md` (대응되는 상위 스택의 기반 문서)
- **Status:**
  - Work: Draft
  - Review: None

---

## 1. 목적

L0은 **단일 LLM 호출**을 수학적으로 정의한다. 이 층위는 주장(theorem)보다는 **정의(definition)와 표기 규약**에 가깝다. L1 이후 모든 층위가 L0의 정의 위에 쌓인다.

L0이 달성해야 할 것은 한 가지다: **"빠삐용 안에서 LLM 호출을 수학적으로 말하려면 무엇을 무엇이라고 부를 것인가"** 를 합의하는 것.

---

## 2. 기본 모델

먼저 기본 객체를 정의한다.

- **Prompt (`x`)**: 호출자가 명시적으로 제공하는 구조화된 입력. system prompt, user message 등.
- **Context (`c`)**: 호출 시점에 모델이 참조하는 부가 입력. 대화 이력, 첨부 파일, 도구 호출 결과 등. Prompt와 의미적으로 구분하여 별개 인자로 둔다.
- **Params (`θ`)**: 샘플링 파라미터. `(T, top_p, ...)` 등.
- **Output 공간 (`Output`)**: finite-length token sequence를 디코딩한 문자열의 집합.
- **Output 확률변수 (`Y`)**: `Output` 공간 위에서 정의되는 확률변수. 관측 표본은 `y`로 표기한다.

단일 호출을 다음 함수로 정의한다.

```
f : Prompt × Context × Params → Dist(Y)
```

여기서 `Dist(Y)`는 `Y`의 조건부 분포 집합이다. 각 `(x, c, θ)`에 대해 `f(x, c, θ)`는 `Y`의 조건부 분포 `P(Y | x, c, θ)`를 결정한다. 이 분포의 explicit form은 **L0에서 직접 관측 불가**이다 (B1).

이 모델은 LLM을 **blackbox 확률함수**로 취급한다. 내부 메커니즘(attention, sampling 세부 등)은 L0 스코프 밖이며, 영원히 L0에서 다루지 않는다.

---

## 3. 스코프 — 포함

L0이 다루는 관측 가능량:

| 관측량 | 표기(잠정) | 출처 |
|---|---|---|
| 입력 토큰 수 | `\|x\|_tok` | tokenizer |
| 입력 문자 수 | `\|x\|_char` | 길이 |
| 컨텍스트 토큰 수 | `\|c\|_tok` | tokenizer + API usage |
| 출력 토큰 수 | `\|y\|_tok` | API usage |
| 출력 문자열 | `y` | API response |
| 샘플링 파라미터 | `θ = (T, top_p, ...)` | 호출 파라미터 |
| Context window 상한 | `W` | 모델 스펙 (공개 상수) |
| N회 호출 샘플 집합 | `{y_i}_{i=1..N}` | 반복 호출 관측 |

### 3.1. 투영(`π`)의 도입

LLM 실무에서 표본 `y_i`는 사실상 중복 없이 흩어진다 (문장 표현·어휘 선택의 미세 변동). 이 환경에서 unprojected `Y` 위의 경험 분포를 직접 정의하면 거의 모든 `y`에 대해 0이 되어 분포로서의 정보량이 사라진다.

이를 해결하기 위해 **투영 `π: Output → ProjectedSpace`의 존재를 전제한다**. `π`는 Output을 측정 목적에 맞는 동치류로 묶는 함수이며, **구체 선택은 use site에서 결정된다**. L0은 `π`의 존재만 전제하고 선택 기준은 규정하지 않는다.

<rationale>
Output 공간의 구조는 측정 목적(AC 검증, semantic 분산, 구조 변동 등)에 따라 서로 다른 투영을 요구한다. 단일 규약으로 못 박으면 프레임 내부의 허용 진폭이 측정 문맥마다 재조정 불가해진다. 따라서 L0은 "존재"만 선언하고, 선택은 유동적으로 유지한다. 투영 선택의 체계화는 필요해지는 시점에 별도로 다룬다.
</rationale>

### 3.2. 경험 분포 (default: 투영된 형태)

`N`회 호출의 표본 집합 `{y_i}_{i=1..N}`이 주어진다. ProjectedSpace 위의 경험 분포는 다음과 같이 정의된다:

```
̂P_N(z | x, c, θ) = (1/N) · Σ_{i=1..N} 𝟙(π(y_i) = z),    z ∈ ProjectedSpace
```

**본 문서에서 `̂P_N`은 기본적으로 투영된 형태로 이해한다.**

투영 없이 정의되는 다음 식

```
̂P_N(y | x, c, θ) = (1/N) · Σ_{i=1..N} 𝟙(y_i = y),    y ∈ Output
```

도 형식상 가능하나, 위에 기술한 대로 거의 모든 `y`에 대해 0이 되어 `point mass` 분포로 붕괴한다. 따라서 **unprojected `̂P_N`은 보조적 표기로만 사용**하며, 실용적 분석은 `π`를 거친 형태로 수행한다.

---

## 4. 스코프 — 명시적 비포함

L0이 **다루지 않는** 것과 그 이유:

| # | 비포함 항목 | 이유 | 이관 |
|---|---|---|---|
| B1 | 이론 분포 `P(y\|x,c,θ)`의 explicit form | Claude logprobs 미노출. cross-model 경로만 가능. | L4 이후 |
| B2 | Prompt 공간의 구조 (유사도, 변환의 불변성) | 별도 층위 주제 | L1 |
| B3 | 다중 호출의 합성 (파이프라인) | 별도 층위 주제 | L2 |
| B4 | 수렴·한계 주장 (`̂P_N → P` 등) | L0은 정의만, 주장은 위 층위에서 | L3 |
| B5 | 모델 내부 메커니즘 (attention, weights, sampling internals) | blackbox 원칙 | 영구 제외 |

---

## 5. 기본 가정 (공리)

L0이 L1 이후로 넘기는 가정. 증명 대상이 아니라 **공리로 둔다**. 위배 가능성과 위배 시 파급은 L3에서 다룬다.

- **A0.1 (Well-definedness)**: 주어진 `(x, c, θ)`에 대해 `f`가 well-defined한 분포 `Dist(Output)`을 induce한다.

- **A0.2 (Observability)**: `y ~ f(x, c, θ)`는 관측 가능하다. 단, 그것이 속한 이론 분포의 explicit form은 L0에서 알 수 없다 (B1).

- **A0.3 (Independence)**: 동일 `(x, c, θ)`로 반복 호출한 결과 `{y_i}_{i=1..N}`은 서로 독립이라고 가정한다.
  - **잠재적 위배**: server-side caching, provider 단의 load balancing 간 fingerprint 차이 등은 호출 간 의존성을 만들 수 있다.
  - **`c`의 무의식적 변화**: "동일 질문"처럼 보여도 `c`(참조 소스코드·문서 등)가 관측 기간 내에 변했다면 `(x, c, θ)` 조건이 애초에 깨진 것이므로 i.i.d. 위배가 아니라 **실험 통제 실패**로 분류한다. 통제 규약은 L3 주제.
  - **L0의 처리**: 가정으로 두되 A0.4와 결합하여 관측 구간을 제한한다.

- **A0.4 (Stationarity within window)**: 관측 기간 내에서 모델 버전·서버 구성이 고정되어 있다고 가정한다.
  - **함의**: 이 가정으로부터 동일 `(x, c, θ)` 호출의 분포가 시점에 무관하게 동일함이 induce된다. 즉 A0.3(독립성)과 A0.4(정상성)가 결합하여 i.i.d. 성질을 구성한다 — `i.i.d.`를 별도 공리로 두지 않는 이유.
  - **실무 함의**: model 업데이트 시 이전 경험 분포 `̂P_N`은 폐기되며 재수집이 필요하다. 이 관리 자체는 L3 주제.

---

## 6. 표기 규약 (잠정)

| 기호 | 의미 |
|---|---|
| `x` | Prompt (명시적 입력) |
| `c` | Context (부가 입력) |
| `θ` | 샘플링 파라미터 |
| `y` | Output (관측값, 특정 표본) |
| `Y` | Output 확률변수 |
| `f` | 호출 함수 `(x, c, θ) → Dist(Y)` |
| `P(Y\|x,c,θ)` | 이론 분포 (L0에서는 unobservable) |
| `̂P_N(y\|x,c,θ)` | N회 샘플 기반 경험 분포 |
| `W` | Context window 상한 (토큰) |
| `\|·\|_tok`, `\|·\|_char` | 토큰 수, 문자 수 |
| `π` | Output 투영 `Output → ProjectedSpace`. 구체 선택은 use site에서. |
| `𝟙(·)` | 지시함수 (indicator function). 조건 참이면 1, 거짓이면 0. |
| `Output` | finite-length token sequence를 디코딩한 문자열의 집합. |
| `ProjectedSpace` | `π`의 공역. use site별로 다름. |

이 규약은 L1 이후 확장될 수 있다. 변경 시 본 문서에 누적 기록한다(변경 이력 섹션 신설).

---

## 7. 다음 단계 (L0 내부 후속 작업)

본 스코프 선언 이후 L0이 완결되기 위해 식별된 세부 작업:

1. **빠삐용 구성요소별 `(x, c, θ)` 매핑**: inquisition·wtth·shackled·papillon 각 호출에서 `x`·`c`·`θ`가 실제로 무엇인지 본 표기법으로 기술. 현 설계서와 교차 검증 필요.
2. **관측 측정 규약**: tokenizer 종류(Anthropic tokenizer 등), API usage 수집 절차, 로깅 포맷.

위 작업의 **산출 형태는 현재 확정하지 않는다** — 단일 문서로 묶을지, 다문서로 분리할지, L1 진행 후 재정리할지는 실제 매핑을 시도해본 다음 결정한다.

---

## References
- 상위 층위 인덱스: [00-index.md](./00-index.md)
- ASEWS 대응 문서: `~/Work/asews/docs/modeling/00-index.md`
- 빠삐용 공통 스펙: `../02-common-spec.md`
