# 로그라이크 회차(런) 상태 관리
# 회차 동안의 휘발 상태: 구간 진행, 방문 지역, 파티, HP, 스킬, 아이템, 골드.
# 레벨/경험치/분배 포인트는 save_data(영구)에서 가져온다.

import random
import save_data
from data import run_data


class RunState:
    """한 회차의 진행 상태."""

    def __init__(self):
        self.active = False
        self.segment = 0            # 현재 구간 번호 (1~6)
        self.last_region = None     # 직전에 방문한 지역 (연속 방문 금지용)
        self.region = None          # 현재 구간 지역
        self.layers = []            # 분기 노드맵: 층별 노드 리스트
        self.cur_layer = -1         # 현재 위치 층 (-1=시작 전)
        self.cur_col = 0            # 현재 위치 열
        self.cleared_boss = False   # 현재 구간 보스 클리어 여부

        # 파티: 주인공 + 합류 동료 이름들 (최대 5)
        self.party = ["주인공"]
        self.temp_allies = []       # 특정 전투 한정 동료 (전투 후 제거)

        # 주인공 보유 스킬(획득 무제한) / 장착 스킬(최대 10)
        self.skills_owned = []      # dict 리스트
        self.skills_equipped = []   # dict 리스트 (최대 10)

        # 아이템(무제한 장착)
        self.items = []             # 아이템 키 리스트

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
        self.party = ["주인공"]
        self.temp_allies = []
        # 시작 스킬 (물리1 + 마법1)
        import copy
        self.skills_owned = [copy.deepcopy(s) for s in run_data.STARTER_SKILLS]
        self.skills_equipped = [copy.deepcopy(s) for s in run_data.STARTER_SKILLS]
        self.items = []
        self.gold = 0
        # 주인공 최대 HP (레벨 성장 반영)
        self.hp_max = self._compute_hp_max()
        self.hp_cur = self.hp_max

    def _compute_hp_max(self):
        """주인공 최대 HP = 기본 + 부가포인트(체력) 반영 + 아이템 hp_flat."""
        from data.characters_data import ALLY_DEFS
        base = ALLY_DEFS["주인공"].get("hp_max", 100)
        g = save_data.get_growth("주인공")
        hp_bonus = g.get("hp_bonus", 0) * 10   # 체력 1포인트당 +10 (기존 규칙)
        item_hp = sum(run_data.ITEMS[k]["value"] for k in self.items
                      if run_data.ITEMS[k]["effect"] == "hp_flat")
        return base + hp_bonus + item_hp

    def refresh_hp_max(self):
        """아이템/성장 변화 후 최대 HP 갱신 (현재 HP 비율 유지)."""
        old_max = max(1, self.hp_max)
        ratio = self.hp_cur / old_max
        self.hp_max = self._compute_hp_max()
        self.hp_cur = int(self.hp_max * ratio)

    # ── 지역 선택 ─────────────────────────────────────────────────
    def selectable_regions(self):
        """이번 구간에 고를 수 있는 지역 (직전 지역 제외)."""
        if self.segment + 1 >= run_data.FINAL_SEGMENT:
            return []  # 마왕성은 선택 불가
        return [r for r in run_data.REGIONS if r != self.last_region]

    def enter_region(self, region):
        """지역을 골라 다음 구간 진입. 분기 노드맵 생성."""
        self.segment += 1
        self.region = region
        count = run_data.SEGMENT_NODE_COUNT.get(self.segment, 6)
        self._build_map(layers=count, width=3, final=False)

    def enter_maw(self):
        """6구간 마왕성 진입. 4갈래."""
        self.segment = run_data.FINAL_SEGMENT
        self.region = "마왕성"
        # 마왕성: 첫 층 + 중간 층(4갈래) + 보스 + 마왕
        self._build_map(layers=4, width=4, final=True)

    def _build_map(self, layers, width, final):
        """슬더스식 분기 노드맵 생성.
        layers: 층 수 (보스/마왕 포함). 첫 층=1개, 마지막 직전까지 width개.
        width: 중간 층의 노드 개수 (구간 3, 마왕성 4).
        final: True 면 마지막 두 층 = 보스 + 마왕, False 면 마지막 = 보스.
        self.layers: [[Node,...], ...] / 각 Node = {"type","col","edges":[다음층 col 인덱스]}
        self.cur_layer, self.cur_col: 현재 위치(아직 진입 전엔 (-1, 0) = 시작 전)
        """
        self.layers = []
        n = max(2, layers)
        for li in range(n):
            if li == 0:
                # 시작 층: 1개 (전투 추천이지만 첫 노드는 일반)
                row = [self._mk_node(run_data.NODE_BATTLE, 0)]
            elif final and li == n - 1:
                row = [self._mk_node(run_data.NODE_MAW, 0)]
            elif li == n - 1:
                row = [self._mk_node(run_data.NODE_BOSS, 0)]
            elif final and li == n - 2:
                # 마왕성 보스 선택 층 (width 갈래, 각 보스)
                row = [self._mk_node(run_data.NODE_BOSS, c) for c in range(width)]
            elif li == n - 2 and not final:
                # 구간: 보스 직전 층은 상점 포함 (한 칸은 상점 확정)
                row = []
                for c in range(width):
                    t = run_data.NODE_SHOP if c == width // 2 else run_data.roll_node_type()
                    row.append(self._mk_node(t, c))
            else:
                row = [self._mk_node(run_data.roll_node_type(), c) for c in range(width)]
            self.layers.append(row)

        # 연결(edges) 생성: 각 노드를 다음 층의 인접 노드와 연결
        self._build_edges()

        self.cur_layer = -1   # 아직 어떤 노드도 안 밟음 (시작 전)
        self.cur_col = 0
        # 진행 가능한 후보 = 0층 노드들
        self.cleared_boss = False

    def _mk_node(self, ntype, col):
        return {"type": ntype, "col": col, "edges": []}

    def _build_edges(self):
        """슬더스식 부분 연결: 각 노드는 다음 층의 col-1/col/col+1 중 일부와 연결.
        모든 다음 층 노드가 최소 1개의 진입 간선을 갖도록 보정."""
        import random
        for li in range(len(self.layers) - 1):
            cur = self.layers[li]
            nxt = self.layers[li + 1]
            nlen = len(nxt)
            clen = len(cur)
            for node in cur:
                if nlen == 1:
                    node["edges"] = [0]
                    continue
                if clen == 1:
                    # 시작 노드는 다음 층 전부로 분기
                    node["edges"] = list(range(nlen))
                    continue
                # 비율로 대응되는 위치 ± 인접
                center = round(node["col"] / max(1, clen - 1) * (nlen - 1))
                cands = sorted({max(0, center - 1), center, min(nlen - 1, center + 1)})
                # 1~2개 랜덤 선택
                k = random.choice([1, 2]) if len(cands) > 1 else 1
                node["edges"] = sorted(random.sample(cands, min(k, len(cands))))
            # 다음 층 노드 전부가 진입 간선을 갖도록 보정
            reached = set()
            for node in cur:
                reached.update(node["edges"])
            for j in range(nlen):
                if j not in reached:
                    # 가장 가까운 cur 노드에 연결 추가
                    best = min(range(clen), key=lambda ci: abs(
                        round(cur[ci]["col"] / max(1, clen - 1) * (nlen - 1)) - j))
                    cur[best]["edges"] = sorted(set(cur[best]["edges"]) | {j})

    # ── 노드 진행 ─────────────────────────────────────────────────
    def reachable_next(self):
        """현재 위치에서 진입 가능한 다음 노드들의 (layer, col) 목록."""
        if self.cur_layer < 0:
            # 시작 전 → 0층 전부 진입 가능
            return [(0, c) for c in range(len(self.layers[0]))]
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

    # ── 스킬 ──────────────────────────────────────────────────────
    def add_skill(self, skill):
        self.skills_owned.append(skill)
        # 장착 여유 있으면 자동 장착
        if len(self.skills_equipped) < 10:
            self.skills_equipped.append(skill)

    def can_equip_more(self):
        return len(self.skills_equipped) < 10

    # ── 아이템 ────────────────────────────────────────────────────
    def add_item(self, key):
        if key not in self.items:
            self.items.append(key)
            self.refresh_hp_max()
            return True
        return False

    def item_effect_total(self, effect):
        """특정 effect 의 아이템 값 합계."""
        return sum(run_data.ITEMS[k]["value"] for k in self.items
                   if run_data.ITEMS[k]["effect"] == effect)

    def has_item_effect(self, effect):
        return any(run_data.ITEMS[k]["effect"] == effect for k in self.items)

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

    # ── 회차 종료 ─────────────────────────────────────────────────
    def end_run(self):
        """회차 종료: 휘발 상태 초기화. 레벨/경험치/포인트는 save_data 에 남음."""
        self.active = False


# 전역 인스턴스 (한 게임에 하나)
RUN = RunState()