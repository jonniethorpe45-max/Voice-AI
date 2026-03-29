import 'app_models.dart';

class DemoData {
  static const processingText = [
    'Analyzing pitch...',
    'Understanding your style...',
    'Matching song energy...',
    'Enhancing your vocal...',
  ];

  static const versions = [
    VocalVersion(
      id: 'studio',
      label: 'Studio Clean',
      fitScore: 95.2,
      duration: '03:24',
      waveSeed: 4,
      bestFit: true,
    ),
    VocalVersion(
      id: 'radio',
      label: 'Radio Pop',
      fitScore: 92.7,
      duration: '03:24',
      waveSeed: 7,
    ),
    VocalVersion(
      id: 'soulful',
      label: 'Soulful',
      fitScore: 90.3,
      duration: '03:24',
      waveSeed: 2,
    ),
    VocalVersion(
      id: 'power',
      label: 'Power Vocal',
      fitScore: 91.4,
      duration: '03:24',
      waveSeed: 9,
    ),
    VocalVersion(
      id: 'natural',
      label: 'Natural',
      fitScore: 88.8,
      duration: '03:24',
      waveSeed: 5,
    ),
  ];
}
