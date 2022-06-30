import rule_engine

rules_dict = {
    'movimento-tra-conti': '"trasferim.tra conti" in causale',
    'ricarica-carta-prepagata': '"ricarica carta" in causale',
    'stipendio': '"stipendi" in causale'
}


def preproc(batch):
    for it in batch:
        for field in it:
            if type(it[field]) == str:
                it[field] = it[field].lower()
    return batch


class RuleEngine:

    def __init__(self, label, rule):
        self.rule = rule
        self.label = label

    def filter(self, batch):
        reng = rule_engine.Rule(self.rule)
        return reng.filter(batch)

    def predict(self, batch):
        filtered_batch = self.filter(batch)
        for trx in filtered_batch:
            trx['labels'].append(self.label)


def rule_engine_test(batch):

    batch = preproc(batch)

    categorizer = []
    for l in rules_dict:
        categorizer.append(RuleEngine(l, rules_dict[l]))

    for it in categorizer:
        it.predict(batch)

    return batch


if __name__ == "__main__":
    rule_engine_test([{'causale': 'ristorante', 'labels': []},
                      {'causale': 'trasferimento a conto', 'labels': []},
                      {'causale': 'ricarica carta', 'labels': []}])
