import re
import operator





class AbeInterpreter:

    def __init__(self):
        self._i = 0
        self._tape = [0]
        self._buffer = []
        self._tokens = list()
        self._loopcons = list()
        self._loopactions = list()
        self._currentlooplevel = 0
        self._cval = 0
        self._output = ''
        self._has_error = False
        self._error = ''
        self._rs = {
            'number': '((\-?\d+\.\d*)|(\-?\d+))',
            'bool': 'True|False',
            'string': '\".*\"'
        }

    
    def _mr(self):
        raw = self._tokens.pop()
        v = self._cast(getParmType(raw), raw)
        self._i += v
        length = len(self._tape) - 1
        if self._i > length:
            for n in range(length, self._i + 1):
                self._tape.append(0)


    def _ml(self):
        raw = self._tokens.pop()
        v = self._cast(self._getParmType(raw), raw)
        self._i -= v
        if self._i < 0:
            self._has_error = True


    def _incr(self):
        raw = self._tokens.pop()
        v = self._cast(self._getParmType(raw), raw)
        self._tape[self._i] += v


    def _decr(self):
        raw = self._tokens.pop()
        v = self._cast(self._getParmType(raw), raw)
        self._tape[self._i] -= v


    def _getInput(self):
        x = input()
        x = self._cast(self._getParmType(x), x)
        self._tape[self._i] = x


    def _storeVal(self):
        raw = self._tokens.pop()
        v = self._cast(self._getParmType(raw), raw)
        self._buffer = self._buffer[1:]
        self._tape[self._i] = v


    def _doLoop(self):
        raw = self._tokens.pop()
        loop_id = self._cast(self._getParmType(raw), raw)

        # get conditions linked to this loop
        op, val = self._loopcons[loop_id]
        condition_met = op(self._tape[self._i], val)

        # if conditions are met, push the loop actions onto the tokens stack
        if condition_met:
            self._tokens.extend(self._loopactions[loop_id])


    def _defineLoop(self):

        # get the loop condition's operator (rawOp) and value (rawVal)
        rawOp = self._tokens.pop()
        rawVal = self._tokens.pop()
        ops = {'>':operator.gt, '<':operator.lt, '==':operator.eq}

        # dict with string as key and function as value
        op = ops[rawOp]
        val = self._cast(self._getParmType(rawVal), rawVal)

        # add the loop condition to the loop condition stack
        self._loopcons.append([op, val])
        loopIndex = len(self._loopactions)
        self._currentlooplevel += 1
        is_inner_loop = self._currentlooplevel > 1  # outermost loop will have loop level 1

        # need to evaluate actions within loop
        self._loopactions.append(list())
        while True:
            if self._tokens[-1] == 'while':
                self._tokens.pop()
                self._loopactions[loopIndex].extend(defineLoop())  # include tokens for any inner loops
            if self._tokens[-1] == 'loopend':
                # can either be loopend token for inner loop or for this loop
                self._tokens.pop()
                break  # either way, exit while loop
            else:
                # append normal token to list of actions for this loop
                self._loopactions[loopIndex].append(self._tokens.pop())

        # when we get to the end of the loop actions, re-evaluate loop condition
        self._loopactions[loopIndex].append('loop')
        self._loopactions[loopIndex].append(str(loopIndex))  # adds loop to end of itself for re-eval
        self._loopactions[loopIndex].reverse()

        self._currentlooplevel -= 1

        if is_inner_loop:  # all inner loops will return their loop token to containing loop
            return ['loop', str(loopIndex)]
        else:  # is base-level loop, so push on loop tokens for stack
            self._tokens.append(str(loopIndex))
            self._tokens.append('loop')


    def _loopend(self):
        op, val = self._loopcons[-1]
        condition_met = op(self._tape[self._i], val)

        if condition_met:
            # if loop conditions are met, re-append the loop actions
            self._tokens.append('loopend')
            self._tokens.extend(self._loopactions[-1])


    def _copyVal(self):
        self._cval = self._tape[self._i]


    def _pasteVal(self):
        self._tape[self._i] = self._cval


    def _cast(self, typeString, val):
        d = dict()
        d['float'] = float
        d['int'] = int
        d['bool'] = bool
        d['str'] = str

        try:
            if typeString == 'str':
                val = val.strip('"')
            return d[typeString](val)
        except:
            self._has_error = True


    def _getParmType(self, p):
        tokens = [
            ('float', r'\-?\d+\.\d*'),
            ('int', r'\-?\d+'),
            ('bool', r'%s' % self._rs['bool']),
            ('str', r'%s' % self._rs['string'])
        ]

        ms = re.compile('|'.join(['(?P<%s>%s)' % tup for tup in tokens]))

        match = re.match(ms, p)
        return match.lastgroup


    def _printCell(self):
        self._output += str(self._tape[self._i]) + '\n'


    def _processCond(self, match):
        s = match.string[match.start():match.end()]
        s = s.replace('He ran into the mountains, but only when ', '')
        cond = s.replace('. This is what happened there:', '')

        # parse condition
        t = [
            ('gt', r'they had more than %s fish' % self._rs['number']),
            ('lt', r'they had less than %s fish' % self._rs['number']),
            ('eq', r'the stone said .*')
        ]

        op = ''
        val = ''
        ms = re.compile('|'.join(["(?P<%s>%s)" % tup for tup in t]))

        optype = re.search(ms, cond).lastgroup

        if optype in ['gt', 'lt', 'deq']:
            d = re.search(r'%s' % self._rs['number'], cond)
            if d:
                val = d.group()

        elif optype=='eq':
            op = '=='
            val = cond.replace('the stone said ', '')

        else:
            self._has_error = True
            return 'error'


        opdict = {'eq':'==', 'gt':'>', 'lt':'<'}
        op = opdict[optype]
        return op, val



    def _processDigitToken(self, match):
        s = match.string[match.start():match.end()]
        ms = re.compile(r'%s' % self._rs['number'])
        m = re.search(ms, s)
        v = 0
        if m is not None:
            v = m.group()
        return v


    def _processStoreToken(self, match):
        s = match.string[match.start():match.end()]
        s = s.replace('Preparing for the storm, he carved ', '')
        s = s.replace(' into the stone.', '')
        return s


    def _consumeToken(self, token):
        comms = dict()
        comms['mr'] = self._mr
        comms['ml'] = self._ml
        comms['incr'] = self._incr
        comms['decr'] = self._decr
        comms['store'] = self._storeVal
        comms['pin'] = self._getInput
        comms['pout'] = self._printCell
        comms['while'] = self._defineLoop
        comms['loop'] = self._doLoop
        comms['loopend'] = self._loopend
        comms['copyval'] = self._copyVal
        comms['pasteval'] = self._pasteVal
        comms[token]()


    def _consumeTokenList(self):
        while len(self._tokens) > 0:
            if self._has_error:
                break
            self._consumeToken(self._tokens.pop())


    def _tokenize(self, s):
        t = [
            ('mr', r'Overhead, the geese flew \d+ miles east\.'),
            ('ml', r'Overhead, the geese flew \d+ miles west\.'),
            ('incr', r'He sold .*? sheep\.'),
            ('decr', r'They paid for their .*? mistakes\.'),
            ('pout', r'And Abraham spoke!'),
            ('pin', r'He listened when his wife spoke\.'),
            ('while', r'He ran into the mountains, but only when .*?\. This is what happened there\:'),
            ('loopend', r'Alas, I digress\.'),
            ('store', r'Preparing for the storm, he carved .*? into the stone\.'),
            ('copyval', r'One day he stole his neighbor\'s goods\.'),
            ('pasteval', r'He repented and returned the property\.'),
            ('s', r'\s+')
        ]

        ms = re.compile('|'.join(['(?P<%s>%s)' % tup for tup in t]))
        output = []
        lastend = 0
        f = [x for x in re.finditer(ms, s)]

        for m in f:
            if m.lastgroup == 's':
                lastend = m.end()
                continue

            if m.start() != lastend:
                self._has_error = True
                self._error = 'Problem with syntax in position %s' % m.start()
                return output

            if m.lastgroup in ['mr', 'ml', 'incr', 'decr']:
                output.append(m.lastgroup)
                output.append(self._processDigitToken(m))

            elif m.lastgroup == 'store':
                output.append(m.lastgroup)
                output.append(self._processStoreToken(m))

            elif m.lastgroup == 'while':
                output.append(m.lastgroup)
                output.extend(self._processCond(m))

            else:
                output.append(m.lastgroup)
            lastend = m.end()

        if lastend != len(s) and s[-1]!=' ':
            self._has_error = True
            self._error = 'Problem with syntax in position'

        output.reverse()

        return output


    def interpret(self, abraham_code, *args):
        self.__buffer = [a for a in args]

        self._i = 0
        self._tape = [0]
        self._tokens = list()
        self._loopcons = list()
        self._loopactions = list()
        self._cval = 0
        self._output = ''

        self._tokens = self._tokenize(abraham_code)
        self._consumeTokenList()
        if self._has_error:
            return self._error
        else:
            return self._output

