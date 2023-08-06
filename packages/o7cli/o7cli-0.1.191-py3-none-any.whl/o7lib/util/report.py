#!/usr/bin/python3
#************************************************************************
# Copyright 2021 O7 Conseils inc (Philippe Gosselin)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#************************************************************************
import time
import os



#---------------------------
# TO DO
#---------------------------
#  
#---------------------------


#*************************************************
#
#*************************************************
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class constant:
    line = '-' * 40
    bigline = '#' * 40


#*************************************************
#
#*************************************************
class Report:

    #---------------------------------------------------------------------------------------------
    #
    #---------------------------------------------------------------------------------------------
    def __init__(self, name="", sectionName=None, print = True):

        self.name = name
        self.sections = []
        self.tests = []
        self.parameters = []
        self.activeSection = -1
        self.in_progress = None

        if print: self.PrintReportHeader()

        if sectionName is not None : 
            self.AddSection(name=sectionName)
        
    #---------------------------------------------------------------------------------------------
    #
    #---------------------------------------------------------------------------------------------
    def AddSection(self, name="", print = True):

        if self.in_progress != None: self.TestFail()

        entry = {"name" : name, "tests": [], "passed" : 0, "failed" : 0, "warning" : 0}
        self.sections.append(entry)
        self.activeSection = len(self.sections) - 1

        if print: 
            if self.activeSection > 0: self.PrintSectionFooter(**self.sections[self.activeSection - 1])
            self.PrintSectionHead(**entry)

    #---------------------------------------------------------------------------------------------
    #
    #---------------------------------------------------------------------------------------------
    def AddResult(self, name="", reason = None, passed = True, critical= True, print=True):

        if self.activeSection < 0 : self.AddSection()

        entry = {"name": name, "passed": passed, "critical": critical, "reason": reason}
        self.sections[self.activeSection]["tests"].append(entry)

        if passed :
            self.sections[self.activeSection]["passed"] += 1
        elif critical : 
            self.sections[self.activeSection]["failed"] += 1
        else: 
            self.sections[self.activeSection]["warning"] += 1

        if print: self.PrintTest(**entry)

    #---------------------------------------------------------------------------------------------
    #
    #---------------------------------------------------------------------------------------------
    def AddParameter(self, name="", value=None, print=True):

        entry = {"name": name, "value": value}
        self.parameters.append(entry)
        if print: self.PrintParameter(**entry)

    #---------------------------------------------------------------------------------------------
    #
    #---------------------------------------------------------------------------------------------
    def AddTest(self, name="", critical= True, print=True):

        if self.in_progress != None: self.TestFail()

        self.in_progress = {"name" : name, "critical": critical, "print" : True}

    #---------------------------------------------------------------------------------------------
    #
    #---------------------------------------------------------------------------------------------
    def TestPass(self, reason = None):
        if self.in_progress == None: return

        self.AddResult(name = self.in_progress["name"], 
                       reason = reason,
                       passed = True, 
                       critical=self.in_progress["critical"], 
                       print=self.in_progress["print"])

        self.in_progress = None

    #---------------------------------------------------------------------------------------------
    #
    #---------------------------------------------------------------------------------------------
    def TestFail(self, reason = None):
        if self.in_progress == None: return

        self.AddResult(name = self.in_progress["name"], 
                       reason = reason,
                       passed = False, 
                       critical=self.in_progress["critical"], 
                       print=self.in_progress["print"])

        self.in_progress = None

    #---------------------------------------------------------------------------------------------
    #
    #---------------------------------------------------------------------------------------------
    def Complete(self, print=True):

        if self.in_progress != None: self.TestFail()

        if print:
            if self.activeSection >= 0: self.PrintSectionFooter(**self.sections[self.activeSection])
            self.PrintReportSummary()

    #---------------------------------------------------------------------------------------------
    #
    #---------------------------------------------------------------------------------------------
    def PrintSectionHead(self, name = "", ** kwargs):

        print(f"{bcolors.HEADER}{constant.line}{bcolors.ENDC}")
        print(f"{bcolors.HEADER}Section : {name}{bcolors.ENDC}")

    #---------------------------------------------------------------------------------------------
    #
    #---------------------------------------------------------------------------------------------
    def PrintSectionFooter(self, ** kwargs):

        #print(f"{bcolors.HEADER}{constant.line}{bcolors.ENDC}")

        pct = 0.0
        if len(kwargs['tests']) > 0 : pct = kwargs['passed'] / len(kwargs['tests']) * 100

        txt = f"{kwargs['passed']} / {len(kwargs['tests'])} ({pct:.2f} %)"
        print(f"{bcolors.HEADER}{kwargs['name']} Summary:{bcolors.ENDC} {txt} ")
        

    #---------------------------------------------------------------------------------------------
    #
    #---------------------------------------------------------------------------------------------
    def PrintReportHeader(self):

        print(f"{bcolors.OKCYAN}{constant.bigline}")
        print(f"    {self.name}")
        print(f"{constant.bigline}{bcolors.ENDC}")
    

    #---------------------------------------------------------------------------------------------
    #
    #---------------------------------------------------------------------------------------------
    def PrintReportSummary(self):

        print(f"{bcolors.OKCYAN}{constant.bigline}")
        print(f"Report Summary")
        print(f"{constant.bigline}{bcolors.ENDC}")
        passed = 0
        warning = 0
        failed = 0
        total = 0

        for s in self.sections:
            passed += s['passed']
            warning += s['warning']
            failed += s['failed']
            total += len(s['tests'])

        
        print(f"  Pass    : {passed}")
        print(f"  Warning : {warning}")
        print(f"  Fail    : {failed}")
        print(f"  TOTAL   : {total}")

    #---------------------------------------------------------------------------------------------
    #
    #---------------------------------------------------------------------------------------------
    def PrintTest(self, name="", passed = True, critical= True, reason = None):

        txt = name
        if reason is not None: txt = f"{name}: {reason}"


        if passed :
            print(f"[{bcolors.OKGREEN}PASS{bcolors.ENDC}] {txt}")
        elif critical : 
            print(f"[{bcolors.FAIL}ERR!{bcolors.ENDC}] {txt}")
        else: 
            print(f"[{bcolors.WARNING}WARN{bcolors.ENDC}] {txt}")

    #---------------------------------------------------------------------------------------------
    #
    #---------------------------------------------------------------------------------------------
    def PrintParameter(self, name="", value = None):

        txt = name
        if value is not None: txt = f"{name}: {value}"
        print(f"{txt}")

