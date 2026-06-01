import 'dart:convert';
import 'dart:math' as math;
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;

void main() {
  runApp(const PocketUniverseApp());
}

class PocketUniverseApp extends StatelessWidget {
  const PocketUniverseApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Pocket Universe',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        brightness: Brightness.dark,
        colorSchemeSeed: const Color(0xFF7C4DFF),
        useMaterial3: true,
        scaffoldBackgroundColor: const Color(0xFF0D0D1A),
      ),
      home: const UniverseScreen(),
    );
  }
}

class UniverseScreen extends StatefulWidget {
  const UniverseScreen({super.key});

  @override
  State<UniverseScreen> createState() => _UniverseScreenState();
}

class _UniverseScreenState extends State<UniverseScreen> {
  final _seedController = TextEditingController();
  Map<String, dynamic>? _universe;
  bool _loading = false;
  String? _error;
  final List<String> _history = [];

  static const _apiBase = 'http://localhost:8080';

  Future<void> _generate({String? seed}) async {
    final s = seed ?? _seedController.text.trim();
    if (s.isEmpty) return;

    setState(() {
      _loading = true;
      _error = null;
    });

    try {
      final uri = Uri.parse('$_apiBase/generate?seed=${Uri.encodeComponent(s)}');
      final response = await http.get(uri);
      if (response.statusCode != 200) {
        throw Exception('API error: ${response.statusCode}');
      }
      final data = jsonDecode(response.body) as Map<String, dynamic>;
      if (data.containsKey('error')) {
        throw Exception(data['error']);
      }
      setState(() {
        _universe = data;
        _loading = false;
        if (!_history.contains(s)) {
          _history.insert(0, s);
          if (_history.length > 20) _history.removeLast();
        }
      });
    } catch (e) {
      setState(() {
        _error = e.toString().replaceFirst('Exception: ', '');
        _loading = false;
      });
    }
  }

  @override
  void initState() {
    super.initState();
    _seedController.text = 'ember';
  }

