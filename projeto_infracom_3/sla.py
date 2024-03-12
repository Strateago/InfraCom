class dia:
    owner = ['', '', '', '', '', '', '', '', '', '']
    horarios = [True, True, True, True, True, True, True, True, True, True]

class week:
    day = {
        'Seg': dia(),
        'Ter': dia(),
        'Qua': dia(),
        'Qui': dia(),
        'Sex': dia()
    }

salas = {
    "E101": week(),
    "E102": week(),
    "E103": week(),
    "E104": week(),
    "E105": week(),
}

consulta = input()
consulta = consulta.split(' ')
string = ""
salas[consulta[0]].day[consulta[1]].owner[int(consulta[2])-8] = "bla"

for cont, i in enumerate(salas[consulta[0]].day[consulta[1]].horarios, 8):
    if i:
      string += str(cont) + ' '
print (salas[consulta[0]].day[consulta[1]].owner[int(consulta[2])-8])