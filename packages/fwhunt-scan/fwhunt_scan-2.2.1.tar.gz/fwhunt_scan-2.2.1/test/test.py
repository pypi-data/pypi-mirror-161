import glob
from typing import List

import click

from fwhunt_scan import UefiAnalyzer, UefiRule, UefiScanner

# images = glob.glob("test/S15_02050100.bin.out/*")
images = glob.glob("test/S74_01070000.bin.out/*")
rules_yml = glob.glob("rules/*.yml")

prefix = click.style("Scanner result", fg="green")
no_threat = click.style("No threat detected", fg="green")
threat = click.style("FwHunt rule has been triggered and threat detected!", fg="red")

# init rules
uefi_rules_all: List[UefiRule] = list()
for rule in rules_yml:
    with open(rule, "r") as f:
        rule_content = f.read()

    rule = UefiRule(rule_content=rule_content)
    uefi_rules_all.append(rule)

for image_path in images:

    uefi_rules: List[UefiRule] = list()
    for rule in uefi_rules_all:
        for guid in rule.volume_guids:
            if guid.lower() in image_path:
                uefi_rules.append(rule)

    if not uefi_rules:
        continue

    # init analyzer
    uefi_analyzer = UefiAnalyzer(image_path=image_path)

    # init scanner
    scanner = UefiScanner(uefi_analyzer, uefi_rules)
    for result in scanner.results:
        print(result.rule.name, result.variant_label, result.res)

    uefi_analyzer.close()
