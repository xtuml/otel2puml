import json

from test_event_generator.graph import Graph
from test_event_generator.solutions.graph_solution import (
    get_audit_event_jsons_and_templates,
    get_audit_event_jsons_and_templates_all_topological_permutations,
    GraphSolution
)
from test_event_generator.io.run import puml_file_to_test_events
import pm4py as pm
import pandas as pd

graph_solutions = [
    GraphSolution.from_event_list(event_list[0])
    for event_list in puml_file_to_test_events(
        "sequence_branch_counts.puml"
    )["Branch_Counts"]["ValidSols"][0]
]

# event_lists = list(
#     event
#     for event_list in
#     get_audit_event_jsons_and_templates_all_topological_permutations(graph_solutions)
#     for event in event_list[0]
# )

event_lists = []
counter = 0
for event_list in get_audit_event_jsons_and_templates_all_topological_permutations(graph_solutions):
    counter += 1
    for event in event_list[0]:
        event_lists.append({**event, 'resource': f"{counter}"})

# event_lists = list(
#     {**event, "resource": f"{i}"}
#     for i, event_list in
#     enumerate(list(get_audit_event_jsons_and_templates(
#         graph_solutions,
#         is_template=False
#     )))
#     for event in event_list[0]
# )



df = pd.DataFrame.from_records(event_lists).drop(
    ["jobName", "previousEventIds", "applicationName"],
    axis=1
)
df.set_index("eventId", inplace=True)

df = pm.format_dataframe(df, case_id='jobId', activity_key='eventType', timestamp_key='timestamp')
batches = pm.discover_batches(df, resource_key='resource')
# dfg = pm.discover_heuristics_net(df)
# powl = pm.discover_powl(df)
# pm.vis.save_vis_powl(powl, 'trial.png')
# pm.vis.save_vis_heuristics_net(dfg, 'trial.png')
# process_tree = pm.discover_process_tree_inductive(df)
# petri_net = pm.discover_petri_net_ilp(df)
# bpmn_model = pm.convert_to_bpmn(petri_net)
# pm.vis.save_vis_petri_net(*petri_net, 'trial.png')
# bpmn_model = pm.convert_to_bpmn(process_tree)
# pm.vis.save_vis_process_tree(process_tree, 'trial.png')
# pm.view_bpmn(bpmn_model)
# pm.save_vis_bpmn(bpmn_model, 'trial.png')
