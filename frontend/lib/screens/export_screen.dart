import 'package:flutter/material.dart';

import '../models.dart';
import '../widgets/primary_button.dart';

class ExportScreen extends StatelessWidget {
  const ExportScreen({
    super.key,
    required this.results,
    required this.onBack,
  });

  final JobResults? results;
  final VoidCallback onBack;

  @override
  Widget build(BuildContext context) {
    final first = (results != null && results!.variations.isNotEmpty)
        ? results!.variations.first
        : null;
    return Padding(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const SizedBox(height: 8),
          const Text(
            'Export',
            style: TextStyle(fontSize: 24, fontWeight: FontWeight.w700),
          ),
          const SizedBox(height: 8),
          Text(
            first == null ? 'No variation selected.' : 'Selected: ${first.label}',
            style: TextStyle(color: Colors.grey.shade300),
          ),
          const SizedBox(height: 12),
          const Text(
            'In production this action can export locally, share to other apps, '
            'or send directly to cloud storage.',
          ),
          const Spacer(),
          PrimaryButton(
            text: 'Export Mix',
            icon: Icons.download_rounded,
            onPressed: () {
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(content: Text('Export hook ready for integration.')),
              );
            },
          ),
          const SizedBox(height: 10),
          TextButton.icon(
            onPressed: onBack,
            icon: const Icon(Icons.arrow_back),
            label: const Text('Back'),
          ),
        ],
      ),
    );
  }
}
