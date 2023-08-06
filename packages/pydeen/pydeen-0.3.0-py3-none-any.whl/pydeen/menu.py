"""
    Menu and user input utils
"""


class UserInput:
    def __init__(self, label:str, default:str=None):
        self.label   = label
        self.default = default

    def get_input(self, empty_allowed:bool=False):
        # label
        label = self.label
        if self.default != None:
            label += f" ({self.default}): "
        else:
            label += ": "    
        
        # input loop
        answer = ""
        valid = False
        while valid == False:
            answer = input(label)
            if self.default != None and ( answer == "" or answer == None ):
                answer = self.default
            if answer == "" and empty_allowed == True:
                valid = True
            elif len(answer) > 0:
                valid = True        

        return answer     

    def get_input_int(self, min:int=None, max:int=None):
        label = self.label
        if self.default != None:
            label += f" ({self.default}): "
        else:
            label += ": "    
        
        result = None
        answer = None
        while answer == None or answer == "":
            answer = input(label)
            if self.default != None and ( answer == "" or answer == None ):
                answer = self.default

            if answer.isdigit():
                result = int(answer)
                if min != None and min > result:
                    answer = None
                if max != None and max < result:
                    answer = None
            else:
                answer = None    
        return result     


class MenuAction:
    def __init__(self, menu, selected, cancel_entered:bool=False, quit_entered:bool=False):
        self.menu = menu
        self.selected = selected
        self.cancel_entered = cancel_entered
        self.quit_entered = quit_entered

    def is_quit_entered(self) -> bool:
        return self.quit_entered

    def is_cancel_entered(self) -> bool:
        return self.cancel_entered

    def is_selected(self) -> bool:
        if self.selected != None and self.quit_entered == False and self.cancel_entered == False:
            return True
        else: 
            return False

    def get_selection(self):
        return self.selected            



class Menu:
    def __init__(self, title, quit:bool=False, cancel:bool=True):
        self.title = title
        self.exit_text = "Quit"
        self.exit_code = "Q"
        self.exit_allowed = quit
        self.cancel_text = "Cancel"
        self.cancel_code = "C"
        self.cancel_allowed = cancel

    def show_menu(self) -> MenuAction:
        print()
        print(self.title)
        sep = ""
        for _ in range(len(self.title)):
            sep += '='
        print(sep)    
        return None


class MenuSelection(Menu):
    def __init__(self, title, entries:dict, quit:bool=False, cancel:bool=True):
        super().__init__(title, quit, cancel)
        self.entries = entries

    def show_menu(self) -> MenuAction:        
        # build menu from given    
        code = []
        text = []
        for key in self.entries.keys():
            entry_text = self.entries[key]
            if len(entry_text) > 0:
                code.append(key)
                text.append(entry_text)

        # menu loop       
        valid = False
        filter = None
        result = None

        while valid == False:
            # print menu
            super().show_menu()
            for index in range(len(text)):
                if filter == None:
                    print(f"{index+1} - {text[index]}")
                else:
                    if text[index].find(filter) >= 0:
                        print(f"{index+1} - {text[index]}")

            if self.cancel_allowed == True:
                print(f"{self.cancel_code} - {self.cancel_text}")

            if self.exit_allowed == True:
                print(f"{self.exit_code} - {self.exit_text}")

            # get user input
            answer = UserInput("\nEnter your selection").get_input()
            if answer.isdigit():
                int_answer = int(answer)
            else:
                int_answer = 0    

            # check answer
            if answer == self.exit_code:
                result = MenuAction(self, None, False, True)
            elif answer == self.cancel_code:
                result = MenuAction(self, None, True, False)
            elif int_answer > 0 and int_answer <= len(text):
                result = MenuAction(self, code[int_answer-1], False, False)
            elif len(answer) > 2 and answer[0] == "*" and answer[-1] == "*":
                filter = answer[1:-1]
                print("Filter: ", filter)

            if result != None:
                valid = True               

        return result

if __name__ == "__main__":
    entries = {
        "selection1" : "selection1",
        "selection2" : "selection2",
        "selection3" : "selection3",
        "selection4" : "selection4",
        "selection5" : "selection5",
    }
    menu = MenuSelection("Testmenue", entries, quit=True)
    action = menu.show_menu()
    if action != None and action.is_selected():
        print("Selected:", action.get_selection())
    else:
        print("Nothing selected. Cancel or Exit.")    