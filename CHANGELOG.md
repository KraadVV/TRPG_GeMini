# 📋 TRPG GeMini 업데이트 내역 (Changelog)

이 프로젝트는 Google Gemini AI와 로컬 파이썬 엔진을 결합한 텍스트 기반 TRPG 게임 엔진입니다. 버전별 변경 사항 및 추가된 기능에 대한 기록을 관리합니다.

---

## [v2.1.0] - 2026-07-15
### 🛡️ D&D 5e 룰북 준수 및 엔진 고도화
코드 리뷰 로드맵에 따라 전투 루프, 장비 장착, 스킬 조건, 저장 안정성 등 게임 엔진 전반의 D&D 5e 규칙 호환성과 LLM 연동의 안정성을 획득하였습니다.

#### 1. ☠️ 죽음 내성 굴림(Death Saving Throws) 구현 ([combat.py](file:///home/kraad/Projects/TRPG_GeMini/combat.py))
- HP가 0이 되었을 때 즉사 처리하지 않고, D&D 5e 규칙에 의거하여 매 턴 Death Saving Throw(d20) 수행.
- 자연 20 시 1 HP로 의식 회복 및 턴 수행, 자연 1 시 2회 실패, 10 이상 성공 / 9 이하 실패 누적.
- 3회 성공 시 안정화(Stable), 3회 실패 시 영구 사망 구현.
- 의식 불명(0 HP) 상태에서 적에게 피격 시 즉시 데스 세이브 실패 추가(치명타 시 2회 실패). 초과 피해량이 최대 체력 이상일 경우 Massive Damage 즉사 규칙 구현.
- 플레이어 및 동료가 모두 쓰러졌을 때 파티 전멸(TPK) 패배 로직 적용.

#### 2. ⚔️ 로그 급소 공격(Sneak Attack) 조건 강화 ([combat.py](file:///home/kraad/Projects/TRPG_GeMini/combat.py))
- Finesse(교묘함 - 단검, 숏소드, 레이피어) 또는 Ranged(원거리 - 활, 크로스보우) 무기 장착 시에만 발동 가능하도록 제한.
- 판정에 Disadvantage(불리함)가 존재할 경우 발동 불가 조건 추가.
- 마법 주문 공격 시에는 발동하지 않도록 변경하여 D&D 5e 기준 완벽 정합.

#### 3. 🦸 파이터 Action Surge 기능 실체화 ([combat.py](file:///home/kraad/Projects/TRPG_GeMini/combat.py) / [character.py](file:///home/kraad/Projects/TRPG_GeMini/character.py))
- 2레벨 파이터의 고유 특성인 **Action Surge** 시전 시, 전투 내에서 추가적인 Action을 수행할 수 있도록 전투 액션 상태 초기화 로직 구현.
- 레벨업 시 획득한 고유 피처가 스펠/기술 선택 메뉴(`S` 키)에 자동으로 활성화되어 전투 중 전략적 선택이 가능하도록 연동.

#### 4. 🛡️ 갑옷 분류 체계 고도화 및 민첩 수정치 제한 ([actions.py](file:///home/kraad/Projects/TRPG_GeMini/actions.py) / [game_data.json](file:///home/kraad/Projects/TRPG_GeMini/game_data.json) / [character.py](file:///home/kraad/Projects/TRPG_GeMini/character.py))
- `game_data.json`에 `armor_type` 속성을 추가하여 Light, Medium, Heavy, Shield의 D&D 공식 카테고리 정의.
- Medium Armor(예: Scale Mail) 장착 시 민첩(DEX) 수정치에 따른 AC 보너스를 최대 +2로 강제하는 룰북 규칙 구현.
- 클레릭의 시작 무기를 기존 Longsword(군용)에서 Mace(단순 무기)로, 갑옷을 Chain Mail(중갑)에서 Scale Mail(평갑)로 조정하여 미숙련 패널티 방지.

#### 5. 🔮 주문 공격 판정 버그 수정 ([combat.py](file:///home/kraad/Projects/TRPG_GeMini/combat.py))
- 주문 공격 시 단순히 가장 높은 수정치를 사용하던 버그를 수정하여 클래스별 주문 시전 능력치(Cleric/Ranger=WIS, Bard/Paladin/Sorcerer=CHA, Wizard/Rogue/Fighter=INT)를 올바르게 사용하도록 수정.

