from epistemictree import rules as rl
from epistemictree import utils
from epistemictree import cli


def main():
    cli.run()
    

def examples():
    tree = exe['ejemplo32']
    value = rl.run_tableau('kt4',tree[0])
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(" Existe contramodelo > "+ str(value[0]))
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    if value[0]:
        print(" Contramodelo:")
        print(value[2].print_model())
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    # print(value[1].print_tree(value[1].root,2))
    # print(value[1].print_label_tree(value[1].root,2))
    utils.dot_to_latex()

exe = {
        # Pag 126. Fig 5.1
        'tree1' : [['-KaKa-p&&Ka-p']], 
        'tree2' : [['p&&-Kap']], 
        'tree3' : [['-Ka-p && Ka-Ka-p']],
        'tree4' : [['-(-KaKa-p && Ka-p)']],
        'tree5' : [['Kap && (-Ka-q && -Ka-(r||-p))']],
        'tree6' : [['-Ka-p','-Kap']],
        'tree7' : [['-Ka-p', 'Ka-q']],
        'tree8' : [['Ka-Ka-p']], 
        'axioma4' : [['Kap=>KaKap']], 
        'axioma5' : [['-Kap=>Ka-Kap']], 
        'axioma_multi4' : [['Kap=>KaKbp']], 
        'ejemplo1':[['-Kc- -Kb- r','-Kb- (p&&-Kb- r)', '-Ka-(q&&-Kb-r)']],
        'ejemplo32':[['Ka-Ka-p','Ka-Kap']]
        }



if __name__ == '__main__':
    main()
