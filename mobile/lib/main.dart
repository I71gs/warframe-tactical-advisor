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
    const DailyTasksPage(),
    const ProgressionChartsPage(),
    const SearchPage(),
    const SettingsPage(),
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Warframe Advisor Companion'),
        backgroundColor: const Color(0xFF0F1724),
        actions: [
          IconButton(
            icon: const Icon(Icons.sync),
            onPressed: () {
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(content: Text('Syncing with local Advisor server...')),
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
          BottomNavigationBarItem(icon: Icon(Icons.check_box), label: 'Daily Tasks'),
          BottomNavigationBarItem(icon: Icon(Icons.bar_chart), label: 'Charts'),
          BottomNavigationBarItem(icon: Icon(Icons.search), label: 'Search'),
          BottomNavigationBarItem(icon: Icon(Icons.settings), label: 'Settings'),
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
            style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold, color: Color(0xFF00A3CC)),
          ),
          const SizedBox(height: 12),
          Expanded(
            child: ListView(
              children: const [
                TaskCard(taskText: 'Progress Story: Complete The New War', isCompleted: false),
                TaskCard(taskText: 'Farm Arbitrations for Galvanized Chamber mod', isCompleted: false),
                TaskCard(taskText: 'Unlock Steel Path: Talk to Teshin at Relay', isCompleted: true),
                TaskCard(taskText: 'Complete a Daily Steel Path Incursion', isCompleted: false),
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
          ),
        ),
      ),
    );
  }
}

class ProgressionChartsPage extends StatelessWidget {
  const ProgressionChartsPage({super.key});

  @override
  Widget build(BuildContext context) {
    return const Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(Icons.insights, size: 80, color: Color(0xFFCAA3FF)),
          SizedBox(height: 16),
          Text(
            'Account Readiness: 71%',
            style: TextStyle(fontSize: 22, fontWeight: FontWeight.bold),
          ),
          SizedBox(height: 8),
          Text(
            'Zariman Readiness: 82%\nSteel Path Readiness: 65%',
            textAlign: TextAlign.center,
            style: TextStyle(color: Colors.grey),
          ),
        ],
      ),
    );
  }
}

class SearchPage extends StatelessWidget {
  const SearchPage({super.key});

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.all(16.0),
      child: Column(
        children: [
          TextField(
            decoration: InputDecoration(
              hintText: 'Search items, relics, or builds...',
              prefixIcon: const Icon(Icons.search),
              border: OutlineInputBorder(borderRadius: BorderRadius.circular(8.0)),
              filled: true,
              fillColor: const Color(0xFF0F1724),
            ),
          ),
          const SizedBox(height: 16),
          const Expanded(
            child: Center(
              child: Text(
                'Type a query to search local Warframe databases.',
                style: TextStyle(color: Colors.grey),
              ),
            ),
          )
        ],
      ),
    );
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
          title: const Text('Version'),
          subtitle: const Text('6.0.0'),
          onTap: () {},
        ),
      ],
    );
  }
}
