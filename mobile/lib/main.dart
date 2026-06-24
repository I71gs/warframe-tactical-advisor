import 'package:flutter/material.dart';

void main() {
  runApp(const WarframeCompanionApp());
}

class WarframeCompanionApp extends StatelessWidget {
  const WarframeCompanionApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Warframe Tactical Companion',
      theme: ThemeData.dark().copyWith(
        primaryColor: const Color(0xFF00A3CC),
        scaffoldBackgroundColor: const Color(0xFF0B1220),
        cardColor: const Color(0xFF0F1724),
        colorScheme: const ColorScheme.dark().copyWith(
          secondary: const Color(0xFFCAA3FF),
        ),
      ),
      home: const CompanionDashboard(),
    );
  }
}

class CompanionDashboard extends StatefulWidget {
  const CompanionDashboard({super.key});

  @override
  State<CompanionDashboard> createState() => _CompanionDashboardState();
}

class _CompanionDashboardState extends State<CompanionDashboard> {
  int _currentIndex = 0;

  final List<Widget> _pages = [
    const DashboardPage(),
    const DailyTasksPage(),
    const SessionPlannerPage(),
    const SettingsPage(),
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Warframe Tactical Advisor Companion'),
        backgroundColor: const Color(0xFF0F1724),
        actions: [
          IconButton(
            icon: const Icon(Icons.sync),
            onPressed: () {
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(content: Text('Syncing with local Advisor server (http://127.0.0.1:8000)...')),
              );
            },
          ),
        ],
      ),
      body: _pages[_currentIndex],
      bottomNavigationBar: BottomNavigationBar(
        currentIndex: _currentIndex,
        selectedItemColor: const Color(0xFF00A3CC),
        unselectedItemColor: Colors.grey,
        type: BottomNavigationBarType.fixed,
        backgroundColor: const Color(0xFF0F1724),
        onTap: (index) {
          setState(() {
            _currentIndex = index;
          });
        },
        items: const [
          BottomNavigationBarItem(icon: Icon(Icons.dashboard), label: 'Dashboard'),
          BottomNavigationBarItem(icon: Icon(Icons.check_box), label: 'Dailies'),
          BottomNavigationBarItem(icon: Icon(Icons.alarm), label: 'Sessions'),
          BottomNavigationBarItem(icon: Icon(Icons.settings), label: 'Settings'),
        ],
      ),
    );
  }
}

class DashboardPage extends StatelessWidget {
  const DashboardPage({super.key});

  @override
  Widget build(BuildContext context) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            'Progression Summary',
            style: TextStyle(fontSize: 22, fontWeight: FontWeight.bold, color: Color(0xFF00A3CC)),
          ),
          const SizedBox(height: 16),
          Card(
            color: const Color(0xFF0F1724),
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
            child: const Padding(
              padding: EdgeInsets.all(16.0),
              child: Column(
                children: [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text('Account Strength', style: TextStyle(fontSize: 16, color: Colors.grey)),
                      Text('71.5%', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: Color(0xFFCAA3FF))),
                    ],
                  ),
                  SizedBox(height: 8),
                  LinearProgressIndicator(
                    value: 0.715,
                    backgroundColor: Color(0xFF0B1220),
                    color: Color(0xFFCAA3FF),
                    minHeight: 8,
                  ),
                  SizedBox(height: 16),
                  Divider(),
                  SizedBox(height: 8),
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceAround,
                    children: [
                      Column(
                        children: [
                          Text('Mastery Rank', style: TextStyle(color: Colors.grey)),
                          SizedBox(height: 4),
                          Text('MR 15', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
                        ],
                      ),
                      Column(
                        children: [
                          Text('Progression Stage', style: TextStyle(color: Colors.grey)),
                          SizedBox(height: 4),
                          Text('MID-GAME', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: Colors.green)),
                        ],
                      ),
                    ],
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(height: 24),
          const Text(
            'Top Recommendation',
            style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: Color(0xFF00A3CC)),
          ),
          const SizedBox(height: 12),
          Card(
            color: const Color(0xFF0F1724),
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
            child: const ListTile(
              leading: Icon(Icons.star, color: Colors.amber, size: 36),
              title: Text('Complete The New War Quest'),
              subtitle: Text('Unlocks Sentient Bow, Narmer bounties, and Zariman access path.'),
            ),
          ),
        ],
      ),
    );
  }
}

