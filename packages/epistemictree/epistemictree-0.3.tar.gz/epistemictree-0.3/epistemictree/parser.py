# Conjunto de funciones para trababajar con tree-sitter. 
from tree_sitter import Parser as TSParser 
from tree_sitter import Language as TSLanguage
import tree_sitter
from epistemictree import utils

LP_LANGUAGE = TSLanguage('../epistemictree/my-languages.so', 'ep')
LABEL_LANGUAGE = TSLanguage('../epistemictree/my-languages.so', 'label')

class Parser():
    """
    A class to handle Tree-sitter parser

    Attributes
    ----------
    formula: str
       The sring containing the formula 
    language: TSLanguage
        Grammar for treesitter

    Methods
    -------
    get_formula()
    get_node_text(node)
    get_parser() 
    get_root_node(self) 
    get_tree(self)
    """

    def __init__(self,cadena:str, language:TSLanguage):
        self.cadena=cadena
        self.language = language

    def get_parser(self) -> tree_sitter.Parser:
        """
        Return the parser class.
        """
        parser = TSParser()
        parser.set_language(self.language)
        return parser

    def get_tree(self) -> tree_sitter.Tree: 
        """
        Return the tree of the parser tree.
        """
        cadena=self.cadena.replace(" ","")
        cadena_bytes=bytes(cadena,'utf-8')
        tree = self.get_parser().parse(cadena_bytes)
        return tree

    def get_root_node(self) -> tree_sitter.Node:
        """
        Return the root node of the parser tree.
        """
        tree = self.get_tree()
        root = tree.root_node
        return root

    def get_node_text(self, node:tree_sitter.Node):
        """
        Return the text of the given node.
        
        Parameters
        -----------
        node : tree_sitter.Node
            The node from which the text is extracted
        """
        source_code_bytes=bytes(self.cadena,'utf-8')
        byte_text = source_code_bytes[node.start_byte:node.end_byte]
        node_text = byte_text.decode('utf-8')
        return node_text


