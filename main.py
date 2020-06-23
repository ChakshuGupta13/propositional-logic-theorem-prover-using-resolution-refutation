PROPOSITIONAL_OPERATORS = ['!', '&', '|', '>', '=', '(', ')']

def is_propositional_op(op):
    """
    Returns whether op is propositional operator or not.

    @param op (str)
    : Operator
    """
    return op in PROPOSITIONAL_OPERATORS


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
    """
    Returns forward slice of sentence begining from index.

    Let us define forward slice as next complete segment in sentence.
    Examples:
        Forward Slice from index = 2 of "A(B(!C&D))" is "(B(!C&D))"
        Forward Slice from index = 3 of "A(B(!C&D))" is "B"
        Forward Slice from index = 4 of "A(B(!C&D))" is "(!C&D)"
        Forward Slice from index = 5 of "A(B(!C&D))" is "!C"
    
    @param sentence (list)
    : Propositional Sentence or Formula
    @param index (int)
    : Index from which slicing should begin (included)
    """
    off_balance = 0
    i = index

    while i < len(sentence):
        off_balance += 1 if sentence[i] == '(' else -1 if sentence[i] == ')' else 0
        if off_balance == 0 and sentence[i] != "!":
            return sentence[index : (i + 1)], i
        i += 1


def backward_slice(sentence):
    """
    Returns backward slice of sentence.

    Let us define backward slice as previous complete segment in sentence.
    Examples:
        Backward Slice of "A(B(!C&D))" is "(B(!C&D))"
        Backward Slice of "B(!C&D)" is "(!C&D)"
        Backward Slice of "!C&D" is "D"
        Backward Slice of "!C" is "!C"
    
    @param sentence (list)
    : Propositional Sentence or Formula
    """
    off_balance = 0
    L = len(sentence)
    i = L - 1

    while i >= 0:
        off_balance += 1 if sentence[i] == ')' else -1 if sentence[i] == '(' else 0
        if off_balance == 0:
            i -= 1 if i > 0 and sentence[i - 1] == "!" else 0
            return sentence[i : L], sentence[0 : i]
        i -= 1


def around_unary_op(sentence, op):
    processed_sentence = []

    i = 0
    L = len(sentence)

    while i < L:
        if sentence[i] == op:
            i += 1

            sentence_slice, i = forward_slice(sentence, i)
            sentence_slice = around_unary_op(sentence_slice, op)

            processed_sentence += ['(', '!'] + sentence_slice.copy() + [')']
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

            processed_sentence += ['('] + A.copy() + [op] + sentence_slice.copy() + [')']
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
    """
    Returns ((A>B)&(B>A)) as equivalent of (A=B).

    @param A (list), B (list)
    : Propositonal Sentences or Formulae
    """
    return ['(', '('] + A.copy() + ['>'] + B.copy() + [')', '&', '('] + B.copy() + ['>'] + A.copy() + [')', ')']


def implies_equivalent(A, B):
    """
    Returns ((!A)|B) as equivalent of (A>B).

    @param A (list), B (list)
    : Propositonal Sentences or Formulae
    """
    return ['(', '(', '!'] + A.copy() + [')', '|'] + B.copy() + [')']


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

            A = eliminate_op(A, op)
            B = eliminate_op(B, op)
            processed_sentence += (iff_equivalent(A, B) if op == '=' else implies_equivalent(A, B)).copy()
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
    """
    Prints the segmented segment as str.

    @param sentence (list)
    : Segmented Propositional Sentence or Formula
    """
    print(''.join(sentence))


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
    """
    Returns Conjunctive Normal Form (CNF) of the sentence.

    @param sentence (list)
    : Propositional Sentence or Formula
    """

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
    
    return split_around_and(sentence)


def clause_map(sentence):
    """
    Returns a map where keys are literals in sentence
    and value is True if they are negated and False otherwise.

    @param sentence (list)
    : Propositional Sentence or Formula in CNF
    : Format : (A|B|...|Z) where literal like A, B, ..., Z can be negated.
    """
    m = {}
    j = 1 if sentence[0] == '(' else 0
    L = len(sentence) - 1 if sentence[0] == '(' else len(sentence)
    while j < L:
        literal, j = forward_slice(sentence, j)
        if literal[0] == "!":
            m[literal[1]] = True
        else:
            m[literal[0]] = False
        # [NOTE] 'j' is incremented by 2 to escape '|' and reach next literal.
        j += 2
    return m


