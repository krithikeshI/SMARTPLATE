# SMARTPLATE
Abstract
SMART PLATE – Intelligent Nutrition Planning is a Python-based desktop application that helps users track meals, manage nutrition, and achieve health goals. The system calculates calorie intake, BMI, and provides meal suggestions based on personal health metrics. It stores user data in SQLite, offers visual charts using Matplotlib/Plotly, and generates analytics on diet adherence. This project demonstrates a practical integration of Python GUI (Tkinter/PyQt), databases, and data visualization for promoting healthy living.
Keywords
●	Nutrition Tracking

●	Meal Planning

●	Python Desktop Application

●	Health Analytics
1. Introduction / Background
Maintaining a healthy diet is challenging in modern life. Many people struggle to track calorie intake, monitor BMI, or receive personalized nutrition advice. Smart Plate Nutrition solves this problem by converting food and meal data into structured digital records. The system helps users monitor daily nutrition, plan meals, and view analytics of their progress through an intuitive desktop interface.
2. Problem Statement
Manual tracking of meals and calories is prone to errors and poor adherence to health goals. An automated system is needed to calculate nutrition metrics, suggest meals, and store data for historical analysis.
3. Objectives
1.	Track daily meals and calorie intake automatically.
2.	Calculate BMI and nutritional metrics based on user input.
3.	Provide meal suggestions based on health goals.
4.	Maintain user profiles and store historical nutrition data.
4. Scope & Limitations
1.	Desktop implementation using Python GUI (Tkinter / PyQt).
2.	SQLite database for data storage.
3.	Analytics limited to recorded meals and calories.
4.	Meal suggestions based on predefined nutritional rules.

   5. Technology Stack
Component	Technology / Tool
Language	Python 3.x (Tkinter / PyQt GUI)
Database	SQLite via sqlite3 module
Charts & Analytics	Matplotlib / Plotly
IDE / Tools	PyCharm / VS Code
Libraries	Tkinter/PyQt, Matplotlib, sqlite3, PIL (for images)
6. System Architecture
Smart Plate Nutrition uses a layered architecture:
Smart Plate Nutrition uses a layered architecture:
Presentation Layer: Python GUI (Tkinter/PyQt) for inputting meals, viewing BMI, and analytics.
Service Layer: Handles calorie calculation, BMI calculation, and meal suggestions.
Persistence Layer: Stores user data, meals, and analytics in SQLite database.
Data Layer: Contains structured tables for Users, Meals, Nutrition Data, and Reports.
7. Data Model / Key Tables / Inputs & Outputs
Table Name	Key Fields	Purpose
UserProfile	user_id, name, DOB, height, weight	Stores user personal details and BMI
Meals	meal_id, user_id, date, meal_type, calories	Tracks meal entries
NutritionData	nutrition_id, user_id, calories, proteins, fats, carbs	Holds calculated nutrition metrics
Reports	report_id, user_id, date, chart_data	Stores generated analytics charts
Step 1: Application Launch
Launches from app.py.
Initializes global state in app_state.py.
Displays Login or Sign-Up window using Tkinter/PyQt GUI.

