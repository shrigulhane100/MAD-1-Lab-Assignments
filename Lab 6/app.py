from flask import Flask, request, redirect
from flask import render_template
from flask_sqlalchemy import SQLAlchemy

import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy import Table, Column, Integer, String, ForeignKey
from sqlalchemy.orm import Session
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


from flask_restful import Resource, Api, fields, marshal_with, reqparse
from validation import NotFoundError, BusineesValidationError, BadRequest
import json
import os

app = Flask(__name__)


current_dir = os.path.abspath(os.path.dirname(__file__))
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(
    current_dir, "week7_database.sqlite3"
)
# app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///week7_database.sqlite3"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy()
db.init_app(app)
api = Api(app)
app.app_context().push()


class Student(db.Model):
    __tablename__ = "student"
    student_id = Column(Integer, autoincrement=True, primary_key=True)
    roll_number = Column(String, unique=True, nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String)
    course = relationship("Course", secondary="enrollment")


class Course(db.Model):
    __tablename__ = "course"
    course_id = Column(Integer, autoincrement=True, primary_key=True)
    course_code = Column(String, unique=True, nullable=False)
    course_name = Column(String, nullable=False)
    course_description = Column(String)


class Enrollment(db.Model):
    __tablename__ = "enrollment"
    enrollment_id = Column(Integer, autoincrement=True, primary_key=True)
    estudent_id = Column(Integer, ForeignKey("student.student_id"), nullable=False)
    ecourse_id = Column(Integer, ForeignKey("course.course_id"), nullable=False)


@app.route("/", methods=["GET", "POST"])
def home():
    returned_students = Student.query.all()
    return render_template("index.html", students=returned_students), 200


@app.route("/student/create", methods=["GET", "POST"])
def input():
    if request.method == "GET":
        return render_template("form.html"), 200
    elif request.method == "POST":
        roll_n = request.form.get("roll")
        first_name = request.form.get("f_name")
        last_name = request.form.get("l_name")
        # selected_courses_values = request.form.getlist("course")
        # selected_courses = []
        # for i in selected_courses_values:
        #     a = i[-1]
        #     b = (
        #         Course.query.with_entities(Course.course_name)
        #         .filter_by(course_id=int(a))
        #         .one()
        #     )

        #     selected_courses.append(b[0])

        stud = Student.query.filter_by(roll_number=roll_n).first()

        if stud:
            return render_template("already_exist.html"), 200
        else:
            try:
                student_new = Student(
                    roll_number=roll_n, first_name=first_name, last_name=last_name
                )
                db.session.add(student_new)
                db.session.flush()

                # max_student_id = student_new.student_id
                # for i in range(len(selected_courses)):
                #     courseid = Course.query.with_entities(Course.course_id).filter_by(
                #         course_name=selected_courses[i]
                #     )

                #     enrollments_new = Enrollment(
                #         estudent_id=max_student_id, ecourse_id=courseid
                #     )

                #     db.session.add(enrollments_new)

            except:
                db.session.rollback()
                return render_template("error.html"), 200
            finally:
                db.session.commit()
                return redirect("/"), 200


@app.route("/student/<int:student_id>/update", methods=["GET", "PUT"])
def update(student_id):
    student_to_update = Student.query.filter(Student.student_id == student_id).one()

    if request.method == "GET":
        app.logger.debug(str(student_to_update))
        app.logger.debug("Debug log level 2")
        return render_template("update_details.html", studenttoupdate=student_to_update)
    elif request.method == "PUT":
        app.logger.debug("Debug log level 3")
        first_name = request.form.get("f_name")
        last_name = request.form.get("l_name")

        # selected_courses_values = request.form.getlist("course")
        # selected_courses = []
        # for i in selected_courses_values:
        #     a = i[-1]
        #     b = (
        #         Course.query.with_entities(Course.course_name)
        #         .filter_by(course_id=int(a))
        #         .one()
        #     )

        #     selected_courses.append(b[0])

        try:
            student_to_update.first_name = first_name
            student_to_update.last_name = last_name
            app.logger.debug("Debug log level 4")
            db.session.flush()
            # Enrollment.query.filter_by(
            #     estudent_id=student_to_update.student_id
            # ).delete()

            # for i in range(len(selected_courses)):

            #     courseid = Course.query.with_entities(Course.course_id).filter_by(
            #         course_name=selected_courses[i]
            #     )

            #     enrollments_new = Enrollment(
            #         estudent_id=student_to_update.estudent_id, ecourse_id=courseid
            #     )
            #     db.session.add(enrollments_new)

        except:
            app.logger.debug("Debug log level 5")
            db.session.rollback()
            return render_template("error.html"), 200
        finally:
            app.logger.debug("Debug log level 6")
            db.session.commit()
            return redirect("/"), 200


@app.route("/student/<int:student_id>/delete", methods=["POST"])
def delete(student_id):
    if request.method == "POST":
        try:
            user = Student.query.filter_by(student_id=student_id).get(1)

            db.delete(user)
            enrollment = Enrollment.query.filter_by(estudent_id=student_id)
            print(enrollment)
            db.delete(enrollment)

        except:
            db.session.rollback()
            return render_template("error.html"), 200
        finally:
            db.session.commit()
            return redirect("/"), 200


@app.route("/student/<int:student_id>", methods=["GET"])
def get_details(student_id):
    if request.method == "GET":
        student_detail_id = Student.query.filter(Student.student_id == student_id).one()

        enrolled_course = student_detail_id.course
        return (
            render_template(
                "personal_details.html",
                studentdetail=student_detail_id,
                course=enrolled_course,
            ),
            200,
        )


@app.route("/student/<int:student_id>/withdraw/<int:course_id>", methods=["GET"])
def withdraw_course(student_id, course_id):
    if request.method == "DELETE":
        try:
            # user = Student.query.filter_by(student_id=student_id).get(1)

            course_id = int(request.args.get("course_id"))
            enrollment = Enrollment.query.filter_by(estudent_id=student_id)
            db.delete(enrollment)

        except:
            db.session.rollback()
            return render_template("error.html"), 200
        finally:
            db.session.commit()
            return redirect("/"), 200


if __name__ == "__main__":
    app.run(debug=True)
