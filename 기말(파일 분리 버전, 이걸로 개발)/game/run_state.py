# 로그라이크 회차(런) 상태 관리
# 회차 동안의 휘발 상태: 구간 진행, 방문 지역, 파티, HP, 아이템, 골드, 레벨/포인트.
# 스킬은 save_data(영구)에 보존되어 회차를 넘어 유지된다.
#
# 세이브 규칙:
#   - 스킬: 영구 보존 (save_data "skills")
#   - 레벨 / 경험치 / 분배 포인트: 회차 시작 시 초기화
#   - 아이템 / 골드 / 파티 / HP: 회차 한정

import copy
import random
import save_data
from data import run_data
from data import encounter_data


class RunState:
    """한 회차의 진행 상태."""

    def __init__(self):
        self.active = False
        self.boss_mode = None       # 보스 모드 정보 {tier, region} (일반 모드면 None)
        self.segment = 0            # 현재 구간 번호 (1~5)
        self.last_region = None     # 직전에 방문한 지역 (연속 방문 금지용)
        self.region = None          # 현재 구간 지역
        self.layers = []            # 분기 노드맵: 층별 노드 리스트
        self.cur_layer = -1         # 현재 위치 층 (-1=시작 전)
        self.cur_col = 0            # 현재 위치 열
        self.cleared_boss = False   # 현재 구간 보스 클리어 여부
        self.visited_regions = []   # 이번 회차에 방문한 지역 순서 (재방문 없음)
        self.cur_visit = 1          # (호환용) 현재 구간 방문 회차 — 고정경로에선 항상 1
        self.node_seq = {}          # 이번 구간에서 노드 종류별 진입 횟수 (배치 순번용)

        # 파티: 주인공 + 합류 동료 이름들 (최대 5)
        self.party = ["주인공"]
        self.temp_allies = []       # 특정 전투 한정 동료 (전투 후 제거)

        # 주인공 보유 스킬(획득 무제한) / 장착 스킬(최대 10)
        self.skills_owned = []      # dict 리스트
        self.skills_equipped = []   # dict 리스트 (최대 10)

        # 아이템 (보유 + 장착 분리, 최대 10 장착)
        self.items = []             # 보유 아이템 키 리스트
        self.items_equipped = []    # 장착 아이템 키 리스트 (효과/HP는 이것만 반영)

        # 자원
        self.gold = 0
        self.hp_cur = 0             # 주인공 현재 HP (회차 동안 유지)
        self.hp_max = 0

    # ── 회차 시작 ─────────────────────────────────────────────────
    def start_new_run(self):
        self.active = True
        self.segment = 0
        self.last_region = None
        self.region = None
        self.layers = []
        self.cur_layer = -1
        self.cur_col = 0
        self.cleared_boss = False
        self.visited_regions = []
        self.cur_visit = 1
        self.node_seq = {}
        self.party = ["주인공"]
        self.temp_allies = []

        # ── 레벨/포인트/포인트분배: 영구 보존 (로그라이트) — 초기화하지 않음 ──
        # (이전에는 reset_growth 로 회차마다 초기화했으나, 이제 파밍 진행이 유지됨)

        # ── 스킬: 영구 보존 — 저장된 스킬 로드 ────────────────────
        # (저장된 게 없으면 시작 스킬을 지급하고 그것부터 영구 저장)
        owned, equipped_names = save_data.get_skills()
        if not owned:
            owned = [copy.deepcopy(s) for s in run_data.STARTER_SKILLS]
            equipped_names = [s["name"] for s in owned]
            save_data.set_skills(owned, equipped_names)
        self.skills_owned = [copy.deepcopy(s) for s in owned]
        by_name = {s["name"]: s for s in self.skills_owned}
        self.skills_equipped = [by_name[n] for n in equipped_names if n in by_name][:10]
        if not self.skills_equipped:
            self.skills_equipped = list(self.skills_owned[:10])

        # ── 아이템: 영구 보존 — 저장된 아이템 로드 ────────────────
        _it_owned, _it_eq = save_data.get_items()
        self.items = [k for k in _it_owned if k in run_data.ITEMS]
        self.items_equipped = [k for k in _it_eq if k in self.items][:self.MAX_ITEM_EQUIP]
        # ── 골드: 회차 한정 — 초기화 ───────────────────────────────
        self.gold = 0
        # 주인공 최대 HP (레벨/포인트/아이템 반영)
        self.hp_max = self._compute_hp_max()
        self.hp_cur = self.hp_max

    def _compute_hp_max(self):
        """주인공 최대 HP = 기본 + 부가포인트(체력) 반영 + 장착 아이템 hp_flat(+시너지)."""
        from data.characters_data import ALLY_DEFS
        base = ALLY_DEFS["주인공"].get("hp_max", 100)
        g = save_data.get_growth("주인공")
        hp_bonus = g.get("hp_bonus", 0) * 10   # 체력 1포인트당 +10 (기존 규칙)
        item_hp = run_data.item_effect_value(self.items_equipped, "hp_flat")
        return base + hp_bonus + item_hp

    def refresh_hp_max(self):
        """아이템/성장 변화 후 최대 HP 갱신 (현재 HP 비율 유지)."""
        old_max = max(1, self.hp_max)
        ratio = self.hp_cur / old_max
        self.hp_max = self._compute_hp_max()
        self.hp_cur = int(self.hp_max * ratio)

    # ── 지역 선택 ─────────────────────────────────────────────────
    def selectable_regions(self):
        """이번 구간에 고를 수 있는 지역.
        일반 모드 고정 경로: 중앙(1구간 고정) 이후, 아직 방문하지 않은 동서남북 중에서 선택.
        모든 지역을 방문했으면 빈 목록.
        """
        visited = set(self.visited_regions)
        return [r for r in run_data.MIDDLE_REGIONS if r not in visited]

    def enter_region(self, region):
        """지역을 골라 다음 구간 진입. 방문 기록 + 노드맵 생성."""
        self.segment += 1
        self.region = region
        if region not in self.visited_regions:
            self.visited_regions.append(region)
        self.cur_visit = 1
        self.node_seq = {}   # 구간이 바뀌면 배치 순번 처음부터
        self._build_map(width=3, final=False)

    def enter_maw(self):
        """6구간 마왕성 진입. 4갈래."""
        self.segment = run_data.FINAL_SEGMENT
        self.region = "마왕성"
        self.cur_visit = 1
        self.node_seq = {}
        self._build_map(width=4, final=True)

    def next_seq(self, kind):
        """이번 구간에서 kind(event/reward) 노드를 몇 번째로 밟는지.
        0부터 시작하는 순번을 반환하고 카운터를 올린다. (encounter_data 번호 슬롯용.
        전투/엘리트는 출현 풀에서 랜덤 조합이라 순번을 쓰지 않는다.)"""
        n = self.node_seq.get(kind, 0)
        self.node_seq[kind] = n + 1
        return n

    def _build_map(self, width, final):
        """좌우 직진 노드맵 생성.
        구조: [시작] + [노드 5층] + [중간] + [노드 5층] + [보스]
              마왕성: [시작] + [중간] + [보스 width갈래] + [마왕]
        각 Node = {"type","col","edges":[다음층 col]}
        시작/중간/보스/마왕은 1칸(단, 마왕성 보스층은 width칸).
        layer_role: 각 층의 역할 태그 리스트 (start/mid/boss/maw/normal)
        """
        self.layers = []
        self.layer_role = []
        m = run_data.SEGMENT_MID_NODES

        def add(row, role):
            self.layers.append(row)
            self.layer_role.append(role)

        if final:
            # 마왕성: 시작 → 중간 → 보스(width) → 마왕
            add([self._mk_node(run_data.NODE_START, 0)], "start")
            add([self._mk_node(run_data.NODE_MID, 0)], "mid")
            add([self._mk_node(run_data.NODE_BOSS, c) for c in range(width)], "boss")
            add([self._mk_node(run_data.NODE_MAW, 0)], "maw")
        else:
            # 일반 구간: 시작 + 5 + 중간 + 5 + 보스
            add([self._mk_node(run_data.NODE_START, 0)], "start")
            # 앞 5층
            for _ in range(m):
                add([self._mk_node(run_data.roll_node_type(), c) for c in range(width)], "normal")
            # 중간 지점
            add([self._mk_node(run_data.NODE_MID, 0)], "mid")
            # 뒤 5층 (마지막 직전 층에 상점 확정)
            for i in range(m):
                if i == m - 1:
                    row = []
                    for c in range(width):
                        t = run_data.NODE_SHOP if c == width // 2 else run_data.roll_node_type()
                        row.append(self._mk_node(t, c))
                    add(row, "normal")
                else:
                    add([self._mk_node(run_data.roll_node_type(), c) for c in range(width)], "normal")
            # 보스
            add([self._mk_node(run_data.NODE_BOSS, 0)], "boss")

        self._build_edges()
        self.cur_layer = 0   # 시작 지점에 서 있음
        self.cur_col = 0
        self.cleared_boss = False

    def _mk_node(self, ntype, col):
        return {"type": ntype, "col": col, "edges": []}

    def _build_edges(self):
        """좌→우로만 이동. 대각선·직선이 섞인 그물 형태로 연결.
        - 시작 노드(1개)는 다음 층 전체로 분기
        - 다음 층이 1개(보스/중간/마왕)면 모두 합류
        - 일반 층끼리는 같은 행 + 위/아래 대각(인접 행) 중 랜덤하게 1~2갈래
        - 모든 다음 노드가 진입 간선을 갖도록 보정 (고립 방지)
        """
        for li in range(len(self.layers) - 1):
            cur = self.layers[li]
            nxt = self.layers[li + 1]
            nlen = len(nxt)
            clen = len(cur)
            for node in cur:
                if nlen == 1:
                    # 다음 층이 1개(보스/중간/마왕) → 합류
                    node["edges"] = [0]
                elif clen == 1:
                    # 시작 노드 → 다음 층 전체로 분기
                    node["edges"] = list(range(nlen))
                else:
                    # 같은 행 + 위/아래 대각(인접 행) 후보
                    c = node["col"]
                    cand = [j for j in (c - 1, c, c + 1) if 0 <= j < nlen]
                    # 직진(같은 행)은 가중치를 높여 자주 나오게, 대각도 섞이게
                    random.shuffle(cand)
                    # 1~2개 랜덤 연결 (대각/직진 섞임)
                    k = 1 if random.random() < 0.55 else 2
                    k = min(k, len(cand))
                    chosen = set(cand[:k])
                    # 같은 행이 후보에 있으면 최소 한 번씩은 직진이 보장되도록 약간 보정
                    if c < nlen and random.random() < 0.5:
                        chosen.add(c)
                    node["edges"] = sorted(chosen)
            # 다음 층 노드 전부가 진입 간선을 갖도록 보정 (고립 노드 방지)
            reached = set()
            for node in cur:
                reached.update(node["edges"])
            for j in range(nlen):
                if j not in reached:
                    # 그 열에 가장 가까운 현재 노드에 간선 추가
                    best = min(range(clen), key=lambda ci: abs(cur[ci]["col"] - j))
                    cur[best]["edges"] = sorted(set(cur[best]["edges"]) | {j})

    # ── 노드 진행 ─────────────────────────────────────────────────
    def reachable_next(self):
        """현재 위치에서 진입 가능한 다음 노드들의 (layer, col) 목록."""
        if self.cur_layer >= len(self.layers) - 1:
            return []
        node = self.layers[self.cur_layer][self.cur_col]
        return [(self.cur_layer + 1, c) for c in node["edges"]]

    def node_at(self, layer, col):
        return self.layers[layer][col]

    def enter_node(self, layer, col):
        """노드 진입 → 현재 위치 갱신. 진입한 노드 타입 반환."""
        self.cur_layer = layer
        self.cur_col = col
        return self.layers[layer][col]["type"]

    def current_node(self):
        if 0 <= self.cur_layer < len(self.layers):
            return self.layers[self.cur_layer][self.cur_col]["type"]
        return None

    def advance_node(self):
        """현재 노드 완료 처리. 분기맵에서는 위치 이동을 enter_node 가 담당하므로
        여기서는 보스 클리어 등 종료 판정만 갱신."""
        if self.current_node() in (run_data.NODE_BOSS, run_data.NODE_MAW):
            self.cleared_boss = True

    def is_segment_done(self):
        """구간(또는 마왕성) 종료 = 마지막 층(보스/마왕) 클리어."""
        return self.cur_layer >= len(self.layers) - 1 and self.cleared_boss

    def is_boss_node(self):
        return self.current_node() in (run_data.NODE_BOSS, run_data.NODE_MAW)

    def current_role(self):
        """현재 층의 역할 태그 (start/mid/boss/maw/normal)."""
        if 0 <= self.cur_layer < len(getattr(self, "layer_role", [])):
            return self.layer_role[self.cur_layer]
        return "normal"

    def current_dialogue(self):
        """현재 지점(시작/중간/보스)의 다이얼로그 cuts. 없으면 None."""
        role = self.current_role()
        spot = {"start": "start", "mid": "mid", "boss": "boss", "maw": "boss"}.get(role)
        if spot is None:
            return None
        return run_data.dialogue_for(self.region, spot, self.cur_visit)

    def current_mid_boss(self):
        """중간 지점에 중간보스가 있으면 그 정의, 없으면 None. (encounter_data 배치)"""
        if self.current_role() != "mid":
            return None
        return encounter_data.mid_boss(self.region, self.cur_visit)

    # ── 파티 ──────────────────────────────────────────────────────
    def add_ally(self, name):
        if name not in self.party and len(self.party) < 5:
            self.party.append(name)
            return True
        return False

    def battle_party(self, temp=None):
        """전투 출전 명단 = 파티 + 임시동료. 최대 5."""
        names = list(self.party)
        for t in (temp or self.temp_allies):
            if t not in names and len(names) < 5:
                names.append(t)
        return names[:5]

    # ── 스킬 (영구 보존) ──────────────────────────────────────────
    def add_skill(self, skill):
        """스킬 획득. 같은 이름을 이미 알면 False. 획득 즉시 영구 저장."""
        if any(s["name"] == skill["name"] for s in self.skills_owned):
            return False
        self.skills_owned.append(skill)
        # 장착 여유 있으면 자동 장착
        if len(self.skills_equipped) < 10:
            self.skills_equipped.append(skill)
        self.save_skills()
        return True

    def save_skills(self):
        """현재 보유/장착 스킬을 영구 저장. 장착 구성이 바뀔 때마다 호출."""
        save_data.set_skills(self.skills_owned,
                             [s["name"] for s in self.skills_equipped])

    def can_equip_more(self):
        return len(self.skills_equipped) < 10

    # ── 아이템 ────────────────────────────────────────────────────
    MAX_ITEM_EQUIP = 10

    def add_item(self, key):
        """아이템 획득 → 보유에 추가. 장착 빈자리가 있으면 자동 장착."""
        if key not in run_data.ITEMS or key in self.items:
            return False
        self.items.append(key)
        if len(self.items_equipped) < self.MAX_ITEM_EQUIP and key not in self.items_equipped:
            self.items_equipped.append(key)
        save_data.set_items(self.items, self.items_equipped)
        self.refresh_hp_max()
        return True

    def equip_item(self, key):
        """아이템 장착 (최대 MAX_ITEM_EQUIP). 성공 시 True."""
        if key not in self.items or key in self.items_equipped:
            return False
        if len(self.items_equipped) >= self.MAX_ITEM_EQUIP:
            return False
        self.items_equipped.append(key)
        save_data.set_items(self.items, self.items_equipped)
        self.refresh_hp_max()
        return True

    def unequip_item(self, key):
        """아이템 장착 해제."""
        if key in self.items_equipped:
            self.items_equipped.remove(key)
            save_data.set_items(self.items, self.items_equipped)
            self.refresh_hp_max()
            return True
        return False

    def active_synergies(self):
        """현재 장착으로 완성된 시너지 목록."""
        return run_data.active_synergies(self.items_equipped)

    def item_effect_total(self, effect):
        """특정 effect 의 장착 아이템 값 합계 (시너지 추가 효과 포함)."""
        return run_data.item_effect_value(self.items_equipped, effect)

    def has_item_effect(self, effect):
        return run_data.item_effect_value(self.items_equipped, effect) != 0 or \
               any(run_data.ITEMS.get(k, {}).get("effect") == effect for k in self.items_equipped)

    # ── 자원 ──────────────────────────────────────────────────────
    def add_gold(self, amount):
        bonus = 1.0 + self.item_effect_total("gold_pct") / 100.0
        self.gold += int(amount * bonus)

    def spend_gold(self, amount):
        if self.gold < amount:
            return False
        self.gold -= amount
        return True

    def heal(self, pct):
        self.hp_cur = min(self.hp_max, self.hp_cur + int(self.hp_max * pct / 100.0))

    def full_heal(self):
        self.hp_cur = self.hp_max

    # ── 경험치 / 레벨 (영구) ──────────────────────────────────────
    def gain_exp(self, base_amount):
        """경험치 획득 → 레벨업 처리. 레벨업 횟수 반환."""
        bonus = 1.0 + self.item_effect_total("exp_pct") / 100.0
        amount = int(base_amount * bonus)
        g = save_data.get_growth("주인공")
        g["exp"] = g.get("exp", 0) + amount
        ups = 0
        while g["exp"] >= run_data.exp_to_next(g.get("level", 1)):
            g["exp"] -= run_data.exp_to_next(g.get("level", 1))
            g["level"] = g.get("level", 1) + 1
            # 레벨업 포인트 적립 (기초/부가 분리 저장)
            g["basic_point"] = g.get("basic_point", 0) + run_data.LEVELUP_BASIC_POINT
            g["extra_point"] = g.get("extra_point", 0) + run_data.LEVELUP_EXTRA_POINT
            ups += 1
        save_data.set_growth(g, "주인공")
        return ups

    def gain_levels(self, n):
        """레벨을 n 만큼 직접 올린다 (경험치 대신). 최대 LEVEL_CAP 까지만.
        레벨업당 분배 포인트(기초/부가) 지급. 실제로 오른 레벨 수 반환."""
        g = save_data.get_growth("주인공")
        ups = 0
        for _ in range(max(0, n)):
            if g.get("level", 1) >= run_data.LEVEL_CAP:
                break  # 최대 레벨 도달 — 더 오르지 않음
            g["level"] = g.get("level", 1) + 1
            g["basic_point"] = g.get("basic_point", 0) + run_data.LEVELUP_BASIC_POINT
            g["extra_point"] = g.get("extra_point", 0) + run_data.LEVELUP_EXTRA_POINT
            ups += 1
        save_data.set_growth(g, "주인공")
        return ups

    # ── 회차 종료 ─────────────────────────────────────────────────
    def end_run(self):
        """회차 종료: 휘발 상태 비활성화.
        레벨/포인트/스킬/아이템은 영구 보존(save_data), 골드/파티/HP만 휘발."""
        self.active = False
        self.boss_mode = None

    def is_normal_complete(self):
        """일반 모드 완료 = 5개 지역 모두 방문하고 마지막 보스까지 클리어."""
        return (len(self.visited_regions) >= len(run_data.MIDDLE_REGIONS)
                and self.segment >= run_data.FINAL_SEGMENT
                and self.cleared_boss)

    # ── 보스 모드 (도전/극한/최종 — 보스전만) ─────────────────────
    def start_boss_battle(self, tier, region):
        """보스 모드 시작: 맵 없이 보스전만. 진행(레벨/스킬/아이템)은 영구분을 그대로 사용.
        tier: 'challenge'/'extreme'/'final', region: 지역명(최종은 '마왕')."""
        self.active = True
        self.boss_mode = {"tier": tier, "region": region}
        self.segment = 0
        self.region = region
        self.visited_regions = []
        self.party = ["주인공"]
        self.temp_allies = []
        # 영구 스킬/아이템 로드 (일반 모드 시작과 동일)
        owned, equipped_names = save_data.get_skills()
        if not owned:
            owned = [copy.deepcopy(s) for s in run_data.STARTER_SKILLS]
            equipped_names = [s["name"] for s in owned]
            save_data.set_skills(owned, equipped_names)
        self.skills_owned = [copy.deepcopy(s) for s in owned]
        by_name = {s["name"]: s for s in self.skills_owned}
        self.skills_equipped = [by_name[n] for n in equipped_names if n in by_name][:10]
        if not self.skills_equipped:
            self.skills_equipped = list(self.skills_owned[:10])
        _it_owned, _it_eq = save_data.get_items()
        self.items = [k for k in _it_owned if k in run_data.ITEMS]
        self.items_equipped = [k for k in _it_eq if k in self.items][:self.MAX_ITEM_EQUIP]
        self.gold = 0
        self.hp_max = self._compute_hp_max()
        self.hp_cur = self.hp_max


# 전역 인스턴스 (한 게임에 하나)
RUN = RunState()