class Formula:
    """
    A class representing an epistemic formula

    Attributes
    ----------
    formula : str
        The sring containing the formula.
    ts : tree_sitter.Parser
        The parser of the given formula, it uses the LABEL_LANGUAGE
    tree: tree_sitter.Tree
        The tree parser of the formula.
    node: tree_sitter.Node
        The root node of the tree parser.

    Methods
    -------
    delete_negation():
    deny_formula():
    get_agent():
    get_formula_type():
    get_len():
    get_subformulas():
    get_terms():
    parse():
    simplify_par():
    """
    def __init__(self, formula:str ):
        if(formula[0]=='(' and formula[-1]==')'): # ESTE IF ELIMINA LOS PARÉNTESIS EXTERIORES
            self.formula=formula[1:-1].replace(" ","")
        else:
            self.formula=formula.replace(" ","")
        self.ts = Parser(self.formula,LP_LANGUAGE)
        self.tree = self.ts.get_tree()
        self.node = self.ts.get_root_node()

    def to_string(self):
        return self.formula

    def get_subformulas(self) -> list:
        """
        Return the subformula function.

        """
        fbf_query = LP_LANGUAGE.query("""
                (formula
                    operator:(or))@or_formula
                (formula
                    operator:(and))@and_formula
                (formula
                    operator:(iff))@iff_formula
                (formula
                    operator:(know))@eq_formula
                (formula
                    operator:(eq))@eq_formula
                (formula
                    operator:(not))@not_formula
                (atom) @atom_formula
                """)
        fbf = fbf_query.captures(self.node)
        formula_stack = []
        subformulas = []
        for i in fbf:
            current_formula = i[0]
            node_text=self.ts.get_node_text(current_formula)
            formula_stack.append(node_text) # Añado las fórmulas a una pila
            formula_stack=list(dict.fromkeys(formula_stack))
        for i in formula_stack:
            formula=Formula(i)
            subformulas.append(formula)

        j=0
        size=len(subformulas)

        # Bubble sort: algoritmo para ordenar de mayor a menor las fórmulas
        for i in range(size-1):
            for j in range(0, size-i-1):
                if subformulas[j].get_len() < subformulas[j + 1].get_len():
                    subformulas[j], subformulas[j + 1] = subformulas[j + 1], subformulas[j]
        return subformulas

    def get_formula_type(self) -> str:
        """
        Return formula type.
        """
        node = self.node
        operator=node.child_by_field_name('operator')
        if(operator == None):
            return "atom"
        elif(operator.type == 'not'): 
            formula = Formula(self.ts.get_node_text(node.child_by_field_name('term')))
            second_operator = formula.get_formula_type()
            return operator.type+"_"+second_operator
        else:
            return operator.type

    def get_terms(self) -> list:
        """
        Return terms list of the formula. For binary operators(&&,=>,||) return
        list with two members. For monary operators(Ka,-) return list with one member.
        """
        node=self.node
        type=self.get_formula_type()
        term_list = []
        if(type=="atom"):
            term_list.append(self)
        elif("not" in type or type=="know"):
            term=node.child_by_field_name('term')
            formula=Formula(self.ts.get_node_text(term))
            term_list.append(formula)
        else:
            first_term=node.child_by_field_name('left_term')
            second_term=node.child_by_field_name('right_term')
            first_formula=Formula(self.ts.get_node_text(first_term))
            second_formula=Formula(self.ts.get_node_text(second_term))
            term_list.append(first_formula)
            term_list.append(second_formula)
        return term_list
    
    def simplify_par(self):
        """
        [Useless] Remove external parenthesis.
        """
        if(self.formula[0]=='('):
                self.formula=self.formula[1:-1]

    def get_len(self) -> int: 
        """"
        Return the size of the formula.
        """
        type=self.get_formula_type()
        len=0
        if(type=="atom"):
            len=1
        else:
            len=1
            for i in self.get_terms():
                len=len+i.get_len()
        return len

    def parse(self) -> bool:
        """
        Return true if the formula is valid; false if it is not.
        """
        fbf_query = LP_LANGUAGE.query("""
                (ERROR)@error
                """)
        # Captura los errores
        fbf = fbf_query.captures(self.node)
        # Bucle que comprueba que hay el mismo numero de parentesis abiuertos y cerrados
        # En caso de que j<0 ocurre cuando ocurre un ) antes que un (. Esto es porque en el caso de los paréntesis Treesitter no lo capta como error
        flag=True
        j = 0
        for char in self.formula:
            if char == ')':
                j -= 1
                if j < 0:
                    flag=False
            elif char == '(':
                j += 1
            flag=j == 0
        return flag and len(fbf)==0

    def get_agent(self):
        """
        Return the agent of the knowledge formula. 
        """
        cursor = self.tree.walk()
        if(self.get_formula_type()=="know"): # Por el árbol que te genera para acceder al agente tenemos que ir a hijo e hijo y hermano
            assert cursor.goto_first_child()
            assert cursor.goto_first_child()
            assert cursor.goto_next_sibling()
            agent = cursor.node
            return self.ts.get_node_text(agent)
        else: 
            # Crear un tipo de error para esto
            # print("No es una fórmula de conocimiento")
            return 

    # TODO: Poner la negación por casos -> Literales y Demás(matiz conocimiento)
    def deny_formula(self):
        """
        Return the deny formula. If the formula is a negation, an atom or a
        knowledge one, return the negation without parenthesis. In other case,
        sourrund te formula with ().
        """
        if 'not' in self.get_formula_type() or self.get_formula_type() == 'atom' or self.get_formula_type() == 'know':
            return Formula("-"+self.formula).delete_negation()
        else: 
            return Formula("-("+self.formula+")").delete_negation()

    def delete_negation(self):
        """
        Return the formula with out repeatd negations.
        --p  ====> p
        ---p ====> -p
        """
        if 'not_not' not in self.get_formula_type():
            return self
        else:
            return self.get_terms()[0].get_terms()[0].delete_negation()
        
    def is_literal(self):
        if self.get_formula_type()=='atom' or self.get_formula_type()=='not_atom':
            return True
        else:
            return False