#### 6. 🤝 동료 공격 크리티컬 히트 및 피해 저항 룰북 정합성 ([combat.py](file:///home/kraad/Projects/TRPG_GeMini/combat.py))
- 동료(Companion) 공격 굴림 시 자연 20(Critical Hit) 시 피해 주사위를 2배로 굴려 피해를 정산하도록 연산 보완.
- 피해 저항(Damage Resistance) 계산 시 1의 피해를 입었을 때 반감하면 0의 피해가 되도록 `max(1, ...)` 강제 제한 제거.

#### 7. 🤖 AI 데이터 동기화 안정성 및 에러 방어 ([trpg_engine.py](file:///home/kraad/Projects/TRPG_GeMini/trpg_engine.py) / [gm_engine.py](file:///home/kraad/Projects/TRPG_GeMini/gm_engine.py))
- AI GM이 몬스터/스펠 데이터 생성 시 단일 객체나 중첩 딕셔너리 중 어떤 구조로 반환하더라도 도감에 정상 적재되도록 폴백 연동.
- 동기화 도중 장착된 무기/방어구/방패가 인벤토리에서 유실되거나 이미 배운 스펠이 날아가지 않도록 동기화 보호 및 병합 로직 추가.
- API 에러 등으로 게임이 비정상 탈출할 때 직전까지의 모험 데이터를 로컬에 안전하게 `save_game()` 하도록 세이프가드 조치.

---

## [v2.0.0] - 2026-07-08
### 🚀 주요 업데이트: Auto-DM Upgraded Engine
클래스 특성, 상태 이상(Conditions) 시스템, 주사위 판정 고도화 및 D&D 5e 기반 룰을 본격적으로 적용하여 로컬 게임 엔진을 업그레이드하였습니다.

#### 1. ⚔️ D&D 5e 상태 이상(Conditions) 시스템 도입 ([conditions.py](file:///home/kraad/Projects/TRPG_GeMini/conditions.py))
- Blinded, Charmed, Deafened, Frightened, Grappled, Incapacitated, Invisible, Paralyzed, Petrified, Poisoned, Prone, Restrained, Stunned, Unconscious 등 총 14가지 상태 이상 정의.
- 상태 이상에 따른 공격 판정 유리/불리함(Advantage/Disadvantage) 및 능력치 판정 영향 자동 계산.
- 라운드 경과에 따른 상태 이상 턴 감소 및 만료 처리 로직 구현.

#### 2. 🦸 클래스 전용 특성(Class Features) 시스템 추가 ([class_features.py](file:///home/kraad/Projects/TRPG_GeMini/class_features.py))
- 캐릭터 클래스별 고유 레벨 특성 정의:
  - **Fighter**: 1레벨 'Second Wind' (보너스 행동으로 체력 회복), 2레벨 'Action Surge' (추가 행동 획득).
  - **Rogue**: 1레벨 'Sneak Attack' (유리한 판정 시 추가 피해).
  - **Wizard**: 1레벨 'Arcane Recovery' (주문 슬롯 일부 회복).
  - **Cleric**: 1레벨 'Divine Domain' (서브클래스 도메인 적용).
  - **Bard**: 1레벨 'Bardic Inspiration' (아군 판정 보너스 주사위).

#### 3. 🎲 주사위 롤러 및 내성 굴림(Saving Throw) 고도화 ([dice.py](file:///home/kraad/Projects/TRPG_GeMini/dice.py))
- `1d4-1`, `2d4+2` 등 주사위 문자열 파서 개선 (음수 보정치 정상 반영).
- 유리함/불리함이 적용된 d20 주사위 굴림(`roll_d20`) 기능 구현.
- D&D 5e 기반의 **내성 굴림(Saving Throw)** 연산 엔진 구현:
  - 클래스별 내성 숙련도(Save Proficiency) 및 능력치 수정치 자동 계산.
  - 마비(Paralyzed) 등 특정 상태 이상일 때 STR/DEX 내성 굴림 자동 실패 처리.

