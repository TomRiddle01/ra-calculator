import sys
import os.path

# Custom Exceptions
class InvalidProjArgumentsException(Exception):
    pass
class InvalidTableNameError(Exception):
    pass
class InvalidTableDimension(Exception):
    pass
class UnexpectedEndOfQuery(Exception):
    pass
class UnexpectedTokenError(Exception):
    pass
class TableDoesNotExistError(Exception):
    pass

# abstract query type/interface
class Query():
    def execute(self):
        raise NotImplementedError("Method not implemented")
    def __str__(self):
        raise NotImplementedError("Method not implemented")

# implementation of sigma query
class Sigma(Query):

    def __init__(self, value1, value2, subquery):
        self.value1 = value1
        self.value2 = value2
        self.subquery = subquery
    
    def formatValue(self, value):
        if type(value) is str:
            return '"%s"'%(value)
        if type(value) is int:
            return value
        return "XXX"
    
    def getValue(self, value, row):
        if type(value) is str:
            return value
        if type(value) is int:
            return row[value-1]
        return None

    def __str__(self):
        value1 = self.formatValue(self.value1)
        value2 = self.formatValue(self.value2)
        return "σ%s=%s(%s)"%(value1, value2, self.subquery)

    def execute(self):
        table = self.subquery.execute()
        result = set()
        for row in table.content:
            value1 = self.getValue(self.value1, row)
            value2 = self.getValue(self.value2, row)
            if value1 == value2:
                result.add(row)
        return Table("result", result)

# implementation of pi query
class PI(Query):
    def __init__(self, proj, subquery):
        if proj == []:
            raise InvalidProjArgumentsException()
        if proj == [0]:
            proj = [] #so the empty tuple will be returned
        if 0 in proj:
            raise InvalidProjArgumentsException()
        self.proj = proj
        self.subquery = subquery
    
    def __str__(self):
        suffix = ",".join([str(d) for d in self.proj])
        return "π%s(%s)"%(suffix, self.subquery)
    
    def execute(self):
        table = self.subquery.execute()
        result = set()
        for row in table.content:
            newRow = ()
            for sel in self.proj:
                newRow += (row[sel-1],)
            result.add(newRow)
        return Table("result", result)

# implementation of cartesian product
class Cartesian(Query):
    def __init__(self, subquery1, subquery2):
        self.subquery1 = subquery1
        self.subquery2 = subquery2
    
    def __str__(self):
        return "%s x %s"%(self.subquery1, self.subquery2)
    
    def execute(self):
        table1 = self.subquery1.execute()
        table2 = self.subquery2.execute()
        result = set()
        for row1 in table1.content:
            for row2 in table2.content:
                result.add(row1 + row2)
        return Table("result", result)

# a plain table in form of a tuple-list that behaves like a query
class Table(Query):
    def __init__(self, name, content):
        self.name = name
        self.content = set(content)

    def __str__(self):
        return self.name

    def execute(self):
        return Table("", self.content)

    def printTable(self):
        string = ""
        for row in self.content:
            string += str(row)
            string += "\r\n"
        return string

