import argparse
from pprint import pprint
import yaml


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Calculate how much each person owes each other person."
    )
    parser.add_argument(
        "file", type=str, help="Path to the YAML file containing the payments."
    )
    parser.add_argument(
        "--payup",
        action="store_true",
        help="Calculate how much each person should pay each other.",
    )
    return parser.parse_args()


def payup(ledger):
    debtors = {}
    for pig in ledger:
        for payment_set in ledger[pig]:
            payees = payment_set["for"]
            payments = payment_set["payments"].items()
            num_payees = len(payees)

            #   sum up debts owed by each payee to each pig
            for item, price in payments:
                for payee in payees:
                    if payee == pig:  #   cannot owe self
                        continue

                    # make sure each debtor-debtee relationship exists:
                    if payee not in debtors:
                        debtors[payee] = {}
                    if pig not in debtors[payee]:
                        debtors[payee][pig] = 0

                    debtors[payee][pig] += price / num_payees

    # simplify debts, if ben owes gibson 1000 and gibson owes ben 500, then gibson owes ben 500, and ben owes gibson 0
    for debtor in debtors:
        for debtee in debtors[debtor]:
            if debtee in debtors and debtor in debtors[debtee]:
                if debtors[debtor][debtee] > debtors[debtee][debtor]:
                    debtors[debtor][debtee] -= debtors[debtee][debtor]
                    debtors[debtee][debtor] = 0
                else:
                    debtors[debtee][debtor] -= debtors[debtor][debtee]
                    debtors[debtor][debtee] = 0

    # remove empty debts
    for debtor in list(debtors):
        for debtee in list(debtors[debtor]):
            if debtors[debtor][debtee] == 0:
                del debtors[debtor][debtee]
        if len(debtors[debtor]) == 0:
            del debtors[debtor]

    ####    print things nicely     ####
    # calculate longest name
    longest_name_length = 0
    all_names = []
    for debtor in debtors:
        all_names.append(debtor)
        for debtee in debtors[debtor]:
            all_names.append(debtee)
    longest_name_length = max([len(name) for name in all_names])

    # print debts
    for debtor in debtors:
        debtor_colored_name = get_colored_string(debtor)
        print(f"{debtor_colored_name} owes")
        for debtee in debtors[debtor]:
            debtee_colored_name = get_colored_string(debtee)
            numstr = f"{debtors[debtor][debtee]:.2f}"
            p = (
                debtee_colored_name
                + " "
                * (
                    longest_name_length
                    + 2
                    + 20
                    - len(debtee_colored_name)
                    - len(numstr)
                )
                + numstr
            )
            print(f"\t{p}")


def get_colored_string(string):
    # pick an n based on the string
    n = sum([ord(char) for char in string]) % 6
    return f"\033[3{n+1}m{string}\033[0m"


def main():
    args = parse_arguments()
    with open(args.file, "r") as file:
        ledger = yaml.safe_load(file)
    if args.payup:
        payup(ledger)


if __name__ == "__main__":
    main()
