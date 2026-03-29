import 'package:file_picker/file_picker.dart';
import 'package:flutter/material.dart';

import '../core/app_models.dart';
import '../core/demo_data.dart';
import '../screens/export_screen.dart';
import '../screens/fine_tune_screen.dart';
import '../screens/home_screen.dart';
import '../screens/processing_screen.dart';
import '../screens/results_screen.dart';
import '../screens/upload_screen.dart';
import '../services/api_client.dart';

enum AppStage { home, upload, processing, results, fineTune, export }

class AppShell extends StatefulWidget {
  const AppShell({super.key});

  @override
  State<AppShell> createState() => _AppShellState();
}

class _AppShellState extends State<AppShell> {
  static const _defaultBase = String.fromEnvironment(
    'API_BASE_URL',
    defaultValue: 'http://localhost:8000',
  );

  late final ApiClient _api = ApiClient(baseUrl: _defaultBase);
  AppStage _stage = AppStage.home;
  final ValueNotifier<double> _progress = ValueNotifier<double>(0.0);

  VocalVersion _selected = DemoData.versions.first;
  List<VocalVersion> _versions = DemoData.versions;
  QuickControls _controls = const QuickControls();
  FineTuneState _fineTune = const FineTuneState();

  bool _refining = false;
  bool _processingActive = false;

  String? _jobId;
  String? _vocalPath;
  String? _songPath;
  String? _vocalName;
  String? _songName;
  String _trackName = 'Neon Skyline';
  String _trackDuration = '03:24';
  String _processingMessage = '';
  String? _error;

  @override
  void dispose() {
    _progress.dispose();
    super.dispose();
  }

  Future<void> _pickVocal() async {
    final result = await FilePicker.platform.pickFiles(
      type: FileType.custom,
      allowedExtensions: const ['wav', 'mp3', 'm4a'],
      allowMultiple: false,
    );
    final file = result?.files.single;
    if (file?.path == null) {
      return;
    }
    setState(() {
      _vocalPath = file!.path!;
      _vocalName = file.name;
    });
  }

  Future<void> _pickSong() async {
    final result = await FilePicker.platform.pickFiles(
      type: FileType.custom,
      allowedExtensions: const ['wav', 'mp3', 'm4a'],
      allowMultiple: false,
    );
    final file = result?.files.single;
    if (file?.path == null) {
      return;
    }
    setState(() {
      _songPath = file!.path!;
      _songName = file.name;
    });
  }

  Future<void> _startFromUpload(QuickControls controls) async {
    _controls = controls;
    await _startProcessing(
      refine: false,
      vocalPath: _vocalPath,
      songPath: _songPath,
    );
  }

  Future<void> _startProcessing({
    required bool refine,
    String? vocalPath,
    String? songPath,
  }) async {
    if (_processingActive) {
      return;
    }
    _processingActive = true;
    setState(() {
      _refining = refine;
      _stage = AppStage.processing;
      _progress.value = 0.0;
      _processingMessage = '';
      _error = null;
    });
    try {
      String jobId;
      if (!refine) {
        if (vocalPath == null) {
          throw Exception('Please select a vocal file before analyzing.');
        }
        jobId = await _api.upload(vocalPath: vocalPath, instrumentalPath: songPath);
        _jobId = jobId;
      } else {
        if (_jobId == null) {
          throw Exception('No previous session found. Upload a vocal first.');
        }
        jobId = _jobId!;
      }

      await _api.process(jobId: jobId, controls: _controls);
      await _pollUntilComplete(jobId);
    } catch (e) {
      if (mounted) {
        setState(() {
          _error = _humanizeError(e);
          _stage = AppStage.upload;
        });
      }
    } finally {
      _processingActive = false;
      if (mounted) {
        setState(() => _refining = false);
      }
    }
  }

