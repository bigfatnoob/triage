from __future__ import print_function, division
import sys, os
sys.path.append(os.path.abspath("."))
import json

__author__ = 'panzer'


def get_json(file_name):
  with open("data/eclipse/%s.json"%file_name, "r") as f:
    data = json.load(f)[file_name]
  return data

def save_json(obj, file_name, folder):
  if folder:
    folder += "/"
  else:
    folder += ""
  with open('%s%s.json'%(folder,file_name), 'w') as f:
    json.dump(obj, f, indent=4)

VALID_RESOLUTION = ["FIXED", "WONTFIX"]

def to_utf(string):
  return string.encode("utf-8")

def consolidate():
  reports = get_json("reports")
  assigned_to = get_json("assigned_to")
  bug_status = get_json("bug_status")
  #cc = get_json("cc")
  component = get_json("component")
  op_sys = get_json("op_sys")
  priority = get_json("priority")
  product = get_json("product")
  #resolution = get_json("resolution")
  severity = get_json("severity")
  short_desc = get_json("short_desc")
  version = get_json("version")
  count = 0
  developer_map = {}
  bug_map = {}
  for bug_id, report in reports.items():
    count += 1
    resolution = to_utf(report["current_resolution"])
    if resolution and resolution not in VALID_RESOLUTION:
      # Invalid bug either DUPLICATE or INVALID or WORKS FOR ME
      continue
    bug = {}
    status = to_utf(report["current_status"])
    bug["resolution"] = resolution
    bug["status"] = status
    # Assignees
    assignees = assigned_to[bug_id]
    bug_assignees = None
    if assignees:
      bug_assignees = []
      for assignee in assignees:
        assignee_id = assignee["who"]
        bug_assignees.append(assignee_id)
        developer_bugs = developer_map.get(assignee_id, [])
        developer_bugs.append(bug_id)
        developer_map[assignee_id] = developer_bugs
    bug["assignees"] = bug_assignees
    # Bug Status
    status_chain =  bug_status[bug_id]
    bug_status_chain = None
    if status_chain:
      bug_status_chain = [to_utf(i_status["what"]) for i_status in status_chain]
    bug["status_chain"] = bug_status_chain
    # Components
    component_chain = component[bug_id]
    components = None
    if component_chain:
      components = [to_utf(c_chain["what"]) for c_chain in component_chain]
    bug["components"] = components
    # Op Systems
    op_systems = op_sys[bug_id]
    systems = None
    if op_systems:
      systems = [to_utf(op_system["what"]) for op_system in op_systems]
    bug["operating_systems"] = systems
    # Priorities
    priority_chain = priority[bug_id]
    priorities = None
    if priority_chain:
      priorities = [to_utf(p_chain["what"]) if p_chain["what"] else None for p_chain in priority_chain]
    bug["priorities"] = priorities
    # Products
    product_chain = product[bug_id]
    products = None
    if product_chain:
      products = [to_utf(p_chain["what"]) for p_chain in product_chain]
    bug["products"] = products
    # Severities
    severity_chain = severity[bug_id]
    severities = None
    if severity_chain:
      severities = [to_utf(s_chain["what"]) for s_chain in severity_chain]
    bug["severities"] = severities
    # Descriptions
    description_chain = short_desc[bug_id]
    descriptions = None
    if description_chain:
      descriptions = [d_chain["what"] for d_chain in description_chain]
    bug["descriptions"] = descriptions
    # Versions
    version_chain = version[bug_id]
    versions = None
    if version_chain:
      versions = [to_utf(v_chain["what"]) for v_chain in version_chain]
    bug["versions"] = versions
    bug_map[bug_id] = bug
  save_json(bug_map, 'eclipse_bugs', "data/eclipse/consolidated")
  save_json(developer_map, 'eclipse_developers', "data/eclipse/consolidated")




if __name__ == "__main__":
  consolidate()