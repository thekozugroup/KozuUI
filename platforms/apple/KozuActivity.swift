import SwiftUI

/// The caller owns microphone state and receives requests to start or stop.
public struct KozuListening: View {
    @Environment(\.accessibilityReduceMotion) private var reduceMotion
    @Environment(\.dynamicTypeSize) private var typeSize
    @Environment(\.scenePhase) private var scenePhase

    private let isListening: Bool
    private let listeningLabel: LocalizedStringKey
    private let idleLabel: LocalizedStringKey
    private let startLabel: LocalizedStringKey
    private let stopLabel: LocalizedStringKey
    private let onListeningChange: (Bool) -> Void

    public init(
        isListening: Bool,
        listeningLabel: LocalizedStringKey = "Listening",
        idleLabel: LocalizedStringKey = "Ready to listen",
        startLabel: LocalizedStringKey = "Start listening",
        stopLabel: LocalizedStringKey = "Stop",
        onListeningChange: @escaping (Bool) -> Void
    ) {
        self.isListening = isListening
        self.listeningLabel = listeningLabel
        self.idleLabel = idleLabel
        self.startLabel = startLabel
        self.stopLabel = stopLabel
        self.onListeningChange = onListeningChange
    }

    public var body: some View {
        ActivityLine(stack: typeSize.isAccessibilitySize) {
            Text(isListening ? listeningLabel : idleLabel)
                .fontWeight(.semibold)
                .fixedSize(horizontal: false, vertical: true)

            Button {
                onListeningChange(!isListening)
            } label: {
                Text(isListening ? stopLabel : startLabel)
                    .fontWeight(.semibold)
                    .fixedSize(horizontal: false, vertical: true)
                    .padding(.horizontal, 12)
                    .padding(.vertical, 8)
                    .frame(minWidth: 48, minHeight: 48)
                    .background(.quaternary, in: Capsule())
                    .contentShape(Rectangle())
            }
            .buttonStyle(.plain)

            let paused = reduceMotion || !isListening || scenePhase != .active
            TimelineView(.animation(minimumInterval: 0.55, paused: paused)) { time in
                let phase = paused ? 0 : Int(time.date.timeIntervalSinceReferenceDate
                    .truncatingRemainder(dividingBy: 3.3) / 0.55)
                ActivityDots(rows: 3) { column, row, _ in
                    isListening && waveIsLit(column: column, row: row, phase: phase)
                }
            }
        }
    }
}

/// A determinate, read-only indicator. The value is a whole percent.
public struct KozuProgress: View {
    @Environment(\.dynamicTypeSize) private var typeSize
    @Environment(\.locale) private var locale

    private let label: String
    private let percent: Int
    private let captionFont: Font

    public init(label: String = "", percent: Int = 0, captionFont: Font = .caption) {
        self.label = label
        self.percent = min(100, max(0, percent))
        self.captionFont = captionFont
    }

    public var body: some View {
        let title = label.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty
            ? Text("Progress") : Text(verbatim: label)
        let value = (Double(percent) / 100).formatted(.percent.precision(.fractionLength(0)).locale(locale))

        ActivityLine(stack: typeSize.isAccessibilitySize, minimumColumns: 10, balanceEnds: true) {
            title.fixedSize(horizontal: false, vertical: true)
            Text(verbatim: value).monospacedDigit()

            ActivityDots(rows: 2) { column, row, count in
                progressDotIsLit(column: column, row: row, columns: count, percent: percent)
            }
        }
        .font(captionFont)
        .padding(.horizontal, 20)
        .accessibilityRepresentation {
            ProgressView(value: Double(percent), total: 100) {
                title
            }
            .accessibilityValue(Text(verbatim: value))
        }
    }
}

// The children stay mounted when the layout switches, including the native button.
private struct ActivityLine: Layout {
    let stack: Bool
    var minimumColumns = 9
    var balanceEnds = false
    private let gap: CGFloat = 8

    func sizeThatFits(proposal: ProposedViewSize, subviews: Subviews, cache: inout ()) -> CGSize {
        arrangement(width: proposal.width, subviews: subviews).size
    }

