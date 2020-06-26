# Propositional Logic Theorem Prover using Resolution-Refutation
[![Build Status](https://travis-ci.com/ChakshuGupta13/propositional-logic-theorem-prover-using-resolution-refutation.svg?token=Fb5MFGC1Visp8xhxeRu4&branch=master)](https://travis-ci.com/ChakshuGupta13/propositional-logic-theorem-prover-using-resolution-refutation)

Method `main` in `main.py` is responsible for taking Knowledge Base (i.e., formulae) and Query as input and implement a refutation proof (by first converting the given formulae into CNF), and report the result (1 if the query holds, and 0 otherwise). Additionally, the program have an option to print the resolution steps used in the proof.

## Input Format

- First line contains two integer value 'n' the number of formulae and 'm' the mode.
- Followed by the formulae (propositional sentences) in the next 'n' lines.
- Last line would contain the propositional sentence that needs to be proved.
- We will use the following characters for different operators/symbols:
  - OR : |
  - AND : &
  - NOT : !
  - IMPLIES : >
  - IFF (bidirectional) : =
  - OPENING BRACKET : (
  - CLOSING BRACKET : )
