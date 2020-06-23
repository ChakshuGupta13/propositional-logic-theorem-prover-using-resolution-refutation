LOGICAL_OPERATORS = ['!', '&', '|', '>', '=', '(', ')']

def is_propositional_op(op):
    return op in LOGICAL_OPERATORS


def segment_sentence(sentence):
    segmented_sentence = []

    i = 0
    L = len(sentence)

    while i < L:
        if is_propositional_op(sentence[i]):
            segmented_sentence.append(sentence[i])
            i += 1
        elif sentence[i] == " ":
            i += 1
        else:
            literal = ""
            while i < L and not is_propositional_op(sentence[i]) and sentence[i] != " ":
                literal += sentence[i]
                i += 1
            segmented_sentence.append(literal)

    return segmented_sentence


def forward_slice(sentence, index):
    sentence_slice = []

    off_balance = 0

    L = len(sentence)

    while index < L:
        sentence_slice.append(sentence[index])

        if sentence[index] == "(":
            off_balance += 1
        elif sentence[index] == ")":
            off_balance -= 1

        if off_balance == 0 and sentence[index] != "!":
            break

        index += 1
    
    assert off_balance == 0

    return sentence_slice, index


def backward_slice(sentence):
    sentence_slice = []
    
    off_balance = 0

    i = len(sentence) - 1

    while i >= 0:
        sentence_slice.insert(0, sentence[i])

        if sentence[i] == ")":
            off_balance += 1
        elif sentence[i] == "(":
            off_balance -= 1
        
        sentence.pop()

        if off_balance == 0:
            if i > 0 and sentence[i - 1] == "!":
                i -= 1
                sentence_slice.insert(0, sentence[i])
                sentence.pop()

            break
        
        i -= 1

    assert off_balance == 0

    return sentence_slice, sentence


def around_unary_op(sentence, op):
    processed_sentence = []

    i = 0
    L = len(sentence)

    while i < L:
        if sentence[i] == op:
            i += 1

            sentence_slice, i = forward_slice(sentence, i)
            sentence_slice = around_unary_op(sentence_slice, op)

            processed_sentence.append("(")
            processed_sentence.append("!")
            processed_sentence += sentence_slice.copy()
            processed_sentence.append(")")
        else:
            processed_sentence.append(sentence[i])
        
        i += 1

    return processed_sentence


def around_binary_op(sentence, op):
    processed_sentence = []

    i = 0
    L = len(sentence)

    while i < L:
        if sentence[i] == op:
            A, processed_sentence = backward_slice(processed_sentence)
            A = around_binary_op(A, op)
            
            i += 1
            assert i < L

            sentence_slice, i = forward_slice(sentence, i)
            sentence_slice = around_binary_op(sentence_slice, op)

            processed_sentence.append("(")
            processed_sentence += A.copy()
            processed_sentence.append(op)
            processed_sentence += sentence_slice.copy()
            processed_sentence.append(")")
        else:
            processed_sentence.append(sentence[i])
        
        i += 1

    return processed_sentence


def induce_parenthesis(sentence):
    sentence = around_unary_op(sentence, "!")
    sentence = around_binary_op(sentence, "&")
    sentence = around_binary_op(sentence, "|")
    sentence = around_binary_op(sentence, ">")
    sentence = around_binary_op(sentence, "=")
    return sentence


def literal_not_protected(sentence):
    contain_op = False
    
    for i in sentence:
        if is_propositional_op(i):
            contain_op = True
            break

    if not contain_op:
        return False

    off_balance = 0

    i = 0
    L = len(sentence)

    while i < L:
        if sentence[i] == "(":
            off_balance += 1
        elif sentence[i] == ")":
            off_balance -= 1
        elif off_balance == 0:
            return True

        i += 1

    return False


