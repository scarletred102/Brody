# Brody 🤖

**Your Proactive Multi-Agent AI Hub**

Brody is a next-generation AI workspace that unifies email, files, and tasks into one intelligent control center. Unlike reactive assistants, Brody anticipates your needs, automates actions, and enables AI-to-AI collaboration—saving you 5–7 hours weekly.

> **Current Status**: MVP in development - basic architecture and "Prepare My Day" feature implemented

---

## 🌟 Key Features

### 🚀 Proactive Intelligence
- **Anticipates Needs**: Brody doesn't wait for commands—it predicts what you need before you ask
- **Automated Actions**: Smart workflows that handle routine tasks automatically
- **AI-to-AI Collaboration**: Multiple AI agents work together seamlessly to solve complex problems

### 📧 Unified Workspace
- **Email Integration**: Smart email management with automated sorting, responses, and follow-ups
- **File Management**: Intelligent file organization and retrieval across all your platforms
- **Task Coordination**: Centralized task management with priority detection and deadline tracking

### 🎮 Gamified Productivity
- **Achievement System**: Earn rewards for completing tasks and maintaining productivity streaks
- **Progress Tracking**: Visual dashboards showing your productivity metrics
- **Team Leaderboards**: Friendly competition to boost team engagement

### 🔗 Seamless Integration
- **App Connectivity**: Works with your favorite tools and platforms
- **Cross-Platform Sync**: Access Brody from anywhere, on any device
- **API Support**: Extensible architecture for custom integrations

---

## 💡 Why Brody?

### For Individuals
- **Save Time**: Reclaim 5–7 hours every week by automating repetitive tasks
- **Stay Organized**: Never miss important emails, deadlines, or files again
- **Reduce Stress**: Let Brody handle the cognitive load of managing your digital life

### For Teams
- **Enhanced Collaboration**: AI agents facilitate better communication and coordination
- **Increased Efficiency**: Automated workflows mean less time on admin, more on creative work
- **Data-Driven Insights**: Understand team productivity patterns and optimize processes

---

## 🏗️ Architecture

Brody is built on a multi-agent architecture where specialized AI agents collaborate:

```
┌─────────────────────────────────────────┐
│         Brody Control Center            │
├─────────────────────────────────────────┤
│  ┌─────────┐  ┌─────────┐  ┌─────────┐ │
│  │  Email  │  │  File   │  │  Task   │ │
│  │  Agent  │  │  Agent  │  │  Agent  │ │
│  └─────────┘  └─────────┘  └─────────┘ │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐ │
│  │Analytics│  │Scheduler│  │  Auto   │ │
│  │  Agent  │  │  Agent  │  │  Agent  │ │
│  └─────────┘  └─────────┘  └─────────┘ │
├─────────────────────────────────────────┤
│      Integration Layer (APIs)           │
├─────────────────────────────────────────┤
│   Email • Files • Calendar • Apps       │
└─────────────────────────────────────────┘
```

---

## 🚀 Getting Started

### Prerequisites
- Python 3.9+ (for backend)
- Node.js 18+ (for frontend)
- API keys for integrations (Gmail, Outlook, etc.) - optional for MVP

### Quick Start

**Option 1: Run Backend Only**
```bash
cd backend
pip install -r requirements.txt
python main.py
```
Visit `http://localhost:8000` to see the API

**Option 2: Run Full Stack**
```bash
# Terminal 1 - Backend
cd backend
pip install -r requirements.txt
python main.py

# Terminal 2 - Frontend
cd frontend
npm install
npm start
```
Visit `http://localhost:3000` to see the web app

### Detailed Setup

See [DEVELOPMENT.md](docs/DEVELOPMENT.md) for complete setup instructions and development workflow.

### MVP Feature: "Prepare My Day"

The core MVP feature is accessible at:
- **API**: `GET http://localhost:8000/api/prepare-day`
- **Web UI**: Click "Prepare My Day" button on the homepage

---

## 📖 Project Structure

