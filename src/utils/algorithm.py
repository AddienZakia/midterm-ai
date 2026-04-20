"""
tmk_algorithm.py
================
TMK Genocide Risk Framework — A* + ACO
Satu class TMKFramework yang encapsulate seluruh pipeline:
  1. Load & bersihkan dataset
  2. Hitung A* escalation path per episode
  3. Jalankan ACO regional contagion
  4. Gabungkan → combined risk tier

Revisi yang diterapkan:
  - Zimbabwe dipindah ke Southern Africa (bukan Central Africa)
  - South Asia dan Southeast Asia dipisah jadi 2 region berbeda
  - Equatorial Guinea dipindah ke West Africa
  - Trig_inst_perp di-fillna(0) sebelum groupby (sudah benar)
"""

import heapq
import math
import random
from collections import defaultdict
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional

try:
    import pandas as pd
except ImportError:
    raise ImportError("Butuh pandas. Jalankan: pip install pandas openpyxl xlrd")


# ---------------------------------------------------------------------------
# REGION MAP — 63 negara → region
# Revisi: Zimbabwe → Southern Africa, Equatorial Guinea → West Africa,
#         South & SE Asia dipisah jadi South Asia + Southeast Asia
# ---------------------------------------------------------------------------
REGION_MAP: dict[str, str] = {
    # Central Africa
    "Angola":                   "Central Africa",
    "Burundi":                  "Central Africa",
    "Central African Republic": "Central Africa",
    "Chad":                     "Central Africa",
    "Congo":                    "Central Africa",
    "DR Congo (Zaire)":         "Central Africa",
    "Rwanda":                   "Central Africa",
    "Uganda":                   "Central Africa",

    # East Africa
    "Ethiopia":                 "East Africa",
    "Kenya":                    "East Africa",
    "Somalia":                  "East Africa",
    "South Sudan":              "East Africa",
    "Sudan":                    "East Africa",
    "Tanzania (Zanzibar)":      "East Africa",
    "Zanzibar":                 "East Africa",

    # West Africa
    "Burkina Faso":             "West Africa",
    "Equatorial Guinea":        "West Africa",
    "Ivory Coast":              "West Africa",
    "Liberia":                  "West Africa",
    "Mali":                     "West Africa",
    "Nigeria":                  "West Africa",

    # Southern Africa (revisi: Zimbabwe dipindah ke sini)
    "Mozambique":               "Southern Africa",
    "Zimbabwe":                 "Southern Africa",

    # MENA
    "Algeria":                  "MENA",
    "Egypt":                    "MENA",
    "Iran":                     "MENA",
    "Iraq":                     "MENA",
    "Israel":                   "MENA",
    "Lebanon":                  "MENA",
    "Libya":                    "MENA",
    "Syria":                    "MENA",

    # Europe / Balkans
    "Bosnia-Herzegovina":       "Europe",
    "Croatia":                  "Europe",
    "Cyprus":                   "Europe",
    "Rumania":                  "Europe",
    "Russia (Soviet Union)":    "Europe",
    "Serbia (Yugoslavia)":      "Europe",
    "Soviet Union":             "Europe",
    "Ukraine":                  "Europe",
    "Uzbekistan":               "Europe",

    # Latin America
    "Argentina":                "Latin America",
    "Chile":                    "Latin America",
    "Colombia":                 "Latin America",
    "El Salvador":              "Latin America",
    "Guatemala":                "Latin America",
    "Haiti":                    "Latin America",
    "Mexico":                   "Latin America",
    "Peru":                     "Latin America",

    # South Asia (revisi: dipisah dari Southeast Asia)
    "Afghanistan":              "South Asia",
    "Bangladesh":               "South Asia",
    "India":                    "South Asia",
    "Pakistan":                 "South Asia",
    "Sri Lanka":                "South Asia",

    # Southeast Asia (revisi: dipisah dari South Asia)
    "Cambodia (Kampuchea)":     "Southeast Asia",
    "Indonesia":                "Southeast Asia",
    "Laos":                     "Southeast Asia",
    "Myanmar (Burma)":          "Southeast Asia",
    "North Vietnam":            "Southeast Asia",
    "Philippines":              "Southeast Asia",
    "South Vietnam":            "Southeast Asia",
    "Taiwan":                   "Southeast Asia",

    # East Asia
    "China":                    "East Asia",
    "North Korea":              "East Asia",
    "South Korea":              "East Asia",

    # Caucasus
    "Azerbaijan":               "Caucasus",
}

