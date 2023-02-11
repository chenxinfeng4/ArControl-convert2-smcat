# %% imports
import os
from xml.dom import minidom
from collections import defaultdict


filepath = 'twoAFPC.aconf'

def getDesinate(FromCi, strip):
    nextstate = strip.getElementsByTagName('nextstate')[0]
    staterandtype = nextstate.getAttribute('type')
    iscomponent = nextstate.getAttribute('iscomponent').lower() == 'true'
    nextstateprefix = 'C' if iscomponent else  f'C{FromCi}S'
    if staterandtype=='fixed':
        number = nextstate.getElementsByTagName('fixed')[0].getAttribute('fixed')
        number = int(number)
        nextstate_numbers = [nextstateprefix+str(number)]
    elif staterandtype=='range':
        number_from = nextstate.getElementsByTagName('range')[0].getAttribute('from')
        number_to = nextstate.getElementsByTagName('range')[0].getAttribute('to')
        number_from = int(number_from)
        number_to = int(number_to)
        numbers = list(range(number_from, number_to+1))
        nextstate_numbers = [nextstateprefix+str(number) for number in numbers]
    elif staterandtype=='goelse':
        number_go = nextstate.getElementsByTagName('goelse')[0].getAttribute('go')
        number_else = nextstate.getElementsByTagName('goelse')[0].getAttribute('else')
        number_go = int(number_go)
        number_else = int(number_else)
        numbers = [number_go, number_else]
        nextstate_numbers = [nextstateprefix+str(number) for number in numbers]
    elif staterandtype=='endup':
        nextstate_numbers = ['final']
    else:
        raise 'Not vernified nextstate type.'
    return nextstate_numbers

def getRandDestinateNumber(strip) -> str:
    domtype = strip.getAttribute('type')
    if domtype=='fixed':
        number = strip.getElementsByTagName('fixed')[0].getAttribute('fixed')
        res = number
    elif domtype=='range':
        number_from = strip.getElementsByTagName('range')[0].getAttribute('from')
        number_to = strip.getElementsByTagName('range')[0].getAttribute('to')
        res = f'{number_from}-{number_to}'
    elif domtype=='goelse':
        number_go = strip.getElementsByTagName('goelse')[0].getAttribute('go')
        number_else = strip.getElementsByTagName('goelse')[0].getAttribute('else')
        res = f'{number_go} OR {number_else}'
    else:
        raise 'Not vernified nextstate type.'
    return res


def next_state_trans(fromci, fromsi, stcomment, nextStateNames):
    if len(nextStateNames)>1:
        stcomment = stcomment + ' (random)'
    trans_l = [f'C{fromci}S{fromsi} => {nextcisi}: {stcomment};' for nextcisi in nextStateNames]
    return trans_l

def convert(filepath):
    file = minidom.parse(filepath)

    root = file.getElementsByTagName('ARC_DESIGNER')[0]
    session = root.getElementsByTagName('SESSION')[0]
    components = session.getElementsByTagName('COMPONENT')
    define_list = []
    functional_list = []
    components_d = {}
    for ci, component in enumerate(components, start=1):
        name = component.getAttribute('comment')
        states = component.getElementsByTagName('STATE')
        states_d = {}
        components_d[ci] = (name, states_d)
        if name:
            component_define = f'C{ci} [label="C{ci}: {name}"]'+'{\n%s;\n}'
        else:
            component_define = f'C{ci} [label="C{ci}"]'+'{\n%s;\n}'

        state_defines = []
        for si, state in enumerate(states, start=1):
            statename = state.getAttribute('comment')
            if statename:
                definition = f'\tC{ci}S{si} [label="S{si}: {statename}"]:' + '"{}"'
            else:
                definition = f'\tC{ci}S{si} [label="S{si}"]:' + '"{}"'

            strips = state.getElementsByTagName('STATE_STRIP')
            strips_d = defaultdict(list)
            for sti, strip in enumerate(strips):
                isEnable = strip.getAttribute('isEnable').lower() == 'true'
                strtype =  strip.getAttribute('type')
                if not isEnable:
                    continue
                stname = strip.getAttribute('comment')
                
                if stname:
                    strips_d[strtype].append(stname)
                    continue
                if strtype=='doVar':
                    strips_d[strtype].append('doVar')
                    continue
                if strtype=='doPin':
                    item = strip.getElementsByTagName('doPin')[0]
                    pinnum = item.getAttribute('number')
                    pinmode = item.getAttribute('type')
                    stname = f'OUT{pinnum} {pinmode}'
                    strips_d[strtype].append(stname)
            
            comments_l = []
            for stname in strips_d['doVar']:
                comments_l.append('🗃️'+stname)
                
            for stname in strips_d['doPin']:
                comments_l.append('💡'+stname)
            comments_str = "\n".join(comments_l)
            comments_str = comments_str.replace('"','').replace("'","")
            definition_str = definition.format(comments_str)
            state_defines.append(definition_str)

        define_list.append(component_define % ',\n'.join(state_defines))

    define_str = 'initial,\nfinal,\n'+',\n'.join(define_list)+';'


    # %% for transitions
    trans_l = ['initial => C1;']
    for ci, component in enumerate(components, start=1):
        name = component.getAttribute('comment')
        states = component.getElementsByTagName('STATE')
        for si, state in enumerate(states, start=1):
            CiSi_id = f'C{ci}S{si}'
            strips = state.getElementsByTagName('STATE_STRIP')
            for sti, strip in enumerate(strips):
                isEnable = strip.getAttribute('isEnable').lower() == 'true'
                strtype =  strip.getAttribute('type')
                if not isEnable:
                    continue

                if not strtype.startswith('when'):
                    continue

                nextStateNames = getDesinate(ci, strip)
                stcomment = strip.getAttribute('comment').strip()
                stcomment = stcomment + '->'
                ind_arrow = stcomment.find('->')
                if ind_arrow>0:  #has comment already
                    stcomment = stcomment[:ind_arrow]
                    stcomment = stcomment.strip()
                    trans_l_now = next_state_trans(ci, si, stcomment, nextStateNames)
                    trans_l.extend(trans_l_now)
                    continue

                if strtype=='whenPin':
                    number = strip.getElementsByTagName(strtype)[0].getAttribute('number')
                    stcomment = f'IN{number}'
                elif strtype=='whenVar':
                    strcomment = 'whenVar'
                elif strtype=='whenTime':
                    substrip = strip.getElementsByTagName('time')[0]
                    rightcomment = getRandDestinateNumber(substrip)
                    strcomment = f't = {rightcomment}'
                elif strtype=='whenCount':
                    substrip = strip.getElementsByTagName('count')[0]
                    rightcomment = getRandDestinateNumber(substrip)
                    if rightcomment=='1':
                        stcomment = ''
                    else:
                        stcomment = f'N = {rightcomment}'
                trans_l_now = next_state_trans(ci, si, stcomment, nextStateNames)
                trans_l.extend(trans_l_now)

    trans_str = '\n'.join(trans_l)
    all_str = define_str + '\n' + trans_str

    smcatfile = os.path.splitext(filepath)[0]+'.smcat'
    with open(smcatfile, 'w', encoding='utf-8') as f:
        f.write(all_str)

    return smcatfile


if __name__ == '__main__':
    filetxts = sys.argv[1:]
    for filetxt in filetxts:
        convert(filetxt)