# parses a string as a valid query
# this class is so long because the parse is split into many private methods
# and might me confusing because its a very rudimentary parser
class ParsedQuery(Query):
    def __init__(self, string, I):
        self.string = string
        self.I = I
        query, string = self.__seekQuery(string)
        self.query = query

    def execute(self):
        return self.query.execute()

    def __str__(self):
        return str(self.query)

    def __number(self, string):
        number = ""
        while string[0] in ["0","1","2","3","4","5","6","7","8","9"]:
            number += string[0]
            string = string[1:]
            if len(string) == 0:
                raise UnexpectedEndOfQuery()
        if number == "":
            return None, string
        return int(number), string

    def __table(self, string):
        word = ""
        while len(string) > 0 and string[0] in list("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"):
            word += string[0]
            string = string[1:]
        if word == "":
            raise UnexpectedTokenError("A Tablename was expected at %s" % (string))
        for table in self.I:
            if table.name == word:
                return table, string
        raise TableDoesNotExistError("Table %s is not definied" % (word))

    def __string(self, string):
        word = ""
        string = self.__token('"', string)
        while not string[0] == '"':
            word += string[0]
            string = string[1:]
            if len(string) == 0:
                raise UnexpectedEndOfQuery()
        if word == "":
            return None, string
        string = self.__token('"', string)
        return word, string

    def __token(self, expect, string):
        if string.startswith(expect):
            return string[len(expect):]
        else:
            raise UnexpectedTokenError("Expected %s at: %s" % (expect, string))

    def __seekQuery(self, string):
        string = string.strip()
        if len(string) == 0:
            raise UnexpectedEndOfQuery()
        if string.startswith("π") or string.startswith("#"):
            query, string = self.__seekPI(string[1:])
        elif string.startswith("σ") or string.startswith("*"):
            query, string = self.__seekSigma(string[1:])
        else:
            query, string = self.__table(string)

        # cartesian operator is between two queries, so we are looking for it now
        nested = True
        while nested:
            string = string.strip()
            if string.startswith("x"):
                query, string = self.__seekCartesian(string[1:], query)
            else:
                nested = False
        return query, string



    def __seekPI(self, string):
        string = string.strip()
        numbers = []
        number, string = self.__number(string)
        while number != None:
            numbers.append(number)
            if string.startswith(","):
                string = string[1:]
            number, string = self.__number(string)
        string = self.__token("(", string)
        subquery, string = self.__seekQuery(string)
        string = self.__token(")", string)
        return PI(numbers, subquery), string

    def __sigmaValue(self,string):
        value, string = self.__number(string)
        if value == None:
            value, string = self.__string(string)
        return value, string


    def __seekSigma(self, string):
        string = string.strip()
        value1, string = self.__sigmaValue(string)
        string = self.__token("=", string)
        value2, string = self.__sigmaValue(string)
 
        string = self.__token("(", string)
        subquery, string = self.__seekQuery(string)
        string = self.__token(")", string)

        return Sigma(value1, value2, subquery), string

    def __seekCartesian(self, string, leftQuery):
        string_ = string
        string = string.strip()
        rightQuery, string = self.__seekQuery(string)
        return Cartesian(leftQuery, rightQuery), string


# creates a database instance (a list of tables)
class DatabaseFile(list):

    def __init__(self,filename):
        list.__init__(self, [])
        self.__currentTable = None

        with open(filename, 'r') as content:
            lines = [l.strip() for l in content.readlines()]
            while len(lines) > 0:
                lines = self.__seekTableName(lines)
                lines = self.__seekTableContent(lines)

    def __seekTableName(self, lines):
        i = 0
        for line in lines:
            i+=1
            if line == "":
                continue
            if line.isalpha():
                self.__currentTable = Table(line, [])
                self.append(self.__currentTable)
                return lines[i:]
            else:
                raise InvalidTableNameError()

    def __seekTableContent(self, lines):
        i = 0
        prev = None
        for line in lines:
            i+=1
            if line == "":
                break
            row = tuple([l.strip() for l in line.split("|")])

            if prev == None:
                prev = row
            else:
                if len(prev) != len(row):
                    raise InvalidTableDimension()
            self.__currentTable.content.add(row)
        self.__currentTable = None
        return lines[i:]



# Shell interface for commandline usage
class Shell():
    def __init__(self):
        self.I = []

    def startShell(self, command=None):
        if not command:
            command = sys.stdin

        self.__prompt()
        for line in command:
            line = line.strip()
            if line == "exit":
                exit()
            if line.startswith("open"):
                if len(line[3:])>1:
                    if line[4] == " ":
                        self.openFile(line[5:])
                        self.__prompt()
                        continue
                print("Please add a filename")
            if line == "tables":
                for table in self.I:
                    print(table)
            else:
                try:
                    q = ParsedQuery(line, self.I)
                    print("Query executed as %s" % q)
                    result = q.execute()
                    print(result.printTable())
                except Exception as e:
                    print("Query Error", e)
            self.__prompt()

    def __prompt(self):
        sys.stdout.write('>>')
        sys.stdout.flush()


    def openFile(self, name):
        if os.path.isfile(name):
            try:
                self.I = DatabaseFile(name)
            except Exception as e:
                print("Invalid Database")
                print(e)
            print("Database loaded")
        else:
            print("File %s does not exists" % name)


