import sys
import json
import csv
from collections import defaultdict
from pathlib import Path

# stage_2_catalog_editor.py
#
# This file takes the output from stage_1_catalog_builder.py as input
# It standardizes the output for input to the next stage (stage_3_course_extraction.py)
# Eventually it will allow editing that data before finalizing the course catalog
#
# TO RUN:
#   python stage_2_catalog_editor.py [stage_1_output.json]
# eg.
#   python stage_2_catalog_editor.py fuzzy_clustering.py



def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def write_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def write_csv(path, rows):
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["course_id", "course_name"])
        writer.writerows(rows)


def main(input_path):

    #--------------------------------
    # Initialize data and variables
    #--------------------------------
    data = load_json(input_path)

    # course_id -> aggregated structure
    # stores course catalog data for json output
    by_course = {}

    # for CSV output (deduplicated)
    csv_rows = {}




    #----------------------------------------------------------
    # restructures course data format to be organized by course id
    #----------------------------------------------------------

    for group_id, group in data.items():
        course_id = group.get("canonical_course_id")
        course_name = group.get("canonical_name")

        if not course_id:
            continue

        # initialize course entry if needed
        if course_id not in by_course:
            by_course[course_id] = {
                "course_id": course_id,
                "canonical_name": course_name,
                "groups": []
            }

        # store group info under this course_id
        by_course[course_id]["groups"].append({
            "group_id": group_id,
            "canonical_match_key": group.get("canonical_match_key"),
            "total_count": group.get("total_count"),
            "variant_count": group.get("variant_count"),
            "variants": group.get("variants", [])
        })

        # keep first seen name as canonical for CSV
        if course_id not in csv_rows:
            csv_rows[course_id] = course_name



    #--------------------------------------
    # Output results
    #--------------------------------------

    # output paths
    input_path = Path(input_path)
    json_out = input_path.with_name(input_path.stem + "_by_course.json")
    csv_out = input_path.with_name(input_path.stem + "_catalog.csv")

    write_json(json_out, by_course)
    
    write_csv(
        csv_out,
        [(cid, csv_rows[cid]) for cid in csv_rows]
    )

    print(f"Written JSON: {json_out}")
    print(f"Written CSV: {csv_out}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python code.py [target_json_file]")
        sys.exit(1)

    main(sys.argv[1])