import math

class BioreactorPATController:
    """
    Continuous manufacturing controller implementing real-time Process Analytical
    Technology (PAT). Executes PID closed-loop feeder rate adjustments and
    calculates Hotelling's T² statistic for Real-Time Release Testing (RTRT).

    Mathematical basis:
        PID: u(t) = Kp*e(t) + Ki*∫e(t)dt + Kd*(de/dt)
        T²:  T² = d^T * S⁻¹ * d  where d = [assay - μ_a, moisture - μ_m]

    Regulatory reference: FDA PAT Guidance (2004), ICH Q8/Q10.
    """

    T2_CRITICAL_95 = 5.991  # Chi-squared critical value: 2 DOF, 95% confidence

    def __init__(self, target_assay=100.0, target_moisture=4.5):
        # ── Target Critical Quality Attributes (CQAs) ──────────────────
        self.target_assay    = target_assay
        self.target_moisture = target_moisture

        # ── PID tuning constants (validated on continuous blender) ──────
        self.kp = 0.8    # Proportional gain
        self.ki = 0.15   # Integral gain
        self.kd = 0.05   # Derivative gain

        # ── PID internal state ──────────────────────────────────────────
        self.integral_error = 0.0
        self.prev_error     = 0.0

        # ── Hotelling T² — inverse covariance matrix (pre-computed) ────
        # Process covariance S = [[0.04, 0.01], [0.01, 0.09]]
        # det(S) = 0.04*0.09 - 0.01² = 0.0035
        # S⁻¹  = (1/det) * [[0.09, -0.01], [-0.01, 0.04]]
        _det         = 0.0035
        self.s_inv_a =  0.09 / _det   # S⁻¹[0,0]
        self.s_inv_b = -0.01 / _det   # S⁻¹[0,1] = S⁻¹[1,0]
        self.s_inv_d =  0.04 / _det   # S⁻¹[1,1]

        self.t2_critical = self.T2_CRITICAL_95

    # ── PID Controller ──────────────────────────────────────────────────
    def reset_state(self):
        """Resets PID integrator state between independent batch runs."""
        self.integral_error = 0.0
        self.prev_error     = 0.0

    def calculate_pid_adjustment(self, current_assay, dt=1.0):
        """
        Returns the feeder rate adjustment (u) based on assay deviation.
        Positive adjustment = increase API powder feed rate.
        """
        error                = self.target_assay - current_assay
        self.integral_error += error * dt
        derivative           = (error - self.prev_error) / dt
        self.prev_error      = error
        return (self.kp * error) + (self.ki * self.integral_error) + (self.kd * derivative)

    # ── Hotelling T² ────────────────────────────────────────────────────
    def calculate_hotelling_t2(self, assay, moisture):
        """
        Returns the Hotelling T² statistic for the 2D CQA vector [assay, moisture].
        Formula: T² = d^T · S⁻¹ · d
        Result > 5.991 → sample is out-of-specification.
        """
        d1 = assay    - self.target_assay
        d2 = moisture - self.target_moisture
        return (d1 * (self.s_inv_a * d1 + self.s_inv_b * d2) +
                d2 * (self.s_inv_b * d1 + self.s_inv_d * d2))

    # ── Batch Release Check ─────────────────────────────────────────────
    def check_rtrt_release(self, batch_measurements):
        """
        Evaluates all CQA sample measurements for a batch run.

        Args:
            batch_measurements: list of dicts with keys 'assay' and 'moisture'

        Returns:
            tuple: (is_released: bool, failed_count: int, max_t2: float)
                   is_released=True → batch certified for real-time release
        """
        failed_count = 0
        max_t2       = 0.0
        failed_samples = []

        for i, m in enumerate(batch_measurements):
            t2 = self.calculate_hotelling_t2(m["assay"], m["moisture"])
            if t2 > max_t2:
                max_t2 = t2
            if t2 > self.t2_critical:
                failed_count += 1
                failed_samples.append({"sample_index": i, "t2": round(t2, 4)})

        is_released = (failed_count == 0)
        return is_released, failed_count, max_t2
