from gmaps_scraper import GmapsScraper
import rule_engine

# TODO: doctstrings
# TODO: keep track of businesses matched in a json file
# TODO: cluster Google types

RULES = {
    'accounts-movement': '"trasferim.tra conti" in causale',
    'prepaid-card-recharge': '"ricarica carta" in causale',
    'salary': '"stipendi" in causale',
    'atm-withdrawal': '"atm" in canale'
}

BUSINESS_RULE = '"pagobancomat" in causale or "maestro" in causale'


class RuleMatcher:

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


class BusinessMatcher:

    def __init__(self, rule=BUSINESS_RULE):
        self.rule = rule
        self.scraper = GmapsScraper()

    def filter(self, batch):
        reng = rule_engine.Rule(self.rule)
        return reng.filter(batch)

    def predict(self, batch):
        filtered_batch = self.filter(batch)
        self.scraper.start()  # TODO: replace with context manager
        for trx in filtered_batch:
            query = trx['causale'].split('-')[-1]
            trx['gmaps_type'] = self.scraper.get_gmaps_type(query)
        self.scraper.stop()


class Categorizer:

    def __init__(self, rules=RULES):
        self.models = []
        for r in rules:
            self.models.append(RuleMatcher(r, RULES[r]))
        self.models.append(BusinessMatcher())

    @staticmethod
    def preproc(batch):
        for it in batch:
            for field in it:
                if type(it[field]) == str:
                    it[field] = it[field].lower()
        return batch

    def predict(self, batch):
        batch = Categorizer.preproc(batch)
        for m in self.models:
            m.predict(batch)
        return batch


def rule_engine_test(batch):
    cat = Categorizer()
    batch_pred = cat.predict(batch)
    return batch_pred


if __name__ == "__main__":
    rule_engine_test([{'causale': 'ristorante', 'labels': []},
                      {'causale': 'trasferimento a conto', 'labels': []},
                      {'causale': 'ricarica carta', 'labels': []}])