# ---------------------------------------------------------------------------
# Konstanta
# ---------------------------------------------------------------------------
DEATHS_MAX_REF  = 3_500_000.0
REFERENCE_YEAR  = 2022
GOAL_LEVEL      = 4

RISK_MATRIX: dict[tuple, str] = {
    ("CRITICAL", "HOT"):  "CRITICAL",
    ("CRITICAL", "WARM"): "CRITICAL",
    ("CRITICAL", "COOL"): "CRITICAL",
    ("HIGH",     "HOT"):  "CRITICAL",
    ("HIGH",     "WARM"): "HIGH",
    ("HIGH",     "COOL"): "HIGH",
    ("MEDIUM",   "HOT"):  "HIGH",
    ("MEDIUM",   "WARM"): "MEDIUM",
    ("MEDIUM",   "COOL"): "MEDIUM",
    ("LOW",      "HOT"):  "MEDIUM",
    ("LOW",      "WARM"): "LOW",
    ("LOW",      "COOL"): "LOW",
}

RECOMMENDATIONS: dict[str, str] = {
    "CRITICAL": "Intervensi segera — eskalasi aktif ≥ L4, contagion regional tinggi.",
    "HIGH":     "Monitoring intensif — dekat threshold atau cluster regional berisiko.",
    "MEDIUM":   "Pengawasan berkala — ada sinyal risiko, pantau tiap kuartal.",
    "LOW":      "Monitoring standar — risiko terkontrol, laporan rutin.",
}

TIER_ORDER: dict[str, int] = {"CRITICAL": 4, "HIGH": 3, "MEDIUM": 2, "LOW": 1}


# ---------------------------------------------------------------------------
# Data class untuk satu hasil episode
# ---------------------------------------------------------------------------
@dataclass
class EpisodeResult:
    tmk_id:          str
    country:         str
    actor:           str
    region:          str
    onset_year:      int
    ordinal:         int
    ordinal_max:     int
    total_deaths:    int
    deaths_norm:     float
    risk_score:      float
    edge_weight:     float
    astar_path:      list[int]
    astar_cost:      float
    risk_search:     str
    pheromone:       float
    contagion_tier:  str
    combined_risk:   str
    recommendation:  str
    genpol_onset:    int
    duration:        float


