import 'package:flutter/material.dart';

import '../core/app_models.dart';
import '../core/demo_data.dart';
import '../screens/export_screen.dart';
import '../screens/fine_tune_screen.dart';
import '../screens/home_screen.dart';
import '../screens/processing_screen.dart';
import '../screens/results_screen.dart';
import '../screens/upload_screen.dart';

enum AppStage { home, upload, processing, results, fineTune, export }

class AppShell extends StatefulWidget {
  const AppShell({super.key});

  @override
  State<AppShell> createState() => _AppShellState();
}

class _AppShellState extends State<AppShell> {
  AppStage _stage = AppStage.home;
  final ValueNotifier<double> _progress = ValueNotifier<double>(0.0);
  VocalVersion _selected = DemoData.versions.first;
  QuickControls _controls = const QuickControls();
  FineTuneState _fineTune = const FineTuneState();
  bool _refining = false;

  Future<void> _runProcessing({bool refine = false}) async {
    setState(() {
      _refining = refine;
      _stage = AppStage.processing;
      _progress.value = 0.0;
    });
    for (int i = 1; i <= 100; i++) {
      await Future<void>.delayed(Duration(milliseconds: refine ? 18 : 24));
      _progress.value = i / 100.0;
    }
    setState(() {
      _refining = false;
      _stage = AppStage.results;
    });
  }

  @override
  Widget build(BuildContext context) {
    final body = switch (_stage) {
      AppStage.home => HomeScreen(
          onUpload: () => setState(() => _stage = AppStage.upload),
          onDemo: () => _runProcessing(refine: false),
        ),
      AppStage.upload => UploadScreen(
          onAnalyze: () => _runProcessing(refine: false),
        ),
      AppStage.processing => ProcessingScreen(
          progress: _progress,
          isRefinement: _refining,
        ),
      AppStage.results => ResultsScreen(
          versions: DemoData.versions,
          selected: _selected,
          controls: _controls,
          onSelect: (value) => setState(() => _selected = value),
          onControlsChanged: (value) => setState(() => _controls = value),
          onMakeBetter: () => _runProcessing(refine: true),
          onFineTune: () => setState(() => _stage = AppStage.fineTune),
          onExport: () => setState(() => _stage = AppStage.export),
        ),
      AppStage.fineTune => FineTuneScreen(
          state: _fineTune,
          onChanged: (value) => setState(() => _fineTune = value),
          onApply: () => setState(() => _stage = AppStage.results),
          onBack: () => setState(() => _stage = AppStage.results),
        ),
      AppStage.export => ExportScreen(
          selected: _selected,
          onBack: () => setState(() => _stage = AppStage.results),
        ),
    };

    return AnimatedSwitcher(
      duration: const Duration(milliseconds: 420),
      switchInCurve: Curves.easeOutCubic,
      switchOutCurve: Curves.easeInCubic,
      child: KeyedSubtree(
        key: ValueKey(_stage),
        child: body,
      ),
    );
  }
}
