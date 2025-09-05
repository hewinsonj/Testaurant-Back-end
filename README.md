# Testaurant

Testaurant is an application designed to help restaurant employees learn about menu items and to help employers keep their employees accountable.
In depth lesson plans with visual aids can be created by employers that can help employees learn about menu items, products offered, company policies and more. Employers will also have the ability to create customizable tests that their employees can take with an array of question formats, such as "multiple choice", "select all that apply", "fill in the blanks", "true or false" and "open ended". Their scores will be logged for viewability between the employee and management through the use of personalized accounts made by the users. Users of Testaurant will also have the ability to add any items they wish to a searchable database of their offerings to aid them in accomodating guests with specific needs, or for educational purposes. The goal is to help shine some light on the gaps of knowledge that may exist within a company, and to close those gaps as they are discovered.

Justin Hewinson - Sole creator and developer of Testaurant


As a user, I want the ability to...

  - create an admin account.
  - create a limited access user account.
  - sign in.
  - change my password.
  - sign out.
  - create, update, and delete lesson plans (Admins/Managers).
  - view lesson plans.
  - view that I have completed a lesson plan.
  - view that others have completed a lesson plan (Admins/Managers).
  - create, update, and delete tests (Admins/Managers).
  - view tests.
  - take tests, including time-limited tests with countdown timers.
  - view my test results, including details on questions answered incorrectly.
  - view other users' test results (Admins/Managers).
  - leave comments on menu items.
  - add menu items to the shared access database.
  - search and filter the database for certain menu items or ingredients.
  - search for other users (Admins/Managers).
  - manage restaurants (Admins/Managers can create, update, delete; Employees have view-only access).
  - assign employees to restaurants.
  - create and manage employee accounts with roles (Admin, GeneralManager, Manager, Employee).
  - filter and search tests, questions, foods, and drinks by restaurant.
  - view audit logs of edits (Admins/Managers).


## General Approach

Testaurant consists of a backend API using Django and a client-side interface built with React and Semantic UI components. PostgreSQL is used for persistent data storage, and the server uses Django to interact with the database. The frontend communicates with the backend via RESTful APIs using Axios.

## Technologies Used
- **Backend API**
    - Django

- **Data Management**
    - PostgreSQL

- **Client Application**
    - React
    - Semantic UI
    - Axios
## Roles & Permissions

Testaurant uses a role-based access control system to ensure the right level of access for each user. The main roles are:

- **Admin**: Full access to all restaurants, users, and data. Can manage restaurants, employees, lesson plans, tests, and view audit logs.
- **GeneralManager**: Access to all restaurants and employees within their organization. Can manage lesson plans, tests, view results, and audit logs.
- **Manager**: Access is scoped to specific restaurant(s). Can manage employees, lesson plans, tests, and view results and audit logs for their assigned restaurants.
- **Employee**: Access is limited to their assigned restaurant(s). Can view lesson plans, take tests, and view their own results.

Role-based filtering and scoping ensure that users only see and manage data relevant to their role and assigned restaurant(s).

## Restaurant & Employee Management

- **Restaurant Management**: Admins and Managers can create, update, and delete restaurants. Employees can view restaurant information relevant to them.
- **Employee Management**: Admins and Managers can create and manage employee accounts, assign them to restaurants, and set their roles.
- **Role Assignment**: Each employee can be assigned a role (Admin, GeneralManager, Manager, Employee) and scoped to one or more restaurants as appropriate.

## Edit Logging (Audit Logs)

Testaurant maintains an audit log of edits and changes made to critical data such as lesson plans, tests, menu items, and employee accounts. Admins and Managers can review these logs to track who made changes, what was changed, and when. This feature improves accountability and transparency across the platform.
    

## Wireframes & Screenshots

 "Landing" Page
    ![](/testuarant_wireframes/Testuraunt-Landing.drawio.png)

 "Sign-up" Page
    ![](/testuarant_wireframes/Testuraunt-Sign%20up.drawio.png)

"Log-in" Page
    ![](/testuarant_wireframes/Testuraunt-Log%20in.drawio.png) 

"Log-out" Page
    ![](/testuarant_wireframes/Testuraunt-Log%20out.drawio.png)

"Admin Test Index" Page
    ![](/testuarant_wireframes/Testuraunt-Admin%20Test%20Index.drawio.png)

"Admin Lesson Index" Page
    ![](/testuarant_wireframes/Testuraunt-Admin%20Lesson%20Index.drawio%20(1).png)

"Non-Admin Test Index" Page
    ![](/testuarant_wireframes/Testuraunt-Test%20Index.drawio.png)    

"Non-Admin Lesson Index" Page
    ![](/testuarant_wireframes/Testuraunt-Lesson%20Index.drawio.png)

"Question" Page
    ![](/testuarant_wireframes/Testuraunt-Test%20Question%20Example.drawio.png)

"Test Results" Page
    ![](/testuarant_wireframes/Testuraunt-Test%20Results.drawio.png)

"Lesson Slide" Page
    ![](/testuarant_wireframes/Testuraunt-Lesson%20Example.drawio.png)

"Food Item Show" Page
    ![](/testuarant_wireframes/Testuraunt-Food%20Item%20Show.drawio.png)

"Food Item Edit" Page
    ![](/testuarant_wireframes/Testuraunt-Food%20Items%20Edit.drawio.png)

"Cocktail Show" Page
    ![](/testuarant_wireframes/Testuraunt-Cocktails%20Show.drawio.png)

"Cocktail Edit" Page
    ![](/testuarant_wireframes/Testuraunt-Cocktails%20Edit.drawio.png)

ERD
    ![](/testuarant_wireframes/Testuraunt-ERD.drawio.png)

Routes Tables
    ![](/testuarant_wireframes/Testuraunt-Routes%20Tables.drawio%20(3).png)