def remove_extra_parenthesis(sentence):
    processed_sentence = []
    
    i = 0
    L = len(sentence)
    brackets = []
    content = []

    while i < L:
        if sentence[i] == "(":
            content.append(processed_sentence.copy())
            brackets.append("(")
            
            processed_sentence.clear()
        elif sentence[i] == ")":
            if literal_not_protected(processed_sentence):
                processed_sentence.insert(0, "(")
                processed_sentence.append(")")

            processed_sentence = content[len(content) - 1].copy() + processed_sentence
            
            brackets.pop()
            content.pop()
        else:
            processed_sentence.append(sentence[i])
        
        i += 1

    return processed_sentence


def iff_equivalent(A, B):
    equivalent = []

    equivalent.append("(")

    equivalent.append("(")
    equivalent += A.copy()
    equivalent.append(">")
    equivalent += B.copy()
    equivalent.append(")")
    
    equivalent.append("&")
    
    equivalent.append("(")
    equivalent += B.copy()
    equivalent.append(">")
    equivalent += A.copy()
    equivalent.append(")")

    equivalent.append(")")

    return equivalent


def implies_equivalent(A, B):
    equivalent = []

    equivalent.append("(")
    
    equivalent.append("(")
    equivalent.append("!")
    equivalent += A.copy()
    equivalent.append(")")
    
    equivalent.append("|")
    
    equivalent += B.copy()
    
    equivalent.append(")")

    return equivalent


def eliminate_op(sentence, op):
    assert op == "=" or op == ">"

    processed_sentence = []
    
    i = 0
    L = len(sentence)

    while i < L:
        if sentence[i] == op:
            A, processed_sentence = backward_slice(processed_sentence)

            i += 1
            assert i < L

            B, i = forward_slice(sentence, i)

            equivalent = []
            if op == "=":
                A = eliminate_op(A, "=")
                B = eliminate_op(B, "=")
                equivalent = iff_equivalent(A, B)
            elif op == ">":
                A = eliminate_op(A, ">")
                B = eliminate_op(B, ">")
                equivalent = implies_equivalent(A, B)

            processed_sentence += equivalent.copy()
        else:
            processed_sentence.append(sentence[i])

        i += 1

    return processed_sentence


def move_not_inwards(sentence):
    processed_sentence = []

    while True:
        processed_sentence = []

        i = 0
        L = len(sentence)
        
        while i < L:
            if sentence[i] == "!":
                i += 1
                assert i < len(sentence)

                B, i = forward_slice(sentence, i)

                if B[0] == "(":
                    processed_sentence.append("(")

                    j = 1
                    N = len(B)

                    while j < N:
                        tmp, j = forward_slice(B, j)

                        if tmp[0] == "!":
                            tmp.pop(0)
                        else:
                            tmp.insert(0, "!")

                        processed_sentence += tmp.copy()

                        j += 1
                        if j < len(B) - 1:
                            if B[j] == "|":
                                processed_sentence.append("&")
                            elif (B[j] == "&"):
                                processed_sentence.append("|")
                            else:
                                assert B[j] == "|" or B[j] == "&"

                        j += 1

                    processed_sentence.append(")")
                else:
                    if B[0] == "!":
                        B.pop(0)
                    else:
                        processed_sentence.append("!")

                    processed_sentence += B.copy()
            else:
                processed_sentence.append(sentence[i])
            
            i += 1
        
        if processed_sentence != sentence:
            sentence = processed_sentence
        else:
            break

    return processed_sentence


