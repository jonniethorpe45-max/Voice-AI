import 'dart:math' as math;

import 'package:flutter/material.dart';

class AnimatedWaveform extends StatefulWidget {
  const AnimatedWaveform({
    super.key,
    this.height = 56,
    this.bars = 44,
    this.baseColor = const Color(0xFF00D4FF),
    this.backgroundMode = false,
    this.seed = 4,
  });

  final double height;
  final int bars;
  final Color baseColor;
  final bool backgroundMode;
  final int seed;

  @override
  State<AnimatedWaveform> createState() => _AnimatedWaveformState();
}

class _AnimatedWaveformState extends State<AnimatedWaveform>
    with SingleTickerProviderStateMixin {
  late final AnimationController _controller;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 1500),
    )..repeat();
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: _controller,
      builder: (context, _) {
        final t = _controller.value * 2 * math.pi;
        return Row(
          crossAxisAlignment: CrossAxisAlignment.end,
          children: List.generate(widget.bars, (index) {
            final motion = math.sin((index * 0.31) + t + widget.seed) *
                math.cos((index * 0.19) - t * 0.8);
            final amp = 0.18 + (motion + 1) / 2 * 0.82;
            return Expanded(
              child: Padding(
                padding: const EdgeInsets.symmetric(horizontal: 1),
                child: Container(
                  height: widget.height * amp,
                  decoration: BoxDecoration(
                    borderRadius: BorderRadius.circular(3),
                    gradient: LinearGradient(
                      begin: Alignment.bottomCenter,
                      end: Alignment.topCenter,
                      colors: [
                        widget.baseColor
                            .withOpacity(widget.backgroundMode ? 0.08 : 0.24),
                        widget.baseColor
                            .withOpacity(widget.backgroundMode ? 0.4 : 0.9),
                      ],
                    ),
                  ),
                ),
              ),
            );
          }),
        );
      },
    );
  }
}
