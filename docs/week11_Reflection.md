# Section 0: Fellow Details

Name: Mashruf Hossain

GitHub Username: mashrufhossain

Preferred Feature Track: Interactive & Smart

Team Interest: Yes


# Section 1: Week 11 Reflection

Key Takeaways:

- Understood the importance of clear scoping and realistic milestones for the capstone.
- Learned how to design modular, scalable code for a larger project.
- Realized the value of early user feedback and iterative development.
- Identified the importance of clear data flow and documentation.
- Gained insight into the final deliverables expected for the showcase.


Concept Connections:

- Strongest: API integration, Tkinter GUI basics, data parsing.
- Needs more practice: advanced error handling, testing strategies, database design.


Early Challenges:

- Managing API and SSH keys professionally and securely.
- Structuring the project folders cleanly from the start.
- Balancing feature ideas with available time.

Support Strategies:

- Attend office hours weekly to get early feedback.
- Use Slack channels to unblock API or DB issues quickly.
- Reference example capstone projects from previous fellows.


# Section 2: Feature Selection Rationale


Feature Name: Simple Statistics / Weather History Tracker

Difficulty (1–3): 2

Why You Chose It / Learning Goal: I want to get better at handling data and I believe this is the core of any weather app.


Feature Name: Trend Detection

Difficulty (1–3): 2

Why You Chose It / Learning Goal: I want to see how this can fit in the weather app to produce meaningful data.


Feature Name: Activity Suggester

Difficulty (1–3): 3

Why You Chose It / Learning Goal: This seems like an awesome way to add a personal touch to the app!


Personal Enhancement: Custom descriptions, possibly sound effects or weather mascot. 


# Section 3: High-Level Architecture Sketch

Modules and Folders:

/main.py: Main application entry point.

/api.py: Handles API requests (e.g., OpenWeatherMap).

/features/: Contains individual feature modules (forecast, journal, etc.).

/data/: Stores local data files or databases.

/docs/: Project documentation.

Data Flow Outline:

User Input → API Module → Data Parsing → Feature Modules → UI Display → Data Persistence


# Section 4: Data Model Plan

Example Row

columns with attribute starting with datetime.

2025-06-09,New Brunswick,78,Sunny, wind speed/direction, humidity.


# Section 5: Personal Project Timeline (Weeks 12–17)

Week	Monday	Tuesday	Wednesday	Thursday	Key Milestone
12	API setup	Error handling	Tkinter shell	Buffer day	Basic working app
13	Feature 1			Integrate	Feature 1 complete
14	Feature 2 start		Review & test	Finish	Feature 2 complete
15	Feature 3	Polish UI	Error passing	Refactor	All features complete
16	Enhancement	Docs	Tests	Packaging	Ready-to-ship app
17	Rehearse	Buffer	Showcase	–	Demo Day


# Section 6: Risk Assessment

1. Risk: Losing data      Impact: High     Mitigation Plan: Have backup data and practice good coding practices.
2. Risk: Breaking files   Impact: Medium   Mitigation Plan: Pay extra attention to what broke the code.
3. Risk: Time Management  Impact: Medium   Mitigation Plan: Work on project a little everyday.

# Section 7: Support Requests

1. Ask for review on error handling patterns.
2. Clarify best practices for structuring large Tkinter apps.
3. Feedback on data model design for journal integration.
