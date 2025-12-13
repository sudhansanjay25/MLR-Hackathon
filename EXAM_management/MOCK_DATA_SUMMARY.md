# Mock Data Summary

## 📊 Database Populated with Comprehensive Test Data

The database has been seeded with **235 students** across **4 departments** and **4 years**, along with realistic Indian names, proper hall configurations, and complete subject data.

---

## 👥 Students Distribution

### **Total: 235 Students**

#### **Year 1 (55 students)**
- **CSE**: 30 students (Register: 724025104001 - 724025104030)
- **ECE**: 25 students (Register: 724025105001 - 724025105025)

#### **Year 2 (55 students)**
- **CSE**: 30 students (Register: 723025104001 - 723025104030)
- **ECE**: 25 students (Register: 723025105001 - 723025105025)

#### **Year 3 (50 students)**
- **CSE**: 30 students (Register: 722025104001 - 722025104030)
- **MECH**: 20 students (Register: 722025106001 - 722025106020)

#### **Year 4 (75 students)**
- **CSE**: 30 students (Register: 714025104001 - 714025104030)
- **ECE**: 25 students (Register: 714025105001 - 714025105025)
- **CIVIL**: 20 students (Register: 714025107001 - 714025107020)

---

## 🏛️ Halls (6 Halls with Column Data)

| Hall | Building | Capacity | Exam Capacity | Columns | Floor | Facilities |
|------|----------|----------|---------------|---------|-------|------------|
| A-101 | Block A | 60 | 30 | **6** | 1 | Projector, AC, CCTV |
| A-102 | Block A | 60 | 30 | **6** | 1 | Projector, AC, CCTV |
| B-201 | Block B | 80 | 40 | **8** | 2 | Projector, AC, CCTV |
| B-202 | Block B | 80 | 40 | **8** | 2 | Projector, AC, CCTV |
| C-301 | Block C | 100 | 50 | **10** | 3 | Projector, AC, CCTV, Smart Board |
| C-302 | Block C | 100 | 50 | **10** | 3 | Projector, AC, CCTV, Smart Board |

**Total Exam Capacity: 240 seats** (Can accommodate all 235 students)

---

## 📚 Departments (4 Departments)

| Code | Name | HOD | Total Students |
|------|------|-----|----------------|
| CSE | Computer Science and Engineering | Dr. Rajesh Kumar | 120 |
| ECE | Electronics and Communication Engineering | Dr. Priya Sharma | 90 |
| MECH | Mechanical Engineering | Dr. Anil Verma | 60 |
| CIVIL | Civil Engineering | Dr. Suresh Babu | 50 |

---

## 📖 Subjects (10 Core Subjects)

### Year 1 (Common - Semester 1)
- **MA101** - Engineering Mathematics-I (4 credits)
- **PH101** - Engineering Physics (4 credits)
- **CS101** - Programming for Problem Solving (3 credits)

### Year 2 (CSE - Semester 3)
- **CS201** - Data Structures (4 credits)
- **CS202** - Database Management Systems (4 credits)

### Year 3 (CSE - Semester 5)
- **CS301** - Operating Systems (4 credits)
- **CS302** - Computer Networks (4 credits)

### Year 4 (CSE - Semester 7 & 8)
- **CS401** - Machine Learning (4 credits)
- **CS402** - Cloud Computing (3 credits)
- **CS403** - Big Data Analytics (3 credits)

---

## 👨‍💼 Users (6 Users)

### **COE (1)**
- Email: `coe@mlrit.ac.in`
- Password: `coe123`
- Role: Controller of Examinations

### **Faculty (2)**
1. **Dr. Rajesh Kumar** (CSE)
   - Email: `faculty001@mlrit.ac.in`
   - Password: `faculty123`
   - Employee ID: FAC001

2. **Dr. Priya Sharma** (ECE)
   - Email: `faculty002@mlrit.ac.in`
   - Password: `faculty123`
   - Employee ID: FAC002

### **Students (Login Examples)**
All students have password: `student123`

