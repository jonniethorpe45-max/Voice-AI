import 'dart:async';

import 'package:flutter/material.dart';

import '../components/progress_orb.dart';
import '../core/demo_data.dart';
import '../theme/app_theme.dart';

class ProcessingScreen extends StatefulWidget {
  const ProcessingScreen({
    super.key,
    required this.progress,
    required this.isRefinement,
  });

  final ValueNotifier<double> progress;
  final bool isRefinement;

  @override
  State<ProcessingScreen> createState() => _ProcessingScreenState();
}

class _ProcessingScreenState extends State<ProcessingScreen> {
  int _messageIndex = 0;
  Timer? _messageTimer;

  @override
  void initState() {
    super.initState();
    _messageTimer = Timer.periodic(const Duration(milliseconds: 900), (_) {
      if (!mounted) {
        return;
      }
      setState(() {
        _messageIndex = (_messageIndex + 1) % DemoData.processingText.length;
      });
    });
  }

  @override
  void dispose() {
    _messageTimer?.cancel();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.all(AppTheme.s20),
      child: ValueListenableBuilder<double>(
        valueListenable: widget.progress,
        builder: (context, value, _) {
          final progress = value.clamp(0.0, 1.0);
          return Column(
            children: [
              const SizedBox(height: AppTheme.s16),
              Text(
                widget.isRefinement ? 'Refining with AI' : 'AI Processing',
                style: Theme.of(context).textTheme.headlineMedium,
              ),
              const SizedBox(height: AppTheme.s12),
              AnimatedSwitcher(
                duration: const Duration(milliseconds: 260),
                child: Text(
                  DemoData.processingText[_messageIndex],
                  key: ValueKey(_messageIndex),
                  style: Theme.of(context).textTheme.bodyLarge,
                ),
              ),
              const Spacer(),
              ProgressOrb(progress: progress, size: 210),
              const Spacer(),
              ClipRRect(
                borderRadius: BorderRadius.circular(999),
                child: LinearProgressIndicator(
                  value: progress,
                  minHeight: 10,
                  backgroundColor: Colors.white12,
                  valueColor: const AlwaysStoppedAnimation<Color>(AppTheme.neonBlue),
                ),
              ),
              const SizedBox(height: AppTheme.s8),
              Text(
                '${(progress * 100).toStringAsFixed(0)}%',
                style: Theme.of(context).textTheme.bodyLarge,
              ),
            ],
          );
        },
      ),
    );
  }
}