class DailyTasksPage extends StatelessWidget {
  const DailyTasksPage({super.key});

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.all(16.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            'Daily Checklist',
            style: TextStyle(fontSize: 22, fontWeight: FontWeight.bold, color: Color(0xFF00A3CC)),
          ),
          const SizedBox(height: 12),
          Expanded(
            child: ListView(
              children: const [
                TaskCard(taskText: 'Progress Story: Complete The New War', isCompleted: false),
                TaskCard(taskText: 'Farm Arbitrations for Galvanized Chamber mod', isCompleted: false),
                TaskCard(taskText: 'Unlock Steel Path: Talk to Teshin at Relay', isCompleted: true),
                TaskCard(taskText: 'Complete a Daily Steel Path Incursion', isCompleted: false),
                TaskCard(taskText: 'Syndicate Standing Cap Run', isCompleted: true),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class TaskCard extends StatelessWidget {
  final String taskText;
  final bool isCompleted;

  const TaskCard({super.key, required this.taskText, required this.isCompleted});

  @override
  Widget build(BuildContext context) {
    return Card(
      color: const Color(0xFF0F1724),
      margin: const EdgeInsets.only(bottom: 8.0),
      child: ListTile(
        leading: Icon(
          isCompleted ? Icons.check_circle : Icons.radio_button_unchecked,
          color: isCompleted ? Colors.green : Colors.grey,
        ),
        title: Text(
          taskText,
          style: TextStyle(
            decoration: isCompleted ? TextDecoration.lineThrough : null,
            color: isCompleted ? Colors.grey : Colors.white,
          ),
        ),
      ),
    );
  }
}

class SessionPlannerPage extends StatefulWidget {
  const SessionPlannerPage({super.key});

  @override
  State<SessionPlannerPage> createState() => _SessionPlannerPageState();
}

class _SessionPlannerPageState extends State<SessionPlannerPage> {
  String _selectedDuration = '1 Hour';

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.all(16.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              const Text(
                'Session Itinerary',
                style: TextStyle(fontSize: 22, fontWeight: FontWeight.bold, color: Color(0xFF00A3CC)),
              ),
              DropdownButton<String>(
                value: _selectedDuration,
                dropdownColor: const Color(0xFF0F1724),
                underline: const SizedBox(),
                items: const [
                  DropdownMenuItem(value: '30 Minutes', child: Text('30 Mins')),
                  DropdownMenuItem(value: '1 Hour', child: Text('1 Hour')),
                  DropdownMenuItem(value: '2 Hours', child: Text('2 Hours')),
                ],
                onChanged: (val) {
                  if (val != null) {
                    setState(() {
                      _selectedDuration = val;
                    });
                  }
                },
              ),
            ],
          ),
          const SizedBox(height: 16),
          Expanded(
            child: ListView(
              children: _getItineraryForDuration(_selectedDuration),
            ),
          ),
        ],
      ),
    );
  }

  List<Widget> _getItineraryForDuration(String duration) {
    if (duration == '30 Minutes') {
      return const [
        TaskCard(taskText: 'Steel Path Incursion Quick Runs (15 mins) - Daily Incursion Nodes', isCompleted: false),
        TaskCard(taskText: 'Relic Run: Capture/Rescue Fissures (15 mins) - Void Fissures', isCompleted: false),
      ];
    } else if (duration == '1 Hour') {
      return const [
        TaskCard(taskText: 'Steel Path Incursions (3 runs) (25 mins) - Active SP Incursion Nodes', isCompleted: false),
        TaskCard(taskText: 'Duviri Circuit: Steel Path Evolution (25 mins) - The Undercroft', isCompleted: false),
        TaskCard(taskText: 'Void Fissures: Radshare Runs (10 mins) - Lith/Meso/Neo/Axi', isCompleted: false),
      ];
    } else {
      return const [
        TaskCard(taskText: 'Full Steel Path Incursion Set (5 runs) (40 mins) - Daily SP Incursion Nodes', isCompleted: false),
        TaskCard(taskText: 'Steel Path Circuit: Target Rank 5/10 (40 mins) - Duviri Undercroft', isCompleted: false),
        TaskCard(taskText: 'Duviri Experience: Pathos Clamps Run (25 mins) - Duviri Landscape', isCompleted: false),
        TaskCard(taskText: 'Void Fissures: Axi Radshares (15 mins) - Axi Fissure', isCompleted: false),
      ];
    }
  }
}

class SettingsPage extends StatelessWidget {
  const SettingsPage({super.key});

  @override
  Widget build(BuildContext context) {
    return ListView(
      padding: const EdgeInsets.all(16.0),
      children: [
        ListTile(
          leading: const Icon(Icons.cloud_sync),
          title: const Text('Server Sync Address'),
          subtitle: const Text('http://127.0.0.1:8000'),
          trailing: const Icon(Icons.edit),
          onTap: () {},
        ),
        ListTile(
          leading: const Icon(Icons.notifications),
          title: const Text('Enable Notifications'),
          subtitle: const Text('Push alerts on daily reset'),
          trailing: Switch(value: true, onChanged: (val) {}),
        ),
        ListTile(
          leading: const Icon(Icons.info),
          title: const Text('Companion Version'),
          subtitle: const Text('8.0.0'),
          onTap: () {},
        ),
      ],
    );
  }
}

