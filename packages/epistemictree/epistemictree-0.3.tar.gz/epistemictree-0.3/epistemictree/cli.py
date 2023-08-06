from epistemictree import rules
import argparse

def run():
    parser = argparse.ArgumentParser(description="Creating your own model")
    parser.add_argument("-f", "--formula", help="List of formulas", required=True)
    parser.add_argument("-s", "--system", type=str, help="System(k, kt, kt4, k4)", required=True, choices=['k', 'kt', 'kt4', 'k4'])
    parser.add_argument("-o", "--output", type=str, help="Path to save your imgs")
    parser.add_argument("-c", "--closure", help="Makes clousure", action='store_true')
    args = parser.parse_args()

    list_formulas = args.formula.split(',')
    rules.epistemic_tableau(list_formulas, args.system, args.output, args.closure)

