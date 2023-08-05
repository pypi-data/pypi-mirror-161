"""
Tokenize SQL.  Supports a wide range of SQL grammars.
"""


class Token:
    # token types
    PUNCT = 'p'
    STRING = 's'
    KEYWORD = 'k'
    REAL = 'r'
    INTEGER = 'i'
    PLACEHOLDER = '?'

    def __init__(self, value, type, pos, len, etc=None):
        self.value = value
        self.type = type
        self.pos = pos
        self.len = len
        self.etc = etc

    def isLiteral(self):
        return self.type in {self.STRING, self.REAL, self.INTEGER, self.PLACEHOLDER}

    def isPunct(self, p):
        return self.type in {self.PUNCT, self.PLACEHOLDER} and self.value == p

    def isKeyword(self, kwd):
        return self.type == self.KEYWORD and self.value.lower() == kwd.lower()


class SqlTokenizer(object):
    WS_CHAR = " \t\r\n\f\b"
    ID_CHAR_START = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz_"
    DIGIT_CHAR = "0123456789"
    ID_CHAR = ID_CHAR_START + DIGIT_CHAR + "."
    NUMBER_CHAR = DIGIT_CHAR + "."
    NON_PUNCT = WS_CHAR + ID_CHAR + NUMBER_CHAR + "'"
    VALID_T_SQL_START = ID_CHAR_START

    def __init__(self, input: str, allowed_operators: set, allow_placeholders: bool=False):
        self.input = input
        self.pos = 0
        self.len = len(input)
        self.tokens = []
        self.allowed_operators = allowed_operators
        self.allow_placeholders = allow_placeholders

    def _comment1(self):
        while self.pos < self.len and self.input[self.pos] != '\n':
            self.pos += 1
        if self.pos < self.len and self.input[self.pos] == '\n':
            self.pos += 1

    def _comment2(self):
        self.pos += 1
        while self.pos < self.len - 1 and self.input[self.pos] != '*' and self.input[self.pos + 1] != '/':
            self.pos += 1
        if self.pos < self.len - 1 and self.input[self.pos] == '*' and self.input[self.pos + 1] == '/':
            self.pos += 2

    def _string_literal(self, c):
        quote = c
        p0 = self.pos
        while self.pos < self.len:
            c = self.input[self.pos]
            if c != quote:
                self.pos += 1
            else:
                if self.pos + 1 < self.len and self.input[self.pos + 1] == quote:
                    self.pos += 2
                else:
                    break
        value = self.input[p0:self.pos].replace(quote + quote, quote)
        if self.pos < self.len and self.input[self.pos] == quote:
            self.pos += 1
        self.tokens.append(Token(value, Token.STRING if quote == "'" else Token.KEYWORD, p0 - 1, self.pos - p0 + 1, etc=c))

    def _keyword(self):
        p0 = self.pos - 1
        while self.pos < self.len and self.input[self.pos] in self.ID_CHAR:
            self.pos += 1
        value = self.input[p0:self.pos]
        if "." in value:
            # keywords separated by '.' are a special case, i.e. for qualified table names
            for n_value, value in enumerate(value.split(".")):
                if n_value:
                    self.tokens.append(Token(".", Token.PUNCT, p0, 1))
                    p0 += 1
                if value:
                    self.tokens.append(Token(value, Token.KEYWORD, p0, len(value)))
                    p0 += len(value)
        else:
            self.tokens.append(Token(value, Token.KEYWORD, p0, len(value)))

    def _tsql_id(self):
        p0 = self.pos - 1
        while self.pos < self.len and self.input[self.pos] != ']' or (self.pos+1 < self.len and self.input[self.pos+1] == ']'):
            self.pos += 1
        value = self.input[p0+1:self.pos]
        value = value.replace("[[", "[").replace("]]", "]")
        self.tokens.append(Token(value, Token.KEYWORD, p0, len(value)))
        if self.pos < self.len and self.input[self.pos] == ']':
            self.pos += 1

    def _numeric(self, c):
        # numeric literal
        p0 = self.pos - 1
        if c == '0' and self.pos < self.len and self.input[self.pos] in ['x', 'X']:
            self._hex(p0)
            return
        rtype = Token.REAL if c == '.' else None
        if c in self.DIGIT_CHAR:
            rtype = Token.INTEGER
        while self.pos < self.len and self.input[self.pos] in self.DIGIT_CHAR:
            self.pos += 1
            rtype = rtype or Token.INTEGER
        if self._detect_real_exp(rtype):
            rtype = Token.REAL
        if rtype == Token.REAL:
            v_raw = self.input[p0:self.pos]
            if v_raw == ".":
                self.tokens.append(Token(v_raw, Token.PUNCT, p0, self.pos - p0))
            else:
                value = float(v_raw)
                self.tokens.append(Token(value, rtype, p0, self.pos - p0))
        elif rtype == Token.INTEGER:
            s = self.input[p0:self.pos]
            value = int(s)
            self.tokens.append(Token(value, rtype, p0, self.pos - p0))
        else:
            self.tokens.append(Token(".", Token.PUNCT, p0, 1))

    def _detect_real_exp(self, rtype):
        """
        Presence of "." or valid exponent means we have a float.
        """
        found = False
        if self.pos < self.len and self.input[self.pos] == ".":
            if rtype == Token.INTEGER:
                found = True
            self.pos += 1
            while self.pos < self.len and self.input[self.pos] in self.DIGIT_CHAR:
                found = True
                self.pos += 1
        if self.pos < self.len and self.input[self.pos] in ['e', 'E']:
            p1 = self.pos
            self.pos += 1
            if self.pos < self.len and self.input[self.pos] in ['+', '-']:
                self.pos += 1
            while self.pos < self.len and self.input[self.pos] in self.DIGIT_CHAR:
                self.pos += 1
                p1 = self.pos
                found = True
            self.pos = p1
        return found

    def _hex(self, p0):
        self.pos += 1
        while self.pos < self.len and self.input[self.pos] in self.DIGIT_CHAR + "abcdefABCDEF":
            self.pos += 1
        value = int(self.input[p0 + 2:self.pos], 16)
        self.tokens.append(Token(value, Token.INTEGER, p0, self.pos - p0, etc="hex"))

    def _punct(self):
        p0 = self.pos - 1
        if self.pos < self.len and self.input[self.pos] not in self.NON_PUNCT and \
                self.input[p0:self.pos + 1] in self.allowed_operators:
            self.pos += 1
        v = self.input[p0:self.pos]
        if v == "%" and self.input[p0:self.pos+1] == "%s" and self.allow_placeholders:
            self.tokens.append(Token("%s", Token.PLACEHOLDER, p0, 2))
            self.pos += 1
        elif self.allow_placeholders and v == "?":
            self.tokens.append(Token(v, Token.PLACEHOLDER, p0, 1))
        else:
            self.tokens.append(Token(v, Token.PUNCT, p0, self.pos-p0))

    def run(self):
        while self.pos < self.len:
            c = self.input[self.pos]
            self.pos += 1
            if c in self.WS_CHAR:
                # ignore whitespace
                pass
            elif c == '-' and self.pos < self.len and self.input[self.pos] == '-':
                self._comment1()
            elif c == '/' and self.pos < self.len - 1 and self.input[self.pos] == '*':
                self._comment2()
            elif c in ("'", '"', '`'):
                self._string_literal(c)
            elif c in self.ID_CHAR_START:
                if c == 'N' and self.pos < self.len and self.input[self.pos] == "'":
                    # sql server format:
                    self.pos += 1
                    self._string_literal("'")
                else:
                    self._keyword()
            elif c in self.NUMBER_CHAR:
                self._numeric(c)
            elif c == '[' and self.pos < self.len and self.input[self.pos] in self.VALID_T_SQL_START and (self.pos <= 1 or self.input[self.pos-2] != '*'):
                self._tsql_id()
            else:
                self._punct()
        self._combine_compound()
        return self.tokens

    def _combine_compound(self):
        # combine compound tokens
        compound = [
            ["is", "not"],
            ["not", "in"],
            ["not", "like"],
            ["not", "ilike"],
            ["not", "match"],
            ["not", "regexp"],
            ["not", "glob"]
        ]
        for p in range(0, len(self.tokens) - 1):
            if self.tokens[p].type == Token.KEYWORD and self.tokens[p].value.lower() in ["is", "not"]:
                for cp in compound:
                    if str(self.tokens[p].value).lower() == cp[0] and str(self.tokens[p + 1].value).lower() == cp[1]:
                        self.tokens[p].value = cp[0] + " " + cp[1]
                        self.tokens.pop(p + 1)
        return self.tokens
