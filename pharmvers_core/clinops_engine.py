import math

class SyntheticTrialSimulator:
    """
    Simulates in-silico clinical trials using patient digital twins.

    Implements:
        1. Nearest-Neighbour Propensity Score Matching over normalised covariates
           to construct a Synthetic Control Arm (SCA) from a real-world patient pool.
        2. Kaplan-Meier non-parametric survival estimator for treatment efficacy
           assessment without a live placebo arm.

    Mathematical basis:
        Distance: d(i,j) = sqrt((age_i - age_j)² + (bio_i - bio_j)²)  [normalised]
        KM:       Ŝ(t) = ∏_{tᵢ ≤ t} (1 - dᵢ/nᵢ)

    Regulatory reference: FDA Guidance on Real-World Evidence (2019), ICH E9(R1).
    """

    def __init__(self):
        pass

    # ── Covariate Normalisation ─────────────────────────────────────────
    def normalize_covariates(self, patients):
        """
        Normalises age and biomarker values to [0, 1] range using min-max scaling,
        ensuring both covariates contribute equally to distance calculations.

        Args:
            patients: list of dicts with keys 'id', 'age', 'biomarker'

        Returns:
            list of dicts with additional keys 'norm_age', 'norm_biomarker'
        """
        if not patients:
            return []

        ages       = [p["age"]       for p in patients]
        biomarkers = [p["biomarker"] for p in patients]

        age_range = max(1.0,     max(ages)       - min(ages))
        bio_range = max(0.0001,  max(biomarkers) - min(biomarkers))

        normalized = []
        for p in patients:
            norm_p = p.copy()
            norm_p["norm_age"]       = (p["age"]       - min(ages))       / age_range
            norm_p["norm_biomarker"] = (p["biomarker"] - min(biomarkers)) / bio_range
            normalized.append(norm_p)

        return normalized

    # ── Nearest-Neighbour Matching ──────────────────────────────────────
    def match_synthetic_control(self, treatment_group, raw_pool, match_limit=1):
        """
        Constructs a Synthetic Control Arm by selecting the closest control patient
        for each treatment patient using Euclidean distance on normalised covariates.
        Each control patient can only be matched once (greedy 1:1 matching).

        Args:
            treatment_group: list of treatment patient dicts
            raw_pool:        list of candidate control patient dicts
            match_limit:     matches per treatment patient (default: 1)

        Returns:
            list of matched control patient dicts (same format as raw_pool)
        """
        combined      = self.normalize_covariates(treatment_group + raw_pool)
        norm_treatment = combined[:len(treatment_group)]
        norm_pool      = combined[len(treatment_group):]

        matched_control = []
        used_pool_ids   = set()

        for t_pat in norm_treatment:
            best_match = None
            min_dist   = float("inf")

            for p_pat in norm_pool:
                if p_pat["id"] in used_pool_ids:
                    continue
                dist = math.sqrt(
                    (t_pat["norm_age"]       - p_pat["norm_age"])       ** 2 +
                    (t_pat["norm_biomarker"] - p_pat["norm_biomarker"]) ** 2
                )
                if dist < min_dist:
                    min_dist   = dist
                    best_match = p_pat

            if best_match:
                matched_control.append(best_match)
                used_pool_ids.add(best_match["id"])

        return matched_control

    # ── Kaplan-Meier Estimator ──────────────────────────────────────────
    def calculate_kaplan_meier(self, group_events):
        """
        Computes the Kaplan-Meier survival probability curve.

        Args:
            group_events: list of tuples (time_to_event: float, event_occurred: int)
                          event_occurred=1 means the event (e.g. progression) happened;
                          event_occurred=0 means the observation was censored.

        Returns:
            list of dicts with keys:
                'time'                 — the event time point
                'survival_probability' — Ŝ(t) at this time
                'prob'                 — alias for survival_probability (compatibility)
                'at_risk'              — number of patients at risk before this step
        """
        if not group_events:
            return []

        sorted_events  = sorted(group_events, key=lambda x: x[0])
        n_at_risk      = len(sorted_events)
        survival_prob  = 1.0
        curve          = []

        unique_times = sorted(set(e[0] for e in sorted_events))

        for t in unique_times:
            events_at_t  = [e for e in sorted_events if e[0] == t]
            d_i          = sum(e[1] for e in events_at_t)  # event count at t

            if n_at_risk > 0:
                survival_prob *= (1.0 - (d_i / n_at_risk))

            curve.append({
                "time":                 t,
                "survival_probability": round(survival_prob, 6),
                "prob":                 round(survival_prob, 6),   # compatibility alias
                "at_risk":              n_at_risk,
            })

            n_at_risk -= len(events_at_t)

        return curve
