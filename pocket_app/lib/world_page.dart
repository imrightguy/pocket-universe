import 'package:flutter/material.dart';
import 'api.dart';
import 'bestiary_page.dart';

class WorldPage extends StatefulWidget {
  final String seed;
  const WorldPage({super.key, required this.seed});

  @override
  State<WorldPage> createState() => _WorldPageState();
}

class _WorldPageState extends State<WorldPage> {
  final PocketUniverseApi _api = PocketUniverseApi();
  Map<String, dynamic>? _world;
  bool _loading = true;
  String? _error;

  @override
  void initState() {
    super.initState();
    _loadWorld();
  }

  Future<void> _loadWorld() async {
    setState(() => _loading = true);
    try {
      final world = await _api.generateWorld(widget.seed);
      setState(() {
        _world = world;
        _loading = false;
      });
    } catch (e) {
      setState(() {
        _error = e.toString();
        _loading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(widget.seed.toUpperCase()),
        centerTitle: true,
        backgroundColor: Colors.transparent,
        elevation: 0,
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: _loadWorld,
          ),
        ],
      ),
      body: _loading
          ? const Center(child: CircularProgressIndicator())
          : _error != null
              ? Center(
                  child: Padding(
                    padding: const EdgeInsets.all(16),
                    child: Text('Error: $_error',
                        style: const TextStyle(color: Colors.red)),
                  ),
                )
              : _worldBody(),
    );
  }

  Widget _worldBody() {
    final world = _world!;
    final name = world['name'] as String? ?? 'Unknown';
    final terrain = world['terrain'] as String? ?? 'unknown';
    final physics = world['physics'] as Map<String, dynamic>? ?? {};
    final regions = world['regions'] as List<dynamic>? ?? [];
    final creatures = (world['ecology'] as Map<String, dynamic>?)
            ?['creatures'] as List<dynamic>? ??
        [];
    final culture = world['culture'] as Map<String, dynamic>?;
    final calendar = world['calendar'] as Map<String, dynamic>?;

    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Hero section
          _HeroCard(name: name, terrain: terrain, seed: widget.seed),
          const SizedBox(height: 16),

          // Physics
          _SectionCard(
            title: 'PHYSICS',
            icon: Icons.science,
            children: [
              _StatRow('Gravity', '${physics['gravity']}G'),
              _StatRow('Radius', '${physics['radius']}× Earth'),
              _StatRow('Day', '${physics['day_length']}h'),
              _StatRow('Year', '${physics['year_length']} days'),
              _StatRow('Tilt', '${physics['axial_tilt']}°'),
              _StatRow('Moons', '${physics['moon_count']}'),
              if (physics['has_rings'] == true)
                const _StatRow('Rings', 'Yes'),
            ],
          ),
          const SizedBox(height: 12),

          // Regions
          _SectionCard(
            title: 'REGIONS',
            icon: Icons.map,
            children: regions
                .map((r) => Padding(
                      padding: const EdgeInsets.symmetric(vertical: 4),
                      child: Row(
                        children: [
                          Container(
                            width: 12,
                            height: 12,
                            decoration: BoxDecoration(
                              color: _terrainColor(
                                  (r as Map<String, dynamic>)['terrain'] as String? ?? ''),
                              shape: BoxShape.circle,
                            ),
                          ),
                          const SizedBox(width: 8),
                          Text(r['name'] as String? ?? ''),
                          const Spacer(),
                          Text(
                            (r['terrain'] as String? ?? '').toUpperCase(),
                            style: TextStyle(
                              fontSize: 11,
                              color: Colors.grey[500],
                              letterSpacing: 1,
                            ),
                          ),
                        ],
                      ),
                    ))
                .toList(),
          ),
          const SizedBox(height: 12),

          // Calendar
          if (calendar != null)
            _SectionCard(
              title: 'CALENDAR',
              icon: Icons.calendar_month,
              children: [
                Wrap(
                  spacing: 8,
                  runSpacing: 4,
                  children: (calendar['seasons'] as List<dynamic>? ?? [])
                      .map((s) => Chip(
                            label: Text(s as String? ?? '',
                                style: const TextStyle(fontSize: 12)),
                            backgroundColor: const Color(0xFF1a3a1a),
                          ))
                      .toList(),
                ),
                const SizedBox(height: 8),
                Text(
                  (calendar['months'] as List<dynamic>? ?? []).join(' · '),
                  style: TextStyle(color: Colors.grey[400], fontSize: 13),
                ),
                if (calendar['festivals'] != null) ...[
                  const SizedBox(height: 8),
                  Text(
                    'Festivals: ${(calendar['festivals'] as List).join(', ')}',
                    style: TextStyle(color: Colors.amber[200], fontSize: 12),
                  ),
                ],
              ],
            ),
          const SizedBox(height: 12),

          // Culture
          if (culture != null)
            _SectionCard(
              title: 'CULTURE',
              icon: Icons.groups,
              children: [
                _StatRow('Structure', culture['social_structure'] as String? ?? ''),
                _StatRow('Values',
                    (culture['values'] as List<dynamic>?)?.join(', ') ?? ''),
                _StatRow('Taboos',
                    (culture['taboos'] as List<dynamic>?)?.join(', ') ?? ''),
                _StatRow('Burial', culture['burial'] as String? ?? ''),
              ],
            ),
          const SizedBox(height: 12),

          // Pantheon
          if (world['pantheon'] is Map)
            _PantheonCard(pantheon: world['pantheon'] as Map<String, dynamic>),
          const SizedBox(height: 12),

          // Bestiary
          if (creatures.isNotEmpty)
            _SectionCard(
              title: 'BESTIARY (${creatures.length} species)',
              icon: Icons.pets,
              children: [
                ...creatures.take(4).map((c) => _CreaturePreview(
                      creature: c as Map<String, dynamic>,
                      seed: widget.seed,
                    )),
                if (creatures.length > 4)
                  Padding(
                    padding: const EdgeInsets.only(top: 8),
                    child: TextButton(
                      onPressed: () => Navigator.push(
                        context,
                        MaterialPageRoute(
                          builder: (_) => BestiaryPage(
                            creatures: creatures.cast<Map<String, dynamic>>(),
                            worldName: name,
                            seed: widget.seed,
                          ),
                        ),
                      ),
                      child: Text('View all ${creatures.length} species →'),
                    ),
                  ),
              ],
            ),

          // Creation myth
          if (world['creation_myth'] != null) ...[
            const SizedBox(height: 16),
            Center(
              child: Text(
                '"${world['creation_myth']}"',
                style: TextStyle(
                  fontStyle: FontStyle.italic,
                  color: Colors.grey[500],
                  fontSize: 14,
                ),
                textAlign: TextAlign.center,
              ),
            ),
          ],
          const SizedBox(height: 32),
        ],
      ),
    );
  }

  Color _terrainColor(String terrain) {
    const colors = {
      'forest': Color(0xFF3a7d34),
      'desert': Color(0xFFe8c86a),
      'tundra': Color(0xFFd4d4d4),
      'marsh': Color(0xFF7a9a6b),
      'oceanic': Color(0xFF2a6bb0),
      'plains': Color(0xFFb8d4a0),
      'highlands': Color(0xFF8b7355),
      'volcanic': Color(0xFF8b4513),
      'archipelago': Color(0xFF4a9be0),
    };
    return colors[terrain] ?? Colors.grey;
  }
}