**Sample Student Logins:**
- Year 4 CSE: `714025104001@mlrit.ac.in` (Rahul Reddy)
- Year 1 CSE: `724025104001@mlrit.ac.in`
- Year 2 ECE: `723025105001@mlrit.ac.in`
- Year 3 MECH: `722025106001@mlrit.ac.in`
- Year 4 CIVIL: `714025107001@mlrit.ac.in`

---

## 🎭 Realistic Indian Names

The seed script uses authentic Indian names for better realism:

**Male Names Sample:**
- Rahul Reddy, Karthik Kumar, Aditya Sharma, Sai Krishna, Vijay Varma
- Rohan Patel, Arjun Singh, Akash Gupta, Nikhil Rao, Pranav Mehta
- Harish Nair, Suresh Babu, Manoj Kumar, etc.

**Female Names Sample:**
- Sneha Patel, Priya Sharma, Divya Reddy, Anjali Singh, Kavya Kumar
- Pooja Nair, Swathi Rao, Meera Gupta, Nidhi Verma, Shruti Patel
- Ananya Reddy, Lavanya Kumar, Sravani Nair, etc.

---

## 📋 Additional Data Features

### Student Details Include:
- ✅ Register Number (unique)
- ✅ Full Name (realistic Indian names)
- ✅ Email (based on register number)
- ✅ Department (CSE, ECE, MECH, CIVIL)
- ✅ Year & Semester
- ✅ Batch (e.g., 2024-2028)
- ✅ Date of Birth (randomized)
- ✅ Gender (balanced distribution)
- ✅ Phone Number (unique per student)
- ✅ Regulation (R18 for Year 4, R22 for Years 1-3)
- ✅ Active Status

### Hall Features Include:
- ✅ **Columns field populated** (6, 8, or 10 columns)
- ✅ Total capacity
- ✅ Exam capacity (50% of total)
- ✅ Building & Floor information
- ✅ Facilities list

---

## 🔄 How to Test

### 1. **Create an Exam Schedule for Year 1**
- Login as COE
- Schedule exam for Year 1, Semester 1
- Select date range
- System will allocate 55 students to halls

### 2. **Create an Exam Schedule for Year 4**
- Schedule for Year 4, Semester 7
- System will handle 75 students across departments

### 3. **View Seating Arrangements**
- After scheduling, view seating PDFs
- Halls will be arranged based on column configuration
- Students distributed across all 6 halls

### 4. **Generate Hall Tickets**
- Authorize hall tickets for a schedule
- System generates for all students in that year
- Students can download their individual hall tickets

---

## 📊 Quick Stats

```
Total Users:         6
Total Students:      235
Total Departments:   4
Total Halls:         6
Total Subjects:      10
Total Capacity:      240 seats

Student Distribution:
- Year 1: 55 (CSE: 30, ECE: 25)
- Year 2: 55 (CSE: 30, ECE: 25)
- Year 3: 50 (CSE: 30, MECH: 20)
- Year 4: 75 (CSE: 30, ECE: 25, CIVIL: 20)

Gender Distribution:
- Male: ~118 students
- Female: ~117 students
```

---

## ✅ Verification Checklist

After seeding, verify:
- [x] 235 students created in database
- [x] All halls have `columns` field populated
- [x] Students distributed across 4 departments
- [x] Realistic Indian names assigned
- [x] Proper register number format
- [x] All email addresses unique
- [x] Phone numbers unique
- [x] Department references correct
- [x] Year and semester values valid
- [x] Can login with any student credential

---

## 🚀 Next Steps

1. **Test Scheduling:**
   - Create schedule for Year 1
   - Verify 55 students allocated
   - Check seating arrangement across halls

2. **Test Hall Tickets:**
   - Generate hall tickets for a year
   - Verify PDFs created
   - Test student download

3. **Test Multiple Departments:**
   - Schedule for Year 4 (3 departments)
   - Verify cross-department handling
   - Check hall allocation logic

4. **Stress Test:**
   - Schedule all 4 years simultaneously
   - Test capacity limits
   - Verify PDF generation performance

---

**Status: Database fully populated with production-ready mock data! ✅**