  @override
  void dispose() {
    _seedController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Pocket Universe'),
        centerTitle: true,
        backgroundColor: const Color(0xFF0D0D1A),
        elevation: 0,
      ),
      body: Column(
        children: [
          _buildInputArea(),
          if (_error != null) _buildError(),
          if (_loading) const Expanded(child: Center(child: CircularProgressIndicator())),
          if (_universe != null && !_loading) Expanded(child: _buildUniverse()),
          if (_universe == null && !_loading && _error == null) _buildEmpty(),
        ],
      ),
    );
  }

  Widget _buildInputArea() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: [
            const Color(0xFF1A1A2E).withValues(alpha: 0.8),
            const Color(0xFF0D0D1A),
          ],
          begin: Alignment.topCenter,
          end: Alignment.bottomCenter,
        ),
      ),
      child: Column(
        children: [
          Row(
            children: [
              Expanded(
                child: TextField(
                  controller: _seedController,
                  style: const TextStyle(fontSize: 18, fontFamily: 'monospace'),
                  decoration: InputDecoration(
                    hintText: 'Enter a seed word...',
                    hintStyle: TextStyle(color: Colors.white.withValues(alpha: 0.3), fontFamily: 'monospace'),
                    filled: true,
                    fillColor: const Color(0xFF1A1A2E),
                    border: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(12),
                      borderSide: BorderSide.none,
                    ),
                    contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
                  ),
                  onSubmitted: (_) => _generate(),
                ),
              ),
              const SizedBox(width: 12),
              FilledButton.icon(
                onPressed: _loading ? null : _generate,
                icon: const Icon(Icons.auto_awesome),
                label: const Text('Generate'),
                style: FilledButton.styleFrom(
                  padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 14),
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                ),
              ),
            ],
          ),
          if (_history.isNotEmpty) ...[
            const SizedBox(height: 8),
            SizedBox(
              height: 36,
              child: ListView.separated(
                scrollDirection: Axis.horizontal,
                itemCount: _history.length,
                separatorBuilder: (_, __) => const SizedBox(width: 6),
                itemBuilder: (context, i) {
                  final seed = _history[i];
                  final active = seed == _seedController.text.trim();
                  return ActionChip(
                    label: Text(seed, style: const TextStyle(fontFamily: 'monospace')),
                    onPressed: () {
                      _seedController.text = seed;
                      _generate(seed: seed);
                    },
                    backgroundColor: active ? const Color(0xFF7C4DFF) : const Color(0xFF1A1A2E),
                    side: BorderSide.none,
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
                    padding: const EdgeInsets.symmetric(horizontal: 4),
                  );
                },
              ),
            ),
          ],
        ],
      ),
    );
  }

  Widget _buildError() {
    return Container(
      margin: const EdgeInsets.all(16),
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: const Color(0xFF4A1C1C),
        borderRadius: BorderRadius.circular(8),
      ),
      child: Row(
        children: [
          const Icon(Icons.error_outline, color: Color(0xFFFF6B6B)),
          const SizedBox(width: 8),
          Expanded(child: Text(_error!, style: const TextStyle(color: Color(0xFFFF6B6B)))),
        ],
      ),
    );
  }

  Widget _buildEmpty() {
    return const Expanded(
      child: Center(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(Icons.auto_awesome, size: 64, color: Color(0xFF3A3A5C)),
            SizedBox(height: 16),
            Text(
              'Type a seed and generate\na pocket universe.',
              textAlign: TextAlign.center,
              style: TextStyle(color: Color(0xFF5A5A7C), fontSize: 16),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildUniverse() {
    final u = _universe!;
    final name = u['name'] as String;
    final terrain = u['terrain'] as String;
    final phys = u['physics'] as Map<String, dynamic>;
    final regions = (u['regions'] as List).cast<Map<String, dynamic>>();
    final cities = (u['cities'] as List).cast<String>();
    final cal = u['calendar'] as Map<String, dynamic>;
    final pantheon = u['pantheon'] as Map<String, dynamic>;
    final myth = u['creation_myth'] as String;
    final eco = u['ecology'] as Map<String, dynamic>;
    final lang = u['language'] as Map<String, dynamic>;
    final culture = u['culture'] as Map<String, dynamic>;

    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Header
          Center(
            child: Column(
              children: [
                Icon(Icons.public, size: 32, color: Colors.white.withValues(alpha: 0.5)),
                const SizedBox(height: 8),
                Text(name, style: const TextStyle(fontSize: 28, fontWeight: FontWeight.bold, letterSpacing: 1)),
                const SizedBox(height: 4),
                Text(terrain.toUpperCase(), style: TextStyle(fontSize: 13, color: Colors.white.withValues(alpha: 0.5), letterSpacing: 2)),
                const SizedBox(height: 16),
              ],
            ),
          ),

          // Physics
          _SectionCard(
            icon: Icons.science_outlined,
            title: 'Physics',
            child: _grid([
              ['Radius', '${phys['radius']}× Earth'],
              ['Gravity', '${phys['gravity']}× Earth'],
              ['Day', '${phys['day_length']}h'],
              ['Year', '${phys['year_length']} days'],
              ['Tilt', '${phys['axial_tilt']}°'],
              ['Rings', phys['has_rings'] ? 'Yes' : 'No'],
              ['Moons', '${phys['moon_count']}'],
            ]),
          ),

          // Regions
          if (regions.isNotEmpty) _SectionCard(
            icon: Icons.map_outlined,
            title: 'Regions',
            child: Column(
              children: [
                for (final r in regions)
                  Padding(
                    padding: const EdgeInsets.symmetric(vertical: 3),
                    child: Row(
                      children: [
                        SizedBox(
                          width: 120,
                          child: Text(r['name'] as String, style: const TextStyle(fontWeight: FontWeight.w500, fontFamily: 'monospace')),
                        ),
                        Text(r['terrain'] as String, style: TextStyle(color: Colors.white.withValues(alpha: 0.6))),
                      ],
                    ),
                  ),
                if (cities.isNotEmpty) ...[
                  const SizedBox(height: 8),
                  Text('Cities: ${cities.map((c) => c as String).join(', ')}',
                    style: TextStyle(color: Colors.white.withValues(alpha: 0.6), fontSize: 13)),
                ],
              ],
            ),
          ),

          // Calendar
          _SectionCard(
            icon: Icons.calendar_month_outlined,
            title: 'Calendar',
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                _label('Seasons', (cal['seasons'] as List).join(' → ')),
                _label('Months', (cal['months'] as List).join(', ')),
                if ((cal['festivals'] as List?)?.isNotEmpty == true)
                  _label('Festivals', (cal['festivals'] as List).join(', ')),
              ],
            ),
          ),

          // Pantheon
          _SectionCard(
            icon: Icons.auto_awesome,
            title: 'Pantheon',
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                for (final entry in pantheon.entries)
                  Padding(
                    padding: const EdgeInsets.only(bottom: 8),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text('\u2022 ${entry.key}',
                          style: const TextStyle(fontWeight: FontWeight.w600, fontFamily: 'monospace', fontSize: 15)),
                        Padding(
                          padding: const EdgeInsets.only(left: 16),
                          child: Text(
                            '${entry.value['archetype']} · ${entry.value['domain']}\n${entry.value['epithet']}',
                            style: TextStyle(color: Colors.white.withValues(alpha: 0.6), fontSize: 13),
                          ),
                        ),
                      ],
                    ),
                  ),
                const SizedBox(height: 4),
                Container(
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: const Color(0xFF1A1A2E),
                    borderRadius: BorderRadius.circular(8),
                    border: Border.all(color: const Color(0xFF2A2A4C)),
                  ),
                  child: Text('"The world was $myth."',
                    style: TextStyle(
                      fontStyle: FontStyle.italic,
                      color: Colors.white.withValues(alpha: 0.7),
                    ),
                  ),
                ),
              ],
            ),
          ),

          // Ecology
          _SectionCard(
            icon: Icons.forest_outlined,
            title: 'Ecology',
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                _label('Signature Flora', eco['signature_flora'] as String),
                _label('Signature Fauna', eco['signature_fauna'] as String),
                const SizedBox(height: 4),
                _label('Flora', (eco['flora'] as List).join(', ')),
                _label('Fauna', (eco['fauna'] as List).join(', ')),
              ],
            ),
          ),

          // Language
          _SectionCard(
            icon: Icons.translate,
            title: 'Language',
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                _label('Grammar', lang['grammar'] as String),
                if (lang['has_gender'] == true || lang['has_tones'] == true)
                  _label('Features', [
                    if (lang['has_gender'] == true) 'Gendered',
                    if (lang['has_tones'] == true) 'Tonal',
                  ].join(', ')),
                const SizedBox(height: 8),
                ...(lang['lexicon'] as Map<String, dynamic>).entries.take(15).map((e) => Padding(
                  padding: const EdgeInsets.symmetric(vertical: 1),
                  child: Row(
                    children: [
                      SizedBox(
                        width: 100,
                        child: Text('${e.key}:', style: TextStyle(color: Colors.white.withValues(alpha: 0.5), fontSize: 12)),
                      ),
                      Text(e.value as String, style: const TextStyle(fontWeight: FontWeight.w500, fontFamily: 'monospace', fontSize: 14)),
                    ],
                  ),
                )),
              ],
            ),
          ),

          // Culture
          _SectionCard(
            icon: Icons.groups_outlined,
            title: 'Culture',
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                _label('Social Structure', culture['social_structure'] as String),
                _label('Values', (culture['values'] as List).join(', ')),
                _label('Taboos', (culture['taboos'] as List).join(', ')),
                _label('Burial', culture['burial'] as String),
              ],
            ),
          ),

          const SizedBox(height: 32),
          Center(
            child: Text('pocket-universe://${_seedController.text.trim()}',
              style: TextStyle(fontSize: 11, color: Colors.white.withValues(alpha: 0.2), fontFamily: 'monospace')),
          ),
          const SizedBox(height: 32),
        ],
      ),
    );
  }

  Widget _label(String label, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 2),
      child: RichText(
        text: TextSpan(
          style: TextStyle(fontSize: 13, color: Colors.white.withValues(alpha: 0.7)),
          children: [
            TextSpan(text: '$label: ', style: TextStyle(color: Colors.white.withValues(alpha: 0.4))),
            TextSpan(text: value),
          ],
        ),
      ),
    );
  }

  Widget _grid(List<List<String>> rows) {
    return Column(
      children: rows.map((r) => Padding(
        padding: const EdgeInsets.symmetric(vertical: 3),
        child: Row(
          children: [
            SizedBox(width: 80, child: Text(r[0], style: TextStyle(color: Colors.white.withValues(alpha: 0.4)))),
            Text(r[1], style: const TextStyle(fontWeight: FontWeight.w500)),
          ],
        ),
      )).toList(),
    );
  }
}

class _SectionCard extends StatelessWidget {
  final IconData icon;
  final String title;
  final Widget child;

  const _SectionCard({required this.icon, required this.title, required this.child});

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      color: const Color(0xFF13132B),
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12), side: const BorderSide(color: Color(0xFF1E1E3A), width: 1)),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(icon, size: 16, color: const Color(0xFF7C4DFF)),
                const SizedBox(width: 8),
                Text(title, style: const TextStyle(fontSize: 16, fontWeight: FontWeight.w600, letterSpacing: 0.5)),
              ],
            ),
            const Divider(color: Color(0xFF1E1E3A), height: 20),
            child,
          ],
        ),
      ),
    );
  }
}