class _HeroCard extends StatelessWidget {
  final String name;
  final String terrain;
  final String seed;
  const _HeroCard(
      {required this.name, required this.terrain, required this.seed});

  @override
  Widget build(BuildContext context) {
    return Card(
      color: const Color(0xFF16213e),
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(16),
        side: BorderSide(color: Colors.white.withOpacity(0.1)),
      ),
      child: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          children: [
            Icon(Icons.public, size: 48,
                color: const Color(0xFF6ecf7e)),
            const SizedBox(height: 12),
            Text(name,
                style: const TextStyle(
                    fontSize: 26, fontWeight: FontWeight.bold)),
            const SizedBox(height: 8),
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 4),
              decoration: BoxDecoration(
                color: const Color(0xFF2a4a2a),
                borderRadius: BorderRadius.circular(20),
              ),
              child: Text(
                terrain.toUpperCase(),
                style: const TextStyle(
                    fontSize: 12, letterSpacing: 2, color: Color(0xFF6ecf7e)),
              ),
            ),
            const SizedBox(height: 4),
            Text('Seed: $seed',
                style: TextStyle(color: Colors.grey[600], fontSize: 12)),
          ],
        ),
      ),
    );
  }
}

class _SectionCard extends StatelessWidget {
  final String title;
  final IconData icon;
  final List<Widget> children;
  const _SectionCard(
      {required this.title, required this.icon, required this.children});

