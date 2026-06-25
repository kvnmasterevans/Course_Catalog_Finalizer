import json
import sys
from collections import defaultdict
from fuzzy_matching import cluster_courses


# stage_1_catalog_builder.py
# this file combines the various reads from the course catalog output from the CELDT repository
# into a partially-processed file ready for the next stage -> stage_2_catalog_editor.py
# This output file is called "fuzzy_clustering.json"
#
# TO RUN:
#   python stage_1_catalog_builder.py [CELDT_catalog_output.py]
# eg. 
#   python stage_1_catalog_builder.py preliminary_course_catalog.json





file_path = sys.argv[1]

with open(file_path, "r") as f:
    data = json.load(f)


# -----------------------------------------
# STEP 1:
# Determine canonical title for each course_id
# -----------------------------------------

course_id_to_title = {}

for course_id, info in data.items():

    titles = info.get("titles", {})

    # pick most frequent OCR title for this course_id
    canonical_title = max(
        titles.items(),
        key=lambda x: x[1][0]
    )[0]

    course_id_to_title[course_id] = canonical_title


# -----------------------------------------
# STEP 2:
# Group ALL course_ids by title
# -----------------------------------------

title_groups = defaultdict(list)

for course_id, title in course_id_to_title.items():

    total_count = data[course_id]["count"]

    titles_w_files = data[course_id]["titles"]

    title_groups[title].append({
        "course_id": course_id,
        "count": total_count,
        "titles": titles_w_files
    })


# -----------------------------------------
# STEP 3:
# For each title:
# choose MOST FREQUENT course_id
# -----------------------------------------

finalized_catalog = {}

for title, entries in title_groups.items():

    # choose course_id with highest count
    winner = max(entries, key=lambda x: x["count"])
    

    all_files = set()
    for entry in entries:
        title_dict = entry["titles"]

        if title in title_dict:
            _, files = title_dict[title]
            all_files.update(files)

    finalized_catalog[title] = {
        "course_id": winner["course_id"],
        "count": winner["count"],
        "files": list(all_files)
    }


# -----------------------------------------
# OUTPUT AS JSON FILE
# -----------------------------------------

with open("strict_clustering.json", "w") as f:
    json.dump(finalized_catalog, f, indent=4)


grouped = cluster_courses(finalized_catalog)

with open("fuzzy_clustering.json", "w", encoding="utf-8") as f:
    json.dump(grouped, f, indent=4)