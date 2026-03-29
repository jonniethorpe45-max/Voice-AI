import 'package:flutter/material.dart';
import 'package:url_launcher/url_launcher.dart';

import '../components/glass_card.dart';
import '../components/neon_button.dart';
import '../core/app_models.dart';
import '../theme/app_theme.dart';

class ExportScreen extends StatefulWidget {
  const ExportScreen({
    super.key,
    required this.selected,
    required this.onBack,
  });

  final VocalVersion selected;
  final VoidCallback onBack;

  @override
  State<ExportScreen> createState() => _ExportScreenState();
}

class _ExportScreenState extends State<ExportScreen> {
  String _format = 'WAV';
  bool _exporting = false;

  Future<void> _launchExport() async {
    if (_exporting) {
      return;
    }
    setState(() => _exporting = true);
    final media = widget.selected.mediaUrl;
    if (media.isEmpty) {
      if (!mounted) {
        return;
      }
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('No media URL available for export.')),
      );
      if (mounted) {
        setState(() => _exporting = false);
      }
      return;
    }
    final uri = Uri.tryParse(media);
    if (uri == null) {
      if (!mounted) {
        return;
      }
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Invalid media URL.')),
      );
      if (mounted) {
        setState(() => _exporting = false);
      }
      return;
    }
    final launched = await launchUrl(
      uri,
      mode: LaunchMode.externalApplication,
    );
    if (!launched && mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Unable to open export URL.')),
      );
    }
    if (mounted) {
      setState(() => _exporting = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.all(AppTheme.s20),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          TextButton.icon(
            onPressed: widget.onBack,
            icon: const Icon(Icons.arrow_back),
            label: const Text('Back'),
          ),
          const SizedBox(height: AppTheme.s12),
          Text('Export', style: Theme.of(context).textTheme.headlineMedium),
          const SizedBox(height: AppTheme.s8),
          Text(
            'Choose output format and export the studio version.',
            style: Theme.of(context).textTheme.bodyMedium,
          ),
          const SizedBox(height: AppTheme.s20),
          GlassCard(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text('Selected Version', style: TextStyle(color: AppTheme.textLow)),
                const SizedBox(height: AppTheme.s8),
                Text(
                  '${widget.selected.label} • ${widget.selected.duration}',
                  style: const TextStyle(fontSize: 20, fontWeight: FontWeight.w700),
                ),
              ],
            ),
          ),
          const SizedBox(height: AppTheme.s20),
          GlassCard(
            child: Wrap(
              spacing: AppTheme.s8,
              runSpacing: AppTheme.s8,
              children: ['MP3', 'WAV', 'Stems'].map((item) {
                final active = _format == item;
                return ChoiceChip(
                  label: Text(item),
                  selected: active,
                  selectedColor: AppTheme.neonBlue.withOpacity(0.18),
                  backgroundColor: Colors.white.withOpacity(0.05),
                  side: BorderSide(color: active ? AppTheme.neonBlue : AppTheme.border),
                  onSelected: (_) => setState(() => _format = item),
                );
              }).toList(),
            ),
          ),
          const Spacer(),
          NeonButton(
            text: _exporting ? 'Exporting...' : 'Export Studio Version',
            icon: Icons.rocket_launch_rounded,
            onPressed: _exporting ? null : _launchExport,
          ),
        ],
      ),
    );
  }
}
