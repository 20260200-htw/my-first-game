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

        if count == "단일":
            if primary_target and primary_target.hp > 0:
                return [primary_target]
            return [random.choice(pool)]

        # 3인 / 5인: 1명 지정 + 나머지 랜덤
        n = int(count.replace("인", ""))
        n = min(n, len(pool))
        chosen = []
        if primary_target and primary_target in pool:
            chosen.append(primary_target)
        remaining = [c for c in pool if c not in chosen]
        random.shuffle(remaining)
        while len(chosen) < n and remaining:
            chosen.append(remaining.pop())
        return chosen

    # ── 턴 시작 ───────────────────────────────────────────────
    def start_turn(self):
        self.turn_count += 1
        combatants = [c for c in (self.allies + self.enemies) if c.hp > 0]

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
            c.shield = 0              # 방어 보호막: 그 턴만 유지
            c.assist_shields = []     # 원호 보호막: 그 턴만 유지
            c.tick_buffs()            # 버프 지속시간 감소 (획득 턴은 미포함)
            c.on_turn_start(self)     # 턴 시작 패시브 (전황 분석 등)

        # 적 스킬 미리 결정 (행동 서열 표시용)
        for e in self.enemies:
            if e.hp > 0 and e.skills:
                e.planned_skill = random.choice(e.skills)
            else:
                e.planned_skill = None

        self.log.append(f"── {self.turn_count}턴 시작 ──")

        # 계획 단계 시작
        self.phase   = "plan"
        self.planned = {}
        self.plan_idx = 0
        self._advance_plan_to_ally()

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
    def use_skill(self, actor, skill, primary_target=None):
        targets = self.resolve_targets(actor, skill, primary_target)
        if self.is_support(skill):
            self._apply_support(actor, skill, targets)
            results = []
        else:
            results = self._apply_attack(actor, skill, targets)
        self._check_battle_over()
        return results

    def apply_single_hit(self, actor, skill, targets, fraction=1.0):
        """1히트 분량의 피해 적용 (모션 연동용). 반환: [(target, amount), ...]
        fraction: 1히트 피해에 곱할 비율 (난무 등 분할 타격 시 1/N 전달)"""
        results = []
        for target in targets:
            if target.hp <= 0:
                continue
            if target.dodging:
                skill_power = actor.calc_skill_power(skill)
                if target.dodge_power > skill_power and "필중" not in skill.get("tags", []):
                    self.log.append(f"{target.name} 회피!")
                    results.append((target, "MISS"))
                    continue
            dmg = actor.calc_damage(skill, target) * fraction
            applied = target.take_damage(dmg)
            self.log.append(f"{actor.name} → {target.name}: {skill['name']} ({applied})")
            results.append((target, applied))
        self._check_battle_over()
        return results

    def _apply_attack(self, actor, skill, targets):
        hits = skill.get("hits", 1)
        results = []
        for target in targets:
            if target.hp <= 0:
                continue
            total = 0
            for _ in range(hits):
                if target.dodging:
                    skill_power = actor.calc_skill_power(skill)
                    if target.dodge_power > skill_power and "필중" not in skill.get("tags", []):
                        continue
                dmg = actor.calc_damage(skill, target)
                applied = target.take_damage(dmg)
                total += applied
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
    def enemy_action(self, enemy):
        skill = getattr(enemy, "planned_skill", None)
        if skill is None:
            if not enemy.skills:
                self.advance()
                return
            skill = random.choice(enemy.skills)
        self.use_skill(enemy, skill, primary_target=None)
        self.advance()

    # ── 승패 판정 ─────────────────────────────────────────────
    def _check_battle_over(self):
        if self.battle_over:
            return
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