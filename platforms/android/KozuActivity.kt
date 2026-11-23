package kozu.ui

import android.os.Build
import androidx.compose.animation.core.LinearEasing
import androidx.compose.animation.core.animateFloat
import androidx.compose.animation.core.infiniteRepeatable
import androidx.compose.animation.core.rememberInfiniteTransition
import androidx.compose.animation.core.tween
import androidx.compose.foundation.Canvas
import androidx.compose.foundation.layout.defaultMinSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.sizeIn
import androidx.compose.material3.Button
import androidx.compose.material3.LocalContentColor
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.derivedStateOf
import androidx.compose.runtime.getValue
import androidx.compose.runtime.remember
import androidx.compose.ui.Modifier
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.layout.Layout
import androidx.compose.ui.platform.LocalConfiguration
import androidx.compose.ui.platform.LocalDensity
import androidx.compose.ui.semantics.ProgressBarRangeInfo
import androidx.compose.ui.semantics.clearAndSetSemantics
import androidx.compose.ui.semantics.contentDescription
import androidx.compose.ui.semantics.progressBarRangeInfo
import androidx.compose.ui.semantics.stateDescription
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.unit.Constraints
import androidx.compose.ui.unit.LayoutDirection
import androidx.compose.ui.unit.constrainHeight
import androidx.compose.ui.unit.constrainWidth
import androidx.compose.ui.unit.dp
import java.text.NumberFormat
import java.util.Locale
import kotlin.math.ceil

/** The caller owns microphone state and receives requests to start or stop. */
@Composable
fun KozuListening(
    isListening: Boolean,
    modifier: Modifier = Modifier,
    listeningLabel: String = "Listening",
    idleLabel: String = "Ready to listen",
    startLabel: String = "Start listening",
    stopLabel: String = "Stop",
    reduceMotion: Boolean = false,
    onListeningChange: (Boolean) -> Unit,
) {
    ActivityLine(
        modifier = modifier,
        leading = { Text(if (isListening) listeningLabel else idleLabel) },
        trailing = {
            Button(
                onClick = { onListeningChange(!isListening) },
                modifier = Modifier.sizeIn(minWidth = 48.dp, minHeight = 48.dp),
            ) {
                Text(if (isListening) stopLabel else startLabel)
            }
        },
        meter = {
            if (isListening && !reduceMotion) {
                val phase = rememberInfiniteTransition(label = "Listening waveform").animateFloat(
                    initialValue = 0f,
                    targetValue = 6f,
                    animationSpec = infiniteRepeatable(tween(3300, easing = LinearEasing)),
                    label = "Wave phase",
                )
                val step by remember(phase) { derivedStateOf { phase.value.toInt() % 6 } }
                ActivityDots(rows = 3) { column, row, _ -> waveIsLit(column, row, step) }
            } else {
                ActivityDots(rows = 3) { column, row, _ ->
                    isListening && waveIsLit(column, row, 0)
                }
            }
        },
    )
}

/** A determinate, read-only indicator. The value is a whole percent. */
@Composable
fun KozuProgress(
    label: String = "Progress",
    percent: Int = 0,
    modifier: Modifier = Modifier,
    captionStyle: TextStyle = MaterialTheme.typography.labelSmall,
) {
    val title = label.ifBlank { "Progress" }
    val value = percent.coerceIn(0, 100)
    val configuration = LocalConfiguration.current
    @Suppress("DEPRECATION")
    val locale = if (Build.VERSION.SDK_INT >= 24) {
        configuration.locales[0] ?: Locale.getDefault()
    } else {
        configuration.locale
    }
    val exactPercent = remember(value, locale) {
        NumberFormat.getPercentInstance(locale).format(value / 100.0)
    }

    ActivityLine(
        modifier = modifier.clearAndSetSemantics {
            contentDescription = title
            stateDescription = exactPercent
            progressBarRangeInfo = ProgressBarRangeInfo(value.toFloat(), 0f..100f)
        }.padding(horizontal = 20.dp),
        minimumColumns = 10,
        balanceEnds = true,
        leading = { Text(title, style = captionStyle) },
        trailing = { Text(exactPercent, style = captionStyle.copy(fontFeatureSettings = "tnum")) },
        meter = {
            ActivityDots(rows = 2) { column, row, count ->
                progressDotIsLit(column, row, count, value)
            }
        },
    )
}

