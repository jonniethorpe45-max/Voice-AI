import 'package:flutter/material.dart';

import '../models.dart';
import '../widgets/primary_button.dart';

class ResultsScreen extends StatelessWidget {
  const ResultsScreen({
    super.key,
    required this.results,
    required this.onAdjust,
    required this.onExport,
    required this.onReset,
  });

  final JobResults? results;
  final VoidCallback onAdjust;
  final VoidCallback onExport;
  final VoidCallback onReset;

  @override
  Widget build(BuildContext context) {
    final data = results;
    if (data == null) {
      return Center(
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              const Text('No results available yet.'),
              const SizedBox(height: 12),
              PrimaryButton(
                text: 'Back to Upload',
                icon: Icons.upload_file,
                onPressed: onReset,
              ),
            ],
          ),
        ),
      );
    }

    return Padding(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text('Results', style: Theme.of(context).textTheme.headlineSmall),
          const SizedBox(height: 8),
          Text(
            'Key: ${data.analysis['key'] ?? 'Unknown'} | Scale: ${data.analysis['scale'] ?? 'Unknown'}',
            style: TextStyle(color: Colors.grey.shade400),
          ),
          const SizedBox(height: 12),
          Expanded(
            child: ListView.separated(
              itemCount: data.variations.length,
              separatorBuilder: (_, __) => const SizedBox(height: 8),
              itemBuilder: (context, index) {
                final variation = data.variations[index];
                return Container(
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: const Color(0xFF171B24),
                    borderRadius: BorderRadius.circular(12),
                    border: Border.all(color: const Color(0xFF2A3140)),
                  ),
                  child: Row(
                    children: [
                      const Icon(Icons.graphic_eq, color: Color(0xFF7C9DFF)),
                      const SizedBox(width: 10),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              variation.label,
                              style: const TextStyle(fontWeight: FontWeight.w600),
                            ),
                            const SizedBox(height: 2),
                            Text(
                              variation.mediaUrl,
                              overflow: TextOverflow.ellipsis,
                              style: TextStyle(
                                color: Colors.grey.shade400,
                                fontSize: 12,
                              ),
                            ),
                          ],
                        ),
                      ),
                      const Icon(Icons.play_circle_outline),
                    ],
                  ),
                );
              },
            ),
          ),
          const SizedBox(height: 12),
          Row(
            children: [
              Expanded(
                child: PrimaryButton(
                  text: 'Controls',
                  icon: Icons.tune,
                  onPressed: onAdjust,
                ),
              ),
              const SizedBox(width: 10),
              Expanded(
                child: PrimaryButton(
                  text: 'Export',
                  icon: Icons.ios_share,
                  onPressed: onExport,
                ),
              ),
            ],
          ),
          const SizedBox(height: 8),
          TextButton.icon(
            onPressed: onReset,
            icon: const Icon(Icons.restart_alt),
            label: const Text('Start Over'),
          ),
        ],
      ),
    );
  }
}
