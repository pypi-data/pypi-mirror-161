import os

def dot_to_latex():
    file = open("/home/karu/model.dot", 'r')
    replaced_content = ""
    for line in file:
        line = line.strip()
        new_line = line.replace("->", "@").replace('-','¬').replace('&&', '∧').replace('=>','→').replace('v','∨').replace('@','->')
        replaced_content = replaced_content + new_line + "\n"
    file.close()
    file_write = open("/home/karu/model.dot",'w')
    file_write.write(replaced_content)
    file_write.close()
    os.system('dot -Tpng ~/model.dot > ~/model.png')


def superfluo(branch, label1, label2):
    # Etiqueta la misma return false
    if label1.label == label2.label or len(label2.label)>len(label1.label):
        return False

    base1 = branch.get_base_set(label1)
    list1=[formula.formula for formula in base1]

    base2 = branch.get_base_set(label2)
    list2=[formula.formula for formula in base2]

    count=0
    flag=True
    while flag and count < len(list1):
        for i in list1:
            if i not in list2:
                flag = False
            count = count+1

    if flag and len(set(list1)) == len(set(list2)):
        # Si son iguales
        if label1.simplify_label()>label2.simplify_label():
            return True
        else:
            return False
    return flag
