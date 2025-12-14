"""
Sources: https://www.youtube.com/watch?v=LEC2FJINg24
https://www.youtube.com/watch?v=KdMAj8Et4xk
"""

import csv
import os
from typing import List


class Assignment:
    """
    Represents a single assignment.

    Attributes:
        assignment_id: Unique ID for the assignment (CSV purposes)
        course_id: ID of the course this belongs to (CSV purposes)
        name: Name of the assignment
        score: Points earned
        max_points: Maximum possible points
    """

    def __init__(self, assignment_id, course_id, name, score, max_points):
        """Initialize an Assignment."""
        self.assignment_id = assignment_id
        self.course_id = course_id
        self.name = name
        self.score = score
        self.max_points = max_points

    def get_percentage(self):
        """
        Calculate the percentage score for this assignment.

        Returns the percentage score (0-100). Returns 0.0 if max_points is 0.
        """
        if self.max_points == 0:
            return 0.0
        return (self.score / self.max_points) * 100


class Course:
    """
    Represents a single course.

    Attributes:
        course_id: Unique ID for the course
        name: Name of the course
        assignments: List of assignments in this course
    """

    def __init__(self, course_id, name):
        """Initialize a Course."""
        self.course_id = course_id
        self.name = name
        self.assignments = []

    def add_assignment(self, assignment):
        """Add an assignment to this course."""
        self.assignments.append(assignment)

    def remove_assignment(self, assignment):
        """Remove an assignment from this course."""
        if assignment in self.assignments:
            self.assignments.remove(assignment)

    def calculate_grade(self):
        """
        Calculate the overall grade percentage for the course.

        Returns the grade percentage (0-100). Returns 0.0 if there are no assignments
        or total points possible is 0.
        """
        if not self.assignments:
            return 0.0

        total_earned = sum(a.score for a in self.assignments)
        total_possible = sum(a.max_points for a in self.assignments)

        if total_possible == 0:
            return 0.0

        return (total_earned / total_possible) * 100

    def get_letter_grade(self):
        """
        Converts course percentage to letter grade.

        Returns letter grade ("A", "B", "C", "D", "F")
        """
        percentage = self.calculate_grade()

        if percentage >= 90:
            return 'A'
        elif percentage >= 80:
            return 'B'
        elif percentage >= 70:
            return 'C'
        elif percentage >= 60:
            return 'D'
        else:
            return 'F'

    def calculate_gpa(self):
        """
        Calculate GPA points based on letter grade.

        Returns GPA value (0.0-4.0)
        """
        letter_grade = self.get_letter_grade()

        grade_scale = {
            'A': 4.0,
            'B': 3.0,
            'C': 2.0,
            'D': 1.0,
            'F': 0.0
        }

        return grade_scale.get(letter_grade, 0.0)


class DataManager:
    """Handles reading and writing CSV files.

    This class manages persistent storage of courses and assignments
    using CSV files.

    Attributes:
        courses_file (str): Path to the courses CSV file
        assignments_file (str): Path to the assignments CSV file
    """

    def __init__(self):
        """Initialize the DataManager.

        Creates CSV files if they don't exist and sets up file paths.
        """
        self.courses_file = 'courses.csv'
        self.assignments_file = 'assignments.csv'
        self.create_files_if_needed()

    def create_files_if_needed(self):
        """Create CSV files with headers if they don't exist.

        Creates courses.csv and assignments.csv with appropriate headers
        if the files are not present in the current directory.
        """
        if not os.path.exists(self.courses_file):
            with open(self.courses_file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['course_id', 'name'])

        if not os.path.exists(self.assignments_file):
            with open(self.assignments_file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['assignment_id', 'course_id', 'name', 'score', 'max_points'])

    def load_courses(self):
        """Load all courses from CSV file.

        Reads the courses.csv file and creates Course objects
        from each row.

        Returns:
            list: List of Course objects loaded from file.
                  Returns empty list if file doesn't exist.
        """
        courses = []
        try:
            with open(self.courses_file, 'r', newline='') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    course = Course(int(row['course_id']), row['name'])
                    courses.append(course)
        except FileNotFoundError:
            pass
        return courses

    def load_assignments(self):
        """Load all assignments from CSV file.

        Reads the assignments.csv file and creates Assignment objects
        from each row.

        Returns:
            list: List of Assignment objects loaded from file.
                  Returns empty list if file doesn't exist.
        """
        assignments = []
        try:
            with open(self.assignments_file, 'r', newline='') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    assignment = Assignment(
                        int(row['assignment_id']),
                        int(row['course_id']),
                        row['name'],
                        float(row['score']),
                        float(row['max_points'])
                    )
                    assignments.append(assignment)
        except FileNotFoundError:
            pass
        return assignments

    def save_all_courses(self, courses):
        """Save all courses to CSV file.

        Writes all course data to courses.csv, overwriting the existing file.

        Args:
            courses (list): List of Course objects to save.
        """
        with open(self.courses_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['course_id', 'name'])
            for course in courses:
                writer.writerow([course.course_id, course.name])

    def save_all_assignments(self, courses):
        """Save all assignments from all courses to CSV file.

        Writes all assignment data to assignments.csv, overwriting
        the existing file. Iterates through all courses and their
        assignments.

        Args:
            courses (list): List of Course objects whose assignments
                           will be saved.
        """
        with open(self.assignments_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['assignment_id', 'course_id', 'name', 'score', 'max_points'])
            for course in courses:
                for assignment in course.assignments:
                    writer.writerow([
                        assignment.assignment_id,
                        assignment.course_id,
                        assignment.name,
                        assignment.score,
                        assignment.max_points
                    ])


