from typing import List

import petl as etl
import sqlite3
import os
import tarfile


def _string_agg(key, rows):
    return [key, "|".join(row[1] for row in rows)]


def _cut_left_join(ltable, rtable, field, attribute):
    return etl.leftjoin(ltable,
                 (etl.cut(rtable, ['id', attribute]).rename(attribute, f"{field}_{attribute}")),
                 lkey=field,
                 rkey="id")

def add_closure(node_file: str,
                edge_file: str,
                kg_archive: str,
                closure_file: str,
                path: str,
                fields: List[str],
                output_file: str):

    print("Generating closure KG...")
    print(f"node_file: {node_file}")
    print(f"edge_file: {edge_file}")
    print(f"kg_archive: {kg_archive}")
    print(f"closure_file: {closure_file}")
    print(f"fields: {','.join(fields)}")
    print(f"output_file: {output_file}")

    tar = tarfile.open(f"{path}/{kg_archive}")
    tar.extract(node_file, path=path)
    tar.extract(edge_file, path=path)

    # add paths, so that steps below can find the file
    node_file = f"{path}/{node_file}"
    edge_file = f"{path}/{edge_file}"

    # db = "closurizer.db"

    # if os.path.exists(db):
    #     os.remove(db)
    # sqlite = sqlite3.connect(db)

    nodes = etl.fromtsv(node_file)
    nodes = etl.addfield(nodes, 'namespace', lambda rec: rec['id'][:rec['id'].index(":")])
    # etl.todb(nodes, sqlite, "nodes", create=True)

    edges = etl.fromtsv(edge_file)

#    for field in fields:
        # edges = etl.addfield(edges, f"{field}_namespace")
        # edges = etl.addfield(edges, f"{field}_category")
        # edges = etl.addfield(edges, f"{field}_closure")
        # edges = etl.addfield(edges, f"{field}_label")
        # edges = etl.addfield(edges, f"{field}_closure_label")


    # Load the relation graph tsv in long format mapping a node to each of it's ancestors
    closure_table = (etl
                     .fromtsv(closure_file)
                     .setheader(['id', 'predicate', 'ancestor'])
                     .cutout('predicate')  # assume all predicates for now
                     )
    print("closure table")
    print(etl.head(closure_table))
    # Prepare the closure id table, mapping node IDs to pipe separated lists of ancestors
    closure_id_table = (etl.rowreduce(closure_table, key='id',
                                      reducer=_string_agg,
                                      header=['id', 'ancestors'])
                        .rename('ancestors', 'closure'))
    print("closure_id_table")
    print(etl.head(closure_id_table))

    # Prepare the closure label table, mapping node IDs to pipe separated lists of ancestor names
    closure_label_table = (etl.leftjoin(closure_table,
                                        etl.cut(nodes, ["id", "name"]),
                                        lkey="ancestor",
                                        rkey="id")
                           .cutout("ancestor")
                           .rename("name", "closure_label")
                           .selectnotnone("closure_label")
                           .rowreduce(key='id', reducer=_string_agg, header=['id', 'ancestor_labels'])
                           .rename('ancestor_labels', 'closure_label'))
    print("closure_label_table")
    print(etl.head(closure_label_table))

    for field in fields:
        # I don't think this was having an effect previously
        # edges = etl.leftjoin(edges, closure_id_table, lkey=field, rkey="id")
        for attribute in ['namespace', 'category']:
            edges = _cut_left_join(edges, nodes, field, attribute)
        edges = _cut_left_join(edges, closure_id_table, field, "closure")
        edges = _cut_left_join(edges, closure_label_table, field, "closure_label")
        edges = etl.leftjoin(edges, (etl.cut(nodes, ["id", "name"]).rename("name", f"{field}_label")), lkey=field, rkey="id")
    print("edges table")
    print(etl.head(edges))
#    etl.todb(edges, sqlite, "edges", create=True)
    etl.totsv(edges, f"{path}/petl_edges.tsv")
    # cur = sqlite.cursor()

#     for field in fields:

        # cur.execute(f"""
        # update edges
        # set {field}_namespace = nodes.namespace
        # from nodes
        # where edges.{field} = nodes.id;
        # """)

        # cur.execute(f"""
        # update edges
        # set {field}_category = nodes.category
        # from nodes
        # where edges.{field} = nodes.id;
        # """)

        # cur.execute(f"""
        # update edges
        # set {field}_closure = ancestors
        # from closure
        # where edges.{field} = closure.id;
        # """)

        # cur.execute(f"""
        # update edges
        # set {field}_label = nodes.name
        # from nodes
        # where edges.{field} = nodes.id;
        # """)

        # cur.execute(f"""
        # update edges
        # set {field}_closure_label = closure_label.ancestor_labels
        # from closure_label
        # where edges.{field} = closure_label.id;
        # """)

#    etl.fromdb(sqlite, 'select * from edges').totsv(f"{path}/{output_file}")

    # Clean up the database
#    if os.path.exists(db):
#        os.remove(db)

    # Clean up extracted node & edge files
    if os.path.exists(f"{path}/{node_file}"):
        os.remove(f"{path}/{node_file}")
    if os.path.exists(f"{path}/{edge_file}"):
        os.remove(f"{path}/{edge_file}")