# ---------------------------------------------------------------------------
# TMKFramework — class utama
# ---------------------------------------------------------------------------
class TMKFramework:
    """
    Pipeline lengkap TMK Risk Analysis menggunakan A* + ACO.

    Cara pakai:
        fw = TMKFramework(events_path, annual_path)
        fw.run()
        results = fw.results        # list[EpisodeResult]
        stats   = fw.get_stats()    # dict ringkasan statistik
    """

    def __init__(
        self,
        events_path:  str,
        annual_path:  str,
        aco_n_iter:   int   = 100,
        aco_n_ants:   int   = 50,
        aco_n_steps:  int   = 5,
        aco_top_k:    int   = 10,
        aco_rho:      float = 0.1,
        aco_alpha:    float = 3.0,
        aco_seed:     int   = 42,
    ):
        self.events_path = events_path
        self.annual_path = annual_path

        # ACO hyperparameters
        self._aco_params = dict(
            n_iter=aco_n_iter, n_ants=aco_n_ants, n_steps=aco_n_steps,
            top_k=aco_top_k, rho=aco_rho, alpha=aco_alpha, seed=aco_seed,
        )

        self._episodes:    Optional[pd.DataFrame] = None
        self._tau_final:   dict[str, float]        = {}
        self._neighbors:   dict[str, list]         = {}
        self.results:      list[EpisodeResult]     = []
        self._ran          = False

    # ── public API ──────────────────────────────────────────────────────

    def run(self) -> list[EpisodeResult]:
        """Jalankan full pipeline. Kembalikan list EpisodeResult."""
        self._episodes = self._load_events()
        self._build_aco_structures()
        self._run_aco()
        self._run_astar_all()
        self._ran = True
        return self.results

    def get_stats(self) -> dict:
        """Kembalikan dict statistik ringkasan untuk ditampilkan di GUI."""
        if not self._ran:
            raise RuntimeError("Panggil run() terlebih dahulu.")

        n = len(self.results)
        dist = {t: 0 for t in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]}
        for r in self.results:
            dist[r.combined_risk] += 1

        genpol    = [r for r in self.results if r.genpol_onset == 1]
        gp_hit    = [r for r in genpol if r.combined_risk in ("CRITICAL", "HIGH")]
        accuracy  = len(gp_hit) / len(genpol) * 100 if genpol else 0

        avg_cost  = sum(r.astar_cost for r in self.results) / n
        avg_phero = sum(r.pheromone  for r in self.results) / n

        # top 10 per combined_risk (ordinal tertinggi dulu)
        top10_critical = sorted(
            [r for r in self.results if r.combined_risk == "CRITICAL"],
            key=lambda x: (-x.ordinal, -x.pheromone)
        )[:10]

        # pheromone per negara (max dari semua episode negara itu)
        country_phero: dict[str, float] = {}
        for r in self.results:
            if r.country not in country_phero or r.pheromone > country_phero[r.country]:
                country_phero[r.country] = r.pheromone
        top10_phero = sorted(country_phero.items(), key=lambda x: -x[1])[:10]

        # region breakdown
        region_data: dict[str, dict] = {}
        for r in self.results:
            if r.region not in region_data:
                region_data[r.region] = {t: 0 for t in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]}
                region_data[r.region]["total"] = 0
            region_data[r.region][r.combined_risk] += 1
            region_data[r.region]["total"] += 1

        return {
            "n_episodes":      n,
            "distribution":    dist,
            "genpol_total":    len(genpol),
            "genpol_hit":      len(gp_hit),
            "accuracy":        round(accuracy, 1),
            "avg_astar_cost":  round(avg_cost, 4),
            "avg_pheromone":   round(avg_phero, 4),
            "top10_critical":  top10_critical,
            "top10_pheromone": top10_phero,
            "region_breakdown":region_data,
        }

    def get_regions(self) -> list[str]:
        """Kembalikan list region yang ada di results."""
        return sorted(set(r.region for r in self.results))

    def get_countries(self) -> list[str]:
        """Kembalikan list negara unik dari results."""
        return sorted(set(r.country for r in self.results))

    def filter(
        self,
        region:      Optional[str] = None,
        country:     Optional[str] = None,
        risk_type:   Optional[str] = None,
        search_text: Optional[str] = None,
    ) -> list[EpisodeResult]:
        """Filter results berdasarkan kriteria. None = tidak difilter."""
        out = self.results
        if region:
            out = [r for r in out if r.region == region]
        if country:
            out = [r for r in out if r.country == country]
        if risk_type:
            out = [r for r in out if r.combined_risk == risk_type]
        if search_text:
            q = search_text.lower()
            out = [r for r in out if q in r.country.lower()
                   or q in r.actor.lower() or q in r.tmk_id.lower()]
        return out

    # ── private: data loading ────────────────────────────────────────────

    def _load_events(self) -> pd.DataFrame:
        raw = pd.read_excel(self.events_path, sheet_name=0)
        raw.columns = raw.columns.str.strip()

        raw["trig.inst.perp"] = pd.to_numeric(
            raw["trig.inst.perp"], errors="coerce"
        ).fillna(0)
        raw["total.deaths"] = pd.to_numeric(
            raw["total.deaths"], errors="coerce"
        ).fillna(0)

        raw["onset_year"] = pd.to_datetime(
            raw["tmk.st"], errors="coerce"
        ).dt.year
        mask = raw["onset_year"].isna()
        raw.loc[mask, "onset_year"] = raw.loc[mask, "year"]
        raw["onset_year"] = raw["onset_year"].fillna(raw["year"]).astype(int)

        raw_sorted  = raw.sort_values("year")
        onset_rows  = raw_sorted.groupby("tmk_id").first().reset_index()

        ep = pd.DataFrame({
            "tmk_id":         onset_rows["tmk_id"],
            "country":        onset_rows["primary.location"],
            "actor":          onset_rows["actor.name"],
            "onset_year":     onset_rows["onset_year"].astype(int),
            "ordinal":        onset_rows["tmk.ordinal"].astype(int),
            "ordinal_max":    onset_rows["tmk.ordinal.max"].astype(int),
            "total_deaths":   onset_rows["total.deaths"].astype(float),
            "intent_4a":      onset_rows["intent.4a.any"].astype(int),
            "trig_inst_perp": onset_rows["trig.inst.perp"].astype(int),
            "genpol_onset":   onset_rows["genpol.onset"].astype(int),
            "duration":       onset_rows["duration"].astype(float),
        })

        ep["region"] = ep["country"].map(REGION_MAP).fillna("Other")
        ep = ep[ep["total_deaths"] >= 0].reset_index(drop=True)
        return ep

    # ── private: ACO ────────────────────────────────────────────────────

    def _build_aco_structures(self):
        region_map_data = dict(zip(
            self._episodes["country"],
            self._episodes["region"]
        ))
        for c, r in REGION_MAP.items():
            if c not in region_map_data:
                region_map_data[c] = r

        self._neighbors = self._build_neighbors(region_map_data)
        self._tau_init  = self._init_pheromone()

    @staticmethod
    def _build_neighbors(region_map: dict) -> dict:
        by_region: dict[str, list] = defaultdict(list)
        for c, r in region_map.items():
            by_region[r].append(c)
        return {
            c: [x for x in by_region[r] if x != c]
            for c, r in region_map.items()
        }

    def _init_pheromone(self) -> dict[str, float]:
        tau_raw: dict[str, float] = defaultdict(float)
        for _, row in self._episodes.iterrows():
            dn    = self._deaths_norm(row["total_deaths"])
            age   = max(0, REFERENCE_YEAR - int(row["onset_year"]))
            decay = math.exp(-0.015 * age)
            tau_ep = (row["ordinal_max"] / 8.0) * dn * decay
            tau_raw[row["country"]] += tau_ep

        max_tau = max(tau_raw.values()) if tau_raw else 1.0
        return {c: v / max_tau for c, v in tau_raw.items()}

    def _run_aco(self):
        p = self._aco_params
        rng       = random.Random(p["seed"])
        tau       = dict(self._tau_init)
        countries = list(tau.keys())

        for _ in range(p["n_iter"]):
            trails = []

            for _ in range(p["n_ants"]):
                start   = rng.choice(countries)
                trail   = [start]
                score   = tau.get(start, 0.0)
                visited = {start}

                for _ in range(p["n_steps"]):
                    nbrs = [
                        n for n in self._neighbors.get(trail[-1], [])
                        if n not in visited and n in tau
                    ]
                    if not nbrs:
                        break

                    weights = [tau[n] ** p["alpha"] for n in nbrs]
                    total_w = sum(weights)

                    if total_w <= 0:
                        nxt = rng.choice(nbrs)
                    else:
                        r_val, acc = rng.random() * total_w, 0.0
                        nxt = nbrs[-1]
                        for n, wt in zip(nbrs, weights):
                            acc += wt
                            if acc >= r_val:
                                nxt = n
                                break

                    trail.append(nxt)
                    score   += tau.get(nxt, 0.0)
                    visited.add(nxt)

                trails.append((trail, score))

            # Evaporasi
            for c in tau:
                tau[c] *= (1.0 - p["rho"])

            # Deposit top-k
            for trail, score in sorted(trails, key=lambda x: -x[1])[:p["top_k"]]:
                deposit = score / len(trail)
                for c in trail:
                    tau[c] = min(1.0, tau[c] + deposit)

        self._tau_final = tau

    # ── private: A* ─────────────────────────────────────────────────────

    def _run_astar_all(self):
        self.results = []
        for _, ep in self._episodes.iterrows():
            ep_dict = ep.to_dict()
            ar      = self._astar(ep_dict)
            phi     = self._tau_final.get(ep_dict["country"], 0.0)
            ct      = self._classify_contagion(phi)
            cr      = RISK_MATRIX.get((ar["risk_search"], ct), "LOW")

            self.results.append(EpisodeResult(
                tmk_id         = ep_dict["tmk_id"],
                country        = ep_dict["country"],
                actor          = ep_dict["actor"],
                region         = ep_dict["region"],
                onset_year     = int(ep_dict["onset_year"]),
                ordinal        = int(ep_dict["ordinal"]),
                ordinal_max    = int(ep_dict["ordinal_max"]),
                total_deaths   = int(ep_dict["total_deaths"]),
                deaths_norm    = ar["deaths_norm"],
                risk_score     = ar["risk_score"],
                edge_weight    = ar["edge_weight"],
                astar_path     = ar["path"],
                astar_cost     = round(ar["cost"], 4),
                risk_search    = ar["risk_search"],
                pheromone      = round(phi, 4),
                contagion_tier = ct,
                combined_risk  = cr,
                recommendation = RECOMMENDATIONS[cr],
                genpol_onset   = int(ep_dict["genpol_onset"]),
                duration       = float(ep_dict["duration"]),
            ))

    def _astar(self, ep: dict) -> dict:
        start = int(ep["ordinal"])
        w     = self._edge_weight(ep)
        dn    = self._deaths_norm(ep["total_deaths"])
        rs    = dn + ep["intent_4a"] + ep["trig_inst_perp"]

        if start >= GOAL_LEVEL:
            return {
                "path":        [start],
                "cost":        0.0,
                "risk_search": "CRITICAL",
                "edge_weight": round(w, 4),
                "deaths_norm": round(dn, 4),
                "risk_score":  round(rs, 4),
            }

        open_set: list = []
        heapq.heappush(
            open_set,
            (self._heuristic(start), 0.0, start, [start])
        )
        visited: dict[int, float] = {}

        while open_set:
            f, g, node, path = heapq.heappop(open_set)

            if node == GOAL_LEVEL:
                return {
                    "path":        path,
                    "cost":        g,
                    "risk_search": self._classify_risk(start, g),
                    "edge_weight": round(w, 4),
                    "deaths_norm": round(dn, 4),
                    "risk_score":  round(rs, 4),
                }

            if node in visited:
                continue
            visited[node] = g

            nxt = node + 1
            if nxt <= 8:
                g2 = g + w
                f2 = g2 + self._heuristic(nxt)
                heapq.heappush(open_set, (f2, g2, nxt, path + [nxt]))

        return {
            "path":        [start],
            "cost":        float("inf"),
            "risk_search": "LOW",
            "edge_weight": round(w, 4),
            "deaths_norm": round(dn, 4),
            "risk_score":  round(rs, 4),
        }

    # ── private: helpers ────────────────────────────────────────────────

    @staticmethod
    def _deaths_norm(deaths: float) -> float:
        return math.log(deaths + 1) / math.log(DEATHS_MAX_REF + 1)

    @staticmethod
    def _edge_weight(ep: dict) -> float:
        rs = (
            TMKFramework._deaths_norm(ep["total_deaths"])
            + ep["intent_4a"]
            + ep["trig_inst_perp"]
        )
        return 1.0 / (rs + 0.1)

    @staticmethod
    def _heuristic(level: int, goal: int = GOAL_LEVEL) -> float:
        return float(max(0, goal - level))

    @staticmethod
    def _classify_risk(start: int, cost: float) -> str:
        if start >= 4:
            return "CRITICAL"
        if start == 3:
            return "CRITICAL" if cost < 0.5 else "HIGH"
        if cost < 1.5:
            return "HIGH"
        if cost <= 4.0:
            return "MEDIUM"
        return "LOW"

    @staticmethod
    def _classify_contagion(tau_val: float) -> str:
        if tau_val > 0.7:
            return "HOT"
        if tau_val >= 0.3:
            return "WARM"
        return "COOL"