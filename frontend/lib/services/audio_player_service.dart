import 'package:just_audio/just_audio.dart';

class AudioPlayerService {
  AudioPlayerService();

  final Map<String, AudioPlayer> _players = {};
  final Map<String, bool> _loading = {};
  final Map<String, String> _errors = {};
  String? _activeId;

  String? get lastError => _activeId != null ? _errors[_activeId!] : null;

  String? lastErrorFor(String id) => _errors[id];

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

  bool get anyPlaying => _players.values.any((p) => p.playing);

  bool get anyLoading => _loading.values.any((v) => v);

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

  Future<bool> toggle({
    required String id,
    required String url,
  }) async {
    if (url.isEmpty) {
      _errors[id] = 'No media URL available for this variation.';
      return false;
    }
    final player = _getPlayer(id);

    if (_activeId != null && _activeId != id) {
      final old = _players[_activeId!];
      if (old != null && old.playing) {
        await old.pause();
      }
    }

    if (player.playing) {
      await player.pause();
      _errors.remove(id);
      return true;
    }

    _loading[id] = true;
    try {
      if (_activeId != id) {
        await player.setUrl(url);
      }
      _activeId = id;
      await player.play();
      _errors.remove(id);
      return true;
    } catch (e) {
      _errors[id] = 'Playback failed. Check media URL/network. (${e.runtimeType})';
      return false;
    } finally {
      _loading[id] = false;
    }
  }

  Future<bool> seekFactor({
    required String id,
    required double factor,
  }) async {
    final player = _players[id];
    if (player == null) {
      _errors[id] = 'Playback is not initialized.';
      return false;
    }
    final duration = player.duration;
    if (duration == null || duration.inMilliseconds <= 0) {
      _errors[id] = 'Track duration is unavailable.';
      return false;
    }
    final millis = (duration.inMilliseconds * factor.clamp(0.0, 1.0)).round();
    try {
      await player.seek(Duration(milliseconds: millis));
      _errors.remove(id);
      return true;
    } catch (e) {
      _errors[id] = 'Seek failed. (${e.runtimeType})';
      return false;
    }
  }

  Future<void> dispose() async {
    for (final player in _players.values) {
      await player.dispose();
    }
    _players.clear();
    _loading.clear();
    _errors.clear();
    _activeId = null;
  }
}