class Label(): 
    """
    A class representing a label

    Attributes
    ----------
    label:str
        The sring containing the label.
    ts: tree_sitter.Parser
        The parser of the given formula, it uses the LABEL_LANGUAGE
    tree: tree_sitter.Tree
        The tree parser of the formula.
    node: tree_sitter.Node
        The root node of the tree parser.

    Methods
    -------
    delete_negation():
    deny_formula():
    get_agent():
    get_formula_type():
    get_len():
    get_subformulas():
    get_terms():
    parse():
    simplify_par():
    """
    def __init__(self,label):
        self.label = label
        self.ts = Parser(self.label,LABEL_LANGUAGE)
        self.tree = self.ts.get_tree()
        self.node = self.ts.get_root_node()

    def parse(self) -> bool:
        """
        Return true if the label is valid; false if it is not.
        """
        fbf_query = LP_LANGUAGE.query("""
                (ERROR)@error
                """)
        fbf = fbf_query.captures(self.node)
        return len(fbf)==0

    def get_agent(self):
        if len(self.label)>1:
            return self.label[-3]
        else: 
            return None

    def len(self) -> int:
        """
        Return size of label.
        """
        return len(self.label.replace('.',''))

    def get_simple_extensions(self,branch):
        extensions = []
        if not branch.label_in_branch(self):
            print("Not in branch")
            return extensions
        lb = branch.get_label_branch()
        for l in lb:
            if l.is_simple_extension(self):
                extensions.append(l)
        return extensions

    def get_originals(self, branch):
        originals=[]
        if not branch.label_in_branch(self):
            print("Not in branch")
            return originals
        lb = branch.get_label_branch()
        for l in lb:
            if utils.superfluo(branch, self,l) and self.label!=l.label:
                originals.append(l)
        return originals 


    def is_superfluo(self, branch) -> bool:
        if(self.get_originals(branch)):
            return True
        return False

    def is_sublabel(self, label)-> bool:
        """
        Return true if the current label is a sublabel of the given label.

        Attributes
        -----------
        label: Label
            The label to compare with the current label.
        """
        if self.len() > label.len():
            return False
        else:
            label1_list = []
            label2_list = []
            for member in self.label:
                label1_list.append(member)

            for member in label.label:
                label2_list.append(member)

            i = 0
            for digit in label1_list:
                if digit != label2_list[i]:
                    return False
                i +=1
            return True

    def is_simple_extension(self,label)-> bool:
        """
        Return true if the current label is a simple extension of the given label.

        Attributes
        -----------
        label: Label
            The label to compare with the current label.
        """
        len1 = self.len()
        len2 = label.len()+2
        return label.is_sublabel(self) and len1==len2 


    def append(self, agent:str, world:str):
        """
        Return new label with the agent and the world.

        Attributes
        -----------
        agent: str
            
        world: str
        """
        new_label = self.label +"."+agent+"."+world
        return Label(new_label)

    def simplify_label(self) -> int:
        """ 
        Return the label as an int with out the agent.
        """
        label_num  = ""
        for number in self.label:
            if number.isdigit():
                label_num = label_num+number
        return int(label_num)
    
    def get_formulas(self, node, formulas = None):
        """ 
        DEPRECATED Return the set of formulas that are true in the label. It uses preorder algorithm.
        """
        if formulas == None:
            formulas = []
        if node:
            if(node != None):
                if node.get_label().label == self.label:
                    print(node.get_labelled_formula_string())
                    formulas.append(node.get_formula())
                self.get_formulas(node.left, formulas)
                self.get_formulas(node.right, formulas)
                return formulas


class LabelledFormula:
    """
    A class representing a labelled formula

    Attributes
    ----------
    label: Label
        The label of the labelled formula.
    formula: Formula
        The formula of the labelled formula.
        
    Methods
    -------
    get_contradiction(lab_formula)
    to_string()
    """
    def __init__(self, label:Label, formula:Formula) -> None:
        self.label = label
        self.formula = formula

    def get_contradiction(self, lab_formula) -> bool:
        """
        Return true if the given formula and the current formular are contradictories;

        Parameters
        -----------
        lab_formula: LabelledFormula
            The formula for compare
        """
        if self.label.label != lab_formula.label.label:
            return False
        deny_formula = self.formula.deny_formula()
        formula = lab_formula.formula.delete_negation()
        if deny_formula.formula == formula.formula:
            return True
        return False
        
    def to_string(self):
        return self.label.label+" "+self.formula.formula

