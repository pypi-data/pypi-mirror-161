from fwhunt_scan import UefiAnalyzer, UefiRule, UefiScanner

rule_path = "test/rules/variants.yml"
rule = UefiRule(rule_path=rule_path)
for variant in rule.variants:
    code = rule.variants[variant].code
    print(variant, code)
