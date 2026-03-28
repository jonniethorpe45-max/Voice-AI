import 'dart:io';

import 'package:flutter/material.dart';

import 'models.dart';
import 'screens/controls_screen.dart';
import 'screens/export_screen.dart';
import 'screens/processing_screen.dart';
import 'screens/results_screen.dart';
import 'screens/upload_screen.dart';
import 'services/api_client.dart';

const _defaultBase = String.fromEnvironment(
  'API_BASE_URL',
  defaultValue: 'http://localhost:8000',
);

void main() {
  runApp(const VocalFitApp());
}

class VocalFitApp extends StatelessWidget {
  const VocalFitApp({super.key});

  @override
  Widget build(BuildContext context) {
    final scheme = ColorScheme.fromSeed(
      seedColor: const Color(0xFF7C4DFF),
      brightness: Brightness.dark,
    );
    return MaterialApp(
      title: 'VocalFit AI',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        colorScheme: scheme,
        scaffoldBackgroundColor: const Color(0xFF0B0F14),
        useMaterial3: true,
      ),
      home: const AppShell(),
    );
  }
}

enum AppStage { upload, processing, results, controls, export }

class AppShell extends StatefulWidget {
  const AppShell({super.key});

  @override
  State<AppShell> createState() => _AppShellState();
}

class _AppShellState extends State<AppShell> {
  final ApiClient _api = ApiClient(baseUrl: _defaultBase);

  AppStage _stage = AppStage.upload;
  StyleControls _controls = StyleControls();

  String? _jobId;
  String? _error;
  JobStatus _status = const JobStatus.initial();
  JobResults? _results;

  Future<void> _startJob(File vocal, File? song) async {
    setState(() {
      _error = null;
      _stage = AppStage.processing;
      _results = null;
      _status = const JobStatus.initial();
    });
    try {
      final jobId = await _api.upload(vocalPath: vocal.path, instrumentalPath: song?.path);
      _jobId = jobId;
      await _api.process(
        jobId: jobId,
        controls: _controls,
        preferredVariations: const [],
      );
      await _pollUntilComplete(jobId);
    } catch (e) {
      setState(() {
        _error = e.toString();
        _stage = AppStage.upload;
      });
    }
  }

  Future<void> _pollUntilComplete(String jobId) async {
    for (var i = 0; i < 120; i++) {
      final status = await _api.status(jobId);
      setState(() => _status = status);
      if (status.status == 'completed' || status.status == 'completed_with_warnings') {
        final results = await _api.results(jobId);
        setState(() {
          _results = results;
          _stage = AppStage.results;
        });
        return;
      }
      if (status.status == 'failed') {
        setState(() {
          _error = status.error ?? status.message;
          _stage = AppStage.upload;
        });
        return;
      }
      await Future.delayed(const Duration(seconds: 2));
    }
    setState(() {
      _error = 'Processing timed out.';
      _stage = AppStage.upload;
    });
  }

  Future<void> _applyControlsAndReprocess(StyleControls next) async {
    if (_jobId == null) {
      return;
    }
    setState(() {
      _controls = next;
      _error = null;
      _stage = AppStage.processing;
      _results = null;
    });
    try {
      await _api.process(
        jobId: _jobId!,
        controls: next,
        preferredVariations: const [],
      );
      await _pollUntilComplete(_jobId!);
    } catch (e) {
      setState(() {
        _error = e.toString();
        _stage = AppStage.results;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    Widget body;
    switch (_stage) {
      case AppStage.upload:
        body = UploadScreen(onSubmit: _startJob);
      case AppStage.processing:
        body = ProcessingScreen(
          progress: (_status.progress.clamp(0, 100)) / 100.0,
          message: _status.message,
        );
      case AppStage.results:
        body = ResultsScreen(
          results: _results,
          onAdjust: () => setState(() => _stage = AppStage.controls),
          onExport: () => setState(() => _stage = AppStage.export),
          onReset: () => setState(() {
            _stage = AppStage.upload;
            _jobId = null;
            _results = null;
            _status = const JobStatus.initial();
            _error = null;
          }),
        );
      case AppStage.controls:
        body = ControlsScreen(
          initial: _controls,
          onApply: _applyControlsAndReprocess,
          onBack: () => setState(() => _stage = AppStage.results),
        );
      case AppStage.export:
        body = ExportScreen(
          results: _results,
          onBack: () => setState(() => _stage = AppStage.results),
        );
    }

    return Scaffold(
      appBar: AppBar(title: const Text('VocalFit AI')),
      body: Column(
        children: [
          if (_error != null)
            Container(
              width: double.infinity,
              color: Colors.red.withOpacity(0.2),
              padding: const EdgeInsets.all(10),
              child: Text(_error!, style: const TextStyle(color: Colors.redAccent)),
            ),
          Expanded(child: body),
        ],
      ),
    );
  }
}
