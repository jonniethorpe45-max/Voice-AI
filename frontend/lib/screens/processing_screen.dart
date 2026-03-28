import 'package:flutter/material.dart';

class ProcessingScreen extends StatefulWidget {
  const ProcessingScreen({
    super.key,
    required this.progress,
    required this.message,
  });

  final double progress;
  final String message;

  @override
  State<ProcessingScreen> createState() => _ProcessingScreenState();
}

class _ProcessingScreenState extends State<ProcessingScreen>
    with SingleTickerProviderStateMixin {
  late final AnimationController _controller;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 900),
    )..repeat(reverse: true);
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final value = widget.progress.clamp(0.0, 1.0);
    return Padding(
      padding: const EdgeInsets.all(18),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const SizedBox(height: 16),
          const Text(
            'Processing',
            style: TextStyle(fontSize: 26, fontWeight: FontWeight.w700),
          ),
          const SizedBox(height: 8),
          Text(
            widget.message,
            style: TextStyle(color: Colors.grey.shade300),
          ),
          const SizedBox(height: 20),
          LinearProgressIndicator(value: value),
          const SizedBox(height: 10),
          Text('${(value * 100).toStringAsFixed(0)}%'),
          const SizedBox(height: 26),
          Expanded(
            child: Center(
              child: AnimatedBuilder(
                animation: _controller,
                builder: (context, child) {
                  return Row(
                    mainAxisAlignment: MainAxisAlignment.center,
                    crossAxisAlignment: CrossAxisAlignment.end,
                    children: List.generate(26, (index) {
                      final wave = 28.0 +
                          ((index % 9) * 6.0) +
                          (_controller.value * 36.0);
                      return Container(
                        margin: const EdgeInsets.symmetric(horizontal: 2),
                        width: 6,
                        height: wave,
                        decoration: BoxDecoration(
                          color: const Color(0xFF58E1FF),
                          borderRadius: BorderRadius.circular(4),
                        ),
                      );
                    }),
                  );
                },
              ),
            ),
          ),
        ],
      ),
    );
  }
}
