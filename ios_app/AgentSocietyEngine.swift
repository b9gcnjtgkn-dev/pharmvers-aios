import Foundation
import Combine

public class AgentSocietyEngine: ObservableObject {
    @Published public var agents: [Agent] = []
    @Published public var acpLogs: [ACPMessage] = []
    
    private var timer: AnyCancellable?
    
    private let agentDefinitions = [
        ("Manufacturing Agent", "CDMO throughput & bioreactor logs"),
        ("Procurement Agent", "Sourcing raw material & packaging"),
        ("Regulatory Agent", "CTD dossiers & FDA warning letters"),
        ("Trade Agent", "Tariff paths & customs routes"),
        ("Hospital Agent", "EHR consumption & local stockouts"),
        ("Market Intelligence Agent", "Patent expirations & competitors"),
        ("Forecasting Agent", "Probabilistic demand trends"),
        ("Knowledge Graph Agent", "Dynamic triple & vector resolution"),
        ("Negotiation Agent", "Nash bidding & dynamic contracts"),
        ("Compliance Agent", "GxP audits & validation ledger"),
        ("Supply Chain Agent", "IoT cold-chain & ETAs"),
        ("Risk Agent", "Geopolitical feeds & credit scoring"),
        ("Pricing Agent", "Dynamic bidding & margin metrics"),
        ("Tender Agent", "Public bidding & win ratios"),
        ("Research Agent", "BioRxiv papers & molecular targets"),
        ("Financial Agent", "Treasury operations & fx hedging"),
        ("Executive Strategy Agent", "Systems arbitrator & global KPIs")
    ]
    
    public init() {
        self.agents = agentDefinitions.map { (name, role) in
            Agent(name: name, role: role, status: .idle, efficiency: Double.random(in: 0.9...1.0), episodicMemoryCount: Int.random(in: 120...450))
        }
        startSimulation()
    }
    
    private func startSimulation() {
        timer = Timer.publish(every: 3.0, on: .main, in: .common)
            .autoconnect()
            .sink { [weak self] _ in
                self?.simulateActivity()
            }
    }
    
    private func simulateActivity() {
        guard !agents.isEmpty else { return }
        
        // Pick a random agent to change status
        let index = Int.random(in: 0..<agents.count)
        let statuses: [AgentStatus] = [.idle, .reasoning, .negotiating, .executing]
        let newStatus = statuses.randomElement() ?? .idle
        
        agents[index].status = newStatus
        agents[index].episodicMemoryCount += 1
        
        // Generate a mock ACP message
        let sender = agents[index].name
        let recipientIndex = (index + Int.random(in: 1...5)) % agents.count
        let recipient = agents[recipientIndex].name
        
        let intents = ["SHORTAGE_RISK_ALERT", "NEGOTIATE_SOURCING", "GXP_VERIFY_REQUEST", "LOGISTICS_UPDATE"]
        let intent = intents.randomElement() ?? "LOGISTICS_UPDATE"
        
        let payloadSummary: String
        switch intent {
        case "SHORTAGE_RISK_ALERT":
            payloadSummary = "Risk threshold crossed for Amoxicillin. Urgency: CRITICAL."
        case "NEGOTIATE_SOURCING":
            payloadSummary = "Opened bid/ask matching on contract for 50,000 units."
        case "GXP_VERIFY_REQUEST":
            payloadSummary = "Querying FDA import alerts for GMP certification hashes."
        default:
            payloadSummary = "Transit corridor delay updated. Cold-chain parameters verified."
        }
        
        let msg = ACPMessage(sender: sender, recipient: recipient, intent: intent, payloadSummary: payloadSummary)
        
        acpLogs.insert(msg, at: 0)
        if acpLogs.count > 50 {
            acpLogs.removeLast()
        }
    }
}