  @override
  Widget build(BuildContext context) {
    return Card(
      color: const Color(0xFF16213e),
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12),
        side: BorderSide(color: Colors.white.withOpacity(0.05)),
      ),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(icon, size: 18, color: const Color(0xFF6ecf7e)),
                const SizedBox(width: 8),
                Text(title,
                    style: const TextStyle(
                        fontSize: 13,
                        fontWeight: FontWeight.bold,
                        letterSpacing: 2)),
              ],
            ),
            const SizedBox(height: 12),
            ...children,
          ],
        ),
      ),
    );
  }
}

class _StatRow extends StatelessWidget {
  final String label;
  final String value;
  const _StatRow(this.label, this.value);

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 2),
      child: Row(
        children: [
          Text('$label: ',
              style: TextStyle(color: Colors.grey[500], fontSize: 13)),
          Text(value, style: const TextStyle(fontSize: 13)),
        ],
      ),
    );
  }
}

class _CreaturePreview extends StatelessWidget {
  final Map<String, dynamic> creature;
  final String seed;
  const _CreaturePreview({required this.creature, required this.seed});

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 6),
      child: Row(
        children: [
          Container(
            width: 40,
            height: 40,
            decoration: BoxDecoration(
              color: const Color(0xFF0a0a1a),
              borderRadius: BorderRadius.circular(8),
              border: Border.all(color: Colors.white.withOpacity(0.1)),
            ),
            child: const Icon(Icons.bug_report,
                size: 20, color: Color(0xFF81c784)),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(creature['name'] as String? ?? '',
                    style: const TextStyle(
                        fontWeight: FontWeight.w600, fontSize: 14)),
                Text(
                  '${creature['height_m']}m · ${creature['diet']} · ${creature['locomotion']}',
                  style: TextStyle(color: Colors.grey[500], fontSize: 12),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class _PantheonCard extends StatelessWidget {
  final Map<String, dynamic> pantheon;
  const _PantheonCard({required this.pantheon});

  @override
  Widget build(BuildContext context) {
    return Card(
      color: const Color(0xFF16213e),
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12),
        side: BorderSide(color: Colors.white.withOpacity(0.05)),
      ),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Row(
              children: [
                Icon(Icons.auto_awesome, size: 18, color: Color(0xFF6ecf7e)),
                SizedBox(width: 8),
                Text('PANTHEON',
                    style: TextStyle(
                        fontSize: 13,
                        fontWeight: FontWeight.bold,
                        letterSpacing: 2)),
              ],
            ),
            const SizedBox(height: 12),
            ...pantheon.entries.map((e) {
              final deity = e.value as Map<String, dynamic>;
              return Padding(
                padding: const EdgeInsets.symmetric(vertical: 4),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(e.key,
                        style: const TextStyle(
                            fontWeight: FontWeight.bold, fontSize: 15)),
                    Text(
                      '${deity['archetype']} of ${deity['domain']} · ${deity['epithet']}',
                      style: TextStyle(color: Colors.grey[400], fontSize: 12),
                    ),
                  ],
                ),
              );
            }).toList(),
          ],
        ),
      ),
    );
  }
}
