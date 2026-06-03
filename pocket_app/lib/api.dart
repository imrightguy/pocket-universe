import 'dart:convert';
import 'package:flutter/foundation.dart' show kIsWeb;
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;

class PocketUniverseApi {
  static String get _baseUrl {
    if (kIsWeb) {
      // Web: relative paths work in production (same origin).
      // In flutter run dev mode the app is served on a localhost port
      // but the backend lives on 8080 — use the explicit URL.
      try {
        final uri = Uri.base;
        if (uri.host == 'localhost' || uri.host == '127.0.0.1') {
          return 'http://localhost:8080';
        }
      } catch (_) {
        // Uri.base unavailable in some contexts; fall through to relative.
      }
      return '';
    }
    // Native (Android/iOS/desktop) — always explicit
    return 'http://localhost:8080';
  }

  Future<Map<String, dynamic>> generateWorld(String seed) async {
    final response = await http.get(
      Uri.parse('$_baseUrl/generate?seed=$seed'),
    );
    if (response.statusCode == 200) {
      return json.decode(response.body) as Map<String, dynamic>;
    }
    throw Exception('Failed to generate world: ${response.statusCode}');
  }

  Future<List<String>> getSeeds() async {
    final response = await http.get(Uri.parse('$_baseUrl/seeds'));
    if (response.statusCode == 200) {
      final data = json.decode(response.body) as Map<String, dynamic>;
      return List<String>.from(data['seeds'] as List);
    }
    return PocketUniverseApi.defaultSeeds();
  }

  static List<String> defaultSeeds() {
    return [
      'ember', 'thaw', 'drift', 'cinder', 'hollow', 'veil',
      'fold', 'knot', 'pulse', 'spark', 'shard', 'echo',
      'bloom', 'rust', 'salt', 'tar', 'lime', 'frost',
      'dust', 'flint', 'mica', 'resin', 'silt', 'brine',
      'char', 'flux', 'grit', 'haze', 'loam', 'moss',
    ];
  }

  String terrainColor(String terrain) {
    const colors = {
      'archipelago': Color(0xFF4a9be0),
      'desert': Color(0xFFe8c86a),
      'forest': Color(0xFF3a7d34),
      'highlands': Color(0xFF8b7355),
      'marsh': Color(0xFF7a9a6b),
      'oceanic': Color(0xFF2a6bb0),
      'plains': Color(0xFFb8d4a0),
      'tundra': Color(0xFFd4d4d4),
      'volcanic': Color(0xFF8b4513),
    };
    final c = colors[terrain] ?? const Color(0xFF888888);
    return '#${c.value.toRadixString(16).substring(2)}';
  }
}
