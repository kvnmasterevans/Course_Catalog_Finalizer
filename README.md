This program processes the preliminary_course_catalog.json file output from git@github.com:kvnmasterevans/celdt.git

It outputs strict_clustering.json into the directory it's run from, which is the new file-name for the strict string-based clustering from v0.01, and also outputs fuzzy_clustering.json which is the fuzzy matching from v0.02
WARNING: It will overwrite any existing strict_clustering.json and fuzzy_clustering.json files in that directory when it does so


To run:
in terminal run "python catalog_predictor.py [name_of_preliminary_course_catalog_file.json]"
eg.
    python catalog_predictor.py preliminary_course_catalog.json


Pipeline:
1) (from v0.01)
First it filters the most likely course name string by accepting the most frequently appearing course string within each course ID as the canonical course name for each particular Course ID

It then filters for any varying Course ID's that share the same course name string
and keeps the Course ID for the more frequent course name string 

2) (from v0.02)
It takes the previous data, normalizes the course title and concatenates it with the course ID for each entry using build_match_key() and normalize_text()

Takes that data and clusters courses using fuzzy matching in cluster_courses() and uses connected_components() to create the simpler non-redundant adjacency graph

Then, similary to step 1, itassumes the most frequently appearing variant is the canonoical variant




Issues:
While this groups more shared courses from before it still leaves some errors such as non-courses (GPA) being misunderstood as courses, and some OCR misreads still exist

Possible improvements could include changing the required fuzzy-match percentage, filtering for course ID length, or requiring minimum appearance frequency for a possible course to be included 






Versions:
v0.01 - Initial commit
v0.01.1 - Updated README - no change to code
v0.01.2 - Fixed typo in README - no change to code
v0.01.3 - updated README to mention all current versions - no change to code
v0.02 - Fuzzy matching added