#### 4. 🎨 시각 효과 및 CLI UI 개선 ([cli_styles.py](file:///home/kraad/Projects/TRPG_GeMini/cli_styles.py))
- ANSI 컬러 색상을 활용한 화려하고 가독성 높은 텍스트 렌더링.
- 대화 상자 패널 및 테두리 상자 그리기 기능 (`draw_box`) 추가.
- 캐릭터 HP/MP 상태 등을 그래픽 바 형태로 표현하는 시각화 도구 (`render_bar`) 구현.

#### 5. 🛠️ 시스템 안정성 및 세이브 파일 강화 ([game_state.py](file:///home/kraad/Projects/TRPG_GeMini/game_state.py))
- 세이브 데이터를 새로 불러올 때 누락될 수 있는 신규 데이터 필드(주문 슬롯, 숙련도, 상태 이상 등)의 기본값 자동 주입.
- 임시 파일(`.tmp`)을 생성한 후 `os.replace`로 덮어쓰는 방식을 도입하여 저장 도중 게임이 강제 종료되더라도 세이브 파일이 손상되지 않도록 안정성 확보.

#### 6. ⚔️ 전투 및 스킬 판정 규칙 상세화 ([combat.py](file:///home/kraad/Projects/TRPG_GeMini/combat.py) / [skills.py](file:///home/kraad/Projects/TRPG_GeMini/skills.py))
- 공격 대상 상태에 따른 melee 공격 자동 치명타(Crit) 판정.
- 무기 및 주문의 피해 속성(화염, 냉기, 번개, 참격 등) 감지 및 몬스터 저항/면역/취약점 적용.
- 스킬 판정 시 숙련도(Proficiency)와 전문화(Expertise) 적용.
- 바드(Bard) 클래스의 'Jack of All Trades' (모든 미숙련 기술에 숙련 보너스 절반 적용) 구현.

---

## [v1.1.0] - 2026-04-03
### ⚔️ 다중 전투 및 스킬 시스템 안정화
- **다중 전투**: 1대1 전투를 넘어서 동료(Companion)와 다수의 적이 함께 싸우는 전투 루프 고도화.
- **스킬 시스템**: AI GM의 판정 요구에 따라 동적으로 로컬 주사위 판정을 연동하는 뼈대 구축.
- **모듈 구조화**: 단일 파일로 구성되어 있던 로직을 `actions.py`, `combat.py`, `gm_engine.py`, `trpg_engine.py` 등으로 분리 및 모듈화.

---

## [v1.0.0] - 2026-03-24
### 🎉 정식 릴리즈: TRPG GeMini 엔진 탄생
- **Gemini AI Game Master**: `gemini-2.5-flash` 기반의 AI GM이 스토리 진행 및 동적 분기 제공.
- **로컬 D&D Mechanics**: 캐릭터 생성(능력치 굴림, 종족, 클래스, 배경), 전투(공격, 아이템 사용, 도망), 레벨업(XP 획득, 능력치 상승) 로직 구현.
- **상점 및 인벤토리**: 아이템 구매/판매, 무기/방어구 장착 및 소모품 사용 시스템.
- **몬스터 도감**: AI GM이 사전에 정의되지 않은 신규 몬스터를 조우시켰을 때, 그 자리에서 스탯을 생성하고 `game_data.json`에 영구 저장하는 동적 도감 시스템 구축.
- **휴식 및 회복**: 안전지대에서의 긴 휴식(Long Rest) 및 일반 지역에서의 짧은 휴식(Short Rest) 구현.

---

## [v0.1.0] - 2026-03-17
### 🧪 초기 프로토타입
- Gemini API 연동 테스트 및 텍스트 입출력 인터페이스 구현.
- 캐릭터 능력치 6종(STR, DEX, CON, INT, WIS, CHA) 기반의 기본 전투 테스트.

[v2.0.0]: file:///home/kraad/Projects/TRPG_GeMini/CHANGELOG.md
[v1.1.0]: file:///home/kraad/Projects/TRPG_GeMini/CHANGELOG.md
[v1.0.0]: file:///home/kraad/Projects/TRPG_GeMini/CHANGELOG.md
[v0.1.0]: file:///home/kraad/Projects/TRPG_GeMini/CHANGELOG.md
