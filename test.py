import unittest
from spc import *




class TestSuite(unittest.TestCase):
    
    def setUp(self):
        self.People = Table("People", [ \
                ("John","1995","musucian"),\
                ("Steward","1996","poker player"),\
                ("Jessie","1996","cashier")])
        
        self.Groups = Table("Groups", [ \
                ("P3","John"), \
                ("P5","Steward"), \
                ("P3","Jessie"), \
                ("P5","Other Dude"), \
                ("P5","Dudette")])
    
    def testPrintProj(self):
        query = PI([1,2], self.People)
        self.assertEqual(str(query), "π1,2(People)")

    def testPrintCartesian(self):
        query = Cartesian(self.People, self.People)
        self.assertEqual(str(query), "People x People")

    def testPrintCartesianCombined(self):
        query = Cartesian(self.People, PI([1,2], self.People))
        self.assertEqual(str(query), "People x π1,2(People)")





    def testTrivialSigma1(self):
        query = Sigma(1,"John", self.People)
        result = query.execute()
        self.assertEqual(len(result.content), 1)
    
    def testTrivialSigma2(self):
        query = Sigma("John","John", self.People)
        result = query.execute()
        self.assertEqual(len(result.content), 3)

    def testTrivialProj(self):
        query = PI([1,2], self.People)
        result = query.execute()
        self.assertEqual(result.content, set([ \
                ("John","1995"),\
                ("Steward","1996"),\
                ("Jessie","1996")]))
    
    def testBooleanProj(self):
        query = PI([0], self.People)
        result = query.execute()
        self.assertEqual(result.content, set([()]))

    def testTrivialCartesian(self):
        query = Cartesian(self.People, self.People)
        self.assertEqual(len(query.execute().content), 9)


    def testComplexQuery(self):
        query = PI([1],Sigma("P3",4,Sigma(1,5,Cartesian(self.People, self.Groups))))
        result = query.execute()
        self.assertEqual(query.execute().content, set([("John",),("Jessie",)]))

    def testParsingProj(self):
        query = "π2,3(People)"
        self.assertEqual(query,str(ParsedQuery(query, [self.People, self.Groups])))

    def testParsingSigma(self):
        query = "σ2=3(People)"
        self.assertEqual(query,str(ParsedQuery(query, [self.People, self.Groups])))

    def testParsingCartesian(self):
        query = "People x Groups x Groups"
        self.assertEqual(query,str(ParsedQuery(query, [self.People, self.Groups])))
    
    def testParsingNested(self):
        query = "σ2=3(π2,3(People x People))"
        self.assertEqual(query,str(ParsedQuery(query, [self.People, self.Groups])))
    
    def testComplexParsedQuery(self):
        query = 'π1(σ"P3"=4(σ1=5(People x Groups)))'
        self.assertEqual(query,str(ParsedQuery(query, [self.People, self.Groups])))
    
    def testComplexParsedQueryEvaluated(self):
        query = 'π1(σ"P3"=4(σ1=5(People x Groups)))'
        parsedQuery = ParsedQuery(query, [self.People, self.Groups])
        self.assertEqual(parsedQuery.execute().content, set([("John",),("Jessie",)]))

    def testReadDatabaseFile(self):
        db = DatabaseFile("example.txt")
        self.assertEqual(len(db), 3)

    def testCaseComplete(self):
        db = DatabaseFile("example.txt")
        query = ParsedQuery('π1(σ5="Hamburg"(σ1=4(People x Living)))', db)
        self.assertEqual((query.execute().content), set([('Alfred',), ('TomRiddle01',)]))