    func placeSubviews(in bounds: CGRect, proposal: ProposedViewSize, subviews: Subviews, cache: inout ()) {
        let layout = arrangement(width: bounds.width, subviews: subviews)
        for (subview, frame) in zip(subviews, layout.frames) {
            subview.place(
                at: CGPoint(x: bounds.minX + frame.minX, y: bounds.minY + frame.minY),
                anchor: .topLeading,
                proposal: ProposedViewSize(frame.size)
            )
        }
    }

    private func arrangement(width proposal: CGFloat?, subviews: Subviews) -> (size: CGSize, frames: [CGRect]) {
        let leading = subviews[0].sizeThatFits(.unspecified)
        let trailing = subviews[1].sizeThatFits(.unspecified)
        let endWidth = max(leading.width, trailing.width)
        let leadingSlot = balanceEnds ? endWidth : leading.width
        let trailingSlot = balanceEnds ? endWidth : trailing.width
        let required = leadingSlot + trailingSlot + 2 * gap + gridSpan(minimumColumns)
        let width = proposal.flatMap { $0.isFinite ? $0 : nil } ?? required

        if !stack && width >= required {
            let meter = subviews[2].sizeThatFits(ProposedViewSize(
                width: width - leadingSlot - trailingSlot - 2 * gap, height: nil
            ))
            let height = max(leading.height, trailing.height, meter.height)
            let frames = [
                CGRect(x: 0, y: (height - leading.height) / 2, width: leading.width, height: leading.height),
                CGRect(x: width - trailing.width, y: (height - trailing.height) / 2,
                       width: trailing.width, height: trailing.height),
                CGRect(x: leadingSlot + gap, y: (height - meter.height) / 2,
                       width: meter.width, height: meter.height)
            ]
            return (CGSize(width: width, height: height), frames)
        }

        let proposal = ProposedViewSize(width: width, height: nil)
        let top = subviews[0].sizeThatFits(proposal)
        let bottom = subviews[1].sizeThatFits(proposal)
        let meter = subviews[2].sizeThatFits(proposal)
        let bottomY = top.height + meter.height + 2 * gap
        let frames = [
            CGRect(origin: .zero, size: top),
            CGRect(x: max(0, width - bottom.width), y: bottomY, width: bottom.width, height: bottom.height),
            CGRect(x: 0, y: top.height + gap, width: meter.width, height: meter.height)
        ]
        return (CGSize(width: width, height: bottomY + bottom.height), frames)
    }
}

private struct ActivityDots: View {
    let rows: Int
    let isLit: (Int, Int, Int) -> Bool

    var body: some View {
        Canvas { context, size in
            let columns = gridColumns(size.width)
            guard columns > 0, size.height >= gridSpan(rows) else { return }
            let left = (size.width - gridSpan(columns)) / 2
            let top = (size.height - gridSpan(rows)) / 2

            var dot = context
            for column in 0..<columns {
                for row in 0..<rows {
                    dot.opacity = isLit(column, row, columns) ? 1 : 0.24
                    dot.fill(Path(ellipseIn: CGRect(
                        x: left + CGFloat(column) * dotPitch, y: top + CGFloat(row) * dotPitch,
                        width: dotDiameter, height: dotDiameter
                    )), with: .foreground)
                }
            }
        }
        .frame(idealWidth: gridSpan(rows == 3 ? 9 : 10), maxWidth: .infinity)
        .frame(height: rows == 3 ? 24 : 20)
        .flipsForRightToLeftLayoutDirection(true)
        .accessibilityHidden(true)
        .allowsHitTesting(false)
    }
}

private let dotPitch: CGFloat = 8
private let dotDiameter: CGFloat = 4

private func gridSpan(_ count: Int) -> CGFloat {
    dotDiameter + CGFloat(count - 1) * dotPitch
}

private func gridColumns(_ width: CGFloat) -> Int {
    width < dotDiameter ? 0 : 1 + Int((width - dotDiameter) / dotPitch)
}

private func progressDotIsLit(column: Int, row: Int, columns: Int, percent: Int) -> Bool {
    let visibleDots = columns * 2
    return column * 2 + row < visibleDots * percent / 100
}

private func waveIsLit(column: Int, row: Int, phase: Int) -> Bool {
    let offset = (column + phase) % 6
    return row == 1 ? offset == 0 || offset == 1 || offset == 5 : offset == 0
}
