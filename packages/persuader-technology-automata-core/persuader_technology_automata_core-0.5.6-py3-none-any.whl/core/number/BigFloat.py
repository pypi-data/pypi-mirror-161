import re


class BigFloat:

    def __init__(self, *args):
        self.base = 10
        self.precision = 18
        self.number = 0
        self.decimals = 0
        self.parse_args(args)

    def parse_args(self, args):
        if len(args) > 1:
            self.number = int(args[0])
            self.decimals = int(args[1])
        else:
            decimal_marker_pos = args[0].find('.')
            if decimal_marker_pos > -1:
                self.number = int(args[0].replace('.', ''))
                self.decimals = len(args[0]) - decimal_marker_pos - 1
            else:
                self.number = int(args[0])

    def add(self, other):
        if self.decimals == other.decimals:
            result = self.number + other.number
            return BigFloat(result, self.decimals)
        else:
            smaller, bigger = [other, self] if self.decimals > other.decimals else [self, other]
            exponent = bigger.decimals - smaller.decimals
            normalised = smaller.number * (self.base ** exponent)
            result = normalised + bigger.number
            return BigFloat(result, bigger.decimals)

    def subtract(self, other):
        negated = BigFloat(-other.number, other.decimals)
        return self.add(negated)

    def multiply(self, other):
        result = self.number * other.number
        return BigFloat(result, self.decimals + other.decimals)

    def divide(self, other):
        distance = self.precision - self.decimals + other.decimals
        if distance == 0:
            numerator = self.number
        elif distance < 0:
            exponent = self.base ** -distance
            numerator = self.number // exponent
        else:
            exponent = self.base ** distance
            numerator = self.number * exponent
        result, mod = divmod(numerator, other.number)
        result = result + 1 if result < 0 and mod else result
        return BigFloat(result, self.precision)

    def gt(self, other):
        delta = self.subtract(other)
        return delta.number > 0

    def ge(self, other):
        delta = self.subtract(other)
        return delta.number >= 0

    def lt(self, other):
        return other.gt(self)

    def le(self, other):
        return other.ge(self)

    def __add__(self, other):
        return self.add(other)

    def __sub__(self, other):
        return self.subtract(other)

    def __mul__(self, other):
        return self.multiply(other)

    def __truediv__(self, other):
        return self.divide(other)

    def __lt__(self, other):
        return self.lt(other)

    def __le__(self, other):
        return self.le(other)

    def __gt__(self, other):
        return self.gt(other)

    def __ge__(self, other):
        return self.ge(other)

    def __eq__(self, other):
        return str(self) == str(other)

    def __str__(self):
        self.chop_zeros()
        return self.build_complete_number()

    def __repr__(self):
        return str(self)

    def chop_zeros(self):
        if self.decimals == 0:
            return
        number_str = self.build_complete_number()
        decimal_marker_pos = number_str.find('.')
        decimals_str = number_str[decimal_marker_pos+1:]
        match_trailing_zeros = re.search('(0+$)', decimals_str)
        if match_trailing_zeros:
            trailing_zeros_len = len(match_trailing_zeros.group(1))
            self.decimals -= trailing_zeros_len
            self.number = int(number_str[:-trailing_zeros_len].replace('.', ''))

    def build_complete_number(self):
        # number is a serialized repr of number & decimals (without '.' marker)
        number_str = str(self.number)
        if self.decimals > len(number_str):
            return f'0.{number_str.rjust(self.decimals, "0")}'
        if self.decimals == 0:
            return f'{self.number}.0'
        complete_number = f'{number_str[:-self.decimals]}.{number_str[-self.decimals:]}'
        return f'0{complete_number}' if complete_number[0:1] == '.' else complete_number

    def crack(self):
        complete_number = self.build_complete_number()
        if complete_number.find('.') > -1:
            return complete_number.split('.')
        return complete_number, '0'
