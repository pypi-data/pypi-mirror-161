from askdata.human2query import nl2query

if __name__ == "__main__":
    nl = 'frotok {{timePeriods.timePeriodA.value}} {{measures.measureA.name}} {{measures.measureB.name}} {{timeDimensions.timeDimensionA.value}} limit by {{numbers.numberA.value}} lines associated with {{measures.measureA.name}} in from {{numbers.numberB.value}} to as {{numbers.numberC.value}} when {{entityTypes.entityTypeA.name}} by {{timeDimensions.timeDimensionB.value}} limited {{numbers.numberD.value}}'
    smartquery, version = nl2query(nl, language="en-US")
    print(smartquery)
    print(version)