```
Brody/
├── backend/              # FastAPI backend server
│   ├── main.py          # API endpoints and core logic
│   └── requirements.txt # Python dependencies
├── frontend/            # React web application
│   ├── public/          # Static assets
│   ├── src/             # React components
│   └── package.json     # Node dependencies
├── agents/              # Multi-agent architecture
│   └── coordinator.py   # Agent orchestration logic
├── Plans/               # Project proposals and documentation
├── docs/                # Development guides
│   └── DEVELOPMENT.md   # Developer setup guide
└── README.md            # This file
```

## 📖 API Examples

### Health Check
```bash
curl http://localhost:8000/health
```

### Prepare Your Day (Core MVP Feature)
```bash
curl http://localhost:8000/api/prepare-day
```

### Classify Email
```bash
curl -X POST http://localhost:8000/api/classify-email \
  -H "Content-Type: application/json" \
  -d '{
    "id": "email1",
    "subject": "Urgent: Meeting tomorrow",
    "body": "We need to discuss the project",
    "sender": "boss@company.com",
    "timestamp": "2025-10-11T10:00:00Z"
  }'
```

---

## 🎯 Current MVP Status

### ✅ Completed
- [x] Basic FastAPI backend with core endpoints
- [x] Multi-agent architecture foundation
- [x] React frontend with "Prepare My Day" UI
- [x] Email classification logic
- [x] Task suggestion system
- [x] Meeting brief generation structure

### 🚧 In Progress
- [ ] Gmail API integration
- [ ] Calendar synchronization
- [ ] LLM integration (Gemini/OpenAI)
- [ ] Proactive scanning loop
- [ ] User authentication

### 📅 Planned
- [ ] Microsoft To Do integration
- [ ] Advanced AI-to-AI agent collaboration
- [ ] Gamification features
- [ ] Mobile app
- [ ] Enterprise features

---

## 📖 Usage Examples

### Email Management
```javascript
// Brody automatically categorizes emails
brody.email.autoSort({
  priority: 'urgent',
  category: 'work',
  action: 'highlight'
});
```

### Task Automation
```javascript
// Create smart task workflows
brody.tasks.createWorkflow({
  trigger: 'email_from_boss',
  actions: ['create_task', 'set_priority_high', 'add_to_today']
});
```

### File Organization
```javascript
// Intelligent file management
brody.files.organize({
  pattern: 'project_reports',
  destination: '/work/reports',
  autoRename: true
});
```

---

## 🎯 Use Cases

- **Busy Professionals**: Manage overwhelming email and task loads effortlessly
- **Remote Teams**: Coordinate across time zones with AI-powered scheduling
- **Entrepreneurs**: Focus on growth while Brody handles administrative tasks
- **Students**: Stay on top of assignments, emails, and project deadlines
- **Project Managers**: Track multiple projects with automated status updates

---

## 🤝 Contributing

We welcome contributions! Brody is built by the community, for the community.

### How to Contribute

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines

- Follow the existing code style
- Write tests for new features
- Update documentation as needed
- Keep commits focused and descriptive

---

## 📝 Roadmap

- [x] Core multi-agent architecture
- [x] Email integration
- [x] Task management
- [ ] Advanced AI-to-AI collaboration protocols
- [ ] Mobile app (iOS & Android)
- [ ] Voice interface
- [ ] Advanced analytics dashboard
- [ ] Custom agent marketplace
- [ ] Enterprise features

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- Built with ❤️ by the Brody community
- Powered by advanced AI and machine learning technologies
- Inspired by the vision of making productivity effortless

---

## 📞 Contact & Support

- **Issues**: [GitHub Issues](https://github.com/scarletred102/Brody/issues)
- **Discussions**: [GitHub Discussions](https://github.com/scarletred102/Brody/discussions)
- **Email**: support@brody.ai (coming soon)

---

<div align="center">

**⭐ Star us on GitHub — it motivates us a lot!**

[Website](https://brody.ai) • [Documentation](https://docs.brody.ai) • [Blog](https://blog.brody.ai)

*Brody: Your AI-powered control center for digital life and team efficiency*

</div>
