import Foundation

public enum AgentStatus: String, Codable, CaseIterable {
    case idle = "Idle"
    case reasoning = "Reasoning"
    case negotiating = "Negotiating"
    case executing = "Executing"
}

public struct Agent: Identifiable, Codable {
    public var id: UUID
    public var name: String
    public var role: String
    public var status: AgentStatus
    public var efficiency: Double
    public var episodicMemoryCount: Int
    
    public init(id: UUID = UUID(), name: String, role: String, status: AgentStatus = .idle, efficiency: Double = 1.0, episodicMemoryCount: Int = 0) {
        self.id = id
        self.name = name
        self.role = role
        self.status = status
        self.efficiency = efficiency
        self.episodicMemoryCount = episodicMemoryCount
    }
}

public enum KGNodeType: String, Codable {
    case molecule = "Molecule"
    case api = "Active Pharmaceutical Ingredient (API)"
    case manufacturer = "Manufacturer / CDMO"
    case route = "Logistics Route"
    case hospital = "Hospital System"
}

public enum NodeStatus: String, Codable {
    case normal = "Normal"
    case warning = "Warning"
    case critical = "Critical"
}

public struct KGNode: Identifiable, Codable {
    public var id: UUID
    public var label: String
    public var type: KGNodeType
    public var status: NodeStatus
    
    public init(id: UUID = UUID(), label: String, type: KGNodeType, status: NodeStatus = .normal) {
        self.id = id
        self.label = label
        self.type = type
        self.status = status
    }
}

public struct SimulationStep: Identifiable, Codable {
    public var id: UUID
    public var stepIndex: Int
    public var hospitalStock: Double
    public var distributorStock: Double
    public var demand: Double
    
    public init(id: UUID = UUID(), stepIndex: Int, hospitalStock: Double, distributorStock: Double, demand: Double) {
        self.id = id
        self.stepIndex = stepIndex
        self.hospitalStock = hospitalStock
        self.distributorStock = distributorStock
        self.demand = demand
    }
}

public struct ACPMessage: Identifiable, Codable {
    public var id: UUID
    public var timestamp: Date
    public var sender: String
    public var recipient: String
    public var intent: String
    public var payloadSummary: String
    
    public init(id: UUID = UUID(), timestamp: Date = Date(), sender: String, recipient: String, intent: String, payloadSummary: String) {
        self.id = id
        self.timestamp = timestamp
        self.sender = sender
        self.recipient = recipient
        self.intent = intent
        self.payloadSummary = payloadSummary
    }
}
