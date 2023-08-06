import os, sys, platform, time
from n4s import fs, strgs

## CLEAR TERMINAL
def clear():
        '''
        Clears the terminal
        '''
        ## WINDOWS
        if platform.system() == "Windows":
                clear = lambda: os.system('cls')
                clear()
                print()
        ## MACOS
        if platform.system() == "Darwin":
                os.system("clear")
                print()

## LIST OF USER DEFINED VARIABLES
def list_variables(Print_Variable_List: bool=False):
        '''
        Print_Variable_List: print list (boolean)

        Returns a list of user defined variables
        '''

        import __main__

        ## NEWLINE
        print()

        ## EMPTY ARRAY FOR OUR LIST OF VARIABLES
        n4s_var_list = []

        ## ITERATE THROUGH GLOBAL VARIABLES AND READ VARIABLE NAMES
        for var_name in __main__.__dict__:

                ## EXCLUDE VARIABLES THAT START WITH '__'
                if not var_name.startswith('__'):

                        ## GET VALUES
                        try:
                                ## READ VARIABLE VALUE
                                var_value = __main__.__dict__[var_name]

                                ## EXCLUDE MODULES AND FUNCTIONS
                                if not str(type(var_value)) == "<class 'module'>" and not str(type(var_value)) == "<class 'function'>":

                                        ## READ VARIABLE TYPE
                                        var_type = strgs.clean_text(strgs.filter_text(str(type(var_value)), ['class ']))

                                        ## CHECKS ONLY FOR...
                                        # INT, FLOAT, STR, LIST, TUPLE, DICT, SET, OBJECT, COMPLEX
                                        if var_type == 'int' or var_type == 'float' or var_type == 'str' or var_type == 'list' or var_type == 'tuple' or var_type == 'dict' or var_type == 'set' or var_type == 'object' or var_type == 'complex':

                                                ## PRINT: VARIABLE NAME, TYPE AND VALUE
                                                if Print_Variable_List:
                                                        print(f"Variable | {var_name}\n"
                                                                f"Type     | {var_type}\n"
                                                                f"Value    | {var_value}\n")

                                                ## APPEND OUR VARIABLE LIST
                                                n4s_var_list.append(var_name)

                                ## EXCLUDE VARIABLES FROM THIS FUNCTION
                                if var_name == 'Print_Variable_List' or var_name == 'n4s_var_list':
                                        pass
                        
                        ## ERROR
                        except Exception:
                                return print("\nn4s.term.list_variables():\n"
                                        f"Unable to process request\n")
        
        ## PRINT: VARIABLE LIST TO TERMINAL
        if Print_Variable_List:
                if len(n4s_var_list) < 1:
                        print('No user defined variables\n')
                else:
                        print(f"TOTAL COUNT: {len(n4s_var_list)}\n")
        
        ## RETURN VARIABLE LIST
        return n4s_var_list

## PAUSES FOR INPUT
def pause(message: str='', header: str='PAUSE'):
        '''
        | ARGS:

                message: print a message on pause

                header: pause message header

        | DESCRIPTION:

                Pauses a Python script with various follow-up actions.

        | ACTIONS:

                List Variables = vars

                Restart Script = r

                Quit Script = q
        '''

        ## PAUSE HEADER
        header = f"--- {str(header)} ---".upper()

        ## WITHOUT MESSAGE
        if message == '':

                ## OUTPUT
                action = input(f"\n{header}\nAction: ")
                print()
        
        ## WITH MESSAGE
        else:

                ## PRINT BOTTOM BORDER LINES
                border_lines = ''
                for line in range(len(str(header))):
                        border_lines = border_lines + "-"
                
                ## OUTPUT
                action = input(f"\n{header}\n{message}\n{border_lines}\nAction: ")
                print()
        
        ## ACTIONS
        if action:

                ## CONVERT INPUT TO LOWERCASE
                action = str(action).lower()

                ## LIST AVAILABLE ACTIONS
                if action == 'list':

                        ## PRINT ACTIONS
                        print(""
                        " List Variables = vars\n",
                        "Restart Script = r\n",
                        "Quit Script = q\n")
                        
                        ## RUN PAUSE AGAIN WITH ORIGINAL PARAMETERS
                        header = strgs.filter_text(header, ['---'])
                        pause(message, header)

                ## PRINT A LIST OF USER DEFINED VARIABLES
                if action == 'vars':

                        ## LIST VARIABLES W/ PRINT ENABLED
                        list_variables(True)

                        ## RUN PAUSE AGAIN WITH ORIGINAL PARAMETERS
                        header = strgs.filter_text(header, ['---'])
                        pause(message, header)

                ## RESTART
                if action == 'r':
                        fs.system('python-restart')

                ## RESTART AND CLEAR TERMINAL
                if action == 'rc':
                        clear()
                        fs.system('python-restart')

                ## QUIT
                if action == 'q':
                        fs.system('python-exit')

                ## QUIT AND CLEAR TERMINAL
                if action == 'qc':
                        clear()
                        fs.system('python-exit')

## RESTART AN APP
def restart_app():
        '''
        Restarts Python application
        '''
        python = sys.executable
        os.execl(python, python, * sys.argv)

## WAITS FOR X SECONDS
def wait(seconds):
        '''
        seconds: wait for x amount of seconds
        '''
        time.sleep(seconds)



## TESTS