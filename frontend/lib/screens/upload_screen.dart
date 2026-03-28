import 'dart:io';

import 'package:file_picker/file_picker.dart';
import 'package:flutter/material.dart';

import '../widgets/primary_button.dart';

class UploadScreen extends StatefulWidget {
  const UploadScreen({super.key, required this.onSubmit});

  final Future<void> Function(File vocalFile, File? songFile) onSubmit;

  @override
  State<UploadScreen> createState() => _UploadScreenState();
}

class _UploadScreenState extends State<UploadScreen> {
  File? _vocalFile;
  File? _songFile;
  bool _submitting = false;

  Future<void> _pickVocal() async {
    final result = await FilePicker.platform.pickFiles(
      type: FileType.custom,
      allowedExtensions: ['wav', 'mp3', 'm4a'],
      allowMultiple: false,
      dialogTitle: 'Select vocal track',
    );
    final path = result?.files.single.path;
    if (path == null) {
      return;
    }
    setState(() => _vocalFile = File(path));
  }

  Future<void> _pickSong() async {
    final result = await FilePicker.platform.pickFiles(
      type: FileType.custom,
      allowedExtensions: ['wav', 'mp3', 'm4a'],
      allowMultiple: false,
      dialogTitle: 'Select instrumental/full song (optional)',
    );
    final path = result?.files.single.path;
    if (path == null) {
      return;
    }
    setState(() => _songFile = File(path));
  }

  Future<void> _submit() async {
    final vocal = _vocalFile;
    if (vocal == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Please select a vocal file first.')),
      );
      return;
    }
    setState(() => _submitting = true);
    try {
      await widget.onSubmit(vocal, _songFile);
    } finally {
      if (mounted) {
        setState(() => _submitting = false);
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.all(20),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const SizedBox(height: 10),
          const Text(
            'VocalFit AI',
            style: TextStyle(fontSize: 30, fontWeight: FontWeight.w700),
          ),
          const SizedBox(height: 8),
          Text(
            'Intelligent Vocal Transformation Engine',
            style: TextStyle(color: Colors.grey.shade300),
          ),
          const SizedBox(height: 24),
          _tile(
            title: 'Vocal Track (required)',
            subtitle: _vocalFile == null ? 'WAV / MP3 / M4A' : _vocalFile!.path,
            icon: Icons.mic,
            action: 'Choose',
            onTap: _pickVocal,
          ),
          const SizedBox(height: 12),
          _tile(
            title: 'Instrumental / Full Song (optional)',
            subtitle: _songFile == null ? 'Recommended for song-aware mode' : _songFile!.path,
            icon: Icons.graphic_eq,
            action: 'Choose',
            onTap: _pickSong,
          ),
          const Spacer(),
          PrimaryButton(
            text: _submitting ? 'Uploading...' : 'Upload & Process',
            icon: Icons.cloud_upload,
            onPressed: _submitting ? null : _submit,
          ),
          const SizedBox(height: 12),
        ],
      ),
    );
  }

  Widget _tile({
    required String title,
    required String subtitle,
    required IconData icon,
    required String action,
    required VoidCallback onTap,
  }) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: const Color(0xFF1A1E2A),
        borderRadius: BorderRadius.circular(14),
        border: Border.all(color: const Color(0xFF2B3142)),
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Icon(icon, color: const Color(0xFF7C9DFF)),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(title, style: const TextStyle(fontWeight: FontWeight.w600)),
                const SizedBox(height: 6),
                Text(
                  subtitle,
                  maxLines: 2,
                  overflow: TextOverflow.ellipsis,
                  style: TextStyle(color: Colors.grey.shade400, fontSize: 13),
                ),
              ],
            ),
          ),
          TextButton(onPressed: onTap, child: Text(action)),
        ],
      ),
    );
  }
}
