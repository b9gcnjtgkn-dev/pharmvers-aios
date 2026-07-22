import SwiftUI
import Charts

struct ContentView: View {
    @StateObject private var simEngine = SimulationEngine()
    @StateObject private var agentEngine = AgentSocietyEngine()
    
    @State private var selectedShock: SupplyChainShock = .none
    @State private var selectedTab = 0
    
    // Core Color Palette
    let bgDark = Color(red: 0.04, green: 0.06, blue: 0.10) // #0A0E1A
    let cardDark = Color(red: 0.11, green: 0.15, blue: 0.22) // #1C2538
    let cyanAccent = Color(red: 0.00, green: 0.94, blue: 1.00) // #00F0FF
    let amberAlert = Color(red: 1.00, green: 0.70, blue: 0.00) // #FFB300
    let redAlert = Color(red: 1.00, green: 0.23, blue: 0.19) // #FF3B30
    
    var body: some View {
        ZStack {
            bgDark.ignoresSafeArea()
            
            VStack(spacing: 0) {
                // Top Header Bar
                HStack {
                    VStack(alignment: .leading, spacing: 4) {
                        Text("PHARMVERS AIOS")
                            .font(.system(size: 20, weight: .bold, design: .monospaced))
                            .foregroundColor(.white)
                        Text("COGNITIVE TERMINAL // ACTIVE")
                            .font(.system(size: 10, weight: .semibold, design: .monospaced))
                            .foregroundColor(cyanAccent)
                    }
                    Spacer()
                    Image(systemName: "bolt.shield.fill")
                        .font(.title2)
                        .foregroundColor(cyanAccent)
                }
                .padding()
                .background(cardDark.opacity(0.5))
                
                // Content Views based on Tab Selection
                TabView(selection: $selectedTab) {
                    // TAB 1: Dashboard & Simulation
                    ScrollView {
                        VStack(spacing: 16) {
                            // System Status Card
                            HStack(spacing: 20) {
                                VStack(alignment: .leading, spacing: 8) {
                                    Text("SYSTEM LATENCY (OODA TARGET)")
                                        .font(.caption2)
                                        .foregroundColor(.gray)
                                    Text("42 ms")
                                        .font(.system(size: 36, weight: .black, design: .monospaced))
                                        .foregroundColor(cyanAccent)
                                }
                                Spacer()
                                Circle()
                                    .stroke(cyanAccent.opacity(0.2), lineWidth: 4)
                                    .background(Circle().fill(cyanAccent.opacity(0.1)))
                                    .frame(width: 60, height: 60)
                                    .overlay(
                                        Text("OK")
                                            .font(.caption)
                                            .fontWeight(.bold)
                                            .foregroundColor(cyanAccent)
                                    )
                            }
                            .padding()
                            .background(cardDark)
                            .cornerRadius(12)
                            
                            // Shock Controller Card
                            VStack(alignment: .leading, spacing: 12) {
                                Text("INJECT SUPPLY CHAIN SHOCK")
                                    .font(.caption)
                                    .fontWeight(.bold)
                                    .foregroundColor(.white)
                                
                                Picker("Shock Selection", selection: $selectedShock) {
                                    ForEach(SupplyChainShock.allCases) { shock in
                                        Text(shock.rawValue.prefix(15) + "...").tag(shock)
                                    }
                                }
                                .pickerStyle(.segmented)
                                .colorMultiply(cyanAccent)
                                .onChange(of: selectedShock) { newShock in
                                    simEngine.runSimulation(with: newShock)
                                }
                            }
                            .padding()
                            .background(cardDark)
                            .cornerRadius(12)
                            
                            // Swift Charts Graph Card
                            VStack(alignment: .leading, spacing: 12) {
                                Text("PROJECTED INVENTORY RUN-RATES (30 DAYS)")
                                    .font(.caption)
                                    .fontWeight(.bold)
                                    .foregroundColor(.white)
                                
                                Chart {
                                    ForEach(simEngine.history) { step in
                                        LineMark(
                                            x: .value("Day", step.stepIndex),
                                            y: .value("Hospital Stock", step.hospitalStock),
                                            series: .value("Stock", "Hospital")
                                        )
                                        .foregroundStyle(cyanAccent)
                                        .interpolationMethod(.catmullRom)
                                        
                                        LineMark(
                                            x: .value("Day", step.stepIndex),
                                            y: .value("Distributor Stock", step.distributorStock),
                                            series: .value("Stock", "Distributor")
                                        )
                                        .foregroundStyle(amberAlert)
                                        .interpolationMethod(.catmullRom)
                                    }
                                    
                                    RuleMark(y: .value("Safety Stock", 1000.0))
                                        .lineStyle(StrokeStyle(lineWidth: 1, dash: [5]))
                                        .foregroundStyle(redAlert)
                                }
                                .frame(height: 200)
                                .chartLegend(position: .bottom)
                            }
                            .padding()
                            .background(cardDark)
                            .cornerRadius(12)
                        }
                        .padding()
                    }
                    .tag(0)
                    .tabItem {
                        Label("Dashboard", systemImage: "chart.bar.xaxis")
                    }
                    
                    // TAB 2: Agent Society Visualizer
                    VStack(spacing: 0) {
                        ScrollView {
                            LazyVGrid(columns: [GridItem(.adaptive(minimum: 100))], spacing: 12) {
                                ForEach(agentEngine.agents) { agent in
                                    VStack(spacing: 8) {
                                        Circle()
                                            .fill(statusColor(for: agent.status))
                                            .frame(width: 14, height: 14)
                                            .shadow(color: statusColor(for: agent.status), radius: 4)
                                        
                                        Text(agent.name.replacingOccurrences(of: " Agent", with: ""))
                                            .font(.system(size: 10, weight: .bold))
                                            .foregroundColor(.white)
                                            .multilineTextAlignment(.center)
                                            .lineLimit(2)
                                        
                                        Text(agent.status.rawValue)
                                            .font(.system(size: 8, design: .monospaced))
                                            .foregroundColor(.gray)
                                    }
                                    .padding(.vertical, 12)
                                    .frame(maxWidth: .infinity)
                                    .background(cardDark)
                                    .cornerRadius(8)
                                    .overlay(
                                        RoundedRectangle(cornerRadius: 8)
                                            .stroke(statusColor(for: agent.status).opacity(0.3), lineWidth: 1)
                                    )
                                }
                            }
                            .padding()
                        }
                        
                        // ACP Messages Terminal Log
                        VStack(alignment: .leading, spacing: 8) {
                            Text("ACP INTER-AGENT TRANSACTION LOG")
                                .font(.system(size: 9, weight: .bold, design: .monospaced))
                                .foregroundColor(cyanAccent)
                                .padding(.horizontal)
                                .padding(.top, 8)
                            
                            ScrollView {
                                LazyVStack(alignment: .leading, spacing: 6) {
                                    ForEach(agentEngine.acpLogs) { log in
                                        HStack(alignment: .top) {
                                            Text("[\(log.sender.replacingOccurrences(of: " Agent", with: "")) -> \(log.recipient.replacingOccurrences(of: " Agent", with: ""))]")
                                                .font(.system(size: 8, weight: .bold, design: .monospaced))
                                                .foregroundColor(cyanAccent)
                                            Text(log.payloadSummary)
                                                .font(.system(size: 8, design: .monospaced))
                                                .foregroundColor(.white)
                                        }
                                        .padding(.horizontal)
                                    }
                                }
                            }
                        }
                        .frame(height: 150)
                        .background(Color.black.opacity(0.4))
                    }
                    .tag(1)
                    .tabItem {
                        Label("Agents", systemImage: "person.3.sequence.fill")
                    }
                }
                .accentColor(cyanAccent)
            }
        }
    }
    
    private func statusColor(for status: AgentStatus) -> Color {
        switch status {
        case .idle: return .gray
        case .reasoning: return cyanAccent
        case .negotiating: return amberAlert
        case .executing: return Color.green
        }
    }
}

struct ContentView_Previews: PreviewProvider {
    static var previews: some View {
        ContentView()
    }
}
