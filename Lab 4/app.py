import os

from flask import Flask, request, redirect
from flask import render_template
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Resource, Api

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.sqlite3"

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
# db.init_app(app)
app.app_context().push()

class Student(db.Model):
    __tablename__ = 'student'
    student_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    roll_number = db.Column(db.String, unique=True,nullable=False)
    first_name = db.Column(db.String, nullable=False)
    last_name = db.Column(db.String)
    courses = db.relationship('Course', secondary = 'enrollments')


class Course(db.Model):
    __tablename__ = 'course'
    course_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    course_code = db.Column(db.String, unique=True, nullable = False)
    course_name = db.Column(db.String, nullable = False)
    course_description = db.Column(db.String)


class Enrollments(db.Model):
    __tablename__ = 'enrollments'
    enrollment_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    estudent_id = db.Column(db.Integer, db.ForeignKey("student.student_id"), nullable=False)
    ecourse_id = db.Column(db.Integer, db.ForeignKey("course.course_id"), nullable = False)

@app.route("/", methods=["GET"])
def home():
    returned_students = Student.query.all()
    return render_template('index.html', students = returned_students)

@app.route("/student/create", methods = ["GET","POST"])
def input():
    if request.method == "GET":
        return render_template("form.html")
    elif request.method == "POST":
        roll_n = request.form.get("roll")
        first_name = request.form.get("f_name")
        last_name = request.form.get("l_name")
        selected_courses_values = request.form.getlist("courses")
        selected_courses =[]
        for i in selected_courses_values:
            a = i[-1]
            b = Course.query.with_entities(Course.course_name).filter_by(course_id = int(a)).one()

            selected_courses.append(b[0])
 
        stud = Student.query.filter_by(roll_number = roll_n).first()
        
        if stud:
            return render_template("already_exist.html") 
        else:
            try:
                student_new = Student(roll_number = roll_n, first_name = first_name, last_name = last_name)
                db.session.add(student_new)
                db.session.flush()
                max_student_id = student_new.student_id

                for i in range(len(selected_courses)):
                    courseid = Course.query.with_entities(Course.course_id).filter_by(course_name = selected_courses[i])

                    enrollments_new = Enrollments(estudent_id = max_student_id, ecourse_id = courseid)
                    
                    db.session.add(enrollments_new)
                
            except:
                db.session.rollback()
                return render_template('error.html')
            else:
                db.session.commit()
                return redirect('/')
            
@app.route("/student/<int:student_id>/update", methods = ["GET","POST"])
def update(student_id):
    student_to_update = Student.query.filter(Student.student_id == student_id).one()

    if request.method == "GET":
        return render_template("update_details.html", studenttoupdate = student_to_update )
    elif request.method == "POST":
        first_name = request.form.get("f_name")
        last_name = request.form.get("l_name")
        selected_courses_values = request.form.getlist("courses")
        selected_courses =[]
        for i in selected_courses_values:
            a = i[-1]
            b = Course.query.with_entities(Course.course_name).filter_by(course_id = int(a)).one()

            selected_courses.append(b[0])

        try:
            student_to_update.first_name = first_name
            student_to_update.last_name = last_name
            Enrollments.query.filter_by(estudent_id = student_to_update.student_id).delete()
            for i in range(len(selected_courses)):
                
                courseid = Course.query.with_entities(Course.course_id).filter_by(course_name = selected_courses[i])
                
                enrollments_new = Enrollments(estudent_id = student_to_update.student_id, ecourse_id = courseid)
                
                db.session.add(enrollments_new)
            
        except:
            db.session.rollback()
            return render_template('error.html')
        else:
            db.session.commit()
            return redirect('/')


@app.route("/student/<int:student_id>/delete", methods = ["GET"])
def delete(student_id):
    if request.method == "GET":
        id = student_id
        try:
            Student.query.filter_by(student_id = id).delete()
            Enrollments.query.filter_by(estudent_id = student_id).delete()
            
        except:
            db.session.rollback()
            return render_template('error.html')
        else:
            db.session.commit()
            return redirect('/')


@app.route("/student/<int:student_id>", methods = ["GET"])
def get_details(student_id):
    if request.method == "GET":
        student_detail_id = Student.query.filter(Student.student_id == student_id).one()
        # all_enrollment = enrollments.query.filter_by(estudent_id = student_id).all()
        # courses_ids = []
        # for enrollment in all_enrollment:
        #     courses_ids.append(enrollment.ecourse_id)
        # enrolled_course = []
        # for courseid in courses_ids:
        #     enrolled_course.append(course.query.filter_by(course_id = courseid).all())

        # print(courses_ids)
        # print(enrolled_course)
        enrolled_course = student_detail_id.courses
        return render_template("personal_details.html", studentdetail = student_detail_id, courses = enrolled_course)




if __name__== "__main__":
    app.run(debug=True)





