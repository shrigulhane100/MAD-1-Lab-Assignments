from jinja2 import Template
import csv
import sys
import matplotlib.pyplot as plt

TEMPLATE3 ="""<!DOCTYPE html>
<html>
    <head>
        <title> Something went wrong </title>
    </head>
    <body>
        <h1>Wrong Inputs</h1>
        <p>Something went wrong </p>
    </body>
</html>"""

TEMPLATE2 = """<!DOCTYPE html>
<html>
    <head>
        <title> Course Data </title>
    </head>
    <body>
        <h1>Course Details</h1>
        <table border= 1>
            <thead>
                <tr>
                    <th>Average Marks</th>
                    <th>Maximum Marks</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>{{average}}</td>
                    <td>{{maximum}}</td>
                </tr>
            </tbody>
        </table>
        <img src="hist.PNG">
    </body>
</html>"""

TEMPLATE1= """<!DOCTYPE html>
<html>
<head>
    <title> Student Data</title>
</head>
<body>
    <h1> Student Details </h1>
    <table border=1px>
        <thead>
            <tr>
                <th>Student ID </th>
                <th>Course ID </th>
                <th>Marks </th>
            </tr>
        </thead>
        <tbody>
            {% for i in range(size) %}
            <tr>
                <td>{{student_id}}</td>
                <td>{{course_id[i]}}</td>
                <td>{{marks[i]}}</td>
            </tr>
            {% endfor %} 
          <tr>
            <td colspan="2" align="center">Total Marks</td>
                <td>{{total}}</td>
          </tr>     
        </tbody>
    </table>
</body>
</html>"""

var_file = open("data.csv", 'r')
var_file.readline()
list = []
for line in var_file:
    list.append(line.strip().split(','))

for i in list:
    print(i)
def main():
    global list
    if(len(sys.argv) > 1):
        req_detail = sys.argv[1]
        s_id = [i[0] for i in list]
        c_id = [int(i[1]) for i in list]
        if(req_detail == '-s' and sys.argv[2] in s_id):
            
            student_id = sys.argv[2]
            course_id=[]
            marks=[]
            total = 0
            count=0
            for i in list:
                if i[0]==student_id:
                    total += int(i[2])
                    marks.append(int(i[2]))
                    course_id.append(int(i[1]))
                    count+=1
            template = Template(TEMPLATE1)
            content=template.render(student_id=student_id ,course_id=course_id,marks=marks,size=count,total=total)
        elif(req_detail == '-c' and int(sys.argv[2]) in c_id):
            print("hello")
            course_id = int(sys.argv[2])
            marks_list=[]
            for i in list:
                if int(i[1])==course_id:
                    marks_list.append(int(i[2]))
            maximum=max(marks_list)
            average=sum(marks_list)/len(marks_list)
            plt.hist(marks_list)
            plt.xlabel("Marks")
            plt.ylabel('Frequency')
            plt.savefig('hist.png')
            template = Template(TEMPLATE2)
            content = template.render(average=average,maximum=maximum)
        else:
            template = Template(TEMPLATE3)
            content = template.render() 
    else:
        template = Template(TEMPLATE3)
        content = template.render()

    # Save the rendered html document
    my_html_document_file = open('Output.html','w')
    my_html_document_file.write(content)
    my_html_document_file.close()

if __name__ == "__main__":
    main()