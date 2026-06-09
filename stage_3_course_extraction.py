import os
import json
import csv
import pickle
import re
import sys
from fuzzy_matching import build_match_key
from rapidfuzz import fuzz


# stage_3_course_extraction.py
# 
# this script checks student transcript data from the CELDT output against
# the finalized catalog from stage_2_catalog_editor.py
#
# TO RUN:
#   python stage_3_course_extraction.py [path to student data directory] [finalized_transcript.json]
# eg.
#   python stage_3_course_extraction.py OCR_Cache fuzzy_clustering_by_course.json





THRESHOLD = 88

REJECT_KEYWORDS = [
    "TERM:",
    "CUMULATI",
    "Entry",
    "Exit",
    "Credit",
    "School",
    "Official",
    "State ID",
    "Grd"
]

CREDIT_PATTERN = re.compile(r"^\d+\.\d{2}$")
GRADE_PATTERN = re.compile(r"^[ABCDF][\+\-t]?$")


def clean_course_code(token):
    digits = re.sub(r"[^\d]", "", token)
    if len(digits) >= 4:
        return digits
    return None


def is_credit(token):
    return bool(CREDIT_PATTERN.match(token))


def is_grade(token):
    return bool(GRADE_PATTERN.match(token))



def write_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def write_csv(path, rows):
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["course_id", "course_name"])
        writer.writerows(rows)



def main(student_data_directory, catalog):
    
    course_catalog = {}
    final_student_courses = []
    with open(catalog, "r", encoding="utf-8") as f:
        course_catalog = json.load(f)


    for filename in os.listdir(student_data_directory):

        if not filename.endswith(".pkl"):
            continue

        path = os.path.join("OCR_Cache", filename)

        with open(path, "rb") as f:
            data = pickle.load(f)



        # ---------------------------------------------
        # extract and identify courses from student trasncript data
        # ---------------------------------------------

        student_courses = []
        confirmed_student_courses = []

        # Extract course names and IDs
        for row in data["rows"]:
            tokens = row.get("text", [])
            if not tokens:
                continue

            joined_row = " ".join(tokens)

            if any(keyword in joined_row for keyword in REJECT_KEYWORDS):
                continue

            # Find course code
            code_index = None
            course_code = None

            for i, token in enumerate(tokens):
                cleaned = clean_course_code(token)
                if cleaned:
                    code_index = i
                    course_code = cleaned
                    break

            if course_code is None:
                continue

            # Find credit
            credit_index = None
            credit_value = None

            for i, token in enumerate(tokens):
                if is_credit(token):
                    credit_index = i
                    credit_value = token
                    break

            if credit_value is None:
                continue

            # Extract title
            middle_tokens = tokens[code_index + 1 : credit_index]
            middle_tokens = [t for t in middle_tokens if not is_grade(t)]

            title = " ".join(middle_tokens).strip()
            title = re.sub(r"\s+", " ", title)

            if not title:
                continue


            course_data = {"course_title":title, 
                        "course_id":course_code}
            
            student_courses.append(course_data)
        


        

        #---------------------------------------------
        # check student courses against the catalog
        #---------------------------------------------

        for student_course_data in student_courses:
            best_score = 0
            best_match = None


            course = student_course_data["course_title"]
            course_id = student_course_data["course_id"]

            match_key = build_match_key(course, course_id)
            

            # setup fuzzy match structure
            match_key = build_match_key(course, course_id)
            print("match against catalog: " + match_key)
            
            # for loop over catalog courses
            for item in course_catalog.values():

                score = fuzz.ratio(
                        match_key,
                        item["groups"][0]["canonical_match_key"]
                    )
                # print(item["groups"][0]["canonical_match_key"])
            
                if score > best_score:
                        best_score = score
                        best_match = item
                        print("new best score: " + str(score))
                        print(best_match)

            if best_score:
                if best_score >= THRESHOLD:
                    matched_course = {
                        "matched_course_id": best_match["course_id"],
                        "matched_course_name": best_match["canonical_name"],
                        "score": best_score
                    }
                    confirmed_student_courses.append(matched_course)
                
        student_course_list = {"filename":data["filename"], "courses":confirmed_student_courses}
        final_student_courses.append(student_course_list)

        '''
        
        
        '''
    write_json("student_courses.json", final_student_courses)





if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python course_schedule_extraction.py [course_cache_folder] [course_catalog.json]")
        sys.exit(1)

    main(sys.argv[1], sys.argv[2])


