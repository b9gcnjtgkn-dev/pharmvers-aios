import math

class SyntheticTrialSimulator:
    """
    Simulates in-silico clinical trials using patient digital twins, performs Propensity Score
    matching over patient baseline features, and computes Kaplan-Meier survival curves.
    """
    def __init__(self):
        pass

    def normalize_covariates(self, patients):
        """
        Normalizes age and biomarker values to a [0, 1] range to ensure fair distance calculation.
        """
        if not patients:
            return []
        
        ages = [p["age"] for p in patients]
        biomarkers = [p["biomarker"] for p in patients]
        
        min_age, max_age = min(ages), max(ages)
        min_bio, max_bio = min(biomarkers), max(biomarkers)
        
        age_range = max(1.0, max_age - min_age)
        bio_range = max(0.001, max_bio - min_bio)
        
        normalized = []
        for p in patients:
            norm_p = p.copy()
            norm_p["norm_age"] = (p["age"] - min_age) / age_range
            norm_p["norm_biomarker"] = (p["biomarker"] - min_bio) / bio_range
            normalized.append(norm_p)
            
        return normalized

    def match_synthetic_control(self, treatment_group, raw_pool, match_limit=1):
        """
        Performs Nearest-Neighbor matching over normalized age and biomarker covariates
        to select a balanced Synthetic Control Arm (SCA) from the raw patient pool.
        """
        # Normalize all candidates together to ensure consistent scale
        combined = self.normalize_covariates(treatment_group + raw_pool)
        
        norm_treatment = combined[:len(treatment_group)]
        norm_pool = combined[len(treatment_group):]
        
        matched_control = []
        used_pool_ids = set()
        
        for t_pat in norm_treatment:
            best_match = None
            min_dist = float('inf')
            
            for p_pat in norm_pool:
                if p_pat["id"] in used_pool_ids:
                    continue
                
                # Calculate Euclidean distance over normalized covariates
                dist = math.sqrt(
                    math.pow(t_pat["norm_age"] - p_pat["norm_age"], 2) +
                    math.pow(t_pat["norm_biomarker"] - p_pat["norm_biomarker"], 2)
                )
                
                if dist < min_dist:
                    min_dist = dist
                    best_match = p_pat
            
            if best_match:
                matched_control.append(best_match)
                used_pool_ids.add(best_match["id"])
                
        return matched_control

    def calculate_kaplan_meier(self, group_events):
        """
        Calculates the Kaplan-Meier survival probability curve for a cohort.
        group_events is a list of tuples: (time_to_event, event_occurred [0 or 1])
        """
        if not group_events:
            return []
        
        # Sort events by time
        sorted_events = sorted(group_events, key=lambda x: x[0])
        
        n_at_risk = len(sorted_events)
        survival_prob = 1.0
        curve = []
        
        # Group events by unique time points
        unique_times = sorted(list(set([e[0] for e in sorted_events])))
        
        for t in unique_times:
            # Count events and censorings at time t
            events_at_t = [e for e in sorted_events if e[0] == t]
            d_i = sum([e[1] for e in events_at_t]) # Number of deaths/events
            
            # Update survival probability
            if n_at_risk > 0:
                survival_prob *= (1.0 - (d_i / n_at_risk))
            
            curve.append({"time": t, "survival_probability": survival_prob, "at_risk": n_at_risk})
            
            # Decrease risk count by the total number of events/censorings at time t
            n_at_risk -= len(events_at_t)
            
        return curve