#*************************************************
# To Test Class
#*************************************************
if __name__ == "__main__":

    r = Report('TheReport', sectionName="First Section")
    assert r.name == 'TheReport'
    assert len(r.sections) == 1
    assert len(r.sections[0]["tests"]) == 0
    assert r.sections[0]["name"] == "First Section"
    
    r.AddResult(name="Test OK", passed=True, critical=True)
    assert len(r.sections[0]["tests"]) == 1
    assert r.sections[0]["passed"] == 1
    
    r.AddResult(name="Test Fail", reason="Funny Stuff", passed=False, critical=True)
    assert len(r.sections[0]["tests"]) == 2
    assert r.sections[0]["failed"] == 1
    
    r.AddResult(name="Test Fail but not critical", passed=False, critical=False)
    assert len(r.sections[0]["tests"]) == 3
    assert r.sections[0]["warning"] == 1

    r.AddSection("Second Section")
    assert len(r.sections) == 2
    assert len(r.sections[1]["tests"]) == 0

    assert r.in_progress == None
    r.AddTest("Step by Step Test 1", False)
    assert r.in_progress != None
    assert r.in_progress["critical"] == False

    r.TestPass()
    assert r.in_progress == None
    assert len(r.sections[1]["tests"]) == 1

    r.AddTest("Step by Step Test 2", True)
    assert r.in_progress != None
    assert r.in_progress["critical"] == True

    r.TestFail("Wrong Id")
    assert r.in_progress == None
    assert len(r.sections[1]["tests"]) == 2


    r.AddTest("Step by Step Test 3", False)
    assert r.in_progress != None
    assert r.in_progress["critical"] == False


    r.Complete()
    assert len(r.sections[1]["tests"]) == 3
    

 
   