def distribute_or_over_and(sentence):
    processed_sentence = []

    i = 0
    L = len(sentence)
    while i < L:
        if sentence[i] == "|":
            A, processed_sentence = backward_slice(processed_sentence)
            A = distribute_or_over_and(A)
            
            tmp3 = []
            if A[0] == "(":
                j = 1
                N = len(A) - 1
                while j < N:
                    tmp, j = forward_slice(A, j)
                    tmp3.append(tmp.copy())
                    j += 2
            else:
                tmp3.append(A.copy())

            i += 1
            assert i < len(sentence)

            B, i = forward_slice(sentence, i)
            B = distribute_or_over_and(B)
            
            tmp2 = []
            if B[0] == "(":
                j = 1
                N = len(B) - 1
                while j < N:
                    tmp, j = forward_slice(B, j)
                    tmp2.append(tmp.copy())
                    j += 2
            else:
                tmp2.append(B.copy())

            k = 0
            N = len(tmp2)
            while k < N:
                m = 0
                M = len(tmp3)
                while m < M:
                    processed_sentence.append("(")
                    processed_sentence += tmp3[m].copy()
                    processed_sentence.append("|")
                    processed_sentence += tmp2[k].copy()
                    processed_sentence.append(")")

                    if m != len(tmp3) - 1:
                        processed_sentence.append("&")
                    m += 1

                if k != len(tmp2) - 1:
                    processed_sentence.append("&")                
                k += 1
        else:
            processed_sentence.append(sentence[i])
        
        i += 1

    return processed_sentence


def print_sentence(sentence):
    for i in sentence:
        print(i, end="")
    print()


def eliminate_invalid_parenthesis(sentence):
    processed_sentence = []
    brackets = []
    content = []
    
    i = 0
    L = len(sentence)
    while i < L:
        if sentence[i] == "(":
            content.append(processed_sentence.copy())
            brackets.append("(")
            processed_sentence.clear()
        elif sentence[i] == ")" and len(content) != 0:
            processed_sentence.insert(0, "(")
            processed_sentence.append(")")
            
            processed_sentence = content[len(content) - 1].copy() + processed_sentence
            
            brackets.pop()
            content.pop()
        else:
            processed_sentence.append(sentence[i])
        i += 1

    return processed_sentence


def split_around_and(sentence):
    processed_sentence = []
    tmp = []

    i = 0
    L = len(sentence)
    while i < L:
        if sentence[i] == "&":
            tmp2 = eliminate_invalid_parenthesis(tmp)
            tmp3 = []
            if tmp2[0] == "(":
                tmp3.append("(")
                
                j = 1
                N = len(tmp2) - 1
                while j < N:
                    if tmp2[j] != "(" and tmp2[j] != ")":
                        tmp3.append(tmp2[j])
                    j += 1
                tmp3.append(")")
            else:
                j = 0
                N = len(tmp2)
                while j < N:
                    if tmp2[j] != "(" and tmp2[j] != ")":
                        tmp3.append(tmp2[j])
                    j += 1
            processed_sentence += tmp3.copy()
            processed_sentence.append("&")
            tmp.clear()
        else:
            tmp.append(sentence[i])
        
        i += 1
    
    tmp2 = eliminate_invalid_parenthesis(tmp)
    tmp3 = []
    if tmp2[0] == "(":
        tmp3.append("(")
        
        j = 1
        N = len(tmp2) - 1
        while j < N:
            if tmp2[j] != "(" and tmp2[j] != ")":
                tmp3.append(tmp2[j])
            j += 1
        tmp3.append(")")
    else:
        j = 0
        N = len(tmp2)
        while j < N:
            if tmp2[j] != "(" and tmp2[j] != ")":
                tmp3.append(tmp2[j])
            j += 1
    processed_sentence += tmp3.copy()
    tmp.clear()

    return processed_sentence


def CNF(sentence):
    sentence = eliminate_op(sentence, "=")
    sentence = remove_extra_parenthesis(sentence)
    sentence = eliminate_op(sentence, ">")
    sentence = remove_extra_parenthesis(sentence)
    sentence = move_not_inwards(sentence)
    sentence = remove_extra_parenthesis(sentence)
    
    prev = []
    while prev != sentence:
        prev = sentence
        sentence = distribute_or_over_and(sentence)
        sentence = remove_extra_parenthesis(sentence)
    
    sentence = split_around_and(sentence)
    return sentence


def clause_map(sentence):
    m = {}
    if sentence[0] == "(":
        j = 1
        while j < len(sentence) - 1:
            literal, j = forward_slice(sentence, j)
            if literal[0] == "!":
                m[literal[1]] = True
            else:
                m[literal[0]] = False
            j += 2
    else:
        j = 0
        while j < len(sentence):
            literal, j = forward_slice(sentence, j)
            if literal[0] == "!":
                m[literal[1]] = True
            else:
                m[literal[0]] = False
            j += 2
    return m


