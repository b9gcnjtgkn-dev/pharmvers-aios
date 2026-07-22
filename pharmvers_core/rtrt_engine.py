import math

class BioreactorPATController:
    """
    Continuous manufacturing controller that simulates real-time Process Analytical Technology (PAT)
    feeders, executes PID closed-loop adjustments, and calculates Hotelling's T^2 statistic
    for Real-Time Release Testing (RTRT).
    """
    def __init__(self, target_assay=100.0, target_moisture=4.5):
        # Target Critical Quality Attributes (CQAs)
        self.target_assay = target_assay
        self.target_moisture = target_moisture
        
        # PID Controller states for powder feeder rate
        self.kp = 0.8
        self.ki = 0.15
        self.kd = 0.05
        
        self.integral_error = 0.0
        self.prev_error = 0.0
        
        # Process covariance parameters for Hotelling's T^2 (pre-calculated from validated process)
        # Represents standard covariance S = [[0.04, 0.01], [0.01, 0.09]]
        # Determinant = 0.04*0.09 - 0.01*0.01 = 0.0035
        # S_inv = [[d, -b], [-c, a]] / det = [[0.09, -0.01], [-0.01, 0.04]] / 0.0035
        self.s_inv_a = 0.09 / 0.0035
        self.s_inv_b = -0.01 / 0.0035
        self.s_inv_d = 0.04 / 0.0035
        
        self.t2_critical = 5.991 # 95% confidence limit for 2 degrees of freedom

    def calculate_pid_adjustment(self, current_assay, dt=1.0):
        """
        Calculates the adjustment to the powder feeder rate based on active assay deviation.
        """
        error = self.target_assay - current_assay
        self.integral_error += error * dt
        derivative = (error - self.prev_error) / dt
        self.prev_error = error
        
        adjustment = (self.kp * error) + (self.ki * self.integral_error) + (self.kd * derivative)
        return adjustment

    def calculate_hotelling_t2(self, assay, moisture):
        """
        Calculates the Hotelling's T^2 statistic for a 2-dimensional vector: [Assay, Moisture].
        Formula: T^2 = (x - mu)^T * S^-1 * (x - mu)
        """
        d1 = assay - self.target_assay
        d2 = moisture - self.target_moisture
        
        # Compute quadratic form d^T * S_inv * d
        t2 = d1 * (self.s_inv_a * d1 + self.s_inv_b * d2) + d2 * (self.s_inv_b * d1 + self.s_inv_d * d2)
        return t2

    def check_rtrt_release(self, batch_measurements):
        """
        Checks if a set of CQA measurements across a batch run satisfies RTRT bounds.
        Returns (is_released, failed_count, max_t2)
        """
        failed_count = 0
        max_t2 = 0.0
        
        for measurement in batch_measurements:
            t2 = self.calculate_hotelling_t2(measurement["assay"], measurement["moisture"])
            if t2 > max_t2:
                max_t2 = t2
            if t2 > self.t2_critical:
                failed_count += 1
                
        # Batch is certified for real-time release if no samples exceed the critical threshold
        is_released = (failed_count == 0)
        return is_released, failed_count, max_t2
