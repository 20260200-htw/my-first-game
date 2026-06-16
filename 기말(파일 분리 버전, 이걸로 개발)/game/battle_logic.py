import random


# ══════════════════════════════════════════════════════════════════
#   전투 로직 엔진 (턴 시스템 + 데미지 계산)
# ══════════════════════════════════════════════════════════════════
class BattleLogic:
    def __init__(self, enemies, allies):
        self.enemies = enemies
        self.allies  = allies
        self.turn_count = 0
        self.turn_order = []
        self.order_idx  = 0
        self.log        = []
        self.battle_over = False
        self.winner      = None
        # 계획 단계
        self.phase      = "plan"   # "plan"(계획) / "exec"(실행)
        self.plan_idx   = 0        # 계획 중인 아군 인덱스 (turn_order 기준)
        self.planned    = {}       # {combatant: {"kind","skill","primary"}}

    # ── 진영 헬퍼 ─────────────────────────────────────────────
    def allies_of(self, actor):
        """actor와 같은 편"""
        return self.allies if actor in self.allies else self.enemies

    def enemies_of(self, actor):
        """actor의 상대 편"""
        return self.enemies if actor in self.allies else self.allies

    # ── 스킬 분류 ─────────────────────────────────────────────
    def is_support(self, skill):
        tags = skill.get("tags", [])
        return ("지원" in tags) or ("회복" in tags) or skill.get("side") in ("자신", "아군")

    def resolve_targets(self, actor, skill, primary_target):
        """스킬의 side/count에 따라 실제 대상 리스트 결정.
        primary_target: 플레이어가 지정한 1명 (없으면 None)"""
        side = skill.get("side", "적")
        count = skill.get("count", "단일")

        if side == "자신":
            return [actor]

        if side == "아군":
            pool = [c for c in self.allies_of(actor) if c.hp > 0]
        else:  # 적
            pool = [c for c in self.enemies_of(actor) if c.hp > 0]

        if not pool:
            return []

        # 공격 대상 수 보너스 (패시브: 나는 검이 두 자루야~ 등). 적 대상에만 적용.
        bonus = actor.target_count_bonus(skill) if side == "적" else 0

        if count == "단일":
            n = 1 + bonus
        else:
            n = int(count.replace("인", "")) + bonus
        n = min(n, len(pool))

        chosen = []
        if primary_target and primary_target in pool and primary_target.hp > 0:
            chosen.append(primary_target)
        remaining = [c for c in pool if c not in chosen]
        random.shuffle(remaining)
        while len(chosen) < n and remaining:
            chosen.append(remaining.pop())
        return chosen

    # ── 오로치(멀티헤드 보스) 처리 ─────────────────────────────
    def _orochi_units(self):
        """살아있는 오로치 머리들 (가운데 + 또다른). 오로치 전투가 아니면 빈 리스트."""
        return [e for e in self.enemies
                if e.hp > 0 and (getattr(e, "is_orochi_center", False)
                                 or getattr(e, "is_orochi_head", False))]

    def _orochi_pre_turn(self):
        """매 턴 시작 시 오로치 상태 갱신:
        - 남은 머리 수 × 11 을 모든 머리의 물/마 레벨로 주입
        - 포식 주기(5턴) 또는 폭주(맛있구나) 시 사용할 스킬 예약
        - 포식/단독 행동 턴에는 행동 머리 외 나머지 머리 속도 0
        """
        center = next((e for e in self.enemies if getattr(e, "is_orochi_center", False)), None)
        if center is None:
            return  # 오로치 전투 아님
        heads = self._orochi_units()
        n = len(heads)
        # 1) 남은 머리 수 × 11 = 물/마 레벨 (개당 11)
        for h in heads:
            h.orochi_heads_alive = n
            h.phys_level = n * 11
            h.magic_level = n * 11
            h.orochi_speed0 = False               # 매 턴 리셋 (아래서 필요시 다시 설정)
            h.orochi_forced_skill = None          # 강제 스킬 예약 초기화

        others = [h for h in heads if not getattr(h, "is_orochi_center", False)]
        center_only = (len(others) == 0)

        # 2) 폭주 모드(맛있구나 발동): 가운데 머리가 매 턴 아마노무라쿠모 사용 (속도 80)
        if getattr(center, "orochi_devoured", False):
            center.orochi_forced_skill = self._find_skill(center, "아마노무라쿠모노츠루기")
            return

        # 3) 포식 주기: 5턴마다 (5,10,15...) 머리 하나가 포식
        #    가운데만 남았으면 포식 대신 아마노무라쿠모
        if self.turn_count > 0 and self.turn_count % 5 == 0:
            if center_only:
                center.orochi_forced_skill = self._find_skill(center, "아마노무라쿠모노츠루기")
            else:
                # 또다른 머리 중 하나가 포식, 나머지(가운데 포함) 머리는 속도 0
                actor = others[0]
                actor.orochi_forced_skill = self._find_skill(actor, "포식")
                for h in heads:
                    if h is not actor:
                        h.orochi_speed0 = True

    def _find_skill(self, combatant, skill_name):
        for s in combatant.skills:
            if s["name"] == skill_name:
                return s
        return None

    def _orochi_on_head_death(self, dead_head):
        """오로치 머리가 죽었을 때 호출. 가운데 머리는 다른 머리가 남아있으면 죽지 않는다."""
        center = next((e for e in self.enemies if getattr(e, "is_orochi_center", False)), None)
        if center is None:
            return
        # 가운데 머리가 죽으려는 경우: 다른 머리가 살아있으면 부활(무적 유지)
        if getattr(dead_head, "is_orochi_center", False):
            others = [e for e in self.enemies
                      if getattr(e, "is_orochi_head", False) and e.hp > 0]
            if others:
                dead_head.hp = 1   # 다른 머리 남아있으면 가운데는 죽지 않음

    def _orochi_devour_kill(self, victim):
        """'포식' 스킬로 대상이 처치되었을 때: 맛있구나 발동.
        모든 머리 재생 + 전체 회복 + 다음 턴부터 폭주(속도 80, 매턴 아마노무라쿠모)."""
        center = next((e for e in self.enemies if getattr(e, "is_orochi_center", False)), None)
        if center is None:
            return
        # 가운데 머리 폭주 플래그
        center.orochi_devoured = True
        center.hp = center.hp_max
        # 또다른 머리 전부 재생(부활) + 풀피
        for e in self.enemies:
            if getattr(e, "is_orochi_head", False):
                e.hp = e.hp_max
        self.log.append("── 오로치: 맛있구나! 모든 머리가 재생되었다 ──")

    # ── 턴 시작 ───────────────────────────────────────────────
    def start_turn(self):
        self.turn_count += 1
        combatants = [c for c in (self.allies + self.enemies) if c.hp > 0]

        # 오로치(멀티헤드 보스) 사전 처리: 머리 수 집계 → 레벨/무적/속도/포식 주기 결정
        self._orochi_pre_turn()

        order = []
        for c in combatants:
            spd = c.roll_speed()
            if spd > 0:
                order.append(c)

        def sort_key(c):
            is_ally = c in self.allies
            return (-c.speed, 0 if is_ally else 1)

        order.sort(key=sort_key)
        self.turn_order = order
        self.order_idx  = 0

        for c in combatants:
            c.defending = False
            c.dodging   = False
            c.dodge_power = 0
            c.guarding  = False       # 방어 상태: 그 턴만 유지
            c.damaged_by_this_turn = set()  # 이번 턴 피격 기록 초기화 (카운터 판정용)
            c.shield = 0              # 방어 보호막: 그 턴만 유지
            c.assist_shields = []     # 원호 보호막: 그 턴만 유지
            c.tick_buffs()            # 버프 지속시간 감소 (획득 턴은 미포함)
            c.on_turn_start(self)     # 턴 시작 패시브 (전황 분석 등)

        # 적 스킬 미리 결정 (행동 서열 표시용)
        # 마력/중첩(require_buff) 조건을 만족하는 스킬만 후보로,
        # 발동 조건이 있는 강력기(여우가 춤을 추니...)는 우선 선택.
        for e in self.enemies:
            if e.hp > 0 and e.skills:
                forced = getattr(e, "orochi_forced_skill", None)
                if forced is not None:
                    # 오로치: 이번 턴 강제 스킬(포식/아마노무라쿠모)
                    e.planned_skill = forced
                    e.planned_primary = self._preview_primary(e, forced)
                    continue
                usable = self._usable_skills(e)
                if not usable:
                    e.planned_skill = None
                    e.planned_primary = None
                else:
                    priority = [s for s in usable if s.get("require_buff")]
                    e.planned_skill = random.choice(priority) if priority else random.choice(usable)
                    e.planned_primary = self._preview_primary(e, e.planned_skill)
            else:
                e.planned_skill = None
                e.planned_primary = None

        self.log.append(f"── {self.turn_count}턴 시작 ──")

        # 계획 단계 시작
        self.phase   = "plan"
        self.planned = {}
        self.plan_idx = 0
        self._advance_plan_to_ally()

    def _preview_primary(self, actor, skill):
        """예고 화살표용 주 대상 1명 선정 (실제 실행과 약간 달라도 무방).
        side='자신'이면 None (화살표 없음)."""
        if skill is None:
            return None
        side = skill.get("side", "적")
        if side == "자신":
            return None
        if actor in self.enemies:
            pool = self.allies if side == "적" else self.enemies
        else:
            pool = self.enemies if side == "적" else self.allies
        alive = [c for c in pool if c.hp > 0]
        if not alive:
            return None
        for c in alive:
            if getattr(c, "ctype", "") == "player":
                return c
        return alive[0]

    # ── 계획 단계 ─────────────────────────────────────────────
    def _advance_plan_to_ally(self):
        """plan_idx를 다음 '살아있는 아군'으로 이동. 끝나면 실행 단계로."""
        while self.plan_idx < len(self.turn_order):
            c = self.turn_order[self.plan_idx]
            if c in self.allies and c.hp > 0:
                return
            self.plan_idx += 1
        # 아군 계획 모두 완료 → 실행 단계
        self.phase = "exec"
        self.order_idx = 0
        self._reorder_for_exec()

    def _is_defense_action(self, c):
        """그 캐릭터의 예약 행동이 수비 스킬인지"""
        act = self.planned.get(c)
        if act and act.get("kind") == "defense":
            return True
        # 적: planned_skill 이 수비 스킬(def_kind)인 경우
        sk = getattr(c, "planned_skill", None)
        if sk and sk.get("def_kind"):
            return True
        return False

    def _reorder_for_exec(self):
        """실행 순서: 수비 스킬 사용자가 (속도순으로) 먼저, 그 다음 나머지(속도순).
        turn_order 는 이미 속도순이므로 안정 정렬로 수비 우선만 적용."""
        defenders = [c for c in self.turn_order if self._is_defense_action(c)]
        others    = [c for c in self.turn_order if not self._is_defense_action(c)]
        self.turn_order = defenders + others

    def planning_actor(self):
        """현재 계획 입력을 받을 아군 (없으면 None)"""
        if self.phase != "plan":
            return None
        if self.plan_idx < len(self.turn_order):
            return self.turn_order[self.plan_idx]
        return None

    def set_plan(self, actor, kind, skill=None, primary=None):
        """아군 행동 계획 저장 후 다음 아군으로"""
        self.planned[actor] = {"kind": kind, "skill": skill, "primary": primary}
        self.plan_idx += 1
        self._advance_plan_to_ally()

    def reset_plan(self):
        """계획 전체 리셋, 첫 아군부터 다시"""
        self.planned = {}
        self.plan_idx = 0
        self.phase = "plan"
        self._advance_plan_to_ally()

    def is_planning_done(self):
        return self.phase == "exec"

    def current_actor(self):
        if self.phase != "exec":
            return None
        if self.order_idx < len(self.turn_order):
            return self.turn_order[self.order_idx]
        return None

    def planned_action_of(self, actor):
        """실행 단계: 해당 actor의 예약 행동 (아군은 planned, 적은 planned_skill)"""
        if actor in self.planned:
            return self.planned[actor]
        # 적: 미리 정해둔 스킬
        sk = getattr(actor, "planned_skill", None)
        if sk:
            return {"kind": "skill", "skill": sk, "primary": None}
        return {"kind": "skip"}

    def advance(self):
        if self.battle_over:
            return
        self.order_idx += 1
        while self.order_idx < len(self.turn_order):
            if self.turn_order[self.order_idx].hp > 0:
                break
            self.order_idx += 1
        if self.order_idx >= len(self.turn_order):
            self._check_battle_over()
            if not self.battle_over:
                self.start_turn()  # 다음 턴 → 다시 계획 단계

    # ── 행동: 스킬 사용 ───────────────────────────────────────
    def consume_skill_cost(self, actor, skill, already_charged=False):
        """스킬 발동 1회당 마력 소모 + 중첩 소모(+마력 회복) 처리.
        다단히트와 무관하게 '스킬 시작 시 1번만' 호출해야 한다.
        already_charged=True 면 모션 시작 때 이미 소모했으므로 마력 소모를 건너뛴다.
        (스킬 객체에 상태를 남기지 않으므로 다음 턴 재사용에 영향이 없다.)"""
        if already_charged:
            return  # 모션 시작 때 이미 소모함
        # 마법 스킬 사용 기록 (검으로 다지는 초석 - 무형검 중첩용)
        if skill.get("type") == "마법":
            actor._used_magic_this_turn = True
        # 마력 소모
        cost = skill.get("cost", 0)
        if cost:
            actor.mp = max(0, actor.mp - cost)
            actor.mp_spent_this_turn = getattr(actor, "mp_spent_this_turn", 0) + cost
            actor.mp_spent_total = getattr(actor, "mp_spent_total", 0) + cost
        # 중첩 소모 (require_buff: 발동 조건이자 소모) → 소모한 중첩만큼 마력 회복
        req = skill.get("require_buff")
        if req and req.get("consume"):
            consumed = actor.buff_stacks(req["name"])
            actor.remove_buff(req["name"])
            if consumed > 0:
                actor.mp = min(actor.mp_max, actor.mp + consumed)
                self.log.append(f"{actor.name} 마력 회복 (+{consumed})")

    def use_skill(self, actor, skill, primary_target=None, already_charged=False):
        # 마력/중첩 소모 (이 경로로 들어오는 스킬: 지원/회복/단순 실행)
        # already_charged=True 면 모션 시작 시 이미 소모했으므로 건너뛴다.
        self.consume_skill_cost(actor, skill, already_charged=already_charged)
        targets = self.resolve_targets(actor, skill, primary_target)
        is_devour = (skill.get("name") == "포식")
        victims_before = {t: t.hp for t in targets} if is_devour else {}
        if self.is_support(skill):
            self._apply_support(actor, skill, targets)
            results = []
        else:
            results = self._apply_attack(actor, skill, targets)
            # 최대 체력 비례 고정 피해 (조건부)
            self._apply_true_damage(actor, skill, targets, results)
        # 오로치 포식 후처리: 만족감 중첩 + 처치 시 맛있구나
        if is_devour:
            actor.add_buff_stacks("만족감", 1, max_stacks=99, icon="")
            for t in victims_before:
                if victims_before[t] > 0 and t.hp <= 0:
                    self._orochi_devour_kill(t)
                    break
        self._check_battle_over()
        return results

    def _apply_true_damage(self, actor, skill, targets, results):
        """스킬의 true_damage_max_hp_pct: 매 히트 대상 최대체력 N% 고정피해.
        조건(true_dmg_cond) 충족 시에만. 히트 수만큼 반복."""
        pct = skill.get("true_damage_max_hp_pct", 0)
        if not pct:
            return
        cond = skill.get("true_dmg_cond")
        hits = skill.get("hits", 1)
        # damage_over 조건: 이 스킬로 입힌 피해가 기준 이상일 때만
        dmg_over = skill.get("true_dmg_if_damage_over")
        dealt = {t: d for (t, d) in results if isinstance(d, (int, float))}
        for target in targets:
            if target.hp <= 0:
                continue
            # 오로치 가운데 머리: 다른 머리 살아있는 동안 고정 피해 무효
            if (getattr(target, "is_orochi_center", False)
                    and getattr(target, "orochi_heads_alive", 1) > 1):
                continue
            if cond and not actor._eval_condition(cond, target):
                continue
            if dmg_over is not None and dealt.get(target, 0) < dmg_over:
                continue
            for _ in range(hits):
                if target.hp <= 0:
                    break
                fixed = int(target.hp_max * pct / 100.0)
                target.hp = max(0, target.hp - fixed)
                self.log.append(f"{target.name} 추가 고정 피해! (-{fixed})")

    def apply_single_hit(self, actor, skill, targets, fraction=1.0):
        """1히트 분량의 피해 적용 (모션 연동용). 반환: [(target, amount), ...]
        fraction: 1히트 피해에 곱할 비율 (난무 등 분할 타격 시 1/N 전달)"""
        results = []
        for target in targets:
            if target.hp <= 0:
                continue
            if target.dodging:
                skill_power = actor.calc_skill_power(skill, target)
                if target.dodge_power > skill_power and not actor.has_sure_hit(skill, target):
                    self.log.append(f"{target.name} 회피!")
                    results.append((target, "MISS"))
                    continue
            dmg = actor.calc_damage(skill, target) * fraction
            applied = target.take_damage(dmg, actor)
            self.log.append(f"{actor.name} → {target.name}: {skill['name']} ({applied})")
            results.append((target, applied))
            # 피격 밀림: 데미지가 0이어도 적중하면 뒤로 조금 밀려난다
            self._apply_hit_push(target)
        self._check_battle_over()
        return results

    def _apply_hit_push(self, target):
        """피격 시 움찔 효과: 짧게 뒤로 밀렸다가 복귀하며, 그 동안 빨갛게.
        움찔과 빨강은 같은 타이머(hit_push_t)로 동기화. 아군=좌 / 적=우."""
        direction = 1 if target in self.enemies else -1
        push = 18.0 * direction        # 최초 움찔 거리(px)
        target.hit_push_max = push     # 복귀 계산 기준
        target.hit_push = push         # 현재 위치(시작=최대)
        target.hit_push_t = 0.22       # 움찔+빨강 지속(초). 이 값이 0이 되면 제자리+빨강제거
        target.hit_flash_t = 0.22

    def _apply_attack(self, actor, skill, targets):
        hits = skill.get("hits", 1)
        results = []
        for target in targets:
            if target.hp <= 0:
                continue
            total = 0
            for _ in range(hits):
                if target.dodging:
                    skill_power = actor.calc_skill_power(skill, target)
                    if target.dodge_power > skill_power and not actor.has_sure_hit(skill, target):
                        continue
                dmg = actor.calc_damage(skill, target)
                applied = target.take_damage(dmg, actor)
                total += applied
                self._apply_hit_push(target)
            self.log.append(f"{actor.name} → {target.name}: {skill['name']} ({total})")
            results.append((target, total))
        return results

    def _apply_support(self, actor, skill, targets):
        # 회복 스킬: 위력 기반 회복, 그 외 지원은 로그만 (효과는 추후 패시브 연동)
        is_heal = "회복" in skill.get("tags", [])
        for target in targets:
            if target.hp <= 0:
                continue
            if is_heal:
                heal = int(actor.calc_damage(skill))
                target.hp = min(target.hp_max, target.hp + heal)
                self.log.append(f"{actor.name} → {target.name}: {skill['name']} (+{heal} 회복)")
            else:
                self.log.append(f"{actor.name} → {target.name}: {skill['name']} (지원)")

    # ── 수비 스킬 ─────────────────────────────────────────────
    def apply_defense_skill(self, actor, skill, primary=None):
        """수비 스킬 적용. def_kind: guard(방어)/dodge(회피)/assist(원호)"""
        kind = skill.get("def_kind", "guard")
        if kind == "guard":
            actor.defending = True
            actor.guarding = True
            shield = actor.calc_guard_shield(skill)
            actor.shield += shield
            self.log.append(f"{actor.name} 방어! (보호막 +{shield})")
        elif kind == "dodge":
            actor.dodging = True
            actor.dodge_power = actor.calc_dodge_skill_power(skill)
            self.log.append(f"{actor.name} 회피 자세! (회피위력 {actor.dodge_power})")
        elif kind == "assist":
            # 자신 제외 아군 1명에게 보호막 부여, 흡수분은 시전자에게 전가
            target = primary
            if target is not None and target is not actor and target.hp > 0:
                shield = actor.calc_guard_shield(skill)
                target.assist_shields.append({"amount": shield, "caster": actor})
                self.log.append(f"{actor.name} → {target.name} 원호! (보호막 +{shield})")

    # 구버전 호환 (사용 안 함)
    def do_defend(self, actor):
        actor.defending = True
        actor.shield += actor.calc_shield()

    # ── 적 AI ─────────────────────────────────────────────────
    def _usable_skills(self, enemy):
        """마력이 충분하고 발동 조건(require_buff)을 만족하는 스킬만."""
        usable = []
        for sk in enemy.skills:
            cost = sk.get("cost", 0)
            if cost and enemy.mp < cost:
                continue
            req = sk.get("require_buff")
            if req:
                need = req.get("stacks", 1)
                if enemy.buff_stacks(req["name"]) < need:
                    continue
            usable.append(sk)
        return usable

    def enemy_action(self, enemy):
        skill = getattr(enemy, "planned_skill", None)
        if skill is None:
            usable = self._usable_skills(enemy)
            if not usable:
                # 쓸 스킬이 없으면(마력 부족 등) 행동 스킵
                self.advance()
                return
            # 발동 조건이 있는 강력기(require_buff)는 우선 사용
            priority = [s for s in usable if s.get("require_buff")]
            skill = random.choice(priority) if priority else random.choice(usable)
        self.use_skill(enemy, skill, primary_target=None)
        self.advance()

    # ── 승패 판정 ─────────────────────────────────────────────
    def _check_battle_over(self):
        if self.battle_over:
            return
        # 오로치: 가운데 머리는 다른 머리가 살아있는 동안 죽지 않는다 (사망 직전 부활)
        center = next((e for e in self.enemies if getattr(e, "is_orochi_center", False)), None)
        if center is not None and center.hp <= 0:
            others = [e for e in self.enemies
                      if getattr(e, "is_orochi_head", False) and e.hp > 0]
            if others:
                center.hp = 1
        # 주인공 사망 → 즉시 패배
        for a in self.allies:
            if a.ctype == "player" and a.hp <= 0:
                self.battle_over = True
                self.winner = "enemy"
                self.log.append("── 패배... ──")
                return
        # 보스 사망 → 즉시 승리
        bosses = [e for e in self.enemies if e.ctype == "boss"]
        if bosses and all(b.hp <= 0 for b in bosses):
            self.battle_over = True
            self.winner = "ally"
            self.log.append("── 승리! ──")
            return
        # 적 전멸 → 승리
        if all(e.hp <= 0 for e in self.enemies):
            self.battle_over = True
            self.winner = "ally"
            self.log.append("── 승리! ──")
            return
        # 아군 전멸 → 패배
        if all(a.hp <= 0 for a in self.allies):
            self.battle_over = True
            self.winner = "enemy"
            self.log.append("── 패배... ──")