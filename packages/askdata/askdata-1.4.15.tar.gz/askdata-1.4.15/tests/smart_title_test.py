from askdata.smartgraph import smart_title

if __name__ == "__main__":
    smartquery = {"components": [{"type": "chart", "queryId": "q0", "chartType": "LINE"}],
                  "queries": [{"datasets": [], "fields": [
                      {"aggregation": "MAX", "column": "totale_casi", "internalDataType": "NUMERIC"},
                      {"aggregation": "AVG", "column": "deceduti", "internalDataType": "NUMERIC"},
                      {"column": "denominazione_regione", "internalDataType": "STRING"},
                      {"column": "monthly", "internalDataType": "DATE"}], "id": "q0", "limit": "3",
                               "where": [{"field": {"column": "deceduti"}, "operator": "GOE", "value": ["30"]},
                                         {"field": {"column": "denominazione_regione"}, "operator": "IN",
                                          "negate": True, "value": ["Lazio"]},
                                         {"field": {"column": "monthly"}, "operator": "RANGE",
                                          "value": ["2020-07-13", "2020-10-16"]},
                                         {"field": {"column": "monthly"}, "operator": "RANGE", "direction": "CURR",
                                          "steps": "2"}]}]}
    metadata = {"totale_casi": "Totale casi", "deceduti": "Deceduti", "denominazione_regione": "Regione",
                "monthly": "Monthly"}
    title = smart_title(smartquery=smartquery, metadata=metadata, lang="en-US", update=False)
    print(title)
    title = smart_title(smartquery=smartquery, metadata=metadata, lang="en-US", update=True)
    print(title)
