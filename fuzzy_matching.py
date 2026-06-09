import json
import re
import unicodedata
from collections import defaultdict
from rapidfuzz import fuzz


# =========================================================
# CONFIGURATION
# =========================================================
# was 92
FUZZY_THRESHOLD = 88

# Common OCR substitutions
OCR_REPLACEMENTS = {
    "0": "o",
    "1": "l",
    "5": "s",
    "|": "l",
}

# =========================================================
# NORMALIZATION
# =========================================================


def normalize_text(text: str) -> str:
    """
    Aggressive OCR-oriented normalization.
    Produces a machine-friendly matching string.
    """

    # Unicode normalization
    text = unicodedata.normalize("NFKD", text)

    # Remove combining accents/marks
    text = "".join(
        c for c in text
        if not unicodedata.combining(c)
    )

    # Lowercase
    text = text.lower()

    # OCR replacement cleanup
    for bad, good in OCR_REPLACEMENTS.items():
        text = text.replace(bad, good)

    # Remove all non-alphanumeric chars
    text = re.sub(r"[^a-z0-9]", "", text)

    return text

# =========================================================
# BUILD MATCH KEY
# =========================================================


def build_match_key(course_name: str, course_id: str) -> str:
    """
    Build normalized fuzzy matching key.
    """

    normalized_name = normalize_text(course_name)
    # normalized_id = normalize_text(str(course_id))

    return f"{normalized_name}|{str(course_id)}"


# =========================================================
# GRAPH CLUSTERING
# =========================================================


def connected_components(graph):
    """
    Find connected components in adjacency graph.
    """

    visited = set()
    components = []

    for node in graph:
        if node in visited:
            continue

        stack = [node]
        component = []

        while stack:
            current = stack.pop()

            if current in visited:
                continue

            visited.add(current)
            component.append(current)

            for neighbor in graph[current]:
                if neighbor not in visited:
                    stack.append(neighbor)

        components.append(component)

    return components


# =========================================================
# MAIN PIPELINE
# =========================================================


def cluster_courses(course_data: dict):
    """
    Main entity resolution pipeline.

    Input format:

    {
        course_name: {
            "course_id": ...,
            "count": ...
        }
    }
    """

    # ---------------------------------------------
    # STEP 1: Prepare records
    # ---------------------------------------------

    records = []

    for course_name, data in course_data.items():

        course_id = str(data["course_id"])
        count = data["count"]

        match_key = build_match_key(course_name, course_id)

        record = {
            "original_name": course_name,
            "course_id": course_id,
            "count": count,
            "match_key": match_key,
        }

        records.append(record)

    # ---------------------------------------------
    # STEP 2: Build similarity graph
    # ---------------------------------------------

    graph = defaultdict(set)

    for i in range(len(records)):
        for j in range(i + 1, len(records)):

            r1 = records[i]
            r2 = records[j]

            # IMPORTANT OPTIMIZATION:
            # only compare same course IDs
            # if r1["course_id"] != r2["course_id"]:
            #     continue

            score = fuzz.ratio(
                r1["match_key"],
                r2["match_key"]
            )

            if score >= FUZZY_THRESHOLD:
                graph[i].add(j)
                graph[j].add(i)

    # ensure isolated nodes exist
    for i in range(len(records)):
        graph[i]


    # ---------------------------------------------
    # STEP 3: Find connected components
    # ---------------------------------------------

    components = connected_components(graph)

    # ---------------------------------------------
    # STEP 4: Build canonical groups
    # ---------------------------------------------

    canonical_groups = {}

    for group_index, component in enumerate(components):

        variants = []
        total_count = 0

        for idx in component:
            record = records[idx]
            variants.append(record)
            total_count += record["count"]

        # choose canonical record
        # strategy: highest count wins
        canonical_record = max(
            variants,
            key=lambda r: r["count"]
        )

        canonical_key = f"group_{group_index}"

        # build enriched variant entries
        enriched_variants = []

        for variant in variants:

            score = fuzz.ratio(
                canonical_record["match_key"],
                variant["match_key"]
            )

            enriched_variants.append({
                "original_name": variant["original_name"],
                "course_id": variant["course_id"],
                "count": variant["count"],
                "match_key": variant["match_key"],
                "similarity_to_canonical": round(score, 2),
            })

        canonical_groups[canonical_key] = {
            "canonical_name": canonical_record["original_name"],
            "canonical_course_id": canonical_record["course_id"],
            "canonical_match_key": canonical_record["match_key"],
            "total_count": total_count,
            "variant_count": len(enriched_variants),
            "variants": sorted(
                enriched_variants,
                key=lambda x: x["count"],
                reverse=True,
            )
        }

    return canonical_groups



# =========================================================
# EXAMPLE USAGE
# =========================================================


# if __name__ == "__main__":

#     with open("courses.json", "r", encoding="utf-8") as f:
#         course_data = json.load(f)

#     grouped = cluster_courses(course_data)

#     with open("canonical_courses.json", "w", encoding="utf-8") as f:
#         json.dump(grouped, f, indent=4)

#     print(f"Built {len(grouped)} canonical groups")