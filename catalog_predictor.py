import json
import sys
from collections import defaultdict
from fuzzy_matching import cluster_courses

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
        key=lambda x: x[1]
    )[0]

    course_id_to_title[course_id] = canonical_title


# -----------------------------------------
# STEP 2:
# Group ALL course_ids by title
# -----------------------------------------

title_groups = defaultdict(list)

for course_id, title in course_id_to_title.items():

    total_count = data[course_id]["count"]

    title_groups[title].append({
        "course_id": course_id,
        "count": total_count
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

    finalized_catalog[title] = {
        "course_id": winner["course_id"],
        "count": winner["count"]
    }


# -----------------------------------------
# OUTPUT AS JSON FILE
# -----------------------------------------

with open("strict_clustering.json", "w") as f:
    json.dump(finalized_catalog, f, indent=4)


grouped = cluster_courses(finalized_catalog)

with open("fuzzy_clustering.json", "w", encoding="utf-8") as f:
    json.dump(grouped, f, indent=4)