def print_dict(dict):
    for key in dict:
        if dict[key]:
            print("!", end="")
        print(key, end=" ")


def resolve(sentence, mode):
    if mode:
        print("Clauses <- The set of clauses in the CNF representation of (KB & !Q)")
        print("Clauses:")
    
    clauses = []
    tmp = []
    i = 0
    while i < len(sentence):
        if sentence[i] == "&":
            if mode:
                print_sentence(tmp)
            
            clauses.append(clause_map(tmp))
            tmp.clear()
        else:
            tmp.append(sentence[i])
        i += 1
    if mode:
        print_sentence(tmp)
    
    clauses.append(clause_map(tmp))
    tmp.clear()

    new_clauses = []
    if mode:
        print("new <- {}")

    while True:
        if mode:
            print("For each pair of clauses Ci, Cj in clauses do:")
        
        i = 0
        while i < len(clauses):
            j = i + 1
            while j < len(clauses):
                resolvent = {}
                for var in clauses[i]:
                    if var not in clauses[j]:
                        resolvent[var] = clauses[i][var]
                    elif clauses[j][var] == clauses[i][var]:
                        resolvent[var] = clauses[i][var]
                
                for var in clauses[j]:
                    if var not in clauses[i]:
                        resolvent[var] = clauses[j][var]
                    elif clauses[i][var] == clauses[j][var]:
                        resolvent[var] = clauses[j][var]

                if mode:
                    print("\t", end="")
                    print_dict(resolvent)
                    print(" <- PL-RESOLVE(", end="")
                    print_dict(clauses[i])
                    print(", ", end="")
                    print_dict(clauses[j])
                    print(")")

                if not bool(resolvent):
                    if mode:
                        print("\tIf resolvents contains the empty clause then return true.")
                    return True

                if mode:
                    print("\tnew <- new ∪ resolvents")
                
                already_present = False
                for k in new_clauses:
                    if k == resolvent:
                        already_present = True
                        break
                
                if not already_present:
                    new_clauses.append(resolvent)
                
                j += 1
            i += 1

        is_subset = True
        for i in new_clauses:
            found = False
            for j in clauses:
                if i == j:
                    found = True
                    break
            if not found:
                is_subset = False
        
        if is_subset:
            if mode:
                print("if new ⊆ clauses then return false")
            
            return False

        if mode:
            print("clauses <- clauses ∪ new")
        
        for i in new_clauses:
            found = False
            for j in clauses:
                if i == j:
                    found = True
                    break
            if not found:
                clauses.append(i)


def get_sentence():
    """
    Returns the one-line input after removing '\n'
    """
    return input().splitlines()[0]


def vet_sentence(sentence):
    """
    Returns the sentence in CNF

    @param sentence
    : Propositional Sentence or Formula
    """
    sentence = segment_sentence(sentence)
    sentence = induce_parenthesis(sentence)
    sentence = remove_extra_parenthesis(sentence)
    return CNF(sentence)


def main():
    n, m = input().split()
    n = int(n)
    m = int(m)

    knowledge_base = []
    for i in range(0, n):
        sentence = vet_sentence(get_sentence())
        
        knowledge_base += sentence.copy()
        if i != n - 1:
            knowledge_base.append("&")

    query = vet_sentence(get_sentence())

    rub = []
    if len(knowledge_base) > 0:
        rub = knowledge_base.copy()
        rub.append("&")
        rub.append("(")
        rub.append("!")
        rub += query.copy()
        rub.append(")")
    else:
        rub.append("!")
        rub += query.copy()

    if len(rub):
        rub = induce_parenthesis(rub)
        rub = remove_extra_parenthesis(rub)
        rub = CNF(rub)

        if resolve(rub, m):
            print("1")
        else:
            print("0")

main()