// The children stay mounted when the layout switches, including the native button.
@Composable
private fun ActivityLine(
    modifier: Modifier,
    minimumColumns: Int = 9,
    balanceEnds: Boolean = false,
    leading: @Composable () -> Unit,
    trailing: @Composable () -> Unit,
    meter: @Composable () -> Unit,
) {
    val largeText = LocalDensity.current.fontScale >= 1.5f
    Layout(
        modifier = modifier,
        content = {
            leading()
            trailing()
            meter()
        },
    ) { children, constraints ->
        val gap = 8.dp.roundToPx()
        val leadingWidth = children[0].maxIntrinsicWidth(Constraints.Infinity)
        val trailingWidth = children[1].maxIntrinsicWidth(Constraints.Infinity)
        val endWidth = maxOf(leadingWidth, trailingWidth)
        val leadingSlot = if (balanceEnds) endWidth else leadingWidth
        val trailingSlot = if (balanceEnds) endWidth else trailingWidth
        val minimumMeterWidth = ceil(gridSpan(minimumColumns).dp.toPx()).toInt()
        val required = leadingSlot + trailingSlot + 2 * gap + minimumMeterWidth
        val width = if (constraints.hasBoundedWidth) constraints.maxWidth else constraints.constrainWidth(required)
        val stack = largeText || width < required

        val label = children[0].measure(Constraints(maxWidth = if (stack) width else leadingWidth))
        val end = children[1].measure(Constraints(maxWidth = if (stack) width else trailingWidth))
        val dots = children[2].measure(Constraints.fixedWidth(
            if (stack) width else width - leadingSlot - trailingSlot - 2 * gap
        ))
        val height = if (stack) label.height + end.height + dots.height + 2 * gap
            else maxOf(label.height, end.height, dots.height)

        layout(width, constraints.constrainHeight(height)) {
            if (stack) {
                label.placeRelative(0, 0)
                dots.placeRelative(0, label.height + gap)
                end.placeRelative(width - end.width, height - end.height)
            } else {
                label.placeRelative(0, (height - label.height) / 2)
                dots.placeRelative(leadingSlot + gap, (height - dots.height) / 2)
                end.placeRelative(width - end.width, (height - end.height) / 2)
            }
        }
    }
}

@Composable
private fun ActivityDots(rows: Int, isLit: (column: Int, row: Int, count: Int) -> Boolean) {
    val color = LocalContentColor.current
    Canvas(
        Modifier.fillMaxWidth()
            .defaultMinSize(minWidth = gridSpan(if (rows == 3) 9 else 10).dp)
            .height(if (rows == 3) 24.dp else 20.dp),
    ) {
        val diameter = DOT_DIAMETER.dp.toPx()
        val pitch = DOT_PITCH.dp.toPx()
        val columns = gridColumns(size.width, pitch, diameter)
        if (columns == 0 || size.height < gridSpan(rows).dp.toPx()) return@Canvas
        val left = firstCenter(size.width, columns, pitch)
        val top = firstCenter(size.height, rows, pitch)
        for (column in 0 until columns) {
            val x = left + column * pitch
            val centerX = if (layoutDirection == LayoutDirection.Rtl) size.width - x else x
            for (row in 0 until rows) {
                drawCircle(
                    color = if (isLit(column, row, columns)) color else color.copy(alpha = color.alpha * 0.24f),
                    radius = diameter / 2,
                    center = Offset(centerX, top + row * pitch),
                )
            }
        }
    }
}

private const val DOT_PITCH = 8
private const val DOT_DIAMETER = 4

private fun gridSpan(count: Int): Int = DOT_DIAMETER + (count - 1) * DOT_PITCH

private fun gridColumns(width: Float, pitch: Float, diameter: Float): Int =
    if (width < diameter) 0 else 1 + ((width - diameter) / pitch).toInt()

private fun firstCenter(length: Float, count: Int, pitch: Float): Float =
    (length - (count - 1) * pitch) / 2

private fun progressDotIsLit(column: Int, row: Int, columns: Int, percent: Int): Boolean {
    val visibleDots = columns * 2
    return column * 2 + row < visibleDots * percent / 100
}

private fun waveIsLit(column: Int, row: Int, phase: Int): Boolean {
    val offset = (column + phase) % 6
    return if (row == 1) offset == 0 || offset == 1 || offset == 5 else offset == 0
}
