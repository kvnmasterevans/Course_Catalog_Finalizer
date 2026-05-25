This program processes the preliminary_course_catalog.json file output from git@github.com:kvnmasterevans/celdt.git

It outputs finalized_catalog.json into the directory it's run from 
WARNING: It will overwrite any existing finalized_catalog.json in that directory when it does so


To run:
in terminal run "python catalog_predictor.py [name_of_preliminary_course_catalog_file.json]"


It finalizes the catalog output by first filtering the most likely course name string by accepting the most frequently appearing course string within each course ID as the canonical course name for each particular Course ID

It then filters for any varying Course ID's that share the same course name string
and keeps the Course ID for the more frequent course name string 


Versions:
v0.01 - Initial commit
v0.01.1 - Updated README - no change to code