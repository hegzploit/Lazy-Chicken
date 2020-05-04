import requests
from bs4 import BeautifulSoup
import os
import glob
from pathlib import Path
import time
import difflib
import filecmp
from multiprocessing import Pool

# Some Confguration
session = requests.Session()
lmsURL = "login_index_page_here"
email = "uni_mail"
password = "pass"
dashboard_link = 'dashboard_link'



form_data = {'anchor': '',
             'username': email,
             'password': password}


def postRequestLogin(): #logins to the website
    post_request = session.post(lmsURL, data=form_data)


def courseLinks():  # scrapes the main dashboard for courses links so it works dynamically on any account
    #postRequestLogin()
    link_list = []
    get_dashboard = session.get(dashboard_link)
    soup = BeautifulSoup(get_dashboard.content, 'html.parser')
    course_link_raw = soup.find_all("div", {"id": "courses-view-in-progress"})
    for link in course_link_raw:
        actual_course_link = link.find_all("a", href=True)
        for link_stripped_from_list in actual_course_link:
            if(link_stripped_from_list.get('href') != '#'):
                link_list.append(link_stripped_from_list.get('href'))
    link_list_no_dupes = list(set(link_list))
    return link_list_no_dupes


def getPages(course_link):  # scrapes the content of the course link from the above fn and outputs clean list with assignments, and lectures etc.. (also scrapes courses titles)
    get_course = session.get(course_link)
    soup = BeautifulSoup(get_course.content, 'html.parser')
    course_title = soup.head.title.text
    course_title_proper = course_title.replace(":", '').strip()
    course_title_proper = course_title_proper.replace("Course", '').strip()
    trash = soup.find_all("span", {"class": "accesshide"})
    for _ in trash:
        _.decompose()
    grab_courses = soup.find_all("span", {"class": "instancename"})
    final_formatted = [_.text.strip() for _ in grab_courses]

    return final_formatted, course_title_proper

def isDirEmpty(dirname): #will check if a directory is empty for avoiding some errors
    if (len(os.listdir(dirname))==0):
        return True
    else:
        return False

def checkMkdir(dirname): #checks if directory exists, if not it's gonna create it
    Path(dirname).mkdir(parents=True, exist_ok=True)


def returnLatestFile(dirname): #returns the latest file in a directory by date
    mypath = dirname + "\*.*"
    latest_file = max(glob.glob(mypath), key=os.path.getmtime)
    return latest_file

def process_instance(p): #main function which is gonna do all the work, scraping then saving each course in a directory and then comparing with last file in the directory
    postRequestLogin()
    dirEmptyFlag=1
    #returnLatestFileOrMkdir("./lazychicken_logs/" + getPages(p)[1])
    datetime_rn = time.strftime("%Y-%m-%d %H-%M")
    checkMkdir("./lazychicken_logs/" + getPages(p)[1]) #MUST FIRST CHECK IF DIR EMPTY WIP
    print('Updating ' + "./lazychicken_logs/" + getPages(p)[1])
    if(not isDirEmpty("./lazychicken_logs/" + getPages(p)[1])):
        last_file_updated = returnLatestFile("./lazychicken_logs/" + getPages(p)[1])
        dirEmptyFlag=0
    with open("./lazychicken_logs/"+getPages(p)[1] + "/lazychicken_" + datetime_rn + ".txt", "w+", encoding="utf-8") as f:
        for item in getPages(p)[0]:
            f.write("%s\n" % item)

    checkMkdir("./lazychicken_logs/" + getPages(p)[1])
    if(dirEmptyFlag == 0):
        with open(last_file_updated, 'r', encoding="utf-8") as old:
            with open("./lazychicken_logs/" + getPages(p)[1] + "/lazychicken_" + datetime_rn + ".txt", 'r', encoding="utf-8") as new:
                diff = difflib.unified_diff(
                    old.readlines(),
                    new.readlines(),
                    fromfile='old',
                    tofile='new',
                    lineterm='',
                    n=0
                )

                if(filecmp.cmp(new.name, old.name)):
                    pass
                else:
                    print("Found changes for: " + getPages(p)[1])
                    checkMkdir("./lazychicken_logs" + "/changes/")
                    with open("./lazychicken_logs" + "/changes/" + getPages(p)[1] + "~" + datetime_rn + ".txt", "w+", encoding="utf-8") as fc:
                        for line in diff:
                            for prefix in ('---', '+++', '@@'):
                                if line.startswith(prefix):
                                    break
                            else:
                                fc.write("%s\n" % line)

if(__name__=='__main__'): #i used multi-processing for speed
    postRequestLogin()
    pool = Pool() 
    pool.map(process_instance, courseLinks())

