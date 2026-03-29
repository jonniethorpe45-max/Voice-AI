import 'package:just_audio/just_audio.dart';

class AudioPlayerService {
  AudioPlayerService();

  final Map<String, AudioPlayer> _players = {};
  final Map<String, bool> _loading = {};
  String? _activeId;

  AudioPlayer _getPlayer(String id) {
    return _players.putIfAbsent(id, AudioPlayer.new);
  }

  bool isPlaying(String id) {
    final player = _players[id];
    return player?.playing ?? false;
  }

  bool isLoading(String id) {
    return _loading[id] ?? false;
  }

  double positionFactor(String id) {
    final player = _players[id];
    if (player == null) {
      return 0.0;
    }
    final duration = player.duration;
    if (duration == null || duration.inMilliseconds <= 0) {
      return 0.0;
    }
    final ratio = player.position.inMilliseconds / duration.inMilliseconds;
    return ratio.clamp(0.0, 1.0);
  }

  double bufferedFactor(String id) {
    final player = _players[id];
    if (player == null) {
      return 0.0;
    }
    final duration = player.duration;
    if (duration == null || duration.inMilliseconds <= 0) {
      return 0.0;
    }
    final ratio = player.bufferedPosition.inMilliseconds / duration.inMilliseconds;
    return ratio.clamp(0.0, 1.0);
  }

  Future<void> toggle({
    required String id,
    required String url,
  }) async {
    final player = _getPlayer(id);

    if (_activeId != null && _activeId != id) {
      final old = _players[_activeId!];
      if (old != null && old.playing) {
        await old.pause();
      }
    }

    if (player.playing) {
      await player.pause();
      return;
    }

    _loading[id] = true;
    try {
      if (_activeId != id) {
        await player.setUrl(url);
      }
      _activeId = id;
      await player.play();
    } finally {
      _loading[id] = false;
    }
  }

  Future<void> seekFactor({
    required String id,
    required double factor,
  }) async {
    final player = _players[id];
    if (player == null) {
      return;
    }
    final duration = player.duration;
    if (duration == null || duration.inMilliseconds <= 0) {
      return;
    }
    final millis = (duration.inMilliseconds * factor.clamp(0.0, 1.0)).round();
    await player.seek(Duration(milliseconds: millis));
  }

  Future<void> dispose() async {
    for (final player in _players.values) {
      await player.dispose();
    }
    _players.clear();
    _loading.clear();
    _activeId = null;
  }
}
