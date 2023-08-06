from askdata import human2query
from askdata.smartquery import SmartQuery, Query, Field, Condition, Sorting, SQLSorting, SQLOperator, TimeOperator, \
    BooleanOperator, CompositeCondition

if __name__ == "__main__":

    # Query2SQL
    smartquery = SmartQuery(
        queries=[
            Query(
                fields=[
                    Field(aggregation="SUM", column="{{measure.A}}", alias="{{measAlias.A}}",
                          internalDataType="NUMERIC",
                          sourceDataType="INT64"),
                    Field(column="{{dimension.A}}", alias="{{dimAlias.A}}",
                          internalDataType="STRING",
                          sourceDataType="VARCHAR"),
                    Field(aggregation="YEAR", column="{{timeDimension.A}}", alias="{{timeDimAlias.A}}",
                          internalDataType="DATE",
                          sourceDataType="DATE")
                ],
                where=[
                    CompositeCondition(conditions=[
                        Condition(field=Field(column="{{dimension.A}}", alias="{{dimAlias.A}}",
                                              internalDataType="STRING",
                                              sourceDataType="VARCHAR"), operator=SQLOperator.IN,
                                  value=["{{entity.A}}", "{{entity.A}}"]),
                        Condition(field=Field(aggregation="YEAR", column="{{timeDimension.A}}", alias="{{timeDimAlias.A}}",
                                              internalDataType="DATE",
                                              sourceDataType="DATE"), operator=TimeOperator.RANGE,
                                  value=["{{timePeriodStart.A}}", "{{timePeriodEnd.A}}"])
                    ], operator=BooleanOperator.AND)

                ],
                orderBy=[
                    Sorting(field="{{timeDimension.A}}", order=SQLSorting.DESC)
                ],
                limit=6
            )
        ]
    )

    response = human2query.query2sql(smartquery=smartquery, driver="MySQL")
    print(response)
    response = human2query.complex_field_calculator(smartquery=smartquery, driver="MySQL")
    print(response)
    response = human2query.complex_filter_calculator(smartquery=smartquery, driver="MySQL")
    print(response)
