import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re
import os

studyGuide = "https://cs.uowm.gr/odigos-spoydon/"
coursesProgram = "https://cs.uowm.gr/archiki-selida/orologio-programma-mathimaton/"

def getStudyGuidePdf(year: int | str = None):
    if not year:
        year = datetime.now().year

    response = requests.get(studyGuide)
    soup = BeautifulSoup(response.text, "html.parser")

    content = soup.find("div", attrs={"id": "content"})

    links = content.find_all("a")

    results = []

    # regex match for the year
    for link in links:
        regex = r"(\S+\s*\S*)\s*(\d+)\s*.?\s*(\d+)"
        match = re.match(regex, link.text)

        if not match:
            continue

        startYear = int(match.group(2))
        endYear = int(match.group(3))

        results.append((link["href"], startYear, endYear))

    # get the link with the given year
    for result in results:
        if result[2] == year:
            return result

    for result in results:
        if result[1] == year:
            return result

    for result in results:
        if result[2] == year - 1:
            return result

    for result in results:
        if result[1] == year - 1:
            return result

    return results[0]

def getCoursesProgramPdf(year: int | str = None, semester: str = None):
    if not year:
        year = datetime.now().year

    if not semester:
        month = datetime.now().month

        if month > 10 and month < 2:
            semester = "Χειμερινό"
        else:
            semester = "Εαρινό"

    response = requests.get(coursesProgram)
    soup = BeautifulSoup(response.text, "html.parser")

    content = soup.find("div", attrs={"class": "entry-content"})

    results = []

    # regex match for link, year and semester
    for child in content.children:
        if not child.name:
            continue

        pChild = child.find("strong")

        if not pChild:
            continue

        if pChild.name == "strong":
            regex = r"(\S+)\s*(\d+)\s*.?\s*(\d+)"
            match = re.match(regex, pChild.text)

            if not match:
                print("No match for", pChild.text)
                continue

            courseSemester = match.group(1)
            courseStartYear = int(match.group(2))
            courseEndYear = int(match.group(3))

            # get the next sibling which is the link
            link = child.find_next_sibling("p").find("a")

            results.append((link["href"], courseStartYear, courseEndYear, courseSemester))

    # get the course program for the given year and semester
    for result in results:
        if result[2] == year and result[3] == semester:
            return result

    for result in results:
        if result[1] == year and result[3] == semester:
            return result

    return results[0]

def convertToPdf(filePath: str):
    os.system(f"libreoffice --headless --convert-to pdf --outdir ./pdfs '{filePath}' > /dev/null 2>&1")
    os.remove(filePath)

def downloadPdfs():
    studyGuidePdf = getStudyGuidePdf()

    fileExtension = studyGuidePdf[0].split(".")[-1]
    with open(f"pdfs/studyGuide - {studyGuidePdf[2]}.{fileExtension}", "wb") as file:
        response = requests.get(studyGuidePdf[0])
        file.write(response.content)
        print("Study guide downloaded successfully!")

    # run libreoffice to convert the file to pdf
    if fileExtension != "pdf":
        convertToPdf(f"pdfs/studyGuide - {studyGuidePdf[2]}.{fileExtension}")

    coursesProgramPdf = getCoursesProgramPdf()

    fileExtension = coursesProgramPdf[0].split(".")[-1]
    with open(f"pdfs/coursesProgram - {coursesProgramPdf[2]} - {coursesProgramPdf[3]}.{fileExtension}", "wb") as file:
        response = requests.get(coursesProgramPdf[0])
        file.write(response.content)
        print("Courses program downloaded successfully!")

    # run libreoffice to convert the file to pdf
    if fileExtension != "pdf":
        convertToPdf(f"pdfs/coursesProgram - {coursesProgramPdf[2]} - {coursesProgramPdf[3]}.{fileExtension}")

if __name__ == "__main__":
    downloadPdfs()