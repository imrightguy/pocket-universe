import 'package:flutter_test/flutter_test.dart';

import 'package:pocket_app/main.dart';

void main() {
  testWidgets('PocketUniverseApp renders without error', (WidgetTester tester) async {
    await tester.pumpWidget(const PocketUniverseApp());

    // Verify the main screen renders with the app title
    expect(find.text('POCKET UNIVERSE'), findsOneWidget);
    expect(find.text('Select a seed to generate a universe'), findsOneWidget);
  });
}