  Future<void> _pollUntilComplete(String jobId) async {
    const maxPolls = 240;
    const pollDelay = Duration(seconds: 2);
    for (int i = 0; i < maxPolls; i++) {
      final status = await _api.status(jobId);
      _progress.value = (status.progress.clamp(0, 100) as num).toDouble() / 100.0;
      if (mounted) {
        setState(() => _processingMessage = status.message);
      }
      if (status.status == 'completed' || status.status == 'completed_with_warnings') {
        final data = await _api.results(jobId);
        if (!mounted) {
          return;
        }
        final versions = data.variations;
        setState(() {
          if (versions.isNotEmpty) {
            _versions = versions;
            _selected = _pickSelected(
              versions: versions,
              selectedLabel: data.selectedVariationLabel,
            );
            _trackDuration = _selected.duration;
          } else {
            _versions = const [];
          }
          _trackName = data.songName ?? _trackName;
          _stage = AppStage.results;
        });
        return;
      }
      if (status.status == 'failed') {
        throw Exception(status.error ?? status.message);
      }
      await Future<void>.delayed(pollDelay);
    }
    throw Exception('Processing timed out. Please retry.');
  }

  VocalVersion _pickSelected({
    required List<VocalVersion> versions,
    String? selectedLabel,
  }) {
    if (selectedLabel != null) {
      for (final item in versions) {
        if (item.label == selectedLabel) {
          return item;
        }
      }
    }
    final sorted = [...versions]..sort((a, b) => b.fitScore.compareTo(a.fitScore));
    return sorted.first;
  }

  String _humanizeError(Object e) {
    final raw = e.toString();
    if (raw.contains('SocketException')) {
      return 'Network error. Check API server availability and API_BASE_URL.';
    }
    if (raw.contains('timed out')) {
      return 'Request timed out. Please try again.';
    }
    if (raw.contains('413')) {
      return 'Uploaded file is too large for server limits.';
    }
    if (raw.contains('404')) {
      return 'Job not found on backend. Please upload again.';
    }
    if (raw.contains('409')) {
      return 'Job is still processing. Please wait a little longer.';
    }
    return raw.replaceFirst('Exception: ', '');
  }

  @override
  Widget build(BuildContext context) {
    final body = switch (_stage) {
      AppStage.home => HomeScreen(
          onUpload: () => setState(() => _stage = AppStage.upload),
          onDemo: () => setState(() {
            _versions = DemoData.versions;
            _selected = DemoData.versions.first;
            _trackName = 'Neon Skyline';
            _trackDuration = _selected.duration;
            _error = null;
            _stage = AppStage.results;
          }),
        ),
      AppStage.upload => UploadScreen(
          onPickVocal: _pickVocal,
          onPickSong: _pickSong,
          vocalName: _vocalName,
          songName: _songName,
          onAnalyze: _startFromUpload,
          busy: _processingActive,
        ),
      AppStage.processing => ProcessingScreen(
          progress: _progress,
          isRefinement: _refining,
          statusText: _processingMessage,
          canCancel: _processingActive,
          onCancel: () {
            setState(() {
              _processingActive = false;
              _refining = false;
              _processingMessage = 'Canceled by user.';
              _stage = AppStage.upload;
            });
          },
        ),
      AppStage.results => ResultsScreen(
          trackName: _trackName,
          trackDuration: _trackDuration,
          versions: _versions,
          selected: _selected,
          controls: _controls,
          onSelect: (value) => setState(() {
            _selected = value;
            _trackDuration = value.duration;
          }),
          onControlsChanged: (value) => setState(() => _controls = value),
          onMakeBetter: () {
            _startProcessing(refine: true);
          },
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

    return Stack(
      children: [
        AnimatedSwitcher(
          duration: const Duration(milliseconds: 420),
          switchInCurve: Curves.easeOutCubic,
          switchOutCurve: Curves.easeInCubic,
          child: KeyedSubtree(
            key: ValueKey(_stage),
            child: body,
          ),
        ),
        if (_error != null)
          Positioned(
            left: 16,
            right: 16,
            top: 16,
            child: Material(
              color: Colors.transparent,
              child: Container(
                padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
                decoration: BoxDecoration(
                  color: const Color(0x33FF4D4D),
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(color: const Color(0x77FF4D4D)),
                ),
                child: Row(
                  children: [
                    const Icon(Icons.error_outline, color: Colors.white),
                    const SizedBox(width: 8),
                    Expanded(
                      child: Text(
                        _error!,
                        style: const TextStyle(color: Colors.white),
                      ),
                    ),
                    IconButton(
                      onPressed: () => setState(() => _error = null),
                      icon: const Icon(Icons.close, color: Colors.white),
                    ),
                  ],
                ),
              ),
            ),
          ),
      ],
    );
  }
}