def format_dict(dictionary):
    return ", ".join([("!" if dictionary[key] else "") + str(key) for key in dictionary])


def resolve(sentence, mode):
    """
    Resolves the given sentence.

    @param sentence (list)
    : Propositional Sentence or Formula
    @param mode (bool)
    : To print or not to print resolution steps
    """
    clause = []
    clauses = []
    clause_maps = []
    for literal in sentence:
        if literal == '&':
            clauses.append(''.join(clause))
            clause_maps.append(clause_map(clause))
            clause.clear()
        else:
            clause.append(literal)
    clauses.append(''.join(clause))
    clause_maps.append(clause_map(clause))
    new_clause_maps = []
    
    if mode:
        print("Clauses <- The set of clauses in the CNF representation of (KB & !Q)")
        print("Clauses: {}".format(clauses))
        print("New Clauses <- {}")
        print("For each pair of clauses C_i, C_j in Clauses do:")
    
    while True:        
        for i in range(0, len(clause_maps)):
            for j in range((i + 1), len(clause_maps)):
                resolvent = {}
                for var in clause_maps[i]:
                    if var not in clause_maps[j] or clause_maps[j][var] == clause_maps[i][var]:
                        resolvent[var] = clause_maps[i][var]
                
                for var in clause_maps[j]:
                    if var not in clause_maps[i]:
                        resolvent[var] = clause_maps[j][var]

                print("\t({}) <- RESOLVE(({}), ({}))".format(format_dict(resolvent), format_dict(clause_maps[i]), format_dict(clause_maps[j]))) if mode else None

                if not bool(resolvent):
                    print("\tIf Resolvents contains the empty clause: Return True.") if mode else None
                    return True

                new_clause_maps.append(resolvent) if resolvent not in new_clause_maps else None
                print("\tNew Clauses <- New Clauses ∪ Resolvents") if mode else None

        if all(new_clause_map in clause_maps for new_clause_map in new_clause_maps):
            print("If New Clauses ⊆ Clauses : Return False") if mode else None
            return False

        clause_maps += [new_clause_map for new_clause_map in new_clause_maps if new_clause_map not in clause_maps]
        print("Clauses <- Clauses ∪ New Clauses") if mode else None


def get_sentence():
    """
    Returns the one-line segmented input without '\n'.
    """
    return segment_sentence(input().splitlines()[0])


def vet_sentence(sentence):
    """
    Returns the sentence in CNF after vetting sentence with proper parenthesis.

    @param sentence (list)
    : Propositional Sentence or Formula
    """
    sentence = induce_parenthesis(sentence)
    sentence = remove_extra_parenthesis(sentence)
    return CNF(sentence)


def main():
    """
    Main driver code
    """

    # n : Number of Propositional Sentence or Formula in Knowledge Base
    # m : Mode for Output
    # 
    # If m == 0 :
    #   Print only the result (int 0 or 1)
    # If m == 1 : 
    #   1. Print the resolution steps used
    #   2. Print the result (int 0 or 1) in the last line
    n, m = input().split()
    n = int(n)
    m = int(m)

    knowledge_base = []
    for i in range(0, n):
        # sentence : Propositional Sentence or Formula in Knowledge Base
        sentence = vet_sentence(get_sentence())
        knowledge_base += sentence.copy()
        
        if i != n - 1:
            knowledge_base.append("&")

    # query : Propositional Sentence or Formula to be proved
    query = vet_sentence(get_sentence())

    # rub : Input for resolution
    rub = ['!'] + query.copy()
    if len(knowledge_base) > 0:
        rub = knowledge_base.copy() + ['&', '('] + rub.copy() + [')']

    if len(rub):
        rub = vet_sentence(rub)
        print(int(resolve(rub, m)))


def run_multiple_test_cases():
    """
    Run multiple test cases.
    
    Input Order:
    First line: Number of test cases
    Then as many test case input followed from next line.
    """
    num_test_cases = int(input().splitlines()[0])
    while num_test_cases:
        main()
        num_test_cases -= 1


run_multiple_test_cases()
# main()