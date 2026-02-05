from datetime import datetime, timedelta
from db import subjects_col, schedules_col, users_col, db
import config
from typing import List, Dict, Tuple, Optional

# Mock config if not exists
if not hasattr(config, 'WEEKENDS'):
    config.WEEKENDS = [5, 6] # Sat, Sun

class ExamScheduler:
    def __init__(self):
        pass
        
    def generate_available_dates(self, start_date: str, end_date: str, 
                                holidays: List[str]) -> List[str]:
        start = datetime.strptime(start_date, '%d.%m.%Y')
        end = datetime.strptime(end_date, '%d.%m.%Y')
        holiday_dates = [datetime.strptime(h, '%d.%m.%Y') for h in holidays]
        
        available_dates = []
        current = start
        
        while current <= end:
            if current.weekday() not in config.WEEKENDS:
                if current not in holiday_dates:
                    available_dates.append(current.strftime('%d.%m.%Y'))
            current += timedelta(days=1)
        
        return available_dates

    def get_subjects(self, year: int, semester: int, exam_type: str) -> List[Dict]:
        """Fetch from MongoDB"""
        query = {'year': int(year)}
        if semester:
            query['semester'] = int(semester)
            
        # In real scheduling, we might want to schedule both sem subjects if it's a makeup?
        # For now, strict semester filtering as requested.
        
        subjects_cursor = subjects_col.find(query)
        subjects = list(subjects_cursor)
        
        # Filter by exam type logic (mocked logic from original SQL)
        # Original SQL: WHERE (exam_type = ? OR exam_type = 'BOTH')
        # Our mock data doesn't explicitly have 'exam_type' column for subject availability, 
        # but let's assume all subjects are eligible for Semester exams.
        
        return subjects

    def build_conflict_graph(self, subjects: List[Dict]) -> Dict[str, List[str]]:
        conflicts = {}
        for subject in subjects:
            s_id = str(subject['_id'])
            dept = subject['department']
            
            # Conflict with same department subjects
            conflicting_ids = [
                str(s['_id']) for s in subjects 
                if s['department'] == dept and str(s['_id']) != s_id
            ]
            conflicts[s_id] = conflicting_ids
        return conflicts

    def schedule_exams(self, year: int, semester: int, start_date: str, end_date: str, 
                      exam_type: str) -> Tuple[List[Dict], List[Dict]]:
        
        # 1. Get Dates
        available_dates = self.generate_available_dates(start_date, end_date, [])
        if not available_dates:
            raise ValueError("No available dates")

        # 2. Get Subjects
        subjects = self.get_subjects(year, semester, exam_type)
        if not subjects:
             raise ValueError(f"No subjects found for Year {year} Sem {semester}")

        # 3. Schedule Logic (Greedy)
        schedule = []
        violations = []
        
        # Track usage: key = "DEPT_DATE" -> True if occupied
        # For Semester exams (2 sessions per day)
        slots = []
        for date in available_dates:
            slots.append({'date': date, 'session': 'FN'})
            slots.append({'date': date, 'session': 'AN'})
            
        # Dept usage tracking: key = "DEPT_DATE_SESSION"
        dept_usage = {} 
        
        for subject in subjects:
            assigned = False
            dept = subject['department']
            
            for slot in slots:
                date = slot['date']
                session = slot['session']
                
                # Check 1: Is Dept free this slot?
                # Constraint: 1 exam per day per dept? Or just per session?
                # Original logic: "Block entire day for this department" in one part, 
                # but let's stick to session for flexibility or follow strict original.
                # Original: date_key = f"{dept}_{best_slot['date']}" -> Blocks entire day.
                
                daily_key = f"{dept}_{date}"
                if daily_key in dept_usage:
                    continue # Dept already has exam this day
                
                # Assign
                dept_usage[daily_key] = True
                
                schedule.append({
                    'subject_code': subject['code'],
                    'subject_name': subject['name'],
                    'department': dept,
                    'date': date,
                    'session': session,
                    'year': year,
                    'semester': semester,
                    'exam_type': exam_type
                })
                assigned = True
                break
            
            if not assigned:
                violations.append({
                    'subject': subject['name'],
                    'error': 'No slot available'
                })
        
        return schedule, violations

    def save_schedule(self, schedule_data):
        # Clear existing schedule for this specific batch if needed, or just append
        schedules_col.insert_many(schedule_data)
        