class GradeCalculator:
    """
    Manages courses and assignments and overall GPA calculations.
    """

    def __init__(self):
        """Initialize the GradeCalculator and load data from CSV.

        Creates a DataManager instance and loads all existing
        courses and assignments from CSV files.
        """
        self.courses = []
        self.data_manager = DataManager()
        self.load_all_data()

    def load_all_data(self):
        """Load courses and assignments from CSV files.

        Loads courses from courses.csv and assignments from
        assignments.csv, then links assignments to their
        corresponding courses.
        """
        # Load courses
        self.courses = self.data_manager.load_courses()

        # Load assignments and link them to courses
        assignments = self.data_manager.load_assignments()
        for assignment in assignments:
            for course in self.courses:
                if course.course_id == assignment.course_id:
                    course.add_assignment(assignment)
                    break

    def save_all_data(self):
        """Save all courses and assignments to CSV files.

        Calls DataManager methods to write all current courses
        and assignments to their respective CSV files.
        """
        self.data_manager.save_all_courses(self.courses)
        self.data_manager.save_all_assignments(self.courses)

    def get_all_courses(self):
        """Get list of all courses."""
        return self.courses

    def add_course(self, name):
        """
        Create and add a new course.

        Args:
            name: Course name

        Returns the created course

        Raises ValueError if course name is empty
        """
        if not name.strip():
            raise ValueError("Course name cannot be empty")

        # Generate new ID
        new_id = max([c.course_id for c in self.courses], default=0) + 1

        course = Course(new_id, name.strip())
        self.courses.append(course)
        self.save_all_data()
        return course

    def delete_course(self, course):
        """Delete a course if it exists in list."""
        if course in self.courses:
            self.courses.remove(course)
            self.save_all_data()

    def add_assignment(self, course, name, score, max_points):
        """
        Adds a new assignment to a course.

        Args:
            course: Course to add
            name: Name of the assignment
            score: Points earned
            max_points: Maximum possible points

        Returns the created assignment

        Raises ValueError if validation fails.
        """
        if not name.strip():
            raise ValueError("Assignment name cannot be empty")
        if max_points <= 0:
            raise ValueError("Max points must be greater than 0")
        if score < 0:
            raise ValueError("Score cannot be negative")
        if score > max_points:
            raise ValueError("Score cannot exceed max points")

        # Generate new ID
        all_assignments = [a for c in self.courses for a in c.assignments]
        new_id = max([a.assignment_id for a in all_assignments], default=0) + 1

        assignment = Assignment(new_id, course.course_id, name.strip(), score, max_points)
        course.add_assignment(assignment)
        self.save_all_data()
        return assignment

    def delete_assignment(self, course, assignment):
        """Delete an assignment from a course."""
        course.remove_assignment(assignment)
        self.save_all_data()

    def calculate_overall_gpa(self):
        """
        Calculate total GPA across all courses.

        Returns overall GPA (0.0-4.0). Returns 0.0 if there are no courses.
        """
        if not self.courses:
            return 0.0

        total_gpa = sum(course.calculate_gpa() for course in self.courses)
        return total_gpa / len(self.courses)