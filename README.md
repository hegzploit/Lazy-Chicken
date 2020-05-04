# This script is just helpful for one person, me!

**Basically logins to my uni learning system and checks if there is any new assignments or lectures, then it outputs the changes in a txt file**
---
<details>
  <summary>DEMO</summary>
  ![demo](demo\lazychick.gif)
</details>


detailed steps on how it's done below:
1. Send a login request with email and pwd to authenticate
2. Navigate to the dashboard which contains all the courses
3. grabs all the links for the courses from the dashoard and then stores them in a list
4. uses the courses links list to visit each course and grab all the titles from it's page (assignment title , lecture title and any title it's gonna find), also stores the course name aswel
5. stores each course data in a list
6. lists are then converted to text files each in it's own folder and organized
7. difflib is used to show the differences between each run of the program, so basically each time i run this, it's gonna store a copy of the data locally and compare it with the data from the last run of the program.
8. each link is fetched in it's own process using the multi-processing library
