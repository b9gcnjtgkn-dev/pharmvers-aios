import Foundation

public enum SupplyChainShock: String, CaseIterable, Identifiable {
    case none = "None"
    case suezBlockade = "Suez Canal Blockade (+12d Lead Time)"
    case apiPlantShutdown = "API Factory Shutdown (-40% Production Yield)"
    case pandemicSurge = "Epidemiologic Disease Surge (+250% Demand)"
    
    public var id: String { self.rawValue }
}

public class SimulationEngine: ObservableObject {
    @Published public var history: [SimulationStep] = []
    
    public init() {
        runSimulation(with: .none)
    }
    
    public func runSimulation(with shock: SupplyChainShock) {
        var steps: [SimulationStep] = []
        
        // Initial parameters
        var hospitalStock = 1200.0
        var distributorStock = 5000.0
        let targetStock = 1000.0
        
        // Base Rates
        var dispenseRate = 100.0
        var productionRate = 120.0
        var leadTimeDays = 6.0
        
        // Apply Shock modification factors
        switch shock {
        case .none:
            break
        case .suezBlockade:
            leadTimeDays = 18.0 // Massive lead time delay
        case .apiPlantShutdown:
            productionRate = 72.0 // Yield reduction by 40%
        case .pandemicSurge:
            dispenseRate = 350.0 // Demand surge by 250%
        }
        
        // Dynamic simulation loop (30 days)
        for t in 0..<30 {
            // Calculate demand
            let currentDemand = dispenseRate * (1.0 + sin(Double(t) / 4.0) * 0.1) // Add daily cycle noise
            
            // Hospital consumption
            hospitalStock -= currentDemand
            
            // Delay buffer representing lead time delay logic
            let transitLatency = leadTimeDays
            
            // Sourcing math
            let shortfall = max(0.0, targetStock - hospitalStock)
            let rawReceipt = (shortfall > 0) ? min(distributorStock, shortfall) : 0.0
            
            // Euler approximation of delayed supply delivery
            let deliveryRate = rawReceipt / transitLatency
            
            hospitalStock += deliveryRate
            distributorStock -= deliveryRate
            
            // Production replenishment to distributor
            distributorStock += productionRate
            
            // Bounds check
            hospitalStock = max(0.0, hospitalStock)
            distributorStock = max(0.0, distributorStock)
            
            steps.append(SimulationStep(stepIndex: t, hospitalStock: hospitalStock, distributorStock: distributorStock, demand: currentDemand))
        }
        
        self.history = steps
    }
}
