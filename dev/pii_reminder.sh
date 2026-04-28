#!/usr/bin/env bash
# Manual PII review reminder for pre-commit. The structured PII checker
# (dev/check_pii.py) catches patterns — emails, CPF, SSN, phones, cards.  # pii:allow
# Contextual PII slips through and must be caught by reading the diff:
# real names, region-specific company names, geographic indicators,
# account paths, anything that ties to the user.

echo
echo "  PII reminder: structured patterns checked. Review the diff for"
echo "  contextual PII before pushing — real names, company names,"
echo "  region-specific identifiers, account paths, anything tied to"
echo "  the user."
echo
