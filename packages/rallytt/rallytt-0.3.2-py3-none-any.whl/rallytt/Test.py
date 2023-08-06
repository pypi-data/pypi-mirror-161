from colorama import Fore,Style,init
import os

if not os.environ.get("forceColor") == "1":
    init()

class Test:

    def __init__(self):
        self.tests = {}
    
    def test(self,condition,testName,**kwargs):
        self.tests[testName] = {
            "result":"pass" if condition else "fail",
            "kwargs": kwargs
        }
    
    def print(self):
        print("---------------")
        for testName in self.tests:
            test = self.tests[testName]
            print("\033[1m" + "Name: " + Style.RESET_ALL + Fore.CYAN + testName + Style.RESET_ALL)
            print("\033[1m" + "Result: " + Style.RESET_ALL + (Fore.GREEN if test["result"] == "pass" else Fore.RED) + test["result"] + Style.RESET_ALL)
            for key in test["kwargs"]:
                print(Style.DIM + str(key) + " = " + str(test["kwargs"][key]))
            print(Style.RESET_ALL+"---------------")
        if any([self.tests[testName]["result"] == "fail" for testName in self.tests]):
            os.environ["testsFailed"] = "1"