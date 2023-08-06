import requests


def search_by_sequence(
    seq,
    evalue_cutoff=1,
    identity_cutoff=0.9,
    polymer="protein",
    return_type="polymer_entity",
    top_n=10,
):
    polymer_map = {
        "protein": "pdb_protein_sequence",
        "dna": "pdb_dna_sequence",
        "rna": "pdb_rna_sequence",
    }
    query = {
        "query": {
            "type": "terminal",
            "service": "sequence",
            "parameters": {
                "evalue_cutoff": evalue_cutoff,
                "identity_cutoff": identity_cutoff,
                "target": polymer_map[polymer],
                "value": seq,
            },
        },
        "request_options": {
            "scoring_strategy": "sequence",
            "pager": {"start": 0, "rows": top_n},
        },
        "return_type": return_type,
    }

    res = requests.post("https://search.rcsb.org/rcsbsearch/v1/query", json=query)
    if res.ok:
        new_res = []
        for rr in res.json()["result_set"]:
            match_ctx = rr["services"][0]["nodes"][0]["match_context"][0]
            newdict = {"identifier": rr["identifier"]}
            newdict.update(match_ctx)
            new_res.append(newdict)
        return new_res
